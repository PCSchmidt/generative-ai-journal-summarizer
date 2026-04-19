"""Tool definitions and implementations for the agentic layer.

Five tools built from API primitives — no LangChain wrappers.
Each tool is a plain async function + an OpenAI-compatible schema.
"""

from __future__ import annotations

import json
from typing import Any

from agent.schemas import ToolDefinition, ToolFunction, ToolParameter, ToolParameters


# =========================================================================
# Tool registry
# =========================================================================

_TOOL_IMPLS: dict[str, Any] = {}  # name → async callable


def _register(name: str):
    """Decorator that registers a tool implementation."""
    def wrap(fn):
        _TOOL_IMPLS[name] = fn
        return fn
    return wrap


async def execute_tool(name: str, args: dict[str, Any], *, retriever, ai_service) -> str:
    """Run a registered tool and return its string observation."""
    fn = _TOOL_IMPLS.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = await fn(args, retriever=retriever, ai_service=ai_service)
        return json.dumps(result, default=str) if not isinstance(result, str) else result
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# =========================================================================
# 1. journal_search — semantic search over past journal entries
# =========================================================================

JOURNAL_SEARCH_SCHEMA = ToolDefinition(
    function=ToolFunction(
        name="journal_search",
        description=(
            "Search the user's past journal entries by semantic similarity. "
            "Returns the most relevant entries with dates and similarity scores. "
            "Use this to find entries about specific topics, emotions, or events."
        ),
        parameters=ToolParameters(
            properties={
                "query": ToolParameter(
                    type="string",
                    description="Natural-language search query describing what to look for in past entries.",
                ),
            },
            required=["query"],
        ),
    ),
)


@_register("journal_search")
async def _journal_search(args: dict, *, retriever, ai_service) -> dict:
    query = args["query"]
    top_k = min(int(args.get("top_k", 5)), 10)
    results = retriever.retrieve(query, top_k=top_k)
    return {
        "entries_found": len(results),
        "entries": [
            {
                "text": r["text"][:500],
                "date": r.get("created_at", "unknown"),
                "similarity": round(r.get("similarity", 0.0), 3),
            }
            for r in results
        ],
    }


# =========================================================================
# 2. analyze_sentiment — run sentiment analysis on a piece of text
# =========================================================================

ANALYZE_SENTIMENT_SCHEMA = ToolDefinition(
    function=ToolFunction(
        name="analyze_sentiment",
        description=(
            "Analyze the emotional tone and sentiment of a given text. "
            "Returns sentiment label, confidence, and a brief explanation. "
            "Use this when you need to understand the emotional state in an entry."
        ),
        parameters=ToolParameters(
            properties={
                "text": ToolParameter(
                    type="string",
                    description="The text to analyze for sentiment.",
                ),
            },
            required=["text"],
        ),
    ),
)


@_register("analyze_sentiment")
async def _analyze_sentiment(args: dict, *, retriever, ai_service) -> dict:
    text = args["text"]
    # Use the existing AI service sentiment method (Groq by default)
    result = await ai_service.analyze_sentiment(text, model="groq-llama3-8b")
    return {
        "sentiment": result.get("sentiment", "unknown"),
        "confidence": result.get("confidence", 0.0),
        "analysis": result.get("result", "")[:400],
    }


# =========================================================================
# 3. trend_analysis — detect patterns across multiple entries
# =========================================================================

TREND_ANALYSIS_SCHEMA = ToolDefinition(
    function=ToolFunction(
        name="trend_analysis",
        description=(
            "Analyze patterns and trends across the user's journal entries. "
            "Examines frequency of themes, sentiment trajectory over time, and "
            "recurring topics. Use this for questions about change over time."
        ),
        parameters=ToolParameters(
            properties={
                "theme": ToolParameter(
                    type="string",
                    description="The theme or topic to track (e.g., 'stress', 'exercise', 'work').",
                ),
            },
            required=["theme"],
        ),
    ),
)


@_register("trend_analysis")
async def _trend_analysis(args: dict, *, retriever, ai_service) -> dict:
    theme = args["theme"]
    limit = min(int(args.get("limit", 20)), 50)

    entries = retriever.retrieve(theme, top_k=limit)
    if not entries:
        return {"trend": "no_data", "entries_scanned": 0, "summary": "No journal entries found for this theme."}

    # Build a compact timeline for the LLM to reason over
    timeline = []
    for e in entries:
        timeline.append({
            "date": e.get("created_at", "unknown"),
            "snippet": e["text"][:200],
            "similarity": round(e.get("similarity", 0.0), 3),
        })

    return {
        "theme": theme,
        "entries_scanned": len(timeline),
        "timeline": timeline,
    }


