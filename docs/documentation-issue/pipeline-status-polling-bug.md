# Pipeline Status Polling Bug - Critical Production Issue

**Date Discovered:** 2025-10-25
**Severity:** HIGH - Pipeline execution invisible to users
**Status:** RESOLVED

## Summary

The frontend pipeline viewer was failing to display real-time progress updates despite the backend successfully executing all pipeline stages. The UI would freeze after launching the pipeline, showing no stage progression, even though the backend was processing normally and sending webhook updates.

## Root Cause

**Status Value Mismatch Between Database and Frontend Polling Logic**

### The Chain of Events:

1. **Database Schema** (`prisma/schema.prisma`):
   ```prisma
   enum PipelineStatus {
     PROCESSING  // Uppercase
     COMPLETED
     FAILED
     CANCELLED
   }
   ```

2. **API Status Endpoint** (`app/api/pipeline/[runId]/status/route.ts:104`):
   ```typescript
   status: run.status.toLowerCase(), // "PROCESSING" → "processing"
   ```

3. **Frontend Polling Logic** (`components/pipeline/PipelineViewer.tsx:167`):
   ```typescript
   // BEFORE FIX (BROKEN):
   if (data.status === 'running') {  // Only checks 'running', not 'processing'
     timeoutId = setTimeout(pollStatus, 5000)
   }
   ```

4. **Result**: Polling stopped after first request because `'processing' !== 'running'`

## Symptoms

### User Experience:
- Upload document → Click "Launch Pipeline" → UI freezes
- No stage progress indicators updating
- Pipeline appears stuck on Stage 1 indefinitely
- Backend logs show successful completion, but frontend shows nothing

### Technical Indicators:
- Vercel logs show only **ONE** status poll instead of continuous polling
- Backend webhook updates arriving successfully (200 OK)
- Railway logs show pipeline completing all 5 stages
- No error messages in browser console
- Browser console shows: `[PipelineViewer] Pipeline status: processing - stopping poll`

## Detection History

This bug was **extremely persistent** and **difficult to diagnose** because:

1. **Multiple false leads**:
   - Initially suspected wrong port configuration (3001 vs 3000)
   - Investigated webhook authentication failures
   - Checked for routing issues (wrong endpoint being polled)
   - Examined database connectivity problems
   - Looked for race conditions in run creation

2. **Misleading symptoms**:
   - Backend logs showed 100% success (all stages completing)
   - Webhook updates were being received (200 OK)
   - API endpoint returned correct data
   - No JavaScript errors in console

3. **Silent failure**:
   - Polling simply stopped without error
   - TypeScript types didn't catch the mismatch
   - No warning about unexpected status value

4. **Required comprehensive logging to discover**:
   - Added 15+ console.log statements across 2 components
   - Traced entire execution flow from launch to polling
   - Finally revealed the critical log: `Pipeline status: processing - stopping poll`

## The Fix

### Code Changes

**File:** `components/pipeline/PipelineViewer.tsx`

**1. Update TypeScript Interface (Line 26-32):**
```typescript
interface PipelineStatus {
  run_id: string
  status: 'running' | 'processing' | 'complete' | 'completed' | 'error'  // Added 'processing'
  current_stage: number
  stage1_data?: Stage1Data
  brand_name?: string
}
```

**2. Update Polling Logic (Line 167-172):**
```typescript
// AFTER FIX (WORKING):
if (data.status === 'running' || data.status === 'processing') {
  console.log('[PipelineViewer] Pipeline still', data.status, '- polling again in 5s')
  timeoutId = setTimeout(pollStatus, 5000)
} else {
  console.log('[PipelineViewer] Pipeline status:', data.status, '- stopping poll')
}
```

**3. Normalize Status for UI State (Line 144-154):**
```typescript
// Normalize status: 'complete' → 'completed', 'processing' → 'running'
let normalizedStatus: 'running' | 'completed' | 'error' = 'running'
if (data.status === 'complete' || data.status === 'completed') {
  normalizedStatus = 'completed'
} else if (data.status === 'error') {
  normalizedStatus = 'error'
} else {
  // 'running' or 'processing' both map to 'running' for UI state
  normalizedStatus = 'running'
}
setStatus(normalizedStatus)
```

### Commits
- **Logging added:** `feat(logging): add comprehensive logging to PipelineViewer and analyze page` (0789f3a)
- **Bug fixed:** `fix(pipeline): continue polling when status is 'processing'` (4e9b063)

## Prevention Strategies

### 1. Type Safety Improvements

**Problem:** TypeScript didn't catch the mismatch because the API returns `string` that gets cast to the union type.

**Solution:** Use a status mapping function with validation:

```typescript
type DatabaseStatus = 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED'
type FrontendStatus = 'running' | 'completed' | 'error'

function mapStatusToFrontend(dbStatus: string): FrontendStatus {
  const normalized = dbStatus.toLowerCase()
  switch (normalized) {
    case 'processing':
      return 'running'
    case 'completed':
    case 'complete':
      return 'completed'
    case 'failed':
    case 'cancelled':
    case 'error':
      return 'error'
    default:
      console.error('Unknown status:', dbStatus)
      return 'error'
  }
}
```

### 2. Comprehensive Logging

**Keep the diagnostic logs** added during debugging:
- Component mount confirmations
- Polling attempts with full URLs
- Status values received from API
- Polling continuation/termination decisions

