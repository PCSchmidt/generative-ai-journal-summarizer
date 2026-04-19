#!/usr/bin/env python3
"""RAG Evaluation Runner.

Ingests the golden test set into a fresh journal store, runs retrieval queries,
and reports retrieval-quality metrics.  No LLM API calls required — this
evaluates the embedding + FAISS retrieval pipeline in isolation.

Usage:
    python -m eval.run_eval          # from project root
    python eval/run_eval.py          # also works
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.golden_set import EVAL_QUERIES, JOURNAL_ENTRIES
from eval.metrics import compute_aggregate_metrics, compute_query_metrics
from rag.retriever import JournalRetriever
from rag.store import JournalStore

# Top-k for retrieval evaluation
K = 3


def run() -> dict:
    """Ingest golden entries, run queries, return results dict."""
    tmp = tempfile.mkdtemp(prefix="rag_eval_")
    db_path = str(Path(tmp) / "eval.db")
    idx_path = str(Path(tmp) / "eval.faiss")

    try:
        store = JournalStore(db_path=db_path, index_path=idx_path)
        retriever = JournalRetriever(store=store)

        # --- Ingest ---
        entry_map: dict[int, str] = {}  # corpus_index → entry_id
        print(f"Ingesting {len(JOURNAL_ENTRIES)} golden entries …")
        for i, entry in enumerate(JOURNAL_ENTRIES):
            record = retriever.ingest(entry["text"], user_id="eval")
            entry_map[i] = record["entry_id"]
        print(f"  Store size: {store.count()} entries\n")

        # Reverse map: entry_id → corpus_index
        id_to_idx = {eid: idx for idx, eid in entry_map.items()}

        # --- Evaluate ---
        per_query: list[dict] = []
        for qi, q in enumerate(EVAL_QUERIES):
            results = retriever.retrieve(q["query"], top_k=K)
            retrieved_ids = [r["entry_id"] for r in results]
            retrieved_indices = [id_to_idx[eid] for eid in retrieved_ids if eid in id_to_idx]
            similarities = [r["similarity"] for r in results]

            metrics = compute_query_metrics(retrieved_indices, similarities, q["expected_relevant_indices"], k=K)
            per_query.append(metrics)

            print(f"Query {qi + 1}: {q['description']}")
            print(f"  Retrieved indices: {retrieved_indices}")
            print(f"  Expected indices:  {q['expected_relevant_indices']}")
            print(f"  Metrics: {json.dumps(metrics, indent=2)}")
            print()

        agg = compute_aggregate_metrics(per_query)
        print("=" * 60)
        print("AGGREGATE METRICS")
        print("=" * 60)
        for k, v in agg.items():
            print(f"  {k:<20s}: {v:.4f}")

        return {"per_query": per_query, "aggregate": agg}

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    results = run()
    # Persist results to JSON for later reference
    out = Path(__file__).resolve().parent.parent / "eval" / "results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {out}")
