# Error Analysis: Prisma Integration 405 Errors

**Date:** 2025-10-25
**Branch:** `architecture-cleanup-prisma`
**Error Type:** HTTP 405 Method Not Allowed
**Impact:** Pipeline executes successfully but database never updates
**Severity:** High (blocking production usage)

---

## 🔴 Error Summary

The innovation intelligence pipeline completes all 5 stages successfully, generates opportunity cards, but the **database remains stuck showing "PROCESSING" status forever**. Railway backend logs show repeated `405 Method Not Allowed` errors when attempting to update stage status via Prisma API.

---

## 📊 Error Logs (Railway Backend)

```
2025-10-25 16:09:21,398 - app.prisma_client - ERROR - [run-1761408561-3984] Prisma API error: 405 -
2025-10-25 16:09:21,398 - app.prisma_client - INFO - [run-1761408561-3984] Initialized pipeline stages in Prisma

2025-10-25 16:09:46,954 - app.prisma_client - ERROR - [run-1761408561-3984] Prisma API error: 405 -
2025-10-25 16:09:46,954 - app.pipeline_runner - INFO - [run-1761408561-3984] Starting Stage 2: Signal Amplification

2025-10-25 16:10:10,348 - app.prisma_client - ERROR - [run-1761408561-3984] Prisma API error: 405 -
2025-10-25 16:10:10,348 - app.pipeline_runner - INFO - [run-1761408561-3984] Starting Stage 3: General Translation

2025-10-25 16:10:54,380 - app.prisma_client - ERROR - [run-1761408561-3984] Prisma API error: 405 -
2025-10-25 16:10:54,381 - app.pipeline_runner - INFO - [run-1761408561-3984] Starting Stage 4: Brand Contextualization

2025-10-25 16:11:18,285 - app.prisma_client - ERROR - [run-1761408561-3984] Prisma API error: 405 -
2025-10-25 16:11:18,285 - app.pipeline_runner - INFO - [run-1761408561-3984] Starting Stage 5: Opportunity Generation

2025-10-25 16:12:27,988 - app.prisma_client - ERROR - [run-1761408561-3984] Prisma API error: 405 -
2025-10-25 16:12:27,989 - app.pipeline_runner - INFO - Pipeline execution completed successfully for run run-1761408561-3984

2025-10-25 16:12:28,074 - app.pipeline_runner - ERROR - [run-1761408561-3984] Webhook failed: 405 -
```

**Pattern:** Every stage update and final completion webhook returns `405 - ` (empty response body)

---

## 🏗️ Architecture Context

### Recent Refactor: File-Based → Prisma-First

**Previous Architecture (Working):**
```
Python Backend (Railway)
  ↓ writes to
/tmp/runs/{runId}/status.json
  ↓ Railway serves via GET /status/{runId}
Frontend (Vercel)
  ↓ reads from Railway
Displays status (out of sync with Prisma)
```

**New Architecture (Current - Broken):**
```
Python Backend (Railway)
  ↓ POST /api/pipeline/{runId}/stage-update
Next.js API (Vercel) ← 405 ERROR HERE
  ↓ prisma.stageOutput.upsert()
PostgreSQL (Prisma)
  ↓ GET /api/pipeline/{runId}/status
Frontend (Vercel)
```

**Migration Document:** `backend/PRISMA_INTEGRATION.md`

---

## 🔍 Root Cause Analysis

### Issue 1: 405 Method Not Allowed

**What 405 Means:**
- HTTP endpoint exists
- But doesn't support the HTTP method being used (GET vs POST)
- OR endpoint doesn't exist at all (server returns 405 instead of 404)

**Backend Code (Python):**
```python
# backend/app/prisma_client.py:60
url = f"{self.frontend_url}/api/pipeline/{run_id}/stage-update"
response = self.session.post(url, json=payload, timeout=30)
# Returns: 405 Method Not Allowed
```

**Frontend Route (TypeScript):**
```typescript
// innovation-web/app/api/pipeline/[runId]/stage-update/route.ts:22
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  // Should handle POST requests ✅
}
```

**Mystery:** Route exists and exports `POST` handler. Why 405?

---

### Issue 2: Brand ID Extraction Failure

**Logs:**
```
2025-10-25 16:10:54,381 - root - WARNING - Research file not found: docs/web-search-setup/unknown-research.md
2025-10-25 16:10:54,381 - app.pipeline_runner - WARNING - No research data found for brand unknown
```

**Expected:** `brand: lactalis-canada`
**Actual:** `brand_id: unknown`