These logs saved us and will help diagnose future issues quickly.

### 3. API Contract Documentation

**Document status value mappings** in API route files:

```typescript
/**
 * GET /api/pipeline/[runId]/status
 *
 * Status Values:
 * - Database: PROCESSING, COMPLETED, FAILED, CANCELLED (uppercase enum)
 * - API Response: processing, completed, failed, cancelled (lowercase)
 * - Frontend: running, completed, error (normalized)
 *
 * IMPORTANT: Frontend must handle both 'processing' and 'running' for active pipelines
 */
```

### 4. Integration Tests

Add tests for status polling behavior:

```typescript
describe('PipelineViewer polling', () => {
  it('continues polling when status is processing', async () => {
    mockAPI.mockReturnValue({ status: 'processing', current_stage: 1 })

    render(<PipelineViewer runId="test-123" />)

    await waitFor(() => expect(mockAPI).toHaveBeenCalledTimes(1))
    await waitFor(() => expect(mockAPI).toHaveBeenCalledTimes(2), { timeout: 6000 })
  })

  it('stops polling when status is completed', async () => {
    mockAPI.mockReturnValue({ status: 'completed', current_stage: 5 })

    render(<PipelineViewer runId="test-123" />)

    await waitFor(() => expect(mockAPI).toHaveBeenCalledTimes(1))
    await new Promise(r => setTimeout(r, 6000))
    expect(mockAPI).toHaveBeenCalledTimes(1) // No second call
  })
})
```

### 5. Status Enum Standardization

**Consider standardizing on one status representation** across the stack:

**Option A:** Use lowercase everywhere
```prisma
enum PipelineStatus {
  processing
  completed
  failed
  cancelled
}
```

**Option B:** Use uppercase in DB, explicit mapping in API layer with validation

## Related Issues

### Issue 1: `/api/analyze-document` Timeout (504)
**Status:** OPEN
**Impact:** MEDIUM - Pre-flight analysis fails for large PDFs
**Cause:** Vercel serverless function 10-second timeout
**Workaround:** Pipeline can still launch without analysis completing

### Issue 2: Webhook Authentication Failures
**Status:** RESOLVED (2025-10-25)
**Cause:** Malformed `.env.local` file (missing newline)
**Fix:** Separated `WEBHOOK_SECRET` onto its own line

### Issue 3: Port Mismatch (Frontend 3000 vs Backend Webhook Target 3001)
**Status:** RESOLVED (2025-10-25)
**Cause:** Backend `.env.local` had wrong port
**Fix:** Changed `FRONTEND_WEBHOOK_URL` to port 3000

## Impact Assessment

### Before Fix:
- **User Impact:** 100% of pipeline launches appeared to freeze
- **Business Impact:** System completely unusable for core workflow
- **Data Impact:** None - backend processed correctly, only display broken

### After Fix:
- **User Experience:** Real-time pipeline progress updates working
- **Confidence:** High - comprehensive logging remains for future debugging
- **Technical Debt:** Minimal - clean fix with good documentation

## Lessons Learned

1. **Status enums must match across layers** - Database → API → Frontend
2. **Lowercase conversions are dangerous** - Easy to miss in code review
3. **TypeScript union types don't validate runtime values** - Need runtime checks
4. **Comprehensive logging is essential** - Silent failures are the worst
5. **Test the unhappy path** - What happens when status is unexpected?
6. **Document API contracts explicitly** - Especially value mappings
7. **Integration tests catch these bugs** - Unit tests alone aren't enough

## Timeline

- **2025-10-25 14:00 UTC**: User reports frontend not updating during pipeline execution
- **2025-10-25 14:15 UTC**: Initial investigation - suspected port mismatch
- **2025-10-25 14:30 UTC**: Fixed port configuration, issue persisted
- **2025-10-25 15:00 UTC**: Investigated webhook authentication, fixed `.env.local`
- **2025-10-25 16:00 UTC**: Added comprehensive logging to trace execution
- **2025-10-25 16:30 UTC**: Deployed logging, user tested and provided console output
- **2025-10-25 16:45 UTC**: **BREAKTHROUGH** - Discovered `status: processing - stopping poll` log
- **2025-10-25 17:00 UTC**: Fixed polling logic to handle 'processing' status
- **2025-10-25 17:15 UTC**: Deployed fix to production
- **2025-10-25 17:30 UTC**: Verified fix working - real-time updates displaying

**Total Time to Resolution:** ~3.5 hours (with 2 previous unrelated fixes along the way)

## References

- **Backend Status Enum:** `backend/prisma/schema.prisma`
- **API Status Endpoint:** `innovation-web/app/api/pipeline/[runId]/status/route.ts`
- **Frontend Polling Logic:** `innovation-web/components/pipeline/PipelineViewer.tsx`
- **Status Update Webhook:** `innovation-web/app/api/pipeline/[runId]/stage-update/route.ts`
- **Backend Prisma Client:** `backend/app/prisma_client.py`

## Related Documentation

- [Frontend Architecture](../architecture.md)
- [Pipeline API Design](../api-design.md)
- [Webhook Authentication](../webhook-auth.md)
- [Environment Configuration](../env-setup.md)

---

**Documented by:** Claude Code Agent
**Last Updated:** 2025-10-25
**Version:** 1.0
