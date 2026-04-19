# Portfolio Integration Pack

Use this content directly in PCSchmidt.github.io and LinkedIn project posts.

Last verified: April 19, 2026

## Project Card Copy (Short)

### AI Journal Summarizer

Production-deployed journaling analysis system built with FastAPI (Railway) and web frontend (Vercel). Multi-provider model routing (Groq + Hugging Face), retrieval-augmented generation (RAG) with FAISS + sentence-transformers, evaluated retrieval quality (precision@3 = 0.80, MRR = 1.0), explicit fallback diagnostics, and a live smoke-test quality gate.

Links:

- Live App: https://generative-ai-journal-summarizer.vercel.app
- API: https://ai-journal-backend-production.up.railway.app
- Repo: https://github.com/PCSchmidt/generative-ai-journal-summarizer
- Reliability Evidence: https://github.com/PCSchmidt/generative-ai-journal-summarizer/tree/main/evidence/reliability-2026-04-12-final-confirmed

## Project Page Copy (Detailed)

### Problem

Most journaling applications store text but analyze each entry in isolation — they do not connect patterns across entries or provide reliable, explainable AI insight generation in production. I built AI Journal Summarizer to combine retrieval-augmented model inference with operational transparency.

### Architecture

- Frontend: static web UI on Vercel
- Backend: FastAPI service on Railway
- AI providers: Groq + Hugging Face with tiered model routing
- RAG pipeline: sentence-transformers (all-MiniLM-L6-v2, 384-dim) → FAISS IndexFlatIP → SQLite journal store; top-k retrieval augments LLM prompts with longitudinal context
- Eval harness: 20-entry golden test set, 5 thematic queries, precision/recall/MRR metrics
- Security: session auth, BYOK ownership controls, encrypted token vault
- Reliability telemetry: provider diagnostics and fallback metadata in responses

### Reliability Proof

During live validation, provider-level changes caused fallback-only behavior. I captured diagnostics evidence, implemented targeted provider remediations, and verified provider-backed inference end-to-end with repeatable smoke checks.

Validation gates:

- Backend API contract tests: `pytest backend/tests`
- Production smoke gate: `py -3 smoke_test_production.py --base-url https://ai-journal-backend-production.up.railway.app`

### Outcomes

- Production health and diagnostics verified
- Provider-backed inference restored for Groq and Hugging Face
- RAG pipeline delivering measurable retrieval quality: precision@3 = 0.80, MRR = 1.0, recall@3 = 0.77
- Repeatable quality gate established for release confidence
- Portfolio documentation aligned to measurable runtime evidence

### Tradeoffs

- Chose explicit fallback metadata over silent failover for auditability
- Used lightweight auth for velocity while enforcing BYOK ownership boundaries
- Prioritized reliability evidence and regression gates before additional feature expansion

## Recruiter/Interviewer 30-Second Script

AI Journal Summarizer is a production AI application that analyzes journal entries for sentiment, insights, and summaries using a FastAPI backend, multi-provider model routing, and a RAG pipeline that retrieves relevant past entries to give the LLM longitudinal context. I evaluated retrieval quality with a golden test set: precision@3 is 0.80, MRR is 1.0. I treat reliability as a first-class requirement: diagnostics expose provider behavior, fallback usage is explicit, and a production smoke gate validates health and provider-backed inference before claims are published.

## LinkedIn Post Copy

Built and deployed AI Journal Summarizer with FastAPI (Railway) + Vercel frontend, multi-provider model routing (Groq + Hugging Face), and a retrieval-augmented generation (RAG) pipeline using sentence-transformers + FAISS. Evaluated retrieval quality with a 20-entry golden test set (precision@3 = 0.80, MRR = 1.0). During live validation I identified provider deprecations, shipped remediations, and verified provider-backed inference with a repeatable smoke-test gate. Result: evidence-based AI engineering with measurable retrieval quality and transparent runtime behavior.

## Suggested Buttons for Portfolio Page

- Live Demo
- GitHub Repository
- Reliability Evidence
- Demo Guide

## Suggested Integration Metadata

- Status: Production deployed
- Last verified: April 19, 2026
- Stack: FastAPI, Python, Vercel, Railway, Groq, Hugging Face, FAISS, sentence-transformers
- Focus: RAG, retrieval evaluation, reliability, observability, secure token handling, API contract quality
