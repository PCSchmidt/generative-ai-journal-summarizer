"""Retrieval quality metrics for RAG evaluation.

Metrics focus on retrieval (the controllable part) rather than LLM generation
quality (which depends on the provider/model and is harder to evaluate offline).
"""

from __future__ import annotations


def recall_at_k(retrieved_indices: list[int], expected_indices: list[int], k: int | None = None) -> float:
    """Fraction of expected entries that appear in the top-k retrieved results.

    recall@k = |retrieved ∩ expected| / |expected|
    """
    if not expected_indices:
        return 1.0
    retrieved_set = set(retrieved_indices[:k] if k else retrieved_indices)
    return len(retrieved_set & set(expected_indices)) / len(expected_indices)


def precision_at_k(retrieved_indices: list[int], expected_indices: list[int], k: int | None = None) -> float:
    """Fraction of top-k retrieved results that are in the expected set.

    precision@k = |retrieved ∩ expected| / k
    """
    top = retrieved_indices[:k] if k else retrieved_indices
    if not top:
        return 0.0
    return len(set(top) & set(expected_indices)) / len(top)


def mrr(retrieved_indices: list[int], expected_indices: list[int]) -> float:
    """Mean Reciprocal Rank: 1/(rank of first relevant result).

    Returns 0.0 if no expected entry is found in retrieved results.
    """
    expected_set = set(expected_indices)
    for rank, idx in enumerate(retrieved_indices, start=1):
        if idx in expected_set:
            return 1.0 / rank
    return 0.0


def avg_similarity(similarities: list[float]) -> float:
    """Average cosine similarity of retrieved results."""
    return sum(similarities) / len(similarities) if similarities else 0.0


def compute_query_metrics(
    retrieved_indices: list[int],
    similarities: list[float],
    expected_indices: list[int],
    k: int = 3,
) -> dict:
    """Compute all metrics for a single query."""
    return {
        "recall@k": round(recall_at_k(retrieved_indices, expected_indices, k), 4),
        "precision@k": round(precision_at_k(retrieved_indices, expected_indices, k), 4),
        "mrr": round(mrr(retrieved_indices, expected_indices), 4),
        "avg_similarity": round(avg_similarity(similarities), 4),
    }


def compute_aggregate_metrics(per_query: list[dict]) -> dict:
    """Average metrics across all queries."""
    if not per_query:
        return {}
    keys = per_query[0].keys()
    return {k: round(sum(q[k] for q in per_query) / len(per_query), 4) for k in keys}
