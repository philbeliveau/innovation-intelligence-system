# Vercel Deployment Constraints & Solutions

**Status:** Critical architectural limitation identified
**Date:** 2025-10-19
**Impact:** Current implementation cannot deploy to Vercel without modifications

---

## Problem Summary

The Innovation Intelligence System pipeline takes **2-3 minutes** to complete (160 seconds measured), but Vercel serverless functions have strict timeout limits that make direct deployment impossible.

### Measured Performance
- **Stage 1 (Input Processing):** ~8 seconds
- **Stage 2 (Signal Amplification):** ~24 seconds
- **Stage 3 (General Translation):** ~45 seconds
- **Stage 4 (Brand Contextualization):** ~35 seconds
- **Stage 5 (Opportunity Generation):** ~48 seconds
- **Total Pipeline Runtime:** 160 seconds (2 minutes 40 seconds)

---

## Vercel Serverless Constraints

### 1. Function Timeout Limits
| Plan | Max Timeout | Pipeline Fit? |
|------|-------------|---------------|
| Hobby | 10 seconds | ❌ No (16x over) |
| Pro | 60 seconds | ❌ No (2.6x over) |
| Enterprise | 900 seconds (15 min) | ✅ Yes (but expensive) |

**Current Code:**
```typescript
// innovation-web/app/api/run/route.ts
execFile(pythonBin, [pythonScript, ...args], {
  timeout: 600000, // 10 minutes - WILL FAIL on Vercel Hobby/Pro
  maxBuffer: 10 * 1024 * 1024,
})
```

### 2. Background Process Limitation
- Serverless functions **terminate** when HTTP response is sent
- Current implementation returns `run_id` immediately but spawns `execFile` callback
- On Vercel: Python process **dies** when `/api/run` returns response
- ❌ **Pipeline never completes** despite returning 200 OK

**Why it works locally but fails on Vercel:**
```typescript
// Returns immediately (Vercel ends function execution here)
return NextResponse.json({ run_id, status: 'running' })

// This callback NEVER FIRES on Vercel (function already terminated)
execFile(..., (error, stdout, stderr) => {
  console.log('Pipeline complete') // Never logged on Vercel
})
```

### 3. File System Constraints
- Only `/tmp` directory is writable on Vercel
- `/tmp` is **ephemeral** (cleared between invocations)
- Current pipeline writes to: `data/test-outputs/{run_id}/`
- ❌ **Files disappear** after function execution

**Current Implementation:**
```typescript
// innovation-web/app/api/status/[runId]/route.ts
const dataDir = process.env.DATA_DIR || join(process.cwd(), '..', 'data')
const logPath = join(dataDir, 'test-outputs', sanitizedRunId, 'logs', 'pipeline.log')

// ❌ On Vercel: dataDir doesn't exist or is inaccessible
// ❌ Log files written to /tmp are lost after function ends
```

---

## Solution Architecture Options

### **Option 1: Queue + Worker Service (Recommended for Production)**

**Architecture:**
```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│ Vercel Next │─────▶│ Queue        │─────▶│ Worker      │─────▶│ Vercel Blob  │
│ /api/run    │      │ (Upstash)    │      │ (Modal.com) │      │ Storage      │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
      │                                                                  ▲
      │ Returns run_id immediately                                      │
      └──────────────────────────────────────────────────────────────────┘
                          /api/status reads from Blob Storage
```

**Implementation Steps:**

1. **Install Upstash Redis (Queue):**
```bash
npm install @upstash/redis
```

2. **Update `/api/run` to push to queue:**
```typescript
// innovation-web/app/api/run/route.ts
import { Redis } from '@upstash/redis'

const redis = Redis.fromEnv()

export async function POST(request: NextRequest) {
  const { blob_url, upload_id } = await request.json()
  const run_id = `run-${Date.now()}`

  // Push job to queue instead of executing locally
  await redis.lpush('pipeline-jobs', {
    run_id,
    blob_url,
    brand: companyId,
    timestamp: Date.now()
  })

  return NextResponse.json({ run_id, status: 'queued' })
}
```