**Code:**
```python
# backend/app/pipeline_runner.py:324
brand_id = brand_profile.get("brand_id", "unknown")
```

**Brand Profile YAML (likely structure):**
```yaml
# data/brand-profiles/lactalis-canada.yaml
id: lactalis-canada          # ← Field is "id", not "brand_id"
company_name: Lactalis Canada
# ...
```

**Fix:** Change to `brand_profile.get("id", brand_profile.get("brand_id", "unknown"))`

---

## 🧪 Diagnosis Steps

### Step 1: Verify Frontend Route Exists in Production

**Hypothesis:** Route was added locally but never deployed to Vercel production.

**Test:**
```bash
# Check Vercel deployment status
vercel ls --scope=philippe-beliveaus-projects

# Or direct URL test
curl -X POST https://innovation-web-rho.vercel.app/api/pipeline/test-run-id/stage-update \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: $WEBHOOK_SECRET" \
  -d '{"stageNumber": 1, "stageName": "Test", "status": "PROCESSING"}'
```

**Expected if route missing:** 404 or 405
**Expected if route deployed:** 401 (auth) or 400 (validation) or 200 (success)

---

### Step 2: Verify Railway Environment Variables

**Required:**
```bash
FRONTEND_WEBHOOK_URL=https://innovation-web-rho.vercel.app
WEBHOOK_SECRET={shared-secret}
```

**Check if set:**
```bash
railway variables
# or via Railway dashboard: Settings → Variables
```

**Test if mismatch:**
- Backend sends `X-Webhook-Secret: abc123`
- Frontend expects `WEBHOOK_SECRET=xyz789`
- Result: 401 Unauthorized (not 405, but worth checking)

---

### Step 3: Check Frontend Deployment Timestamp

**Files to check:**
```
innovation-web/app/api/pipeline/[runId]/stage-update/route.ts
innovation-web/app/api/pipeline/[runId]/complete/route.ts
```

**Git log:**
```bash
git log --oneline --follow innovation-web/app/api/pipeline/[runId]/stage-update/route.ts
```

**Vercel deployment log:**
- Check if latest deployment includes these files
- Check build logs for errors during deployment

---

## 🎯 Likely Root Causes (Ranked by Probability)

### 1. **Frontend Routes Not Deployed** (90% probability)

**Evidence:**
- Local development may have these routes
- Production deployment may be stale
- 405 suggests endpoint doesn't exist or wrong method

**Fix:**
```bash
cd innovation-web
vercel --prod --yes
```

**Verification:**
- Check Vercel deployment logs
- Confirm routes appear in build output
- Test endpoint directly with curl

---

### 2. **Vercel Caching Old Deployment** (5% probability)

**Evidence:**
- Vercel may serve cached version of API routes
- Edge functions not updated

**Fix:**
```bash
# Force rebuild without cache
vercel --prod --yes --force
```

---

### 3. **Route File Naming Issue** (3% probability)

**Evidence:**
- Next.js 15 requires specific naming conventions
- Dynamic route parameters must use `[param]` folder structure

**Expected structure:**
```
app/api/pipeline/[runId]/
  ├── stage-update/
  │   └── route.ts  ← exports POST
  └── complete/
      └── route.ts  ← exports POST
```

**Verify:**
```bash
ls -la innovation-web/app/api/pipeline/[runId]/stage-update/
# Should show: route.ts
```

---

### 4. **TypeScript Build Errors** (2% probability)

**Evidence:**
- TypeScript compilation errors during Vercel build
- Routes excluded from production bundle

**Check:**
```bash
cd innovation-web
npm run build
# Look for errors in output
```

---

## 📝 Secondary Issues Found

### Issue: Brand ID Field Name Mismatch

**File:** `backend/app/pipeline_runner.py:324`

**Current code:**
```python
brand_id = brand_profile.get("brand_id", "unknown")
```

**Brand YAML likely structure:**
```yaml
id: lactalis-canada  # ← Using "id", not "brand_id"
```

**Fix:**
```python
brand_id = brand_profile.get("id", brand_profile.get("brand_id", "unknown"))
```

**Impact:**
- Research data loading fails
- Pipeline runs with empty research context
- Stage 4 quality reduced

---

## 🔧 Recommended Fix Sequence

### Fix 1: Verify and Redeploy Frontend

