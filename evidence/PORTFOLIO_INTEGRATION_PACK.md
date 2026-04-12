# Portfolio Integration Pack

Use this content directly in PCSchmidt.github.io and LinkedIn project posts.

Last verified: April 12, 2026

## Project Card Copy (Short)

### AI Journal Summarizer

Production-deployed journaling analysis system built with FastAPI (Railway) and web frontend (Vercel). Multi-provider model routing (Groq + Hugging Face), explicit fallback diagnostics, and a live smoke-test quality gate for reliability validation.

Links:

- Live App: https://generative-ai-journal-summarizer.vercel.app
- API: https://ai-journal-backend-production.up.railway.app
- Repo: https://github.com/PCSchmidt/generative-ai-journal-summarizer
- Reliability Evidence: https://github.com/PCSchmidt/generative-ai-journal-summarizer/tree/main/evidence/reliability-2026-04-12-final-confirmed

## Project Page Copy (Detailed)

### Problem

Most journaling applications store text but do not provide reliable, explainable AI insight generation in production. I built AI Journal Summarizer to combine model-backed inference with operational transparency.

### Architecture

- Frontend: static web UI on Vercel
- Backend: FastAPI service on Railway
- AI providers: Groq + Hugging Face with tiered model routing
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
- Repeatable quality gate established for release confidence
- Portfolio documentation aligned to measurable runtime evidence

### Tradeoffs

- Chose explicit fallback metadata over silent failover for auditability
- Used lightweight auth for velocity while enforcing BYOK ownership boundaries
- Prioritized reliability evidence and regression gates before additional feature expansion

## Recruiter/Interviewer 30-Second Script

AI Journal Summarizer is a production AI application that analyzes journal entries for sentiment, insights, and summaries using a FastAPI backend and multi-provider model routing. I treat reliability as a first-class requirement: diagnostics expose provider behavior, fallback usage is explicit, and a production smoke gate validates health and provider-backed inference before claims are published.

## LinkedIn Post Copy

Built and deployed AI Journal Summarizer with FastAPI (Railway) + Vercel frontend, multi-provider model routing (Groq + Hugging Face), and production reliability instrumentation. During live validation I identified provider deprecations, shipped remediations, and verified provider-backed inference with a repeatable smoke-test gate. Result: evidence-based AI engineering with transparent runtime behavior and robust release checks.

## Suggested Buttons for Portfolio Page

- Live Demo
- GitHub Repository
- Reliability Evidence
- Demo Guide

## Suggested Integration Metadata

- Status: Production deployed
- Last verified: April 12, 2026
- Stack: FastAPI, Python, Vercel, Railway, Groq, Hugging Face
- Focus: Reliability, observability, secure token handling, API contract quality
