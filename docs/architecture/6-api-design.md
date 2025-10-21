# 6. API Design

## 6.1 Endpoints

### `POST /api/onboarding/set-company`
**Purpose:** Set company context for session (team-led onboarding)

**Request:**
```json
{
  "company_id": "lactalis-canada"
}
```

**Response:**
```json
{
  "success": true,
  "company_id": "lactalis-canada",
  "company_name": "Lactalis Canada",
  "brand_profile": {
    "brand_name": "Lactalis Canada",
    "country": "Canada",
    "industry": "Dairy / Food & Beverage",
    "positioning": "Canada's premier dairy company...",
    "product_portfolio": [...],
    "target_customers": [...],
    "strategic_priorities": [...]
  }
}
```

**Implementation:**
```typescript
// app/api/onboarding/set-company/route.ts
import { readFile } from 'fs/promises'
import { parse } from 'yaml'
import { cookies } from 'next/headers'

export async function POST(request: Request) {
  const { company_id } = await request.json()

  // Load brand profile from YAML
  const profilePath = `data/brand-profiles/${company_id}.yaml`
  const yamlContent = await readFile(profilePath, 'utf-8')
  const brandProfile = parse(yamlContent)

  // Save to cookie (expires in 7 days)
  cookies().set('company_id', company_id, {
    maxAge: 60 * 60 * 24 * 7,
    httpOnly: true,
    sameSite: 'lax'
  })

  return NextResponse.json({
    success: true,
    company_id,
    company_name: brandProfile.brand_name,
    brand_profile: brandProfile
  })
}
```

**Cookie Storage:**
- `company_id` cookie persists for 7 days
- Available to all pages via `cookies().get('company_id')`
- Client-side accessible for display (company name in top-right)

---

### `GET /api/onboarding/current-company`
**Purpose:** Get currently selected company from session

**Response:**
```json
{
  "company_id": "lactalis-canada",
  "company_name": "Lactalis Canada"
}
```

**Implementation:**
```typescript
// app/api/onboarding/current-company/route.ts
export async function GET() {
  const companyId = cookies().get('company_id')?.value

  if (!companyId) {
    return NextResponse.json({ error: 'No company selected' }, { status: 404 })
  }

  // Load brand name from YAML
  const profilePath = `data/brand-profiles/${companyId}.yaml`
  const yamlContent = await readFile(profilePath, 'utf-8')
  const brandProfile = parse(yamlContent)

  return NextResponse.json({
    company_id: companyId,
    company_name: brandProfile.brand_name
  })
}
```

---

### `POST /api/analyze-document`
**Purpose:** Use LLM to extract summary and metadata from uploaded document

**Request:**
```json
{
  "blob_url": "https://blob.vercel-storage.com/uploads/abc123.pdf"
}
```

**Response:**
```json
{
  "upload_id": "upload-20250115-142030",
  "analysis": {
    "title": "Ad-generating QR codes incorporated into garments to make resale easy",
    "summary": "Most people only wear a fraction of the clothes they own. To keep their products in use, the Danish fashion brand Samsøe Samsøe is adding smart labels that simplify future resales. Sewn into garments...",
    "industry": "fashion",
    "theme": "marketing strategies",
    "sources": ["trendwatching.com", "8 others"]
  },
  "blob_url": "https://blob.vercel-storage.com/uploads/abc123.pdf",
  "analyzed_at": "2025-01-15T14:20:35Z"
}
```

**Implementation:**
```typescript
// app/api/analyze-document/route.ts
import { NextResponse } from 'next/server'
import { ChatOpenAI } from '@langchain/openai'
import { readFile } from 'fs/promises'
import { writeFile } from 'fs/promises'

export async function POST(request: Request) {
  const { blob_url } = await request.json()
  const upload_id = `upload-${Date.now()}`

  // Download PDF from Blob
  const response = await fetch(blob_url)
  const buffer = await response.arrayBuffer()
  const tmpPath = `/tmp/${upload_id}.pdf`
  await writeFile(tmpPath, Buffer.from(buffer))

  // Extract text from PDF
  const { PdfReader } = await import('pypdf')
  const reader = new PdfReader(tmpPath)
  const pages = await reader.getPages()
  const fullText = pages.map(p => p.extractText()).join('\n')

  // Use LLM to analyze document
  const llm = new ChatOpenAI({
    modelName: process.env.LLM_MODEL || 'anthropic/claude-sonnet-4.5',
    openAIApiKey: process.env.OPENROUTER_API_KEY,
    configuration: {
      baseURL: process.env.OPENROUTER_BASE_URL
    }
  })

  const analysisPrompt = `Analyze this document and extract:

1. A compelling title (10-15 words) that captures the main innovation or trend
2. A concise summary (2-3 sentences, ~50 words) explaining what the document is about
3. The primary industry (single word: fashion, food, technology, healthcare, etc.)
4. The main theme or topic (2-3 words: e.g. "marketing strategies", "sustainability", "customer experience")
5. Any identifiable sources mentioned in the document

Document text:
${fullText.slice(0, 4000)}

Respond in JSON format:
{
  "title": "...",
  "summary": "...",
  "industry": "...",
  "theme": "...",
  "sources": ["source1", "source2"]
}
`

  const result = await llm.invoke(analysisPrompt)
  const analysis = JSON.parse(result.content)

  return NextResponse.json({
    upload_id,
    analysis,
    blob_url,
    analyzed_at: new Date().toISOString()
  })
}
```

---

