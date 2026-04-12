# Deployment Troubleshooting

This runbook documents deployment failure patterns and the current known-good workflow for this repository.

## Scope

Use this guide when frontend or backend changes do not appear in production after deployment.

## Current Deployment Model

- Frontend host: Vercel
- Backend host: Railway
- Frontend build output: `dist/index.html` copied from `web/index.html`
- Frontend build command: `npm run vercel-build`

## Known Failure Modes

### 1. Build script cross-platform failures

Symptoms:

- `dist/index.html` not updated locally
- Vercel deploy succeeds but serves stale content

Root cause:

- Shell-specific copy commands (`cp`, `copy`, `mkdir -p`) can fail or behave differently depending on terminal/OS.

Resolution:

- Use Node.js file copy logic in `build:html` script (already implemented in `package.json`).

Validation:

```bash
npm run vercel-build
```

Expected:

- Build command succeeds
- `dist/index.html` reflects latest `web/index.html` content

### 2. Vercel project/scope confusion

Symptoms:

- Deploy commands target wrong project
- Logs or settings appear inconsistent with expected deployment

Root cause:

- Mixed usage of project name and team scope in CLI commands.

Resolution:

- Run deploy from repository root using:

```bash
npx vercel --prod
```

- Confirm linked project in Vercel CLI output before promoting changes.

### 3. Configuration override misunderstanding

Symptoms:

- Vercel Project Settings changes do not affect build behavior

Root cause:

- `vercel.json` with `builds` configuration overrides dashboard build settings.

Resolution:

- Treat `vercel.json` and `package.json` scripts as source of truth.

### 4. Backend healthy but inference stale

Symptoms:

- `/health` returns healthy
- inference still returns fallback unexpectedly

Root cause:

- Provider model deprecations or endpoint migrations
- Deployment not yet rolled out after push

Resolution:

1. Verify provider model mappings and endpoint configuration in backend code.
1. Confirm latest commit is deployed.
1. Run smoke quality gate:

```bash
npm run test:smoke
```

1. Inspect diagnostics:

```bash
curl -s https://ai-journal-backend-production.up.railway.app/api/ai/diagnostics
```

## Standard Troubleshooting Workflow

1. Validate local frontend build:

```bash
npm run vercel-build
```

1. Confirm frontend artifact freshness:

- Compare `web/index.html` and `dist/index.html` content.

1. Deploy frontend:

```bash
npx vercel --prod
```

1. Validate backend health:

```bash
curl -s https://ai-journal-backend-production.up.railway.app/health
```

1. Execute full smoke gate:

```bash
npm run test:smoke
```

1. If failures remain, inspect diagnostics and provider error details.

## Prevention Checklist

Before deploy:

- [ ] `npm run vercel-build` succeeds locally
- [ ] `dist/index.html` updated correctly
- [ ] backend changes committed and pushed
- [ ] smoke tests pass against production

After deploy:

- [ ] frontend reflects expected UI changes
- [ ] `/health` is healthy
- [ ] diagnostics endpoint shows expected provider state
- [ ] no unexpected fallback spike during smoke run

## Related Documents

- `README.md`
- `PROJECT_STATUS_NEXT_STEPS.md`
- `DEMO_GUIDE.md`
- `evidence/RECRUITER_READY_EVIDENCE_BLOCK_2026-04-12.md`