```bash
cd innovation-web

# Verify routes exist locally
ls -la app/api/pipeline/[runId]/stage-update/route.ts
ls -la app/api/pipeline/[runId]/complete/route.ts

# Build locally to catch errors
npm run build

# Deploy to production
vercel --prod --yes

# Verify deployment includes routes
# Check Vercel dashboard → Deployments → Functions
```

---

### Fix 2: Update Brand ID Extraction

```python
# backend/app/pipeline_runner.py

# BEFORE (line 324):
brand_id = brand_profile.get("brand_id", "unknown")

# AFTER:
brand_id = brand_profile.get("id", brand_profile.get("brand_id", "unknown"))
```

**Commit:**
```bash
git add backend/app/pipeline_runner.py
git commit -m "fix: use 'id' field for brand_id extraction"
```

**Deploy to Railway:**
```bash
git push railway fix/prisma-405-errors-video:main
# or via Railway dashboard: Manual Deploy
```

---

### Fix 3: Enhanced Error Logging (Optional but Recommended)

```python
# backend/app/prisma_client.py:89

# Add more context to 405 errors
if not response.ok:
    logger.error(
        f"[{run_id}] Prisma API error: {response.status_code} - {response.text}"
    )
    logger.error(f"[{run_id}] Request URL: {url}")
    logger.error(f"[{run_id}] Request method: POST")
    logger.error(f"[{run_id}] Request headers: {dict(self.session.headers)}")
    logger.error(f"[{run_id}] Response headers: {dict(response.headers)}")
    return False
```

---

## ✅ Verification Tests

### Test 1: Manual API Call

```bash
# Test stage-update endpoint directly
curl -X POST https://innovation-web-rho.vercel.app/api/pipeline/test-run-123/stage-update \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: $WEBHOOK_SECRET" \
  -d '{
    "stageNumber": 1,
    "stageName": "Input Processing",
    "status": "PROCESSING",
    "output": "Test output"
  }'

# Expected: 200 OK or 404 Not Found (run doesn't exist)
# NOT: 405 Method Not Allowed
```

---

### Test 2: End-to-End Pipeline Run

```bash
# Trigger new pipeline run from frontend
# Upload test document (e.g., savannah-bananas.pdf)

# Monitor Railway logs:
railway logs --follow

# Expected logs:
# ✅ [run-xxx] Successfully updated stage 1 in Prisma
# ✅ [run-xxx] Successfully updated stage 2 in Prisma
# ✅ [run-xxx] Successfully updated stage 3 in Prisma
# ✅ [run-xxx] Successfully updated stage 4 in Prisma
# ✅ [run-xxx] Successfully updated stage 5 in Prisma
# ✅ [run-xxx] Successfully notified frontend of completion

# NOT:
# ❌ [run-xxx] Prisma API error: 405 -
```

---

### Test 3: Database Verification

```sql
-- Check StageOutput records were created
SELECT * FROM "StageOutput"
WHERE "runId" = 'run-xxx'
ORDER BY "stageNumber";

-- Expected: 5 rows (stages 1-5) with status = 'COMPLETED'

-- Check PipelineRun status
SELECT id, status, "completedAt"
FROM "PipelineRun"
WHERE id = 'run-xxx';

-- Expected: status = 'COMPLETED', completedAt = timestamp
-- NOT: status = 'PROCESSING', completedAt = null
```

---

## 📊 Success Criteria

✅ **No more 405 errors in Railway logs**
✅ **Stage updates appear in real-time** (check Prisma Studio)
✅ **PipelineRun status changes** from PROCESSING → COMPLETED
✅ **OpportunityCards saved** to database (5 cards per run)
✅ **Frontend updates in real-time** (progress bar advances)
✅ **Brand research data loads** correctly (not "unknown")

---

## 📚 Related Documentation

- `backend/PRISMA_INTEGRATION.md` - Architecture migration guide
- `innovation-web/app/api/pipeline/[runId]/stage-update/route.ts` - Stage update endpoint
- `innovation-web/app/api/pipeline/[runId]/complete/route.ts` - Completion webhook endpoint
- `backend/app/prisma_client.py` - Prisma HTTP API client
- `backend/app/pipeline_runner.py` - Pipeline execution logic

---

## 🎬 Video Documentation

This error is documented for **Newcode Video Series - Subject 1: FastAPI MCP Debugging**.

See companion files:
- `video-scenario-technical.md` - Technical audience version
- `video-scenario-non-technical.md` - Business audience version

---

**Last Updated:** 2025-10-25
**Status:** ❌ Unresolved (documented for video production)
**Next Steps:** Record debugging session, then apply fixes
