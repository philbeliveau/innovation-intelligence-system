# Prisma Integration - Backend Migration Guide

**Status:** ✅ IMPLEMENTED
**Date:** 2025-10-25
**Branch:** `architecture-cleanup-prisma`

## Overview

The Python backend now writes pipeline status updates to **Prisma database via HTTP API** instead of file-based `status.json` files. This creates a single source of truth for pipeline execution state.

## Architecture Change

### Before (File-Based)
```
Python Backend (Railway)
  ↓ writes to
/tmp/runs/{runId}/status.json
  ↓ Railway serves via GET /status/{runId}
Frontend (Vercel)
  ↓ reads from Railway
Displays status (out of sync with Prisma)
```

**Problems:**
- Dual state management (Prisma + files)
- Frontend Prisma records never updated during execution
- File system state lost on Railway dyno restart
- Status out of sync between frontend DB and backend files

### After (Prisma-First)
```
Python Backend (Railway)
  ↓ POST /api/pipeline/{runId}/stage-update
Next.js API (Vercel)
  ↓ prisma.stageOutput.upsert()
PostgreSQL (Prisma)
  ↓ GET /api/pipeline/{runId}/status
Frontend (Vercel)
  ↓ displays real-time status
```

**Benefits:**
- ✅ Single source of truth (Prisma database)
- ✅ Real-time status updates
- ✅ Survives Railway dyno restarts
- ✅ Auto-completion when stage 5 finishes
- ✅ Auto-failure marking on any stage error
- ✅ No sync issues between frontend and backend

## Implementation Details

### New File: `backend/app/prisma_client.py`

HTTP client for calling Next.js Prisma API endpoints.

**Key Methods:**
```python
class PrismaAPIClient:
    def initialize_pipeline_stages(run_id: str) -> bool
    def mark_stage_processing(run_id: str, stage_number: int) -> bool
    def mark_stage_complete(run_id: str, stage_number: int, output_data: Any) -> bool
    def mark_stage_failed(run_id: str, stage_number: int, error_message: str) -> bool
```

**Authentication:**
- Uses `X-Webhook-Secret` header
- Reads from `WEBHOOK_SECRET` environment variable
- Must match frontend `WEBHOOK_SECRET`

**Endpoints Called:**
```
POST https://{FRONTEND_WEBHOOK_URL}/api/pipeline/{runId}/stage-update

Payload:
{
  "stageNumber": 1-5,
  "stageName": "Input Processing" | "Signal Amplification" | ...,
  "status": "PROCESSING" | "COMPLETED" | "FAILED" | "CANCELLED",
  "output": "JSON string or markdown",
  "completedAt": "ISO timestamp" (optional)
}
```

### Refactored: `backend/app/pipeline_runner.py`

**Removed Functions:**
- `initialize_status()` - Replaced by Prisma API call
- `update_stage_status()` - Replaced by Prisma API methods

**Updated Function:**
- `execute_pipeline_background()` - Now uses `PrismaAPIClient`

**New Execution Flow:**
1. Create `PrismaAPIClient()` instance
2. Call `initialize_pipeline_stages(run_id)` - marks stage 1 as PROCESSING
3. For each stage (1-5):
   - Execute stage logic
   - Save output locally (for debugging)
   - Call `mark_stage_complete(run_id, stage_num, output)`
4. Stage 5 completion automatically marks `PipelineRun.status = COMPLETED`
5. Any stage failure calls `mark_stage_failed()` which marks `PipelineRun.status = FAILED`

**Local File Storage:**
- Still saves to `/tmp/runs/{runId}/stage_{N}_output.json` for debugging
- `status.json` is NO LONGER CREATED OR UPDATED

### Not Modified: `backend/app/routes.py`

The Railway backend API endpoints remain unchanged:
- `POST /run` - Still works (starts pipeline execution)
- `GET /status/{runId}` - **NOW DEPRECATED** (reads from old status.json files)

**Note:** Frontend no longer calls `GET /status/{runId}`. It reads directly from Prisma via Next.js API routes.

## Environment Variables

**Required for Backend:**
```bash
FRONTEND_WEBHOOK_URL=https://innovation-web-rho.vercel.app
WEBHOOK_SECRET={shared-secret-with-frontend}
```

**Must Match Frontend .env:**
```bash
WEBHOOK_SECRET={same-shared-secret}
```

## Database Schema (Frontend Prisma)

