# Groq Setup Guide

This guide explains how to configure Groq for provider-backed inference in AI Journal Summarizer.

## Prerequisites

- Groq account at `console.groq.com`
- Access to local `.env` (for local development) or Railway Variables (for production)

## Create a Groq API Key

1. Open [console.groq.com](https://console.groq.com/)
2. Sign in or create an account
3. Navigate to API Keys
4. Create a new key
5. Copy the key value

## Configure Local Development

Add key to `.env`:

```env
GROQ_API_KEY=gsk_your_key_here
```

Restart backend:

```bash
npm run backend:dev
```

## Configure Production (Railway)

Set environment variable in Railway service configuration:

```text
GROQ_API_KEY=gsk_your_key_here
```

Redeploy or restart service after updating variables.

## Verify Configuration

### 1. Health check

```bash
curl -s https://ai-journal-backend-production.up.railway.app/health
```

### 2. Provider diagnostics

```bash
curl -s https://ai-journal-backend-production.up.railway.app/api/ai/diagnostics
```

Expected diagnostics field:

- `groq_configured: true`

### 3. End-to-end smoke test

```bash
npm run test:smoke
```

Expected smoke check includes provider-backed Groq sentiment route:

- model: `groq-llama3-70b`
- metadata: `provider_used=groq`, `fallback_used=false`

## Troubleshooting

### Groq configured but fallback still occurs

- Check diagnostics `last_provider_errors` for deprecation or request errors
- Confirm model mappings in backend are current
- Ensure latest backend commit is deployed

### Local key works but production fails

- Confirm key exists in Railway Variables (exact name `GROQ_API_KEY`)
- Restart or redeploy Railway service
- Re-run smoke quality gate against production

### Rate-limit or auth-like failures

- Verify request path and payload match API contracts
- Use diagnostics endpoint to identify provider-specific HTTP errors

## Notes

- Application supports fallback behavior; fallback usage should be observable via diagnostics and metadata.
- Portfolio-facing reliability claims should be backed by smoke test evidence.

## Related Documents

- `README.md`
- `DEPLOYMENT_TROUBLESHOOTING.md`
- `PROJECT_STATUS_NEXT_STEPS.md`
- `smoke_test_production.py`
