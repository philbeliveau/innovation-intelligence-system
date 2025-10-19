# Hackathon Analysis: Current State to Web App Migration

**Analysis Date:** January 2025
**Architect:** Winston
**Goal:** Transform CLI pipeline into Vercel-hosted web application in 1 day

---

## Executive Summary

You have a **fully functional Python CLI pipeline** that successfully processes innovation documents through 5 LangChain stages. The architecture document describes an **ambitious full-stack web application** with React Server Components, Postgres, Blob storage, and serverless Python functions.

**Gap Analysis:** The current architecture is 90% CLI, 10% web-ready. For a 1-day hackathon, you need **aggressive scope reduction** and **maximum reuse** of existing Python pipeline.

**Recommendation:** Build a **minimal web wrapper** around your existing pipeline rather than rebuilding it as serverless functions.

---

## Current State Analysis

### ✅ What You Have (Working & Production-Ready)

#### 1. **Complete Python Pipeline** (`/pipeline/`)
- **5 Stages Fully Implemented:**
  - `stage1_input_processing.py` - Inspiration extraction
  - `stage2_signal_amplification.py` - Trend identification
  - `stage3_general_translation.py` - Universal lessons
  - `stage4_brand_contextualization.py` - Brand-specific insights
  - `stage5_opportunity_generation.py` - 5 opportunity cards

- **LangChain Integration:** Uses OpenRouter API with model configuration in `.env`
- **File-Based Execution:** Reads PDFs from `documentation/document/`, writes markdown to `data/test-outputs/`
- **Research Data Integration:** Loads brand research from `docs/web-search-setup/{brand}-research.md` (550-720 lines each)
- **Logging & Error Handling:** Comprehensive logging to `logs/pipeline.log` and `logs/errors.log`

#### 2. **Execution Scripts** (`/scripts/`)
- `run_pipeline.py` - Main orchestrator (single run or batch mode)
- `auto_score_opportunities.py` - Quality assessment
- `validate_differentiation.py` - Brand differentiation analysis
- `collect_opportunities.py` - Output aggregation

#### 3. **Data Assets**
- **Brand Profiles:** 4 YAML files in `data/brand-profiles/` (Lactalis, McCormick, Columbia, Decathlon)
- **Input Documents:** PDFs in `documentation/document/`
- **Research Files:** Comprehensive brand research (8 sections, 120+ data points per brand)

#### 4. **Pipeline Utilities** (`pipeline/utils.py`)
```python
create_llm(temperature, max_tokens)           # LLM factory with OpenRouter
load_input_document(input_id)                 # PDF loading
load_brand_profile(brand_id)                  # YAML parsing
load_research_data(brand_id)                  # Research markdown loading
create_test_output_dir(input_id, brand_id)    # Output directory creation
setup_pipeline_logging(output_dir)            # Multi-handler logging
```

---

### ❌ What You Don't Have (Described in Architecture, Not Built)

#### 1. **Web Frontend**
- No Next.js application
- No React components
- No Monaco editor for prompt editing
- No UI for file upload or drag-and-drop

#### 2. **API Layer**
- No Next.js Route Handlers (`/api/pipeline/execute`, `/api/pipeline/status`, etc.)
- No TypeScript API interfaces
- No request/response models