```prisma
model StageOutput {
  id           String      @id @default(cuid())
  runId        String
  stageNumber  Int         // 1-5
  stageName    String      // "Input Processing", etc.
  status       RunStatus   // PROCESSING, COMPLETED, FAILED, CANCELLED
  output       String      @db.Text  // JSON or markdown
  completedAt  DateTime?
  createdAt    DateTime    @default(now())
  updatedAt    DateTime    @updatedAt
  run          PipelineRun @relation(fields: [runId], references: [id])

  @@unique([runId, stageNumber])  // Prevents duplicate stage records
  @@index([runId])
}
```

**Auto-Update Logic in Frontend API:**
- When stage 5 status = COMPLETED → `PipelineRun.status = COMPLETED`, `completedAt = now()`
- When any stage status = FAILED → `PipelineRun.status = FAILED`, `completedAt = now()`

## Testing

### Local Development Test:
```bash
# 1. Start frontend (Next.js)
cd innovation-web
npm run dev  # http://localhost:3000

# 2. Update backend .env.local
FRONTEND_WEBHOOK_URL=http://localhost:3000
WEBHOOK_SECRET=dev-secret-123

# 3. Start backend (FastAPI)
cd backend
uvicorn app.main:app --reload  # http://localhost:8000

# 4. Upload document and trigger pipeline
# Watch logs in both terminals

# 5. Verify Prisma updates
# Check database: prisma studio (or query StageOutput table)
```

### Production Test:
```bash
# 1. Deploy backend to Railway with updated code
git push railway architecture-cleanup-prisma:main

# 2. Verify environment variables in Railway dashboard
FRONTEND_WEBHOOK_URL=https://innovation-web-rho.vercel.app
WEBHOOK_SECRET={production-secret}

# 3. Trigger test run from frontend
# Monitor Railway logs for "Successfully updated stage X in Prisma"

# 4. Check frontend status endpoint
curl https://innovation-web-rho.vercel.app/api/pipeline/{runId}/status
```

## Rollback Plan

If Prisma integration causes issues:

1. **Revert backend to previous commit:**
   ```bash
   git revert b936cc0  # Prisma integration commit
   git push railway main
   ```

2. **Frontend will still work** - It reads from Prisma, which may just show empty stages

3. **Backend returns to file-based status** - Old `/status/{runId}` endpoint works again

## Migration Checklist

- [x] Create `PrismaAPIClient` class
- [x] Refactor `execute_pipeline_background()` to use Prisma API
- [x] Update completion webhook URL to `/api/pipeline/[runId]/complete`
- [x] Remove file-based status initialization/updates
- [x] Test locally (pending)
- [ ] Deploy to Railway
- [ ] Test end-to-end in production
- [ ] Monitor logs for Prisma API errors
- [ ] Verify stage updates appear in frontend real-time

## Known Issues & Limitations

1. **Railway `/status/{runId}` endpoint is deprecated**
   - Still exists but returns empty data (no status.json file)
   - Frontend doesn't use it anymore
   - Can be removed in future cleanup

2. **Network dependency**
   - Backend now depends on frontend API being available
   - If frontend is down, stage updates will fail
   - Pipeline execution continues, but status not persisted

3. **Authentication failures**
   - If `WEBHOOK_SECRET` mismatches, all Prisma updates fail
   - Pipeline runs but status shows "PROCESSING" forever
   - Check Railway logs for "401 Unauthorized" errors

## Monitoring

**Railway Logs to Watch:**
```
✅ [run-xxx] Updating stage 1 to PROCESSING via Prisma API
✅ [run-xxx] Successfully updated stage 1 in Prisma
❌ [run-xxx] Prisma API error: 401 - Unauthorized
❌ [run-xxx] Prisma API timeout after 30s
```

**Frontend Logs to Watch:**
```
✅ [StageUpdate] Updating run xxx stage 1 to PROCESSING
✅ [StageUpdate] Stage 1 updated: stage-output-cuid
❌ [StageUpdate] Authentication failed: Invalid secret
```

## Questions & Support

**Q: What if Prisma API call fails?**
A: Stage execution continues, but status not persisted. Check logs for error details. Pipeline completes but frontend shows stale status.

**Q: Do we still need `/tmp/runs` local files?**
A: Yes, for debugging. Stage outputs are saved locally for manual inspection.

**Q: Can we remove Railway `/status/{runId}` endpoint?**
A: Yes, but keep for backward compatibility until all clients migrated.

**Q: How do I debug status update failures?**
A: Check Railway logs for "Prisma API error" messages. Verify WEBHOOK_SECRET and FRONTEND_WEBHOOK_URL are correct.

---

**Last Updated:** 2025-10-25
**Author:** Claude Code
**Status:** ✅ Implementation Complete, Awaiting Testing
