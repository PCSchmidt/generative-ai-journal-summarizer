# Portfolio and Demo Narrative Block

Use this block directly for portfolio project pages, demo intros, and LinkedIn posts.

## Problem

Most journaling tools store text but do not provide reliable, explainable insight generation. I built AI Journal Summarizer to deliver production-grade journal analysis with explicit provider telemetry and fallback transparency so users and reviewers can trust what happened on each inference.

## Architecture

- Frontend: Vercel-hosted web interface
- Backend: FastAPI on Railway
- Model layer: multi-provider routing (Groq + Hugging Face), premium/BYOK-ready paths
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
- Production smoke quality gate established:
  - health, diagnostics, tier-info, and per-provider analyze checks
- Documentation aligned to measurable runtime behavior

## Tradeoffs and Engineering Decisions

- Chose explicit fallback metadata over silent failover to preserve operational trust
- Kept auth lightweight for portfolio velocity, while still enforcing token ownership boundaries
- Prioritized production evidence capture before additional feature expansion

## 30-Second Demo Script

"AI Journal Summarizer is a FastAPI + Vercel system that analyzes journal entries with multi-provider model routing. I intentionally expose provider/fallback metadata and diagnostics so reliability is observable. During production validation I found upstream deprecations, shipped targeted provider remediations, and verified model-backed inference end-to-end with a smoke quality gate."

## LinkedIn-Ready Version

Built and deployed an AI Journal Summarizer with FastAPI (Railway) + web frontend (Vercel), multi-provider model routing, and production reliability diagnostics. During live validation I detected provider deprecations, implemented remediation (Groq model updates + Hugging Face router migration), and confirmed provider-backed inference with a repeatable smoke quality gate. The project now demonstrates production AI engineering discipline: measurable reliability, transparent fallback behavior, and evidence-based documentation.