3. **Create Modal.com worker** (Python):
```python
# worker/pipeline_worker.py
import modal
import redis
from pipeline import run_pipeline

stub = modal.Stub("innovation-pipeline")

@stub.function(
    image=modal.Image.debian_slim().pip_install("langchain", "openai"),
    timeout=600,  # 10 minutes
    secrets=[modal.Secret.from_name("openrouter-api")]
)
def process_job(job_data):
    run_id = job_data['run_id']
    # Download PDF from blob_url
    # Execute pipeline
    # Upload results to Vercel Blob
    # Write status to Redis
```

4. **Update `/api/status` to read from Blob:**
```typescript
// Read pipeline status from Vercel Blob instead of filesystem
const status = await get(`${run_id}/status.json`)
```

**Cost:** $0-10/month (Modal free tier: 30 CPU hours/month)

**Pros:**
- ✅ No timeout issues (Modal handles long-running jobs)
- ✅ Vercel stays serverless (no infrastructure management)
- ✅ Persistent storage via Blob
- ✅ Production-ready scalability

**Cons:**
- ⚠️ Additional service dependency (Modal + Upstash)
- ⚠️ More complex architecture

---

### **Option 2: Railway.app Python Backend (Recommended for Hackathon)**

**Architecture:**
```
┌─────────────┐                    ┌─────────────┐
│ Vercel Next │───────────────────▶│ Railway     │
│ Frontend    │  HTTP POST /run    │ Python API  │
└─────────────┘                    └─────────────┘
      │                                    │
      │ /api/status/{runId}                │ Runs pipeline
      │                                    │ Stores to /tmp
      └────────────────────────────────────┘
                  Returns log data
```

**Implementation Steps:**

1. **Create FastAPI backend** (project root):
```python
# api-server/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import time
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run")
async def run_pipeline(file: UploadFile = File(...), brand: str = ""):
    run_id = f"run-{int(time.time() * 1000)}"

    # Save uploaded file
    file_path = f"/tmp/{run_id}.pdf"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Execute pipeline in background (subprocess)
    subprocess.Popen([
        "python", "scripts/run_pipeline.py",
        "--input-file", file_path,
        "--brand", brand,
        "--run-id", run_id
    ])

    return {"run_id": run_id, "status": "running"}

@app.get("/status/{run_id}")
async def get_status(run_id: str):
    log_path = f"data/test-outputs/{run_id}/logs/pipeline.log"

    if not os.path.exists(log_path):
        return {"error": "Run ID not found"}, 404

    with open(log_path) as f:
        log_content = f.read()

    # Same status detection logic as current route.ts
    # Return status, current_stage, stage1_data
```

2. **Create `requirements.txt`:**
```txt
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
langchain==0.0.335
openai==1.3.5
```

3. **Deploy to Railway:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and init
railway login
railway init

# Deploy
railway up
```

4. **Update Next.js to use Railway API:**
```typescript
// innovation-web/lib/config.ts
export const config = {
  pipelineApiUrl: process.env.NEXT_PUBLIC_PIPELINE_API_URL || 'http://localhost:8000'
}

// innovation-web/app/api/run/route.ts
import { config } from '@/lib/config'

