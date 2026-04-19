"""Persistent journal entry store: SQLite for text + FAISS for vector search."""

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import faiss
import numpy as np


class JournalStore:
    """Stores journal entries with text in SQLite and embeddings in a FAISS index."""

    def __init__(self, db_path: str = "data/journal.db", index_path: str = "data/journal.faiss", dim: int = 384):
        self.db_path = db_path
        self.index_path = index_path
        self.dim = dim

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._load_or_create_index()

    # ── database ──────────────────────────────────────────────────────

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS journal_entries (
                    entry_id   TEXT PRIMARY KEY,
                    text       TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    user_id    TEXT,
                    faiss_idx  INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    # ── FAISS index ───────────────────────────────────────────────────

    def _load_or_create_index(self) -> None:
        if Path(self.index_path).exists():
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexFlatIP(self.dim)  # inner-product on L2-normalised vectors = cosine sim

    def _persist_index(self) -> None:
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, self.index_path)

    # ── public API ────────────────────────────────────────────────────

    def add_entry(self, text: str, embedding: np.ndarray, user_id: Optional[str] = None) -> dict:
        """Store a journal entry and its embedding. Returns the created record."""
        entry_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        # Normalise so inner-product = cosine similarity
        vec = np.array(embedding, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(vec)

        faiss_idx = self.index.ntotal
        self.index.add(vec)
        self._persist_index()

        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO journal_entries (entry_id, text, created_at, user_id, faiss_idx) VALUES (?, ?, ?, ?, ?)",
                (entry_id, text, created_at, user_id, faiss_idx),
            )
            conn.commit()

        return {"entry_id": entry_id, "created_at": created_at, "faiss_idx": faiss_idx}

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> list[dict]:
        """Return the top-k most similar journal entries for a query embedding."""
        if self.index.ntotal == 0:
            return []

        vec = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(vec)

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(vec, k)

        # Map FAISS indices back to entries
        results = []
        with self._get_conn() as conn:
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:
                    continue
                row = conn.execute(
                    "SELECT entry_id, text, created_at, user_id FROM journal_entries WHERE faiss_idx = ?",
                    (int(idx),),
                ).fetchone()
                if row:
                    results.append({
                        "entry_id": row["entry_id"],
                        "text": row["text"],
                        "created_at": row["created_at"],
                        "similarity": float(score),
                    })

        return results

    def list_entries(self, user_id: Optional[str] = None, limit: int = 50) -> list[dict]:
        """List recent journal entries, optionally filtered by user."""
        with self._get_conn() as conn:
            if user_id:
                rows = conn.execute(
                    "SELECT entry_id, text, created_at, user_id FROM journal_entries WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                    (user_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT entry_id, text, created_at, user_id FROM journal_entries ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [dict(r) for r in rows]

    def count(self) -> int:
        return self.index.ntotal

    def reset(self) -> None:
        """Delete all entries and recreate the index. Used in tests."""
        self.index = faiss.IndexFlatIP(self.dim)
        self._persist_index()
        with self._get_conn() as conn:
            conn.execute("DELETE FROM journal_entries")
            conn.commit()
