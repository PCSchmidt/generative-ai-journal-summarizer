# AI Journal Summarizer Demo Guide

This guide is optimized for portfolio demos, recruiter walkthroughs, and interview presentations.

## Demo Objective

Demonstrate that the application provides:

- Provider-backed AI inference in production
- Observable reliability through diagnostics and fallback metadata
- Clear end-to-end product behavior from input to analyzed output

## Live Endpoints

- Frontend: [generative-ai-journal-summarizer.vercel.app](https://generative-ai-journal-summarizer.vercel.app)
- Backend: [ai-journal-backend-production.up.railway.app](https://ai-journal-backend-production.up.railway.app)

## Recommended Demo Duration

- Short version: 2-3 minutes
- Full version: 5-7 minutes

## Pre-Demo Checklist

1. Confirm backend health:

```bash
curl -s https://ai-journal-backend-production.up.railway.app/health
```

1. Run production smoke gate:

```bash
npm run test:smoke
```

1. Confirm diagnostics endpoint is reachable:

```bash
curl -s https://ai-journal-backend-production.up.railway.app/api/ai/diagnostics
```

## Demo Script (5-7 Minutes)

### Step 1: Open the Product Surface

1. Open the live frontend.
2. Briefly explain this is a deployed FastAPI + Vercel system with multi-provider model routing.

### Step 2: Show Journal Analysis Flow

Use one sample entry:

```text
I stabilized a production service this week after tracing provider-level failures and updating model routing. I still feel pressure to move fast, but I am more confident now because our reliability checks are explicit and repeatable.
```

Run analysis and show:

- Sentiment result
- Insights result
- Summary result
- Provider/fallback metadata in the UI

### Step 3: Show Reliability and Observability

Open diagnostics endpoint and explain:

- Provider configuration status
- Fallback counter behavior
- Last provider error visibility

Reference evidence artifacts:

- evidence/reliability-2026-04-12/
- evidence/reliability-2026-04-12-final-confirmed/
- evidence/RECRUITER_READY_EVIDENCE_BLOCK_2026-04-12.md

### Step 4: Show Engineering Quality Gate

Run or reference smoke test output:

```bash
py -3 smoke_test_production.py --base-url https://ai-journal-backend-production.up.railway.app
```

Explain that this validates:

- health
- diagnostics
- tier-info
- Groq sentiment provider path
- Hugging Face sentiment provider path

### Step 5: Close with Engineering Decisions

Summarize tradeoffs:

- Explicit fallback metadata over silent failover
- Lightweight auth with ownership controls for BYOK speed vs complexity
- Evidence-first documentation tied to live behavior

## Interviewer Q&A Prompts

### What production issue did you solve?

Provider deprecations caused fallback-only behavior. I captured diagnostics evidence, migrated endpoints/model mappings, and verified provider-backed inference through repeatable smoke tests.

### How do you prove reliability claims are real?

Every major claim is linked to live endpoint checks, diagnostics output, and timestamped evidence artifacts in the repository.

### How do you prevent regressions?

The smoke quality gate validates core production contracts, and backend API contract tests cover auth and route behavior.

## Optional Local Demo Setup

If presenting locally:

```bash
npm install
npm run backend:install
npm run backend:dev
npm run web
```

## Source of Truth

For current implementation status and next steps, use:

- PROJECT_STATUS_NEXT_STEPS.md
- README.md