### `POST /api/upload`
**Purpose:** Upload PDF to Vercel Blob storage

**Request:**
```typescript
Content-Type: multipart/form-data

{
  file: File (PDF)
}
```

**Response:**
```json
{
  "blob_url": "https://blob.vercel-storage.com/uploads/abc123.pdf",
  "file_name": "sustainable-packaging-2025.pdf",
  "file_size": 2457600
}
```

**Implementation:**
```typescript
// app/api/upload/route.ts
import { put } from '@vercel/blob'

export async function POST(request: Request) {
  const formData = await request.formData()
  const file = formData.get('file') as File

  const blob = await put(`uploads/${Date.now()}-${file.name}`, file, {
    access: 'public',
  })

  return NextResponse.json({
    blob_url: blob.url,
    file_name: file.name,
    file_size: file.size,
  })
}
```

---

### `POST /api/run`
**Purpose:** Proxy pipeline execution request to Railway backend

**Request:**
```json
{
  "blob_url": "https://blob.vercel-storage.com/uploads/abc123.pdf"
}
```

**Note:** `brand_id` is read from cookie (set during onboarding), not passed in request

**Response:**
```json
{
  "run_id": "run-7f3e4a2b-9c1d-4e8f-b5a6-3d2c1e0f9a8b",
  "status": "running",
  "brand_id": "lactalis-canada",
  "created_at": "2025-01-15T14:20:30Z"
}
```

**Implementation (Railway Backend Integration - Story 5.3):**
```typescript
// app/api/run/route.ts
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'
import { runPipeline } from '@/lib/backend-client'

export async function POST(request: Request) {
  const { blob_url } = await request.json()

  // Get brand from cookie (set during onboarding)
  const brand_id = cookies().get('company_id')?.value

  if (!brand_id) {
    return NextResponse.json(
      { error: 'No company selected. Please complete onboarding.' },
      { status: 400 }
    )
  }

  try {
    // Call Railway backend to execute pipeline
    const result = await runPipeline(blob_url, brand_id)

    return NextResponse.json({
      run_id: result.run_id,
      status: result.status,
      brand_id,
      created_at: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Pipeline execution error:', error)
    return NextResponse.json(
      { error: 'Failed to start pipeline execution' },
      { status: 500 }
    )
  }
}
```

**Railway Backend Endpoint (`POST /run`):**
```python
# backend/app/routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid

router = APIRouter()

class RunRequest(BaseModel):
    blob_url: str
    brand_id: str

@router.post("/run")
async def run_pipeline(request: RunRequest):
    run_id = f"run-{uuid.uuid4()}"

    # Download PDF from Vercel Blob
    # Execute pipeline stages 1-5
    # Write outputs to /tmp/{run_id}/

    return {
        "run_id": run_id,
        "status": "running"
    }
```

---

### `GET /api/status/:runId`
**Purpose:** Proxy pipeline status request to Railway backend

**Response:**
```json
{
  "run_id": "run-20250115-142030",
  "status": "running",
  "current_stage": 2,
  "stages": {
    "1": {
      "status": "complete",
      "output": {
        "inspiration_1_title": "Experience Theater",
        "inspiration_1_content": "The Savannah Bananas have...",
        "inspiration_2_title": "Community Building",
        "inspiration_2_content": "Creating a sense of belonging..."
      },
      "completed_at": "2025-01-15T14:24:15Z"
    },
    "2": {
      "status": "running",
      "started_at": "2025-01-15T14:24:16Z"
    },
    "3": { "status": "pending" },
    "4": { "status": "pending" },
    "5": { "status": "pending" }
  }
}
```

**Implementation (Railway Backend Integration - Story 5.3):**
```typescript
// app/api/status/[runId]/route.ts
import { NextResponse } from 'next/server'
import { getStatus } from '@/lib/backend-client'

export async function GET(
  request: Request,
  { params }: { params: { runId: string } }
) {
  const runId = params.runId

  try {
    // Call Railway backend for status
    const status = await getStatus(runId)

    return NextResponse.json(status)
  } catch (error) {
    console.error('Status fetch error:', error)
    return NextResponse.json(
      {
        run_id: runId,
        status: 'error',
        error: 'Run not found or backend unavailable'
      },
      { status: 404 }
    )
  }
}
```

**Railway Backend Endpoint (`GET /status/{run_id}`):**
```python
# backend/app/routes.py
@router.get("/status/{run_id}")
async def get_status(run_id: str):
    log_path = f"/tmp/{run_id}/pipeline.log"

    try:
        # Read log file and detect current stage
        with open(log_path, 'r') as f:
            log_content = f.read()

        current_stage = detect_stage_from_log(log_content)
        stages = parse_stage_outputs(run_id)

        return {
            "run_id": run_id,
            "status": "complete" if current_stage == 5 else "running",
            "current_stage": current_stage,
            "stages": stages
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Run not found")
```

---

### `GET /api/results/:runId`
**Purpose:** Get final opportunity cards

**Response:**
```json
{
  "run_id": "run-20250115-142030",
  "opportunities": [
    {
      "number": 1,
      "title": "Plant-Based Dairy Theater",
      "strategic_rationale": "...",
      "implementation_approach": "...",
      "success_metrics": "...",
      "timeline": "6-12 months",
      "investment": "$500K-$1M",
      "markdown_content": "# Opportunity #1\n\n..."
    },
    // ... 4 more
  ],
  "completed_at": "2025-01-15T14:45:30Z"
}
```

---
