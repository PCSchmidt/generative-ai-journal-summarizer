"""ReAct-style planner — the core reasoning loop.

Sends messages + tool schemas to the LLM, parses tool-call responses,
executes tools, feeds observations back, and repeats until the LLM
produces a final text response or hits the step limit.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import httpx

from agent.memory import ConversationMemory
from agent.schemas import AgentTrace, Message, Role, ToolCall, TraceStep
from agent.tools import execute_tool, get_tool_schemas_for_api

SYSTEM_PROMPT = """You are an intelligent journal analysis assistant with access to tools.
Your job is to help users understand patterns in their journal entries, analyze emotions,
identify trends over time, and suggest actionable improvements.

You MUST use tools to gather evidence before answering. Do NOT guess or fabricate information
about the user's journal. If you don't find relevant entries, say so honestly.

Approach each question methodically:
1. Search for relevant journal entries using journal_search.
2. Analyze the evidence (sentiment, trends) using the appropriate tools.
3. If your analysis could be biased or incomplete, use reflect to self-critique.
4. Provide actionable suggestions when appropriate using suggest_actions.

Always cite which journal entries informed your analysis. Be specific and grounded."""


class ReActPlanner:
    """Drives the ReAct loop: Thought → Action → Observation → repeat."""

    def __init__(
        self,
        groq_base_url: str,
        api_key: str,
        model_name: str = "llama-3.3-70b-versatile",
        *,
        retriever: Any = None,
        ai_service: Any = None,
    ):
        self.groq_base_url = groq_base_url
        self.api_key = api_key
        self.model_name = model_name
        self.retriever = retriever
        self.ai_service = ai_service
        self.tool_schemas = get_tool_schemas_for_api()

    async def run(
        self,
        user_message: str,
        memory: ConversationMemory,
        *,
        max_steps: int = 6,
    ) -> tuple[str, AgentTrace]:
        """Execute the ReAct loop and return (final_response, trace)."""
        trace = AgentTrace(conversation_id=memory.conversation_id)
        start = time.time()

        # Ensure system prompt is first
        if not memory.messages or memory.messages[0].role != Role.system:
            memory.add(Message(role=Role.system, content=SYSTEM_PROMPT))

        # Add user message
        memory.add(Message(role=Role.user, content=user_message))

        for step_idx in range(1, max_steps + 1):
            # ---- Call LLM with tools ----
            llm_response = await self._call_llm(memory)

            if llm_response is None:
                # LLM call failed — return graceful error
                trace.latency_ms = (time.time() - start) * 1000
                return "I'm sorry, I couldn't process your request right now. Please try again.", trace

            message = llm_response.get("choices", [{}])[0].get("message", {})
            usage = llm_response.get("usage", {})
            trace.total_tokens += usage.get("total_tokens", 0)

            tool_calls_raw = message.get("tool_calls")
            content = message.get("content")

            # ---- No tool calls → final response ----
            if not tool_calls_raw:
                final = content or ""
                memory.add(Message(role=Role.assistant, content=final))
                trace.steps.append(TraceStep(step=step_idx, thought=final))
                trace.latency_ms = (time.time() - start) * 1000
                return final, trace

            # ---- Parse tool calls ----
            parsed_calls = []
            for tc in tool_calls_raw:
                fn = tc.get("function", {})
                raw_args = fn.get("arguments", "{}")
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except json.JSONDecodeError:
                    args = {}
                parsed = ToolCall(
                    id=tc.get("id", ""),
                    function_name=fn.get("name", ""),
                    function_args=args,
                )
                parsed_calls.append(parsed)

            # Record assistant message with tool calls
            memory.add(Message(
                role=Role.assistant,
                content=content,
                tool_calls=parsed_calls,
            ))

            # ---- Execute each tool and feed observation back ----
            for tc in parsed_calls:
                trace.total_tool_calls += 1
                trace_step = TraceStep(
                    step=step_idx,
                    thought=content,
                    tool_call=tc,
                )

                observation = await execute_tool(
                    tc.function_name,
                    tc.function_args,
                    retriever=self.retriever,
                    ai_service=self.ai_service,
                )

                trace_step.observation = observation[:1000]  # cap for trace size
                trace.steps.append(trace_step)

                # Feed observation back as tool message
                memory.add(Message(
                    role=Role.tool,
                    content=observation,
                    tool_call_id=tc.id,
                    name=tc.function_name,
                ))

        # Exhausted max steps — ask LLM to synthesize
        memory.add(Message(
            role=Role.user,
            content="Please synthesize your findings into a final response now.",
        ))
        llm_response = await self._call_llm(memory, force_no_tools=True)
        final = ""
        if llm_response:
            final = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "")
        memory.add(Message(role=Role.assistant, content=final))
        trace.latency_ms = (time.time() - start) * 1000
        return final, trace

    async def _call_llm(self, memory: ConversationMemory, *, force_no_tools: bool = False) -> dict | None:
        """Single LLM call with optional tool schemas."""
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": memory.get_messages_for_api(),
            "temperature": 0.4,
            "max_tokens": 512,
        }
        if not force_no_tools:
            payload["tools"] = self.tool_schemas
            payload["tool_choice"] = "auto"

        max_retries = 5
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=45.0) as client:
                    resp = await client.post(
                        self.groq_base_url,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json=payload,
                    )
                    if resp.status_code == 200:
                        return resp.json()
                    if resp.status_code == 429 and attempt < max_retries - 1:
                        wait = max(float(resp.headers.get("retry-after", 2 ** (attempt + 1))), 5.0)
                        print(f"[agent/planner] Rate limited, retrying in {wait:.0f}s (attempt {attempt+1}/{max_retries})…")
                        await asyncio.sleep(wait)
                        continue
                    print(f"[agent/planner] LLM error: status={resp.status_code} body={resp.text[:300]}")
                    return None
            except Exception as exc:
                print(f"[agent/planner] LLM exception: {exc}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** (attempt + 1))
                    continue
                return None
        return None
