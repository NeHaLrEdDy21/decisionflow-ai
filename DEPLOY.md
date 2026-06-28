# Deploying DecisionFlow AI

Frontend → **Vercel**. Backend (FastAPI + LangGraph + SQLite + ChromaDB) →
**Render**. Vercel can't run the stateful backend (no persistent disk), so the
two halves are deployed separately and connected by an environment variable.

```
  Vercel (Next.js)  ──HTTPS──►  Render (FastAPI)  ──►  Gemini · SQLite · Chroma
   NEXT_PUBLIC_API_BASE ───────────────┘
```

---

## 1. Backend on Render (do this first — you need its URL)

1. Go to <https://render.com> → sign in with GitHub.
2. **New +  →  Blueprint**, select this repository. Render reads `render.yaml`
   and creates the `decisionflow-backend` web service (root dir `backend`).
   - *Or* **New + → Web Service** manually: Root Directory `backend`,
     Build `pip install -r requirements.txt`,
     Start `uvicorn main:app --host 0.0.0.0 --port $PORT`.
3. In the service's **Environment** tab, add the secret:
   - `GOOGLE_API_KEY` = your Gemini key.
   (`GEMINI_MODEL`, `LLM_PROVIDER`, `FORCE_MOCK` come from `render.yaml`.)
4. Deploy. When live, copy the URL, e.g. `https://decisionflow-backend.onrender.com`.
5. Verify: open `https://<your-backend>.onrender.com/api/health` — it should show
   `"provider_ready": true`.

> **Free-tier notes:** the instance sleeps after ~15 min idle (first request then
> takes ~50s to wake), and its disk resets on redeploy — so stored memory persists
> while the instance is running but not across redeploys. For durable memory, add a
> Render **Disk** mounted at `backend/db` (paid) or swap SQLite for a hosted DB.

---

## 2. Frontend on Vercel

1. Go to <https://vercel.com> → **Add New… → Project** → import this repo.
2. Set **Root Directory** to `frontend`.
3. Add an Environment Variable:
   - `NEXT_PUBLIC_API_BASE` = `https://<your-backend>.onrender.com/api`
4. Deploy. Vercel auto-detects Next.js; no other settings needed.

That's it — open the Vercel URL and click **Analyze & Recommend**.

---

## 3. Connect the two (CORS)

The backend already sends `Access-Control-Allow-Origin: *`, so the Vercel domain
can call Render out of the box. To lock it down later, replace `allow_origins=["*"]`
in `backend/main.py` with your exact Vercel URL.

---

## 4. Quick checklist

- [ ] Render backend live; `/api/health` shows `provider_ready: true`
- [ ] `GOOGLE_API_KEY` set in Render (not committed to git)
- [ ] Vercel `NEXT_PUBLIC_API_BASE` points to the Render `/api` URL
- [ ] Dashboard loads and returns live (non-mock) recommendations