# =========================================================================
# 4. reflect — LLM self-critique of its own reasoning
# =========================================================================

REFLECT_SCHEMA = ToolDefinition(
    function=ToolFunction(
        name="reflect",
        description=(
            "Critically review the analysis so far and identify gaps, biases, or "
            "alternative interpretations. Use this after gathering evidence to "
            "ensure the final response is balanced and well-supported."
        ),
        parameters=ToolParameters(
            properties={
                "analysis_so_far": ToolParameter(
                    type="string",
                    description="Summary of the analysis and conclusions reached so far.",
                ),
                "user_question": ToolParameter(
                    type="string",
                    description="The original user question for context.",
                ),
            },
            required=["analysis_so_far", "user_question"],
        ),
    ),
)


@_register("reflect")
async def _reflect(args: dict, *, retriever, ai_service) -> dict:
    import httpx

    analysis = args["analysis_so_far"]
    question = args["user_question"]

    prompt = (
        "You are a critical reviewer. Given the user's question and the analysis so far, "
        "identify:\n"
        "1. Any unsupported claims or assumptions\n"
        "2. Alternative interpretations of the evidence\n"
        "3. Missing information that would strengthen the analysis\n"
        "4. Potential biases in the reasoning\n\n"
        f"User question: {question}\n\n"
        f"Analysis so far: {analysis}\n\n"
        "Respond concisely with specific, actionable critique."
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                ai_service.groq_base_url,
                headers={
                    "Authorization": f"Bearer {ai_service.groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 300,
                },
            )
            if response.status_code == 200:
                critique = response.json()["choices"][0]["message"]["content"]
                return {"critique": critique}
            return {"critique": "Reflection unavailable.", "error": f"status {response.status_code}"}
    except Exception as exc:
        return {"critique": "Reflection unavailable.", "error": str(exc)}


# =========================================================================
# 5. suggest_actions — generate actionable next steps
# =========================================================================

SUGGEST_ACTIONS_SCHEMA = ToolDefinition(
    function=ToolFunction(
        name="suggest_actions",
        description=(
            "Generate specific, actionable suggestions based on journal patterns. "
            "Use this after analyzing entries to provide the user with concrete "
            "steps they can take."
        ),
        parameters=ToolParameters(
            properties={
                "context": ToolParameter(
                    type="string",
                    description="Summary of patterns and insights discovered from journal entries.",
                ),
                "focus_area": ToolParameter(
                    type="string",
                    description="The area to focus suggestions on (e.g., 'stress management', 'career growth').",
                ),
            },
            required=["context"],
        ),
    ),
)


@_register("suggest_actions")
async def _suggest_actions(args: dict, *, retriever, ai_service) -> dict:
    import httpx

    context = args["context"]
    focus = args.get("focus_area", "general wellbeing")

    prompt = (
        "Based on the following journal analysis, generate 3-5 specific, actionable "
        "suggestions the person can implement this week. Be concrete — avoid vague advice "
        f"like 'be mindful.' Focus area: {focus}\n\n"
        f"Journal analysis:\n{context}\n\n"
        "Format each suggestion as a numbered item with a clear action and brief rationale."
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                ai_service.groq_base_url,
                headers={
                    "Authorization": f"Bearer {ai_service.groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 400,
                },
            )
            if response.status_code == 200:
                suggestions = response.json()["choices"][0]["message"]["content"]
                return {"suggestions": suggestions, "focus_area": focus}
            return {"suggestions": "Suggestion generation unavailable.", "error": f"status {response.status_code}"}
    except Exception as exc:
        return {"suggestions": "Suggestion generation unavailable.", "error": str(exc)}


# =========================================================================
# Public: all tool schemas for the planner
# =========================================================================

ALL_TOOL_DEFINITIONS: list[ToolDefinition] = [
    JOURNAL_SEARCH_SCHEMA,
    ANALYZE_SENTIMENT_SCHEMA,
    TREND_ANALYSIS_SCHEMA,
    REFLECT_SCHEMA,
    SUGGEST_ACTIONS_SCHEMA,
]


def get_tool_schemas_for_api() -> list[dict]:
    """Return tool definitions in the OpenAI function-calling JSON format."""
    return [t.model_dump(exclude_none=True) for t in ALL_TOOL_DEFINITIONS]
