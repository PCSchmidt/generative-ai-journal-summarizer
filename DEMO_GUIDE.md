# AI Journal Summarizer Demo Guide

This guide is optimized for portfolio demos, recruiter walkthroughs, and interview presentations.

## Demo Objective

Demonstrate that the application provides:

- Provider-backed AI inference in production
- Retrieval-augmented generation (RAG) with measurable retrieval quality
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

### Step 3: Show RAG Pipeline (Key Differentiator)

Demonstrate the retrieval-augmented analysis flow via API:

1. **Ingest a few journal entries** to populate the vector store:

```bash
curl -X POST https://ai-journal-backend-production.up.railway.app/api/journal \
  -H "Content-Type: application/json" \
  -d '{"text": "Started a new ML project at work. The timeline is tight but I am excited about the challenge.", "user_id": "demo"}'
```

```bash
curl -X POST https://ai-journal-backend-production.up.railway.app/api/journal \
  -H "Content-Type: application/json" \
  -d '{"text": "Ran my first 10K today. Six months ago I could barely do 2K. Consistency beats intensity.", "user_id": "demo"}'
```

2. **Run RAG-augmented analysis** — the LLM now sees relevant past entries:

```bash
curl -X POST https://ai-journal-backend-production.up.railway.app/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"text": "Feeling stressed about the project deadline but went for a run to clear my head", "task_type": "insights", "top_k": 3}'
```

3. **Show the response** — point out:
   - `rag.retrieved_count` and `rag.retrieved_entries` showing which past entries were found
   - Similarity scores demonstrating semantic matching quality
   - The LLM output now references patterns across multiple entries

4. **Or use `use_rag: true` on existing endpoints:**

```bash
curl -X POST https://ai-journal-backend-production.up.railway.app/api/ai/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "The project demo went well today", "use_rag": true}'
```

Show the `rag_used: true` and `retrieved_count` in the response metadata.

### Step 4: Show Eval Results

```bash
python eval/run_eval.py
```

Explain the eval methodology:
- 20-entry golden test set simulating 3 weeks of journaling
- 5 thematic queries with hand-labeled expected retrievals
- Metrics: precision@3 = 0.80, recall@3 = 0.77, MRR = 1.0
- MRR = 1.0 means the first result is always relevant

### Step 5: Show Reliability and Observability

Open diagnostics endpoint and explain:

- Provider configuration status
- Fallback counter behavior
- Last provider error visibility

Reference evidence artifacts:

- evidence/reliability-2026-04-12/
- evidence/reliability-2026-04-12-final-confirmed/
- evidence/RECRUITER_READY_EVIDENCE_BLOCK_2026-04-12.md

### Step 6: Show Engineering Quality Gate

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

### Step 7: Close with Engineering Decisions

Summarize tradeoffs:

- Explicit fallback metadata over silent failover
- Lightweight auth with ownership controls for BYOK speed vs complexity
- Evidence-first documentation tied to live behavior

### Step 8: Agentic Layer Demo

Show the ReAct agent making multi-step decisions:

```bash
curl -X POST $BACKEND/api/agent/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Search my journal for entries about stress, analyze the sentiment, and suggest improvements."}'
```

Highlight in the response:
- `trace.steps`: each Thought → Action → Observation loop
- `metadata.tools_called`: which of the 5 tools the agent selected
- `metadata.latency_ms`: end-to-end timing

Then show the eval results:

```bash
python -m agent.eval_agent
# → 90% pass rate, 0.92 tool recall, 0.77 precision, 4.8s avg latency
```

## Interviewer Q&A Prompts

### What production issue did you solve?

Provider deprecations caused fallback-only behavior. I captured diagnostics evidence, migrated endpoints/model mappings, and verified provider-backed inference through repeatable smoke tests.

### How do you prove reliability claims are real?

Every major claim is linked to live endpoint checks, diagnostics output, and timestamped evidence artifacts in the repository.

### How do you prevent regressions?

The smoke quality gate validates core production contracts, and backend API contract tests cover auth and route behavior.

### How does the RAG pipeline work?

Journal entries are embedded with sentence-transformers (all-MiniLM-L6-v2, 384-dim vectors), L2-normalized, and indexed in FAISS IndexFlatIP for cosine similarity search. When a user submits text for analysis, the retriever finds the top-k most similar past entries and injects them as context into the LLM prompt. The LLM can then reference longitudinal patterns across entries rather than analyzing each entry in isolation.

### How did you evaluate the retrieval quality?

I built an eval harness with a 20-entry golden test set simulating real journaling patterns across work, health, and personal themes. Five thematic queries have hand-labeled expected retrievals. Metrics: precision@3 = 0.80, recall@3 = 0.77, MRR = 1.0. MRR of 1.0 means the most relevant entry always ranks first.

### Why FAISS over ChromaDB?

FAISS gives direct control over the index type and similarity metric without the overhead of a client-server architecture. For a single-user journal app, an in-process flat index with exact search is simpler and faster than running a separate vector database. If the entry count grew to millions, I'd switch to FAISS IVF or consider a managed vector store.

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