#### 3. **Serverless Functions**
- Pipeline stages are NOT serverless functions (they're local Python modules)
- No Vercel Python function configuration (`api/` directory with `requirements.txt`)

#### 4. **Database & Blob Storage**
- No Vercel Postgres schema or Drizzle ORM setup
- No Vercel Blob storage integration
- All data is file-based (local disk)

#### 5. **Deployment Configuration**
- No `vercel.json`
- No NPM workspaces or monorepo structure (`apps/web`, `api/python`)
- No environment variable configuration for Vercel

---

## Architecture Document vs. Reality

| Architecture Component | Described in Doc | Currently Exists | Implementation Gap |
|------------------------|-----------------|------------------|-------------------|
| **Python Pipeline (Stages 1-5)** | ✅ | ✅ | **0% - READY** |
| **Next.js 15 Frontend** | ✅ | ❌ | **100% - NOT STARTED** |
| **API Route Handlers** | ✅ | ❌ | **100% - NOT STARTED** |
| **Vercel Postgres** | ✅ | ❌ | **100% - NOT STARTED** |
| **Vercel Blob Storage** | ✅ | ❌ | **100% - NOT STARTED** |
| **Serverless Python Functions** | ✅ | ❌ | **100% - NOT STARTED** |
| **Monaco Prompt Editor** | ✅ | ❌ | **100% - NOT STARTED** |
| **Model Selection UI** | ✅ | ❌ | **100% - NOT STARTED** |
| **Cost Estimation** | ✅ | ❌ | **100% - NOT STARTED** |
| **Real-time Progress Tracking** | ✅ | ❌ | **100% - NOT STARTED** |

**Overall Implementation Status: 10% Complete**
(Pipeline logic exists, but 90% of web infrastructure is missing)

---

## Pipeline Execution Model: CLI vs. Serverless

### Current Model (CLI - What Works)

```python
# scripts/run_pipeline.py (Simplified)

def run_single_test(input_id, brand_id):
    # 1. Create output directory
    output_dir = create_test_output_dir(input_id, brand_id)

    # 2. Load inputs
    input_text = load_input_document(input_id)
    brand_profile = load_brand_profile(brand_id)
    research_data = load_research_data(brand_id)

    # 3. Run stages sequentially (blocking, 15-30 min total)
    stage1 = create_stage1_chain()
    result1 = stage1.run(input_text)
    stage1.save_output(result1['stage1_output'], output_dir)

    stage2 = create_stage2_chain()
    result2 = stage2.run(result1['stage1_output'])
    stage2.save_output(result2['stage2_output'], output_dir)

    # ... stages 3, 4, 5 (each takes 3-6 minutes)

    # 4. Write final opportunities to data/test-outputs/{run-id}/stage5/
    return output_dir
```

**Execution Time:** 15-30 minutes for complete pipeline
**Blocking:** User waits for all stages to complete
**Output:** Local files in `data/test-outputs/`

---

### Target Model (Serverless - Architecture Description)

```typescript
// Described in architecture but NOT implemented

// 1. User triggers test in UI
POST /api/pipeline/execute
→ Creates TestRun record in Postgres (status: pending)
→ Returns run_id immediately

// 2. Backend triggers Stage 1 serverless function
invoke_serverless_function('api/python/stage1.py', {run_id, input_id})
→ Loads PDF from Blob storage
→ Calls OpenRouter API
→ Saves output to Blob
→ Updates Postgres (status: stage_1_complete)
→ Triggers Stage 2

// 3-6. Stages 2-5 execute sequentially via serverless functions
// Each stage:
// - Loads previous stage output from Blob
// - Processes with LLM
// - Saves to Blob
// - Updates Postgres status
// - Triggers next stage

// 7. Frontend polls /api/pipeline/status/{runId} every 5 seconds
GET /api/pipeline/status/{runId}
→ Returns current_stage, progress_percentage, actual_cost_usd

// 8. When complete, fetch results
GET /api/pipeline/results/{runId}
→ Returns 5 opportunity cards from Blob storage
```

**Execution Time:** Same 15-30 min, but asynchronous
**Non-blocking:** User gets immediate response, watches progress
**Output:** Blob storage URLs, metadata in Postgres

---

## Critical Challenges for 1-Day Hackathon

### 🚨 HIGH RISK: Cannot Be Solved in 1 Day

1. **Serverless Function Timeout (300s limit)**
   - **Problem:** Each pipeline stage takes 3-6 minutes of LLM API calls
   - **Required Solution:** Stage-by-stage orchestration with state persistence
   - **Effort:** 4-6 hours of debugging async workflows

2. **Blob Storage Integration**
   - **Problem:** All inputs/outputs are currently local files
   - **Required Changes:**
     - Upload PDFs to Blob on drag-and-drop
     - Read from Blob URLs instead of file paths
     - Write outputs to Blob instead of local disk
   - **Effort:** 3-4 hours (SDK learning + refactoring)

3. **Postgres Schema Design & ORM Setup**
   - **Problem:** No database, need schema for TestRun, PromptConfiguration, StageOutput
   - **Required Work:** Drizzle ORM setup, migrations, CRUD operations
   - **Effort:** 3-4 hours

4. **Serverless Python Function Configuration**
   - **Problem:** Pipeline stages are local modules, not deployable functions
   - **Required Changes:**
     - Create `api/python/stage{1-5}.py` entry points
     - Configure `requirements.txt` for each function
     - Handle cold starts and import optimization
   - **Effort:** 2-3 hours

5. **Next.js 15 App Router Setup**
   - **Problem:** No frontend application exists
   - **Required Work:**
     - Initialize Next.js project
     - Install shadcn/ui components
     - Build file upload UI
     - Create progress polling UI
     - Build results viewer
   - **Effort:** 6-8 hours (even with copy-paste components)

**Total Estimated Effort:** 18-25 hours (2-3 full days of development)

---

### ✅ LOW RISK: Achievable in 1 Day (Simplified Approach)

**Strategy:** Build a **thin web wrapper** that runs your existing Python pipeline as-is.

---

## Recommended Hackathon Architecture: "Minimal Viable Web Wrapper"

### Core Principle
**Don't rebuild the pipeline as serverless functions. Wrap the CLI in a web interface.**

---

### Simplified System Architecture

```mermaid
graph TB
    subgraph "Frontend - Next.js (Simplified)"
        A[File Upload UI<br/>Drag & Drop]
        B[Brand Selector]
        C[Run Button]
        D[Progress Viewer<br/>Server-Sent Events]
        E[Results Display]
    end

    subgraph "Backend - Next.js API Routes"
        F[POST /api/upload<br/>Save to /tmp]
        G[POST /api/run<br/>Spawn Python subprocess]
        H[GET /api/status/:runId<br/>Read log files]
        I[GET /api/results/:runId<br/>Read markdown files]
    end

    subgraph "Pipeline - Python CLI (UNCHANGED)"
        J[run_pipeline.py<br/>--input /tmp/upload.pdf<br/>--brand {brand_id}]
        K[Stage 1-5 Execution<br/>EXACTLY AS IS]
        L[Output to<br/>data/test-outputs/]
    end

    A --> F
    B --> G
    C --> G
    D --> H
    E --> I

    F --> G
    G --> J
    J --> K
    K --> L
    L --> H
    L --> I

    style J fill:#4ecdc4
    style K fill:#95e1d3
    style L fill:#f38181
```

---

### Architecture Modifications (Minimal)

#### 1. **Frontend** (2-3 hours)
- **Framework:** Next.js 15 (create-next-app)
- **UI Library:** shadcn/ui (install via CLI, copy-paste 5 components)
- **Pages:**
  - `/` - Home page with file upload, brand selector, run button
  - `/run/[runId]` - Progress tracking page
  - `/results/[runId]` - Results viewer

**Key Components:**
```tsx
// app/page.tsx
'use client'
export default function Home() {
  return (
    <>
      <FileDropzone onUpload={uploadFile} />
      <BrandSelector brands={['lactalis-canada', 'mccormick-usa', ...]} />
      <Button onClick={runPipeline}>Generate Opportunities</Button>
    </>
  )
}
```

#### 2. **API Routes** (3-4 hours)
```typescript
// app/api/upload/route.ts
export async function POST(request: Request) {
  const formData = await request.formData()
  const file = formData.get('file') as File

  // Save to /tmp or Vercel Blob (if using Blob)
  const tmpPath = `/tmp/${crypto.randomUUID()}.pdf`
  await writeFile(tmpPath, Buffer.from(await file.arrayBuffer()))

  return NextResponse.json({ file_path: tmpPath })
}

// app/api/run/route.ts
export async function POST(request: Request) {
  const { file_path, brand_id } = await request.json()
  const run_id = crypto.randomUUID()

  // Spawn Python subprocess (non-blocking)
  exec(`python scripts/run_pipeline.py --input ${file_path} --brand ${brand_id}`, {
    cwd: process.cwd(),
    env: { ...process.env, RUN_ID: run_id }
  })

  return NextResponse.json({ run_id, status: 'running' })
}

// app/api/status/[runId]/route.ts
export async function GET(request: Request, { params }: { params: { runId: string } }) {
  // Read logs/pipeline.log to determine current stage
  const logPath = `data/test-outputs/${params.runId}/logs/pipeline.log`
  const logs = await readFile(logPath, 'utf-8')

  const currentStage = detectStageFromLogs(logs)

  return NextResponse.json({
    run_id: params.runId,
    status: currentStage === 5 ? 'completed' : 'running',
    current_stage: currentStage,
    progress_percentage: (currentStage / 5) * 100
  })
}

// app/api/results/[runId]/route.ts
export async function GET(request: Request, { params }: { params: { runId: string } }) {
  const outputDir = `data/test-outputs/${params.runId}/stage5`

  // Read opportunity markdown files
  const opportunities = await Promise.all(
    [1,2,3,4,5].map(num => readFile(`${outputDir}/opportunity-${num}.md`, 'utf-8'))
  )

  return NextResponse.json({ opportunities })
}
```

#### 3. **Python Pipeline Modifications** (1-2 hours)
**MINIMAL CHANGES:**

```python
# scripts/run_pipeline.py (add at top)
import os

# Accept input as file path instead of manifest ID
def run_single_test_from_file(input_file_path: str, brand_id: str):
    run_id = os.getenv('RUN_ID', f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

    # Create output directory using RUN_ID
    output_dir = Path(f"data/test-outputs/{run_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read PDF directly instead of using manifest
    from pypdf import PdfReader
    reader = PdfReader(input_file_path)
    input_text = "".join(page.extract_text() for page in reader.pages)

    # Rest of pipeline UNCHANGED
    brand_profile = load_brand_profile(brand_id)
    research_data = load_research_data(brand_id)

    # Run stages 1-5 (EXACTLY AS IS)
    # ...
```

**That's it. No serverless functions. No Blob storage. No Postgres.**

---

### Technology Stack (Simplified)

| Component | Technology | Why |
|-----------|-----------|-----|
| **Frontend** | Next.js 15 + shadcn/ui | Fast setup, copy-paste components |
| **API** | Next.js Route Handlers | Same runtime, no separate server |
| **File Storage** | Local `/tmp` (or Vercel Blob if needed) | Simplest approach |
| **Database** | None (file-based state) | Avoid ORM/migration overhead |
| **Python Runtime** | Node.js `child_process.exec()` | Run CLI directly from API route |
| **Progress Tracking** | Log file polling | No WebSockets/SSE complexity |
| **Deployment** | Vercel | One-click deploy |

---

### What You Can Build in 1 Day

#### Hour 0-1: Setup
- [ ] Create Next.js app: `npx create-next-app@latest innovation-web`
- [ ] Install shadcn/ui: `npx shadcn-ui@latest init`
- [ ] Add components: `npx shadcn-ui@latest add button card input select`

#### Hour 1-3: Frontend
- [ ] File dropzone with react-dropzone
- [ ] Brand selector dropdown (4 brands hardcoded)
- [ ] "Generate Opportunities" button
- [ ] Simple progress bar (polling-based)

#### Hour 3-6: API Routes
- [ ] `POST /api/upload` - Save PDF to `/tmp`
- [ ] `POST /api/run` - Spawn `run_pipeline.py` subprocess
- [ ] `GET /api/status/:runId` - Parse log files for stage detection
- [ ] `GET /api/results/:runId` - Read opportunity markdown files

#### Hour 6-7: Pipeline Integration
- [ ] Modify `run_pipeline.py` to accept file paths instead of manifest IDs
- [ ] Add `RUN_ID` environment variable support
- [ ] Ensure outputs go to predictable directories

#### Hour 7-8: UI Polish & Testing
- [ ] Results page with opportunity card display
- [ ] Error handling (show errors from `logs/errors.log`)
- [ ] Basic styling with Tailwind

#### Hour 8: Deploy to Vercel
- [ ] `vercel` (one command)
- [ ] Set environment variables (OPENROUTER_API_KEY)
- [ ] Test live deployment

---

### File Upload to Blob Storage (If Needed)

If Vercel's `/tmp` doesn't work (it should for PDFs <50MB), add Blob:

```typescript
// app/api/upload/route.ts
import { put } from '@vercel/blob'

export async function POST(request: Request) {
  const formData = await request.formData()
  const file = formData.get('file') as File

  const blob = await put(`uploads/${file.name}`, file, { access: 'public' })

  return NextResponse.json({ blob_url: blob.url })
}

// Then modify run_pipeline.py to download from URL:
import requests

def load_pdf_from_url(url: str) -> str:
    response = requests.get(url)
    with open('/tmp/input.pdf', 'wb') as f:
        f.write(response.content)
    # ... extract text
```

**Effort:** +30 minutes

---

## Deployment Checklist for Vercel

### 1. Project Structure
```
innovation-intelligence-system/
├── app/                    # Next.js App Router
│   ├── page.tsx
│   ├── layout.tsx
│   ├── run/[runId]/page.tsx
│   ├── results/[runId]/page.tsx
│   └── api/
│       ├── upload/route.ts
│       ├── run/route.ts
│       ├── status/[runId]/route.ts
│       └── results/[runId]/route.ts
├── components/ui/          # shadcn components
├── scripts/                # Python pipeline (UNCHANGED)
├── pipeline/               # Python modules (UNCHANGED)
├── data/                   # Brand profiles, outputs
├── package.json
├── vercel.json             # Configuration
└── .env.local              # OPENROUTER_API_KEY
```

### 2. `vercel.json`
```json
{
  "buildCommand": "npm run build",
  "framework": "nextjs",
  "env": {
    "OPENROUTER_API_KEY": "@openrouter-api-key",
    "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1"
  },
  "functions": {
    "app/api/run/route.ts": {
      "maxDuration": 300
    }
  }
}
```

### 3. Environment Variables (Vercel Dashboard)
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `OPENROUTER_BASE_URL` - `https://openrouter.ai/api/v1`
- `LLM_MODEL` - `deepseek/deepseek-chat` (or your preferred model)

### 4. Python Dependencies
```bash
# Vercel automatically detects requirements.txt
# Your existing requirements.txt should work as-is
```

---

## Risk Assessment

### ✅ Low Risk (Will Definitely Work)
- File upload UI
- Running Python pipeline as subprocess
- Reading output files from disk
- Basic progress tracking via log polling

### ⚠️ Medium Risk (Might Need Tweaks)
- Vercel function timeout (300s) - Pipeline takes 15-30 min
  - **Mitigation:** Use background jobs or split into stages
- File size limits in `/tmp` (512MB limit)
  - **Mitigation:** Use Vercel Blob if PDFs are large

### 🚨 High Risk (May Not Work on Vercel)
- Long-running Python subprocesses (Vercel kills after 300s)
  - **Solution:** Split pipeline into 5 separate API calls, or use Vercel Cron + Queue

---

## Alternative: Long-Running Pipeline Solution

If Vercel kills your subprocess after 300s:

### Option A: Client-Side Stage Triggering
```typescript
// Frontend triggers each stage sequentially

async function runPipeline(fileUrl: string, brandId: string) {
  const runId = crypto.randomUUID()

  for (let stage = 1; stage <= 5; stage++) {
    await fetch('/api/run-stage', {
      method: 'POST',
      body: JSON.stringify({ runId, stage, fileUrl, brandId })
    })

    // Wait for stage completion (max 300s per stage is fine)
    await pollStageCompletion(runId, stage)
  }
}
```

### Option B: Vercel Cron + Queue
```typescript
// POST /api/run → Creates job in DB → Returns immediately
// Vercel Cron (every 1 min) → Checks for pending jobs → Runs 1 stage
// Repeat until all 5 stages complete
```

**Effort:** +2-3 hours

---

## Final Recommendation

### For 1-Day Hackathon: Build "Minimal Viable Web Wrapper"

**DO:**
- ✅ Use Next.js for UI
- ✅ Use API routes to spawn Python subprocess
- ✅ Keep pipeline logic 100% unchanged
- ✅ Save files to local disk (or Vercel Blob if needed)
- ✅ Poll log files for progress
- ✅ Display results from markdown files

**DON'T:**
- ❌ Rebuild pipeline as serverless functions
- ❌ Implement Postgres database
- ❌ Build Monaco prompt editor
- ❌ Add model selection UI
- ❌ Implement cost estimation
- ❌ Add WebSocket real-time updates

### What You'll Demo
1. **Drag & drop PDF** (innovation trend report)
2. **Select brand** (Lactalis, McCormick, etc.)
3. **Click "Generate"** (spawns pipeline)
4. **Watch progress bar** (polling logs every 5s)
5. **View 5 opportunity cards** (markdown rendered as HTML)

**Demo Time:** 2-3 minutes
**Implementation Time:** 8 hours
**Polish Time:** 30 minutes
**Buffer:** 30 minutes for deployment debugging

---

## Next Steps

1. **Validate Approach** - Does this simplified architecture meet your demo needs?
2. **Prioritize Features** - Which UI elements are must-haves vs. nice-to-haves?
3. **Decide on Blob** - Use local `/tmp` or Vercel Blob for file storage?
4. **Plan Deployment** - Test Vercel timeout behavior with a dummy long-running process

**Ready to proceed?** Let me know and I'll help you scaffold the Next.js app with the exact structure needed.
