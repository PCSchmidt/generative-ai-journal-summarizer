#!/usr/bin/env python3
"""Production smoke tests for AI Journal Summarizer.

Checks:
1) /health
2) /api/ai/diagnostics
3) /api/ai/tier-info
4) /api/ai/sentiment for one Groq model and one Hugging Face model
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Tuple


def http_json(method: str, url: str, payload: Dict[str, Any] | None = None, timeout: int = 45) -> Tuple[int, Dict[str, Any]]:
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return exc.code, parsed


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run production smoke tests for AI Journal Summarizer")
    parser.add_argument("--base-url", default="https://ai-journal-backend-production.up.railway.app", help="Production API base URL")
    parser.add_argument("--timeout", type=int, default=45, help="HTTP timeout in seconds")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    print(f"Running smoke tests against: {base}")

    # 1) Health
    status, health = http_json("GET", f"{base}/health", timeout=args.timeout)
    assert_true(status == 200, f"/health returned {status}")
    assert_true(health.get("status") == "healthy", f"/health status unexpected: {health}")
    print("PASS /health")

    # 2) Diagnostics
    status, diagnostics_before = http_json("GET", f"{base}/api/ai/diagnostics", timeout=args.timeout)
    assert_true(status == 200, f"/api/ai/diagnostics returned {status}")
    assert_true("groq_configured" in diagnostics_before and "hf_configured" in diagnostics_before, "diagnostics missing provider flags")
    fallback_before = int(diagnostics_before.get("fallback_count", 0))
    print("PASS /api/ai/diagnostics")

    # 3) Tier info
    status, tier_info = http_json("GET", f"{base}/api/ai/tier-info", timeout=args.timeout)
    assert_true(status == 200, f"/api/ai/tier-info returned {status}")
    models = {m.get("key"): m for m in tier_info.get("models", [])}
    assert_true("groq-llama3-70b" in models, "tier-info missing groq-llama3-70b")
    assert_true("hf-mistral-7b" in models, "tier-info missing hf-mistral-7b")
    print("PASS /api/ai/tier-info")

    text = (
        "Smoke test validation for production reliability. "
        "This checks provider-backed inference metadata for portfolio quality gates."
    )

    # 4a) Analyze route for Groq
    payload = {"text": text, "task_type": "sentiment", "model": "groq-llama3-70b"}
    status, groq_resp = http_json("POST", f"{base}/api/ai/sentiment", payload=payload, timeout=args.timeout)
    assert_true(status == 200, f"Groq sentiment returned {status}: {groq_resp}")
    groq_md = groq_resp.get("metadata", {})
    assert_true(groq_md.get("provider_used") == "groq", f"Groq provider mismatch: {groq_md}")
    assert_true(groq_md.get("fallback_used") is False, f"Groq unexpectedly fell back: {groq_md}")
    print("PASS /api/ai/sentiment (Groq)")

    # 4b) Analyze route for Hugging Face
    payload = {"text": text, "task_type": "sentiment", "model": "hf-mistral-7b"}
    status, hf_resp = http_json("POST", f"{base}/api/ai/sentiment", payload=payload, timeout=args.timeout)
    assert_true(status == 200, f"HF sentiment returned {status}: {hf_resp}")
    hf_md = hf_resp.get("metadata", {})
    assert_true(hf_md.get("provider_used") == "huggingface", f"HF provider mismatch: {hf_md}")
    assert_true(hf_md.get("fallback_used") is False, f"HF unexpectedly fell back: {hf_md}")
    print("PASS /api/ai/sentiment (Hugging Face)")

    # Optional post-check diagnostics to ensure no fallback increments for this run.
    status, diagnostics_after = http_json("GET", f"{base}/api/ai/diagnostics", timeout=args.timeout)
    assert_true(status == 200, f"post diagnostics returned {status}")
    fallback_after = int(diagnostics_after.get("fallback_count", 0))
    assert_true(fallback_after == fallback_before, f"fallback_count changed during smoke test: {fallback_before} -> {fallback_after}")
    assert_true(not diagnostics_after.get("last_provider_errors"), f"provider errors present: {diagnostics_after.get('last_provider_errors')}")
    print("PASS diagnostics fallback/error post-check")

    print("\nSMOKE TEST SUITE PASSED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"\nSMOKE TEST SUITE FAILED: {exc}")
        raise SystemExit(1)
