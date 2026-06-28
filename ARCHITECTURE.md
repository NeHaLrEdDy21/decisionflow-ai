# DecisionFlow AI — Architecture & Procedure

This document explains *how the system is built and how it runs*: the layers,
the components, the request lifecycle, and the step-by-step procedure from a
raw upload to a stored human decision. For the *why* (theory and concepts), see
`CONCEPTS.md`.

---

## 1. System at a Glance

DecisionFlow AI is a two-tier application with an agentic reasoning core.

| Tier | Technology | Responsibility |
|------|-----------|----------------|
| Presentation | Next.js 14, TailwindCSS, shadcn-style components | Upload UI, agent timeline, recommendation cards, evidence panel, memory page |
| Service | FastAPI (Uvicorn) | REST endpoints, request orchestration, persistence |
| Reasoning | LangGraph + LangChain + Gemini | Multi-agent workflow that analyses, reasons, and recommends |
| Knowledge | ChromaDB (keyword fallback) | Vector retrieval over enterprise documents |
| State | SQLite | Customers, runs, recommendations, and long-term memory |

The reasoning core is deliberately isolated behind the service tier so the same
agents can be reused by other front-ends, schedulers, or batch jobs.

---

## 2. High-Level Architecture

```
            ┌─────────────────────────────────────────────────────────┐
            │                 Next.js Dashboard (3000)                 │
            │  Upload · Agent Timeline · Recommendations · Evidence    │
            │  · Memory page · Approve / Reject / Modify               │
            └───────────────────────────┬─────────────────────────────┘
                                        │  HTTP (/api/* proxied)
            ┌───────────────────────────▼─────────────────────────────┐
            │                  FastAPI Service (8000)                  │
            │   /upload /analyze /recommendations /approve /reject     │
            │   /modify /memory /customer                              │
            └───────────────────────────┬─────────────────────────────┘
                                        │  run_workflow(inputs)
            ┌───────────────────────────▼─────────────────────────────┐
            │              LangGraph Orchestration Layer               │
            │                                                          │
            │   Planner ─► Conversation ─► CRM ─► Knowledge ─► Risk    │
            │     ─► Opportunity ─► Recommendation ─► Explanation      │
            │       ─► Memory                                          │
            └───────┬───────────────────────┬──────────────────┬──────┘
                    │                       │                  │
         ┌──────────▼─────┐      ┌──────────▼────────┐  ┌──────▼───────┐
         │   Gemini LLM   │      │     ChromaDB      │  │    SQLite    │
         │ (+ mock layer) │      │ enterprise docs   │  │  + memory    │
         └────────────────┘      └───────────────────┘  └──────────────┘
```

---

## 3. Backend Component Breakdown

```
backend/
├── main.py              FastAPI entrypoint; imports agents so they self-register;
│                        startup initialises SQLite + ChromaDB.
├── config.py            Single source of tunables (no business logic hardcoded
│                        in agents): provider, model, pipeline order, paths,
│                        MOCK_MODE flag, MAX_RECOMMENDATIONS.
├── llm.py               Provider wrapper. llm_text() / llm_json() are the only
│                        way agents talk to a model. Handles JSON extraction and
│                        a deterministic mock fallback on any error.
├── logging_config.py    Shared logger → console + logs/decisionflow.log.
├── agents/
│   ├── base.py          BaseAgent abstract class + REGISTRY + @register.
│   │                    execute() wraps run() with timing, logging, trace.
│   ├── planner.py       Orchestration only — chooses which agents run.
│   ├── conversation_agent.py
│   ├── crm_agent.py
│   ├── knowledge_agent.py
│   ├── risk_agent.py
│   ├── opportunity_agent.py
│   ├── recommendation_agent.py
│   ├── explanation_agent.py
│   └── memory_agent.py
├── tools/
│   ├── vector_store.py  ChromaDB index + keyword fallback.
│   ├── rag.py           Multi-query retrieval + de-duplication.
│   ├── crm_tool.py      Normalises raw CRM JSON to a clean record.
│   └── memory_tool.py   recall() / remember() over SQLite.
├── workflow/
│   ├── graph.py         Builds the LangGraph StateGraph; sequential fallback.
│   └── state.py         FlowState TypedDict (shared state schema).
├── api/routes.py        All REST endpoints.
├── db/database.py       SQLite schema + CRUD for every table.
├── knowledge/           Enterprise corpus (pricing, implementation, FAQ, …).
└── sample_data/         transcript, crm.json, email, ticket, notes.
```

### The reusable agent interface

Every agent subclasses `BaseAgent`, sets a `key` and `label`, and implements
`run(state) -> dict`. The class decorator `@register` adds an instance to the
global `REGISTRY`. `execute()` wraps `run()` to log start/end, measure latency,
capture errors, and append a trace entry. Because of this, **adding a new agent
is a three-step procedure**: create the file, subclass + `@register`, and add
its key to `DEFAULT_PIPELINE` in `config.py`. No orchestration code changes.

