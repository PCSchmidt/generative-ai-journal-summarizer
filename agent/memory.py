"""Conversation memory — short-term (message history) and long-term (SQLite).

Short-term: bounded message list with token-budget-aware truncation.
Long-term: persisted conversation artifacts in SQLite for cross-session retrieval.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Optional
from uuid import uuid4

from agent.schemas import Message, Role


class ConversationMemory:
    """Manages a single conversation's message history with bounded context."""

    def __init__(self, conversation_id: Optional[str] = None, max_messages: int = 40):
        self.conversation_id = conversation_id or uuid4().hex
        self.max_messages = max_messages
        self.messages: list[Message] = []
        self.created_at = datetime.utcnow().isoformat()

    def add(self, message: Message) -> None:
        self.messages.append(message)
        self._trim()

    def get_messages_for_api(self) -> list[dict]:
        """Return messages in OpenAI-compatible format for the next LLM call."""
        out = []
        for m in self.messages:
            d: dict = {"role": m.role.value, "content": m.content or ""}
            if m.tool_calls:
                d["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function_name,
                            "arguments": json.dumps(tc.function_args),
                        },
                    }
                    for tc in m.tool_calls
                ]
                d.pop("content", None)
            if m.tool_call_id:
                d["tool_call_id"] = m.tool_call_id
            if m.name:
                d["name"] = m.name
            out.append(d)
        return out

    def _trim(self) -> None:
        """Keep the system message + most recent messages within budget."""
        if len(self.messages) <= self.max_messages:
            return
        system_msgs = [m for m in self.messages if m.role == Role.system]
        other_msgs = [m for m in self.messages if m.role != Role.system]
        keep = self.max_messages - len(system_msgs)
        self.messages = system_msgs + other_msgs[-keep:]


class LongTermMemory:
    """Persists conversation summaries and artifacts in SQLite."""

    def __init__(self, db_path: str = "data/agent_memory.db"):
        self.db_path = db_path
        # For :memory: DBs, keep a single persistent connection
        # (each sqlite3.connect(":memory:") creates a separate DB).
        self._persistent_conn: sqlite3.Connection | None = None
        if db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(":memory:")
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._persistent_conn is not None:
            return self._persistent_conn
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    summary TEXT,
                    message_count INTEGER DEFAULT 0,
                    tool_calls_count INTEGER DEFAULT 0
                )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )"""
            )
            conn.commit()

    def save_conversation(
        self,
        conversation_id: str,
        summary: str,
        message_count: int,
        tool_calls_count: int,
    ) -> None:
        now = datetime.utcnow().isoformat()
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO conversations (conversation_id, created_at, updated_at, summary, message_count, tool_calls_count)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(conversation_id) DO UPDATE SET
                     updated_at = excluded.updated_at,
                     summary = excluded.summary,
                     message_count = excluded.message_count,
                     tool_calls_count = excluded.tool_calls_count""",
                (conversation_id, now, now, summary, message_count, tool_calls_count),
            )
            conn.commit()

    def save_artifact(
        self, conversation_id: str, artifact_type: str, content: str
    ) -> str:
        artifact_id = uuid4().hex
        now = datetime.utcnow().isoformat()
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?)",
                (artifact_id, conversation_id, artifact_type, content, now),
            )
            conn.commit()
        return artifact_id

    def get_recent_conversations(self, limit: int = 10) -> list[dict]:
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM conversations ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_conversation(self, conversation_id: str) -> Optional[dict]:
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM conversations WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()
            return dict(row) if row else None

    def get_artifacts(self, conversation_id: str) -> list[dict]:
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM artifacts WHERE conversation_id = ? ORDER BY created_at",
                (conversation_id,),
            ).fetchall()
            return [dict(r) for r in rows]
