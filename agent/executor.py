"""Agent executor — top-level orchestrator that ties planner + memory + tools.

This is the single entry point used by main.py endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from agent.memory import ConversationMemory, LongTermMemory
from agent.planner import ReActPlanner
from agent.schemas import AgentChatResponse, AgentTrace


class AgentExecutor:
    """Stateful executor managing conversations and the ReAct planner."""

    def __init__(
        self,
        groq_base_url: str,
        api_key: str,
        *,
        retriever: Any = None,
        ai_service: Any = None,
        db_path: str = "data/agent_memory.db",
    ):
        self.planner = ReActPlanner(
            groq_base_url=groq_base_url,
            api_key=api_key,
            retriever=retriever,
            ai_service=ai_service,
        )
        self.long_term = LongTermMemory(db_path=db_path)
        # In-memory conversation cache (keyed by conversation_id)
        self._conversations: dict[str, ConversationMemory] = {}

    def _get_or_create_conversation(self, conversation_id: Optional[str]) -> ConversationMemory:
        if conversation_id and conversation_id in self._conversations:
            return self._conversations[conversation_id]
        mem = ConversationMemory(conversation_id=conversation_id)
        self._conversations[mem.conversation_id] = mem
        return mem

    async def chat(
        self,
        message: str,
        *,
        conversation_id: Optional[str] = None,
        model: str = "groq-llama3-70b",
        max_steps: int = 6,
    ) -> AgentChatResponse:
        """Handle one user turn through the full agentic pipeline."""

        memory = self._get_or_create_conversation(conversation_id)

        # Resolve model name from the model registry key
        model_name = self._resolve_model_name(model)
        self.planner.model_name = model_name

        response_text, trace = await self.planner.run(
            message, memory, max_steps=max_steps
        )

        # Persist to long-term memory
        self.long_term.save_conversation(
            conversation_id=memory.conversation_id,
            summary=response_text[:500],
            message_count=len(memory.messages),
            tool_calls_count=trace.total_tool_calls,
        )

        # Save the response as an artifact
        if response_text:
            self.long_term.save_artifact(
                conversation_id=memory.conversation_id,
                artifact_type="agent_response",
                content=response_text,
            )

        return AgentChatResponse(
            conversation_id=memory.conversation_id,
            response=response_text,
            trace=trace,
            metadata={
                "model": model,
                "model_name": model_name,
                "steps_taken": len(trace.steps),
                "tools_called": trace.total_tool_calls,
                "total_tokens": trace.total_tokens,
                "latency_ms": round(trace.latency_ms, 1),
            },
        )

    def get_conversation_history(self, conversation_id: str) -> dict:
        """Return conversation details and artifacts."""
        conv = self.long_term.get_conversation(conversation_id)
        artifacts = self.long_term.get_artifacts(conversation_id)
        messages = []
        if conversation_id in self._conversations:
            mem = self._conversations[conversation_id]
            messages = [
                {"role": m.role.value, "content": m.content}
                for m in mem.messages
                if m.role in ("user", "assistant") and m.content
            ]
        return {
            "conversation": conv,
            "artifacts": artifacts,
            "messages": messages,
        }

    def get_recent_conversations(self, limit: int = 10) -> list[dict]:
        return self.long_term.get_recent_conversations(limit=limit)

    @staticmethod
    def _resolve_model_name(model_key: str) -> str:
        """Map a model registry key to the actual model name for the API."""
        mapping = {
            "groq-llama3-8b": "llama-3.1-8b-instant",
            "groq-llama3-70b": "llama-3.3-70b-versatile",
            "groq-llama4-scout": "meta-llama/llama-4-scout-17b-16e-instruct",
            "groq-mixtral": "mixtral-8x7b-32768",
        }
        return mapping.get(model_key, model_key)