export async function POST(request: NextRequest) {
  const formData = new FormData()
  formData.append('file', pdfBlob)
  formData.append('brand', companyId)

  const response = await fetch(`${config.pipelineApiUrl}/run`, {
    method: 'POST',
    body: formData
  })

  return NextResponse.json(await response.json())
}
```

5. **Set Vercel environment variable:**
```bash
# In Vercel dashboard
NEXT_PUBLIC_PIPELINE_API_URL=https://your-app.up.railway.app
```

**Cost:** $0/month (Railway free tier: 512MB RAM, $5 credit/month)

**Pros:**
- ✅ Simple to implement (minimal code changes)
- ✅ No timeout issues (Railway supports long-running processes)
- ✅ Free tier sufficient for hackathon demo
- ✅ Keeps Python pipeline unchanged

**Cons:**
- ⚠️ Requires managing separate deployment
- ⚠️ Free tier has limited concurrent executions

---

### **Option 3: Pre-Generated Demo Results (Fastest for Stakeholder Demo)**

**For stakeholder presentations only** - bypass pipeline execution entirely.

**Implementation:**
```typescript
// innovation-web/app/api/run/route.ts
export async function POST(request: NextRequest) {
  const run_id = `demo-${Date.now()}`

  // Copy pre-generated pipeline output
  await fs.copy('data/demo-output', `data/test-outputs/${run_id}`)

  // Return immediately with demo results
  return NextResponse.json({ run_id, status: 'completed' })
}
```

**Pros:**
- ✅ Works perfectly on Vercel (no timeouts)
- ✅ Instant results for demos
- ✅ Zero infrastructure complexity

**Cons:**
- ❌ Not a real product (fake pipeline)
- ❌ Can't process actual uploaded PDFs

---

## Recommended Path Forward

### For Hackathon Demo (Next 48 hours):
**Use Option 2: Railway.app**
- Fastest path to working Vercel deployment
- Real pipeline execution (not faked)
- Free tier sufficient for demo load
- ~2 hours implementation time

### For Production Launch (Post-Hackathon):
**Use Option 1: Queue + Worker**
- Production-grade scalability
- Proper separation of concerns
- Can handle concurrent users
- Background job processing patterns

---

## Current Code Issues for Vercel

### File: `innovation-web/app/api/run/route.ts`
```typescript
// ❌ ISSUE 1: Timeout too long for Vercel Hobby/Pro
timeout: 600000, // 10 minutes - exceeds Vercel limits

// ❌ ISSUE 2: Background process terminates on Vercel
execFile(pythonBin, [pythonScript, ...args], {
  // This callback never fires on Vercel
  // Function execution ends before pipeline completes
}, (error, stdout, stderr) => {
  console.log('Done') // Never logged on Vercel
})

// ✅ Response sent (Vercel terminates function here)
return NextResponse.json({ run_id, status: 'running' })
```

### File: `innovation-web/app/api/status/[runId]/route.ts`
```typescript
// ❌ ISSUE 3: File system access fails on Vercel
const dataDir = process.env.DATA_DIR || join(process.cwd(), '..', 'data')

// On Vercel:
// - process.cwd() returns /var/task
// - Parent directory '../data' doesn't exist
// - Only /tmp is writable and it's ephemeral
```

---

## Environment Variables Required

### For Railway Option:
```bash
# Vercel (.env.production)
NEXT_PUBLIC_PIPELINE_API_URL=https://innovation-pipeline.up.railway.app

# Railway (.env)
OPENROUTER_API_KEY=sk-or-v1-...
DATA_DIR=/app/data
```

### For Modal + Upstash Option:
```bash
# Vercel
UPSTASH_REDIS_REST_URL=https://...
UPSTASH_REDIS_REST_TOKEN=...
BLOB_READ_WRITE_TOKEN=...

# Modal
OPENROUTER_API_KEY=sk-or-v1-...
BLOB_READ_WRITE_TOKEN=...
```

---

## Testing Checklist

- [ ] Local development works (current state: ✅)
- [ ] Railway deployment succeeds
- [ ] Vercel can call Railway API
- [ ] Pipeline completes on Railway
- [ ] Status polling works from Vercel
- [ ] Results page loads correctly
- [ ] Error handling for Railway downtime
- [ ] CORS configured properly
- [ ] Environment variables set in both platforms

---

## References

- [Vercel Function Limits](https://vercel.com/docs/functions/runtimes#max-duration)
- [Railway Documentation](https://docs.railway.app/)
- [Modal.com Documentation](https://modal.com/docs)
- [Upstash Redis](https://upstash.com/)
