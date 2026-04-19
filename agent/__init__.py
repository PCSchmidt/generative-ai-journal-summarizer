"""Agentic layer for the AI Journal Summarizer.

Provides a ReAct-style reasoning agent with 5 tools:
- journal_search: semantic retrieval over past entries
- analyze_sentiment: emotion analysis on text
- trend_analysis: pattern detection across entries over time
- reflect: LLM self-critique of its own reasoning
- suggest_actions: actionable next steps based on patterns

Architecture: API primitives (no LangChain) → function calling → ReAct loop → memory.
"""

from agent.executor import AgentExecutor
from agent.memory import ConversationMemory, LongTermMemory
from agent.planner import ReActPlanner
from agent.schemas import AgentChatRequest, AgentChatResponse, AgentTrace

__all__ = [
    "AgentExecutor",
    "AgentChatRequest",
    "AgentChatResponse",
    "AgentTrace",
    "ConversationMemory",
    "LongTermMemory",
    "ReActPlanner",
]
