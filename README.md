# AI Journal Summarizer

AI Journal Summarizer is a production-deployed journaling analysis application with a FastAPI backend and web frontend. It focuses on reliable model-backed inference, transparent fallback diagnostics, and security-aware bring-your-own-key (BYOK) support.

## Live Deployment

- Frontend: [generative-ai-journal-summarizer.vercel.app](https://generative-ai-journal-summarizer.vercel.app)
- Backend API: [ai-journal-backend-production.up.railway.app](https://ai-journal-backend-production.up.railway.app)

## Project Purpose

This project demonstrates practical AI engineering for a real user-facing workflow:

- Analyze unstructured journal text for sentiment, insights, and summarization
- Support multiple providers and models behind one consistent API contract
- Preserve reliability through diagnostics, fallback behavior, and smoke-test gates
- Expose operational behavior clearly for portfolio and reviewer validation

## Architecture

### Runtime Components

- Frontend: static web app served via Vercel
- Backend: FastAPI service deployed on Railway
- AI providers: Groq and Hugging Face (plus premium/BYOK provider paths)
- Token vault: encrypted persistent storage for BYOK tokens

### Core Backend Capabilities

- Sentiment, insights, and summarize routes under /api/ai
- Provider-aware model catalog and tier metadata
- Session-based auth with guest and authenticated modes
- BYOK token ownership checks and restricted token usage
- Rate limiting and CORS controls for production hardening
- Diagnostics endpoint with provider error visibility

## Reliability and Provider Strategy

The service is designed to return model-backed output when providers are healthy, while surfacing fallback details if provider calls fail.

Recent reliability work included:

- Migrating deprecated provider paths to currently supported APIs
- Replacing deprecated Groq model IDs with supported model IDs
- Updating Hugging Face routing and model compatibility
- Capturing evidence artifacts for both failing and successful runs

See evidence artifacts in:

- evidence/reliability-2026-04-12/
- evidence/reliability-2026-04-12-final-confirmed/
- evidence/RECRUITER_READY_EVIDENCE_BLOCK_2026-04-12.md

## Engineering Quality Gate

A production smoke-test gate is required before updating portfolio-facing reliability claims.

### Smoke Scope

- GET /health
- GET /api/ai/diagnostics
- GET /api/ai/tier-info
- POST /api/ai/sentiment with Groq model: groq-llama3-70b
- POST /api/ai/sentiment with Hugging Face model: hf-mistral-7b

### Run Smoke Tests

Option 1:

```bash
npm run test:smoke
```

Option 2:

```bash
py -3 smoke_test_production.py --base-url https://ai-journal-backend-production.up.railway.app
```

### Pass Criteria

- Health endpoint returns status=healthy
- Diagnostics and tier-info return HTTP 200 with expected metadata
- Groq sentiment returns provider_used=groq and fallback_used=false
- Hugging Face sentiment returns provider_used=huggingface and fallback_used=false
- fallback_count does not increase during smoke run
- last_provider_errors is empty in the post-check snapshot

## Security Model

- Session token auth with guest and authenticated user modes
- Auth-required BYOK token connection route
- User ownership enforcement for BYOK token use
- Encrypted token persistence in backend vault storage
- Strict CORS configuration through environment variables
- Request rate limiting on AI routes

## API Overview

- GET /health
- GET /api/ai/models
- GET /api/ai/tier-info
- GET /api/ai/diagnostics
- POST /api/ai/sentiment
- POST /api/ai/insights
- POST /api/ai/summarize
- POST /api/auth/session
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/connect-token

## Local Development

### Prerequisites

- Node.js 16+
- Python 3.8+

### Setup

```bash
npm install
npm run backend:install
```

### Run

```bash
npm run backend:dev
npm run web
```

## Current Status

Authoritative project status and next steps are tracked in:

- PROJECT_STATUS_NEXT_STEPS.md

## Portfolio Notes

This repository is maintained as a portfolio-grade AI engineering project. Documentation and claims are expected to remain evidence-based and aligned with live production behavior.

## Reusable Portfolio and Demo Narrative

Use this concise narrative block directly in portfolio pages and LinkedIn project posts:

- Problem: journaling tools often lack reliable, explainable AI inference in production.
- Architecture: Vercel frontend + FastAPI on Railway, multi-provider routing (Groq and Hugging Face), session auth, BYOK token controls, encrypted token vault, and diagnostics telemetry.
- Reliability proof: live production failures were captured, root causes identified (provider deprecations and endpoint migration), remediations shipped, and final confirmation validated provider-backed output.
- Outcomes: production health stability, provider-backed inference restored, and repeatable smoke quality gate established.
- Tradeoffs: explicit fallback visibility prioritized over silent failover; lightweight auth chosen for delivery speed while preserving ownership boundaries.

Extended, copy-ready versions (portfolio + 30-second demo + LinkedIn) are available in:

- evidence/PORTFOLIO_DEMO_NARRATIVE_BLOCK.md