---

## 4. The Shared State Object

All agents read from and contribute to one dictionary (`FlowState`). Each agent
returns a *patch* that is merged in. By the end of a run the state holds:

| Key | Produced by | Contents |
|-----|------------|----------|
| `inputs` | caller | transcript, crm, email, support_ticket, notes |
| `plan` | Planner | ordered list of agents to execute |
| `conversation` | Conversation | summary, pain points, goals, sentiment, urgency, gaps |
| `crm` | CRM | name, health, renewal_days, arr, opportunities |
| `knowledge` | Knowledge | retrieved document snippets |
| `risk` | Risk | risk_level, risks[], confidence |
| `opportunity` | Opportunity | opportunities[] with priority + confidence |
| `recommendations` | Recommendation + Explanation | Top-5 NBAs, each with evidence |
| `memory_recall` / `memory_history` | Memory | prior interactions for this customer |
| `trace` | every agent | per-agent status + latency for the UI timeline |

---

## 5. End-to-End Procedure (Request Lifecycle)

1. **Upload.** The dashboard collects the five input types and POSTs them. The
   CRM record is upserted into SQLite so the customer exists before analysis.
2. **Analyze.** `POST /analyze` calls `run_workflow(inputs)`.
3. **Seed memory.** Before any agent runs, the workflow pre-loads prior memory
   for the customer (`memory_recall`) so downstream agents can use history.
4. **Plan.** The Planner inspects which inputs are present and emits an ordered
   execution plan. It performs no business reasoning.
5. **Execute the pipeline.** LangGraph runs each planned node in order:
   Conversation → CRM → Knowledge → Risk → Opportunity → Recommendation →
   Explanation → Memory. Each node merges its patch into the shared state and
   appends a trace entry with its latency.
6. **Persist.** The run is saved; the Top-5 recommendations are written to the
   `recommendations` table with status `pending`; the Memory agent stores an
   analysis summary.
7. **Respond.** The API returns the customer profile, plan, trace, knowledge,
   risk, opportunities, recommendations (with evidence), and memory history.
8. **Human-in-the-loop.** The CSM clicks Approve / Reject / Modify on each card.
   `POST /approve|/reject|/modify` updates the recommendation's status and
   writes the decision to memory.
9. **Future reuse.** On the next analysis for that customer, step 3 recalls
   these stored decisions, closing the loop.

---

## 6. The LLM Access Procedure

Agents never call a provider directly. They call `llm_json(prompt, mock=…)`:

- If `MOCK_MODE` is on (no API key, or `FORCE_MOCK=true`, or a provider error),
  the supplied deterministic `mock` value is returned — the workflow never breaks.
- Otherwise the prompt goes to Gemini (`gemini-2.5-flash` by default, with
  "thinking" disabled for low latency), the response is parsed as JSON, and the
  result is returned. Parsing tolerates markdown fences and bare arrays.

This keeps provider choice, model name, and failure handling in exactly one file.

---

## 7. Knowledge Retrieval Procedure (RAG)

On startup, every file in `knowledge/` is chunked and indexed into ChromaDB
(with a keyword index as fallback). When the Knowledge agent runs, it builds
queries from the conversation's pain points and goals plus the email/ticket
text, retrieves the top matches per query, de-duplicates them, and attaches the
snippets to state. The Explanation agent later cites these documents as evidence.

---

## 8. REST API Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/upload` | Stage customer inputs; upsert the customer |
| POST | `/api/analyze` | Run the full agent workflow; persist recommendations |
| GET | `/api/recommendations` | List recommendations (optionally per customer) |
| POST | `/api/approve` | Approve a recommendation → memory |
| POST | `/api/reject` | Reject a recommendation → memory |
| POST | `/api/modify` | Edit a recommendation's action → memory |
| GET | `/api/memory` | Retrieve the memory timeline |
| GET | `/api/customer` | Customer record + memory |
| GET | `/api/health` | Health + mock-mode status |

---

## 9. Setup Procedure

**Backend**

```bash
cd decisionflow-ai/backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # add GOOGLE_API_KEY for live Gemini, or leave blank for mock
uvicorn main:app --reload --port 8000
```

**Frontend**

```bash
cd decisionflow-ai/frontend
npm install
npm run dev          # http://localhost:3000 (proxies /api → :8000)
```

**Configuration knobs** (`backend/.env`): `GOOGLE_API_KEY`, `GEMINI_MODEL`
(default `gemini-2.5-flash`), and `FORCE_MOCK` to force offline mode.

---

## 10. Design Properties Enforced by the Architecture

- **Modularity** — one agent per file behind a uniform interface.
- **Reusability** — re-target the domain by swapping prompts + knowledge docs.
- **Explainability** — every recommendation carries structured evidence.
- **Configurability** — the pipeline is a list in `config.py`.
- **Observability** — every agent logs timing and contributes to the trace.
- **Resilience** — mock fallback and graph→sequential fallback keep demos alive.
