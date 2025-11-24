# Handoff: Fix Gradio-Backend Integration Issues

## Context

Railway backend deployment is now **SUCCESSFUL** ✅ (see `railway-deploy.md` for full deployment fix documentation).

However, when Gradio UI (running on HuggingFace Spaces) calls the Railway backend, the pipeline execution fails with multiple integration issues.

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Gradio UI (HuggingFace Spaces)                         │
│  https://philbeli-mboi-experiment.hf.space              │
│  File: backend/experimentation/hf-space-deploy/app.py   │
└──────────────┬──────────────────────────────────────────┘
               │
               │ HTTP POST /run/local
               │ {"pdf_text": "...", "brand_profile": {...}}
               ▼
┌─────────────────────────────────────────────────────────┐
│  Railway Backend                                         │
│  https://innovation-backend-production.up.railway.app   │
│  Branch: gradio-pipeline-deployment                     │
│  Commit: d95bb89                                         │
└──────────────┬──────────────────────────────────────────┘
               │
               │ Executes 7-stage pipeline
               ▼
┌─────────────────────────────────────────────────────────┐
│  OpenRouter API (LLM)                                    │
│  https://openrouter.ai/api/v1                           │
└─────────────────────────────────────────────────────────┘
```

---

## Issues Identified from Logs

### ❌ Issue 1: OpenRouter Authentication Failure (401)

**Error:**
```
openai.AuthenticationError: Error code: 401 - {'error': {'message': 'User not found.', 'code': 401}}
2025-11-23 22:10:03,263 - httpx - INFO: HTTP Request: POST https://openrouter.ai/api/v1/chat/completions "HTTP/1.1 401 Unauthorized"
```

**Root Cause:**
Railway backend is missing the `OPENROUTER_API_KEY` environment variable or the key is invalid/expired.

**Location:** Backend tries to call OpenRouter in `pipeline/stages/stage1_input_processing.py:78`

**Fix Required:**
1. Verify `OPENROUTER_API_KEY` exists in Railway environment variables
2. Ensure the API key is valid (test with direct curl request)
3. Check if the key has sufficient credits/permissions

**Railway Settings to Check:**
```
Settings → Variables → OPENROUTER_API_KEY
```

**Test Command:**
```bash
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek/deepseek-chat-v3.1",
    "messages": [{"role": "user", "content": "test"}]
  }'
```

Expected: 200 OK with response
Actual (currently): 401 Unauthorized

---

### ❌ Issue 2: Prisma API "Run not found" (404)

**Error:**
```
2025-11-23 22:10:02,678 - app.prisma_client - ERROR - [edc5b254] Prisma API error: 404 - {"error":"Run not found"}
2025-11-23 22:10:03,347 - app.prisma_client - ERROR - [edc5b254] Prisma API error: 404 - {"error":"Run not found"}
```

**Context:**
The backend tries to update pipeline run status via Prisma API but the run doesn't exist in the database.

**Root Cause:**
The `/run/local` endpoint (used by Gradio) creates a run_id (`edc5b254`) but doesn't create a corresponding PipelineRun record in the database BEFORE starting execution.

**Location:**
- `backend/app/routes.py` - `/run/local` endpoint
- `backend/app/prisma_client.py` - Prisma API client

**Expected Flow:**
1. Gradio → POST `/run/local` with run_id
2. Backend creates PipelineRun record in database
3. Backend starts pipeline execution
4. Backend updates PipelineRun stages as they complete

**Actual Flow:**
1. Gradio → POST `/run/local` with run_id
2. Backend skips database record creation (local dev mode)
3. Backend starts pipeline execution
4. Backend tries to update PipelineRun → **404 Run not found**

**Fix Required:**
The `/run/local` endpoint needs to create a PipelineRun record in the database even in local/Gradio mode, OR the Prisma client needs to gracefully handle missing runs for local development.

**Option A (Recommended):** Create PipelineRun record in `/run/local`
```python
@router.post("/run/local")
async def run_pipeline_local(request: RunPipelineLocalRequest):
    run_id = request.run_id or str(uuid.uuid4())

    # Create PipelineRun record in database
    await create_pipeline_run(
        run_id=run_id,
        brand_profile=request.brand_profile,
        report_source="gradio_upload"
    )

    # Then start pipeline execution
    ...
```

**Option B:** Make Prisma client ignore 404 for local runs
```python
def update_stage_status(self, run_id, stage_num, status):
    try:
        response = self.session.patch(f"/runs/{run_id}/stages/{stage_num}", ...)
    except HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"[{run_id}] Run not found (local dev mode), skipping update")
            return  # Gracefully skip
