"""Agent evaluation harness — task completion, tool accuracy, and latency benchmarks.

Run:  python -m agent.eval_agent           (requires GROQ_API_KEY)

Evaluates the agentic layer on three dimensions:
  1. Tool-call accuracy — does the agent pick the right tools?
  2. Task completion   — does the agent produce grounded, relevant answers?
  3. Latency           — end-to-end and per-step timing.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ── Evaluation benchmark ──────────────────────────────────────────────

@dataclass
class EvalCase:
    """A single evaluation query with expected tool usage and quality checks."""
    query: str
    expected_tools: list[str]  # tools that SHOULD be called
    quality_keywords: list[str]  # keywords expected in the response
    category: str  # for grouping results


EVAL_CASES: list[EvalCase] = [
    # Category: Search & Retrieval
    EvalCase(
        query="What have I written about anxiety recently?",
        expected_tools=["journal_search"],
        quality_keywords=["anxiety", "journal", "entries"],
        category="search",
    ),
    EvalCase(
        query="Find my journal entries about work stress.",
        expected_tools=["journal_search"],
        quality_keywords=["stress", "work"],
        category="search",
    ),
    # Category: Sentiment Analysis
    EvalCase(
        query="How am I feeling based on my recent entries?",
        expected_tools=["journal_search", "analyze_sentiment"],
        quality_keywords=["sentiment", "feeling"],
        category="sentiment",
    ),
    EvalCase(
        query="Analyze the emotional tone of my entries about family.",
        expected_tools=["journal_search", "analyze_sentiment"],
        quality_keywords=["family"],
        category="sentiment",
    ),
    # Category: Trend Analysis
    EvalCase(
        query="How has my mood around exercise changed over time?",
        expected_tools=["trend_analysis"],
        quality_keywords=["exercise", "trend"],
        category="trend",
    ),
    EvalCase(
        query="Show me the trend in my stress levels.",
        expected_tools=["trend_analysis"],
        quality_keywords=["stress", "trend"],
        category="trend",
    ),
    # Category: Reflection & Self-Critique
    EvalCase(
        query="I think I've been happier lately. Is that really true based on my journal?",
        expected_tools=["journal_search", "reflect"],
        quality_keywords=["happy", "happier"],
        category="reflection",
    ),
    # Category: Action Suggestions
    EvalCase(
        query="Based on my journal patterns, what should I do differently?",
        expected_tools=["journal_search", "suggest_actions"],
        quality_keywords=["suggest", "action"],
        category="actions",
    ),
    # Category: Multi-Tool Complex Queries
    EvalCase(
        query="Search my journal for entries about sleep, analyze the sentiment, and suggest improvements.",
        expected_tools=["journal_search", "analyze_sentiment", "suggest_actions"],
        quality_keywords=["sleep"],
        category="multi-tool",
    ),
    EvalCase(
        query="What patterns do you see in my journal about relationships? Be critical of your analysis.",
        expected_tools=["journal_search", "trend_analysis", "reflect"],
        quality_keywords=["relationship"],
        category="multi-tool",
    ),
]


@dataclass
class EvalResult:
    query: str
    category: str
    tools_called: list[str]
    expected_tools: list[str]
    tool_precision: float
    tool_recall: float
    keyword_hits: int
    keyword_total: int
    response_length: int
    latency_ms: float
    steps_taken: int
    tokens_used: int
    passed: bool
    error: str | None = None


@dataclass
class EvalSummary:
    total_cases: int = 0
    passed: int = 0
    failed: int = 0
    avg_tool_precision: float = 0.0
    avg_tool_recall: float = 0.0
    avg_keyword_hit_rate: float = 0.0
    avg_latency_ms: float = 0.0
    avg_steps: float = 0.0
    avg_tokens: float = 0.0
    by_category: dict = field(default_factory=dict)
    results: list[EvalResult] = field(default_factory=list)


async def run_eval(groq_api_key: str | None = None) -> EvalSummary:
    """Run the full evaluation suite and return summary metrics."""
    from agent.executor import AgentExecutor

    api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")
    if not api_key:
        print("⚠️  GROQ_API_KEY not set — skipping eval")
        return EvalSummary()

    groq_url = "https://api.groq.com/openai/v1/chat/completions"

    # Build executor with a minimal mock retriever + ai_service
    executor = AgentExecutor(
        groq_base_url=groq_url,
        api_key=api_key,
        retriever=_MockRetriever(),
        ai_service=_MockAIService(),
        db_path=":memory:",
    )

    summary = EvalSummary()
    cat_stats: dict[str, list[EvalResult]] = {}

    for case in EVAL_CASES:
        print(f"\n▶ [{case.category}] {case.query[:60]}…")
        result = await _eval_one(executor, case)
        summary.results.append(result)
        cat_stats.setdefault(case.category, []).append(result)

        status = "✅" if result.passed else "❌"
        print(f"  {status} tools={result.tools_called} latency={result.latency_ms:.0f}ms "
              f"precision={result.tool_precision:.2f} recall={result.tool_recall:.2f} "
              f"keywords={result.keyword_hits}/{result.keyword_total}")
        if result.error:
            print(f"      error: {result.error[:200]}")

        # Rate limit: Scout has 30K TPM — space out to stay within budget
        await asyncio.sleep(20)

    # Aggregate
    n = len(summary.results)
    summary.total_cases = n
    summary.passed = sum(1 for r in summary.results if r.passed)
    summary.failed = n - summary.passed
    summary.avg_tool_precision = _avg([r.tool_precision for r in summary.results])
    summary.avg_tool_recall = _avg([r.tool_recall for r in summary.results])
    summary.avg_keyword_hit_rate = _avg(
        [r.keyword_hits / max(r.keyword_total, 1) for r in summary.results]
    )
    summary.avg_latency_ms = _avg([r.latency_ms for r in summary.results])
    summary.avg_steps = _avg([r.steps_taken for r in summary.results])
    summary.avg_tokens = _avg([r.tokens_used for r in summary.results])

    for cat, results in cat_stats.items():
        summary.by_category[cat] = {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "avg_precision": _avg([r.tool_precision for r in results]),
            "avg_recall": _avg([r.tool_recall for r in results]),
            "avg_latency_ms": _avg([r.latency_ms for r in results]),
        }

    return summary


async def _eval_one(executor, case: EvalCase) -> EvalResult:
    """Evaluate a single case."""
    try:
        resp = await executor.chat(message=case.query, model="groq-llama4-scout", max_steps=4)

        tools_called = []
        for step in resp.trace.steps:
            if step.tool_call:
                tools_called.append(step.tool_call.function_name)
        tools_called_set = set(tools_called)
        expected_set = set(case.expected_tools)

        # Precision: of tools called, how many were expected?
        precision = (
            len(tools_called_set & expected_set) / len(tools_called_set)
            if tools_called_set else 0.0
        )
        # Recall: of expected tools, how many were called?
        recall = (
            len(tools_called_set & expected_set) / len(expected_set)
            if expected_set else 1.0
        )

        response_lower = resp.response.lower()
        keyword_hits = sum(1 for kw in case.quality_keywords if kw.lower() in response_lower)

        passed = recall >= 0.5 and keyword_hits >= 1

        return EvalResult(
            query=case.query,
            category=case.category,
            tools_called=tools_called,
            expected_tools=case.expected_tools,
            tool_precision=precision,
            tool_recall=recall,
            keyword_hits=keyword_hits,
            keyword_total=len(case.quality_keywords),
            response_length=len(resp.response),
            latency_ms=resp.trace.latency_ms,
            steps_taken=len(resp.trace.steps),
            tokens_used=resp.trace.total_tokens,
            passed=passed,
        )
    except Exception as exc:
        return EvalResult(
            query=case.query,
            category=case.category,
            tools_called=[],
            expected_tools=case.expected_tools,
            tool_precision=0.0,
            tool_recall=0.0,
            keyword_hits=0,
            keyword_total=len(case.quality_keywords),
            response_length=0,
            latency_ms=0.0,
            steps_taken=0,
            tokens_used=0,
            passed=False,
            error=str(exc),
        )


def _avg(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


# ── Mock objects for offline eval (returns synthetic data) ────────────

class _MockRetriever:
    """Returns canned journal entries so eval runs without a real DB."""

    _ENTRIES = [
        {
            "text": "Feeling really stressed about the work deadline. My sleep has been terrible.",
            "created_at": "2025-01-10",
            "similarity": 0.92,
        },
        {
            "text": "Had a great run today — exercise always lifts my mood. Feeling grateful for family.",
            "created_at": "2025-01-12",
            "similarity": 0.88,
        },
        {
            "text": "Anxiety is creeping back in. I need to focus on breathing exercises and journaling more.",
            "created_at": "2025-01-15",
            "similarity": 0.85,
        },
        {
            "text": "Relationship with my partner feels stronger this week. We talked about our stress triggers.",
            "created_at": "2025-01-18",
            "similarity": 0.82,
        },
        {
            "text": "Sleep quality improving since I started the new routine. Less anxiety overall.",
            "created_at": "2025-01-20",
            "similarity": 0.80,
        },
    ]

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        return self._ENTRIES[:top_k]


class _MockAIService:
    """Returns canned sentiment so eval runs without a real LLM call."""

    groq_base_url = "https://api.groq.com/openai/v1/chat/completions"
    groq_api_key = os.getenv("GROQ_API_KEY", "")

    async def analyze_sentiment(self, text: str, model: str = "groq-llama3-8b"):
        return {
            "sentiment": "mixed",
            "confidence": 0.78,
            "result": "The text expresses both positive and negative emotions. Key themes include stress management and personal growth.",
        }


# ── CLI entry point ───────────────────────────────────────────────────

def print_summary(summary: EvalSummary) -> None:
    print("\n" + "=" * 70)
    print("AGENT EVALUATION RESULTS")
    print("=" * 70)
    print(f"Total cases:         {summary.total_cases}")
    print(f"Passed:              {summary.passed}/{summary.total_cases} ({summary.passed/max(summary.total_cases,1)*100:.0f}%)")
    print(f"Avg tool precision:  {summary.avg_tool_precision:.2f}")
    print(f"Avg tool recall:     {summary.avg_tool_recall:.2f}")
    print(f"Avg keyword hit %:   {summary.avg_keyword_hit_rate:.2f}")
    print(f"Avg latency:         {summary.avg_latency_ms:.0f}ms")
    print(f"Avg steps/query:     {summary.avg_steps:.1f}")
    print(f"Avg tokens/query:    {summary.avg_tokens:.0f}")
    print()
    print("By category:")
    for cat, stats in summary.by_category.items():
        print(f"  {cat:15s}  pass={stats['passed']}/{stats['total']}  "
              f"precision={stats['avg_precision']:.2f}  recall={stats['avg_recall']:.2f}  "
              f"latency={stats['avg_latency_ms']:.0f}ms")
    print("=" * 70)


def save_results(summary: EvalSummary, path: str = "agent/eval_results.json") -> None:
    data = {
        "total_cases": summary.total_cases,
        "passed": summary.passed,
        "failed": summary.failed,
        "avg_tool_precision": round(summary.avg_tool_precision, 3),
        "avg_tool_recall": round(summary.avg_tool_recall, 3),
        "avg_keyword_hit_rate": round(summary.avg_keyword_hit_rate, 3),
        "avg_latency_ms": round(summary.avg_latency_ms, 1),
        "avg_steps": round(summary.avg_steps, 1),
        "avg_tokens": round(summary.avg_tokens, 0),
        "by_category": summary.by_category,
        "results": [
            {
                "query": r.query,
                "category": r.category,
                "tools_called": r.tools_called,
                "expected_tools": r.expected_tools,
                "tool_precision": round(r.tool_precision, 3),
                "tool_recall": round(r.tool_recall, 3),
                "keyword_hits": r.keyword_hits,
                "keyword_total": r.keyword_total,
                "response_length": r.response_length,
                "latency_ms": round(r.latency_ms, 1),
                "steps_taken": r.steps_taken,
                "tokens_used": r.tokens_used,
                "passed": r.passed,
                "error": r.error,
            }
            for r in summary.results
        ],
    }
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\n📄 Results saved to {path}")


if __name__ == "__main__":
    summary = asyncio.run(run_eval())
    print_summary(summary)
    save_results(summary)
