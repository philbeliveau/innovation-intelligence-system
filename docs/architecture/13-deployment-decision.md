# Deployment Architecture Decision - Vercel Serverless Incompatibility

**Status:** Decision Required
**Date:** 2025-10-19
**Context:** QA Gate 3.1 identified critical serverless incompatibility
**Related:** docs/qa/gates/3.1-api-routes-pipeline-execution.yml (ARCH-001)

---

## Problem Statement

The current implementation executes Python pipeline via `execFile()` in Next.js API routes. This works locally but **will fail in Vercel production** due to serverless function time limits (10-60 seconds max).

**Pipeline execution time:** 2-5 minutes for full 5-stage LLM workflow
**Vercel serverless timeout:** 10s (Hobby), 60s (Pro), 300s (Enterprise)

---

## Options Analysis

### Option 1: Deploy Python Separately + Queue Pattern ⭐ RECOMMENDED

**Architecture:**
```
Next.js (Vercel)     →  Queue (Vercel KV/Upstash)  ←→  Python Worker (separate host)
    ↓                          ↓                              ↓
  Upload PDF             Enqueue job                   Poll queue
  Return run_id          Store status                  Execute pipeline
  Poll status            Update progress               Write to blob storage
```

**Pros:**
- ✅ Works within Vercel serverless constraints
- ✅ Horizontal scaling of Python workers
- ✅ Real-time progress updates
- ✅ Retry logic and failure handling
- ✅ Minimal Next.js changes

**Cons:**
- ❌ Requires additional infrastructure (worker hosting + queue)
- ❌ Added operational complexity
- ❌ Increased latency (queue polling)

**Implementation:**
1. Deploy Python workers on: Railway, Render, Fly.io, or AWS Lambda
2. Use Vercel KV (Redis) for job queue
3. API route enqueues job, returns immediately
4. Status endpoint polls queue for progress
5. Results stored in Vercel Blob

**Cost:** ~$5-10/month (Vercel KV + worker hosting)

---

### Option 2: Change Hosting Platform (All-in-one)

**Architecture:**
```
Platform (Railway/Render)
    ↓
  Next.js + Python (long-running process)
```

**Pros:**
- ✅ Simplest architecture (no queue)
- ✅ Direct process execution works
- ✅ Single deployment target

**Cons:**
- ❌ Loses Vercel edge network benefits
- ❌ Manual scaling configuration
- ❌ Potentially higher hosting costs
- ❌ Abandons Vercel Blob integration

**Implementation:**
1. Containerize Next.js + Python in Docker
2. Deploy to Railway/Render/DigitalOcean
3. No code changes required

**Cost:** ~$15-25/month (platform hosting)

---

### Option 3: Vercel Cron + Background Jobs (Vercel Enterprise Only)

**Architecture:**
```
Next.js API Route  →  Vercel Background Function (300s limit)
                            ↓
                      Python execution via Docker
```

**Pros:**
- ✅ Stays on Vercel platform
- ✅ Built-in job queue
- ✅ 300s timeout (may be sufficient)

**Cons:**
- ❌ Requires Vercel Enterprise plan ($400+/month)
- ❌ 300s may still be insufficient for complex pipelines
- ❌ Docker image size limits

**Implementation:**
1. Upgrade to Vercel Enterprise
2. Package Python in Docker container
3. Use Vercel Background Functions API

**Cost:** $400+/month (Enterprise plan)

---

### Option 4: Client-Side Orchestration (NOT RECOMMENDED)

**Architecture:**
```
Browser  →  Direct OpenRouter API calls  →  LLM providers
```

**Pros:**
- ✅ No serverless timeout issues
- ✅ Zero backend infrastructure

**Cons:**
- ❌ Exposes API keys to client
- ❌ Cannot use Python processing logic
- ❌ Inconsistent with existing pipeline
- ❌ Poor UX (browser must stay open)

**Not viable** - security and UX concerns.

---

## Decision Matrix

| Criteria | Option 1 (Queue) | Option 2 (Platform) | Option 3 (Enterprise) |
|----------|------------------|---------------------|-----------------------|
| Serverless compatible | ✅ Yes | ⚠️ N/A | ✅ Yes |
| Cost (monthly) | $5-10 | $15-25 | $400+ |
| Complexity | Medium | Low | Medium |
| Scalability | High | Medium | High |
| Vercel benefits | ✅ Keep | ❌ Lose | ✅ Keep |
| Implementation time | 2-3 days | 1 day | 3-4 days |

---

## Recommendation

**Option 1: Queue Pattern** for MVP/hackathon demo:

1. **Immediate (Hackathon MVP):**
   - Keep current implementation for local demo
   - Document limitation in README
   - Add warning banner: "Demo mode - processing may timeout in production"

2. **Production (Post-MVP):**
   - Implement queue pattern with Railway Python workers
   - Use Vercel KV for job queue
   - Minimal refactoring of existing code

**Rationale:**
- Lowest cost for startup/MVP
- Most scalable long-term
- Preserves Vercel edge network benefits
- Clear migration path from demo to production

---

## Implementation Plan (Production)

### Phase 1: Queue Infrastructure (Day 1)
- [ ] Set up Vercel KV (Redis) for job queue
- [ ] Create job schema: `{ run_id, status, progress, error }`
- [ ] Deploy Python worker to Railway with job polling

### Phase 2: API Refactoring (Day 2)
- [ ] Modify `/api/run` to enqueue job instead of executing
- [ ] Update `/api/status` to read from queue
- [ ] Add progress percentage to status response

### Phase 3: Worker Implementation (Day 3)
- [ ] Create `worker.py` that polls Redis queue
- [ ] Add status update calls after each stage
- [ ] Implement retry logic and error handling

### Phase 4: Testing & Deployment (Day 4)
- [ ] Integration testing with real PDFs
- [ ] Load testing with concurrent jobs
- [ ] Deploy to production

---

## Migration Path from Current Code

**Current:**
```typescript
// app/api/run/route.ts
execFile('python', [pythonScript, ...args], ...)  // Blocks until complete
return NextResponse.json({ run_id, status: 'running' })
```

**After Migration:**
```typescript
// app/api/run/route.ts
await redis.lpush('pipeline_jobs', JSON.stringify({ run_id, blob_url, brand }))
return NextResponse.json({ run_id, status: 'queued' })

// worker.py (Railway)
while True:
    job = redis.brpop('pipeline_jobs')
    run_pipeline(job['blob_url'], job['brand'], job['run_id'])
    redis.set(f"status:{job['run_id']}", 'completed')
```

---

## Risk Mitigation

**Risk:** Worker downtime causes job backlog
**Mitigation:** Health checks, auto-restart, Redis persistence

**Risk:** Queue grows faster than processing
**Mitigation:** Horizontal scaling of workers, rate limiting

**Risk:** Long-running jobs exceed 5 minutes
**Mitigation:** Stage-by-stage checkpointing, resume capability

---

## References

- Vercel Serverless Limits: https://vercel.com/docs/functions/serverless-functions/runtimes#max-duration
- Vercel KV (Redis): https://vercel.com/docs/storage/vercel-kv
- Railway Python Deployment: https://docs.railway.app/guides/python
- QA Gate Report: docs/qa/gates/3.1-api-routes-pipeline-execution.yml

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-19 | Documented options | QA gate identified blocker |
| TBD | Final decision needed | Awaiting stakeholder input |