```

---

### ⚠️ Issue 3: LangChain Deprecation Warning

**Warning:**
```
/usr/local/lib/python3.11/site-packages/langchain_core/_api/deprecation.py:119: LangChainDeprecationWarning:
The class `LLMChain` was deprecated in LangChain 0.1.17 and will be removed in 0.3.0.
Use RunnableSequence, e.g., `prompt | llm` instead.
```

**Impact:** Low priority (warning only, not breaking)

**Location:** All pipeline stages using LangChain (Stages 1-5)

**Fix Required:**
Migrate from deprecated `LLMChain` to new `RunnableSequence` pattern:

**Before:**
```python
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.invoke({"input_text": text})
```

**After:**
```python
from langchain_core.runnables import RunnableSequence
chain = prompt | llm
result = chain.invoke({"input_text": text})
```

---

## Environment Variables Required

### Railway Backend (`innovation-backend-production`)

**Critical (must exist):**
- `OPENROUTER_API_KEY` - OpenRouter API key for LLM calls
- `DATABASE_URL` - PostgreSQL connection string (for Prisma)
- `PORT` - Railway sets this automatically

**Optional:**
- `OPENROUTER_BASE_URL` - Default: `https://openrouter.ai/api/v1`
- `LLM_MODEL` - Default: `deepseek/deepseek-chat-v3.1`
- `FRONTEND_WEBHOOK_URL` - For completion callbacks (optional for Gradio)
- `WEBHOOK_SECRET` - Webhook authentication (optional for Gradio)
- `VERCEL_BLOB_READ_WRITE_TOKEN` - For PDF downloads (not needed for Gradio)

### HuggingFace Gradio Space

**Required:**
- `BACKEND_API_URL` - Railway backend URL: `https://innovation-backend-production.up.railway.app`
- `DATABASE_URL` - PostgreSQL connection string (if Gradio saves experiments directly)

---

## Files to Review

### Backend Files
1. **`backend/app/routes.py`** - `/run/local` endpoint
   - Line ~500: `run_pipeline_local()` function
   - Check if PipelineRun record is created

2. **`backend/app/pipeline_runner.py`** - Pipeline execution
   - Line ~457: Stage 1 execution fails with OpenRouter 401
   - Check OpenRouter API key loading

3. **`backend/app/prisma_client.py`** - Prisma API client
   - Line ~50-100: `update_stage_status()` method
   - Handle 404 errors for local dev runs

4. **`backend/pipeline/stages/stage1_input_processing.py`** - Stage 1
   - Line 78: LangChain LLMChain invocation
   - Migrate to RunnableSequence

5. **`backend/app/main.py`** - FastAPI app initialization
   - Check environment variable loading

### Gradio Files
1. **`backend/experimentation/hf-space-deploy/app.py`** - Gradio UI
   - Check `BACKEND_API_URL` configuration
   - Verify run_id generation and POST request

---

## Recommended Fix Order

### Priority 1: Fix OpenRouter Authentication (BLOCKER)
1. Check Railway environment variables for `OPENROUTER_API_KEY`
2. Test API key validity with curl command above
3. If missing/invalid, add valid API key to Railway
4. Redeploy backend (Railway auto-deploys on env var change)

### Priority 2: Fix Prisma "Run not found" Error
**Choose one approach:**

**Approach A (Recommended):** Create PipelineRun in `/run/local`
- Modify `backend/app/routes.py` to create database record
- Ensures consistency between Next.js and Gradio flows

**Approach B:** Gracefully skip Prisma updates for local runs
- Modify `backend/app/prisma_client.py` to log and skip 404 errors
- Faster fix but inconsistent with production flow

### Priority 3: Migrate LangChain Chains (OPTIONAL)
- Low priority - warning only, not breaking
- Update all 5 pipeline stages to use RunnableSequence
- Test locally before deploying

---

## Testing Checklist

After fixes are implemented, test the complete flow:

### 1. Test OpenRouter Connection
```bash
# SSH into Railway container or use Railway CLI
railway run bash

# Test OpenRouter API
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek/deepseek-chat-v3.1", "messages": [{"role": "user", "content": "test"}]}'
```

Expected: 200 OK with completion response

### 2. Test Gradio → Railway Integration
1. Open Gradio UI: https://philbeli-mboi-experiment.hf.space
2. Upload test PDF (e.g., WGSN report)
3. Select brand profile (e.g., Decathlon)
4. Click "Run Pipeline"
5. Monitor Railway logs: `railway logs --tail`

Expected: No 401 or 404 errors, pipeline completes all 7 stages

### 3. Test Database Integration
```sql
-- Check if PipelineRun was created
SELECT * FROM "PipelineRun" ORDER BY "createdAt" DESC LIMIT 5;

-- Check stage statuses
SELECT run_id, stage_number, status FROM "PipelineStage"
WHERE run_id = 'edc5b254' ORDER BY stage_number;
```

Expected: Run exists with all stages tracked

---

## Success Criteria

✅ **Integration Fixed When:**
1. Gradio can successfully call Railway `/run/local` endpoint
2. Pipeline executes all 7 stages without 401/404 errors
3. PipelineRun record exists in database with stage statuses
4. Gradio UI receives complete results and displays all stages
5. No authentication or database errors in Railway logs

---

## Reference Documentation

- **Railway Deployment Fix:** `railway-deploy.md`
- **Pipeline Architecture:** `CLAUDE.md` (lines 80-150)
- **Gradio Integration:** `backend/experimentation/README.md`
- **Backend API:** `backend/DEPLOYMENT.md`

---

## Current Status

- ✅ Railway backend deployed successfully (commit `d95bb89`)
- ❌ OpenRouter authentication failing (401)
- ❌ Prisma database integration failing (404)
- ⚠️ LangChain deprecation warnings (non-blocking)

**Next Agent Focus:** Fix Issues 1 & 2 to enable Gradio → Railway → Database integration.
