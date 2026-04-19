# Portfolio and Demo Narrative Block

Use this block directly for portfolio project pages, demo intros, and LinkedIn posts.

## Problem

Most journaling tools store text but analyze each entry in isolation — they do not connect patterns across entries or provide reliable, explainable insight generation. I built AI Journal Summarizer to deliver production-grade journal analysis with retrieval-augmented generation (RAG), explicit provider telemetry, and fallback transparency so users and reviewers can trust what happened on each inference.

## Architecture

- Frontend: Vercel-hosted web interface
- Backend: FastAPI on Railway
- Model layer: multi-provider routing (Groq + Hugging Face), premium/BYOK-ready paths
- RAG layer: sentence-transformers (all-MiniLM-L6-v2, 384-dim) → FAISS IndexFlatIP → SQLite journal store; retrieval-augmented prompts inject longitudinal context into LLM calls
- Agent layer: ReAct-style planner (built from Groq API primitives, no LangChain) with 5 tools (search, sentiment, trends, reflect, suggest), conversation + artifact memory (SQLite), observable planning traces; eval: 90% pass rate, 0.92 tool recall
- Eval layer: 20-entry golden test set, 5 thematic queries, retrieval metrics (precision@3, recall@3, MRR); 10-case agent benchmark (6 categories, tool accuracy + keyword grounding)
- Security layer: session auth, BYOK token ownership checks, encrypted token vault, CORS controls, and per-route rate limiting
- Observability: diagnostics endpoint, provider/fallback metadata on responses, and evidence snapshots

## Reliability Proof

I ran live production reliability proofs and captured artifacts for both failure and remediation phases.

- Initial proof identified real provider drift:
  - deprecated Groq model IDs
  - Hugging Face endpoint migration requirement
- Remediation shipped in production:
  - updated Groq model mappings
  - migrated Hugging Face integration to router API and compatible model mapping
- Final confirmation showed provider-backed inference for Groq and Hugging Face with no residual provider errors in diagnostics.

Evidence paths:

- `evidence/reliability-2026-04-12/`
- `evidence/reliability-2026-04-12-final-confirmed/`
- `evidence/RECRUITER_READY_EVIDENCE_BLOCK_2026-04-12.md`

## Outcomes

- Live API health and model routing validated in production
- Provider-backed inference restored after upstream API/model changes
- RAG pipeline delivering measurable retrieval quality: precision@3 = 0.80, MRR = 1.0, recall@3 = 0.77
- Production smoke quality gate established:
  - health, diagnostics, tier-info, and per-provider analyze checks
- Documentation aligned to measurable runtime behavior

## Tradeoffs and Engineering Decisions

- Chose explicit fallback metadata over silent failover to preserve operational trust
- Kept auth lightweight for portfolio velocity, while still enforcing token ownership boundaries
- Prioritized production evidence capture before additional feature expansion

## 30-Second Demo Script

"AI Journal Summarizer is a FastAPI + Vercel system that analyzes journal entries with multi-provider model routing and a RAG pipeline backed by FAISS + sentence-transformers. Past entries are embedded and retrieved to give the LLM longitudinal context — the system doesn't just analyze one entry, it connects patterns across your journal. I evaluated retrieval quality with a golden test set: precision@3 is 0.80, MRR is 1.0. I also intentionally expose provider/fallback metadata and diagnostics so reliability is observable."

## LinkedIn-Ready Version

Built and deployed an AI Journal Summarizer with FastAPI (Railway) + web frontend (Vercel), multi-provider model routing, and a retrieval-augmented generation (RAG) pipeline using sentence-transformers + FAISS. The RAG layer embeds journal entries and retrieves relevant past context for LLM analysis — evaluated with a 20-entry golden test set (precision@3 = 0.80, MRR = 1.0). During live validation I detected provider deprecations, implemented remediation, and confirmed provider-backed inference with a repeatable smoke quality gate. The project demonstrates production AI engineering discipline: measurable retrieval quality, transparent fallback behavior, and evidence-based documentation.
