"""Pydantic models for the agentic layer."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Tool definitions (OpenAI-compatible function-calling format)
# ---------------------------------------------------------------------------

class ToolParameter(BaseModel):
    type: str
    description: str
    enum: Optional[list[str]] = None


class ToolParameters(BaseModel):
    type: str = "object"
    properties: dict[str, ToolParameter]
    required: list[str] = Field(default_factory=list)


class ToolFunction(BaseModel):
    name: str
    description: str
    parameters: ToolParameters


class ToolDefinition(BaseModel):
    type: str = "function"
    function: ToolFunction


# ---------------------------------------------------------------------------
# Conversation / message types
# ---------------------------------------------------------------------------

class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"


class ToolCall(BaseModel):
    """A single tool invocation decided by the planner."""
    id: str = Field(default_factory=lambda: f"call_{uuid4().hex[:12]}")
    type: str = "function"
    function_name: str
    function_args: dict[str, Any]


class Message(BaseModel):
    role: Role
    content: Optional[str] = None
    tool_calls: Optional[list[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


# ---------------------------------------------------------------------------
# Trace / observability
# ---------------------------------------------------------------------------

class TraceStep(BaseModel):
    """One step in the ReAct reasoning trace."""
    step: int
    thought: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    observation: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AgentTrace(BaseModel):
    conversation_id: str
    steps: list[TraceStep] = Field(default_factory=list)
    total_tokens: int = 0
    total_tool_calls: int = 0
    latency_ms: float = 0.0


# ---------------------------------------------------------------------------
# API request / response
# ---------------------------------------------------------------------------

class AgentChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model: str = "groq-llama3-70b"
    user_token_id: Optional[str] = None
    max_steps: int = Field(default=6, ge=1, le=10)


class AgentChatResponse(BaseModel):
    conversation_id: str
    response: str
    trace: AgentTrace
    metadata: dict[str, Any] = Field(default_factory=dict)
