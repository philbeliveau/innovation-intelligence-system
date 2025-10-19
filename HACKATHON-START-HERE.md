# 🚀 Hackathon Implementation Guide - START HERE

**Goal:** Build a working web app in 1 day that runs your existing pipeline with a beautiful UI

**Architecture:** `/docs/architecture-hackathon-web-app.md`

---

## Quick Start Checklist

### ✅ Phase 1: Setup (30 minutes)

```bash
# 1. Create Next.js app
npx create-next-app@latest innovation-web --typescript --tailwind --app --no-src-dir
cd innovation-web

# 2. Install dependencies
npm install @vercel/blob react-dropzone react-markdown
npm install -D @types/node

# 3. Install shadcn/ui
npx shadcn-ui@latest init
# Select: TypeScript, Tailwind, App Router, @/ alias

# 4. Add shadcn components
npx shadcn-ui@latest add card button select badge skeleton separator

# 5. Link to existing pipeline
ln -s ../pipeline ./pipeline
ln -s ../data ./data
ln -s ../scripts ./scripts
```

### ✅ Phase 2: Homepage (2 hours)

**Reference Design:** `docs/image/main-page.png`

**File:** `app/page.tsx`

**Use Claude Code MCP Tool:**
```typescript
// In Claude Code, run:
/ui Create a homepage matching this design:
- Title "My Board of Ideators" centered
- Large upload card with drag & drop zone
- Upload icon, "Drag & drop or choose file to upload" text
- Supported file types: PDF, txt, Markdown, Audio
- Brand selector dropdown (after upload)
- "Generate Opportunities" button
```

**Manual API Integration:**
```typescript
'use client'
import { useState } from 'react'
import { put } from '@vercel/blob'

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [blobUrl, setBlobUrl] = useState<string>('')
  const [brand, setBrand] = useState<string>('')

  const handleUpload = async (file: File) => {
    const blob = await put(`uploads/${Date.now()}-${file.name}`, file, {
      access: 'public',
    })
    setBlobUrl(blob.url)
    setFile(file)
  }

  const handleRun = async () => {
    const response = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ blob_url: blobUrl, brand_id: brand })
    })
    const { run_id } = await response.json()
    window.location.href = `/pipeline/${run_id}`
  }

  return (
    // ... UI components
  )
}
```

### ✅ Phase 3: API Routes (1.5 hours)

**File:** `app/api/upload/route.ts`
```typescript
import { put } from '@vercel/blob'
import { NextResponse } from 'next/server'

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

**File:** `app/api/run/route.ts`
```typescript
import { exec } from 'child_process'
import { NextResponse } from 'next/server'
import { writeFile } from 'fs/promises'

export async function POST(request: Request) {
  const { blob_url, brand_id } = await request.json()
  const run_id = `run-${Date.now()}`

  // Download PDF from Blob
  const response = await fetch(blob_url)
  const buffer = await response.arrayBuffer()
  const tmpPath = `/tmp/${run_id}.pdf`
  await writeFile(tmpPath, Buffer.from(buffer))

  // Execute pipeline (don't await - runs in background)
  exec(
    `python scripts/run_pipeline.py --input-file ${tmpPath} --brand ${brand_id} --run-id ${run_id}`,
    { cwd: process.cwd() }
  )

  return NextResponse.json({ run_id, status: 'running' })
}
```

**File:** `app/api/status/[runId]/route.ts`
```typescript
import { readFile } from 'fs/promises'
import { NextResponse } from 'next/server'

export async function GET(
  request: Request,
  { params }: { params: { runId: string } }
) {
  const runId = params.runId
  const logPath = `data/test-outputs/${runId}/logs/pipeline.log`

  try {
    const logContent = await readFile(logPath, 'utf-8')
    const currentStage = detectStageFromLog(logContent)

    // If Stage 1 complete, read inspirations.json
    let stage1Data = null
    if (currentStage >= 1) {
      const jsonPath = `data/test-outputs/${runId}/stage1/inspirations.json`
      const jsonContent = await readFile(jsonPath, 'utf-8')
      stage1Data = JSON.parse(jsonContent)
    }

    return NextResponse.json({
      run_id: runId,
      status: currentStage === 5 ? 'complete' : 'running',
      current_stage: currentStage,
      stage1_data: stage1Data,
    })
  } catch (error) {
    return NextResponse.json({ run_id: runId, status: 'error' }, { status: 404 })
  }
}

function detectStageFromLog(logContent: string): number {
  if (logContent.includes('Stage 5 execution completed')) return 5
  if (logContent.includes('Starting Stage 5')) return 5
  if (logContent.includes('Stage 4 execution completed')) return 4
  if (logContent.includes('Starting Stage 4')) return 4
  if (logContent.includes('Stage 3 execution completed')) return 3
  if (logContent.includes('Starting Stage 3')) return 3
  if (logContent.includes('Stage 2 execution completed')) return 2
  if (logContent.includes('Starting Stage 2')) return 2
  if (logContent.includes('Stage 1 execution completed')) return 1
  if (logContent.includes('Starting Stage 1')) return 1
  return 0
}
```

### ✅ Phase 4: Pipeline Modifications (1 hour)

**File:** `scripts/run_pipeline.py` (add at top of `main()` function)

```python
# Add new CLI arguments
parser.add_argument('--input-file', type=str, help='Direct PDF file path')
parser.add_argument('--run-id', type=str, help='Unique run identifier')

# Add new execution mode
if args.input_file and args.brand and args.run_id:
    run_from_uploaded_file(args.input_file, args.brand, args.run_id)
    sys.exit(0)

# New function
def run_from_uploaded_file(input_file_path: str, brand_id: str, run_id: str):
    """Execute pipeline from uploaded file."""

    # Create output directory with run_id
    output_dir = Path(f"data/test-outputs/{run_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup logging
    setup_pipeline_logging(output_dir)

    # Read PDF
    from pypdf import PdfReader
    reader = PdfReader(input_file_path)
    input_text = "".join(page.extract_text() for page in reader.pages)

    # Load brand data
    brand_profile = load_brand_profile(brand_id)
    research_data = load_research_data(brand_id)

    # Run pipeline (UNCHANGED)
    # ... existing stage execution code
```

**File:** `pipeline/stages/stage1_input_processing.py` (modify `save_output()`)

```python
import json
from datetime import datetime

def save_output(self, output: str, output_dir: Path) -> Path:
    """Save Stage 1 output with JSON for API."""

    stage1_dir = output_dir / "stage1"
    stage1_dir.mkdir(parents=True, exist_ok=True)

    # Save markdown (existing)
    markdown_path = stage1_dir / "inspiration-analysis.md"
    markdown_path.write_text(output, encoding='utf-8')

    # Parse inspirations (simple regex or LLM parsing)
    inspirations = self._parse_inspirations(output)

    # Save JSON for API
    json_path = stage1_dir / "inspirations.json"
    json_data = {
        "inspiration_1": inspirations[0],
        "inspiration_2": inspirations[1],
        "completed_at": datetime.now().isoformat()
    }
    json_path.write_text(json.dumps(json_data, indent=2), encoding='utf-8')

    return markdown_path

def _parse_inspirations(self, output: str) -> list:
    """Extract 2 inspirations from LLM output."""
    # TODO: Implement parsing logic
    # For now, return mock data
    return [
        {
            "title": "Inspiration Track 1",
            "content": "Content extracted from output...",
            "key_elements": ["Element 1", "Element 2"]
        },
        {
            "title": "Inspiration Track 2",
            "content": "Content extracted from output...",
            "key_elements": ["Element 1", "Element 2"]
        }
    ]
```

### ✅ Phase 5: Pipeline Viewer UI (2.5 hours)

**File:** `app/pipeline/[runId]/page.tsx`

```typescript
'use client'
import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export default function PipelineViewer({ params }: { params: { runId: string } }) {
  const [status, setStatus] = useState<any>(null)

  useEffect(() => {
    const pollStatus = async () => {
      const response = await fetch(`/api/status/${params.runId}`)
      const data = await response.json()
      setStatus(data)

      // Continue polling if not complete
      if (data.status !== 'complete') {
        setTimeout(pollStatus, 5000) // Poll every 5 seconds
      }
    }

    pollStatus()
  }, [params.runId])

  if (!status) return <div>Loading...</div>

  return (
    <div className="max-w-6xl mx-auto p-8 space-y-6">
      {/* Stage 1: Two-Track UI */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Stage 1: Extracting Key Inspirations</h2>
        <div className="grid grid-cols-2 gap-6">
          <InspirationTrack
            data={status.stage1_data?.inspiration_1}
            loading={!status.stage1_data}
          />
          <InspirationTrack
            data={status.stage1_data?.inspiration_2}
            loading={!status.stage1_data}
          />
        </div>
      </div>

      {/* Stages 2-5: Minimal Boxes */}
      <StageBox stage={2} title="Signal Amplification" currentStage={status.current_stage} />
      <StageBox stage={3} title="Universal Translation" currentStage={status.current_stage} />
      <StageBox stage={4} title="Brand Contextualization" currentStage={status.current_stage} />
      <StageBox stage={5} title="Opportunity Generation" currentStage={status.current_stage} />

      {/* Results */}
      {status.current_stage === 5 && (
        <div className="mt-8">
          <a href={`/results/${params.runId}`} className="btn btn-primary">
            View Opportunities →
          </a>
        </div>
      )}
    </div>
  )
}

function InspirationTrack({ data, loading }: any) {
  if (loading) {
    return (
      <Card className="p-6">
        <Skeleton className="h-6 w-48 mb-4" />
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-4 w-3/4" />
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <h3 className="text-xl font-semibold mb-3">🎯 {data.title}</h3>
      <p className="text-sm text-gray-700 mb-4">{data.content}</p>
      <ul className="list-disc list-inside space-y-1">
        {data.key_elements.map((el: string, i: number) => (
          <li key={i} className="text-sm">{el}</li>
        ))}
      </ul>
    </Card>
  )
}

function StageBox({ stage, title, currentStage }: any) {
  const status = currentStage === stage ? 'running' : currentStage > stage ? 'complete' : 'pending'

  return (
    <Card className={`p-6 ${status === 'complete' ? 'bg-green-50' : ''}`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Stage {stage}: {title}</h3>
          <p className="text-sm text-gray-600">
            {stage === 2 && 'Extracting broader trends from inspiration patterns'}
            {stage === 3 && 'Converting insights into brand-agnostic lessons'}
            {stage === 4 && 'Applying lessons to target brand'}
            {stage === 5 && 'Creating 5 actionable innovation opportunities'}
          </p>
        </div>
        <div className="text-2xl">
          {status === 'pending' && '⌛'}
          {status === 'running' && '⏳'}
          {status === 'complete' && '✓'}
        </div>
      </div>
    </Card>
  )
}
```

### ✅ Phase 6: Results Page (1 hour)

**File:** `app/results/[runId]/page.tsx`

```typescript
import { readFile } from 'fs/promises'
import ReactMarkdown from 'react-markdown'
import { Card } from '@/components/ui/card'

export default async function Results({ params }: { params: { runId: string } }) {
  const outputDir = `data/test-outputs/${params.runId}/stage5`

  const opportunities = await Promise.all(
    [1, 2, 3, 4, 5].map(async (num) => {
      const markdown = await readFile(`${outputDir}/opportunity-${num}.md`, 'utf-8')
      return { number: num, markdown }
    })
  )

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">
        ✓ Pipeline Complete - 5 Opportunities Generated
      </h1>

      <div className="space-y-6">
        {opportunities.map(({ number, markdown }) => (
          <Card key={number} className="p-6">
            <ReactMarkdown>{markdown}</ReactMarkdown>
          </Card>
        ))}
      </div>

      <div className="mt-8 flex gap-4">
        <a href="/" className="btn btn-primary">New Pipeline</a>
        <button className="btn btn-secondary">Download All as PDF</button>
      </div>
    </div>
  )
}
```

### ✅ Phase 7: Deploy to Vercel (30 minutes)

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Login
vercel login

# 3. Deploy
vercel --prod

# 4. Set environment variables in Vercel dashboard
# - OPENROUTER_API_KEY
# - OPENROUTER_BASE_URL
# - LLM_MODEL
# - BLOB_READ_WRITE_TOKEN (auto-generated)

# 5. Test live app
```

---

## 🎨 Use shadcn/ui MCP for Components

Instead of writing components manually, use Claude Code's MCP tool:

```typescript
// In Claude Code, type:
/ui Create a drag and drop file upload zone with centered upload icon,
"Drag & drop or choose file" text, supported file types list,
and hover state animation. Use shadcn/ui card component.

// This generates the component code automatically
```

---

## Troubleshooting

### Python subprocess not executing
- Check `process.cwd()` is correct
- Use absolute path: `exec(\`cd ${process.cwd()} && python ...\`)`
- Add logging: `console.log('Executing:', command)`

### Vercel Blob upload fails
- Check `BLOB_READ_WRITE_TOKEN` is set
- Use `put()` not `upload()` (deprecated)

### Stage 1 JSON not found
- Check `stage1_input_processing.py` saves JSON file
- Verify path: `data/test-outputs/${runId}/stage1/inspirations.json`

### Pipeline timeout on Vercel
- Don't `await` the Python subprocess
- Use `exec()` not `execSync()`
- Let it run in background

---

## Success Criteria

**Demo Flow:**
1. Upload `savannah-bananas.pdf`
2. Select "Lactalis Canada"
3. Click "Generate Opportunities"
4. Watch Stage 1 display 2 inspiration tracks
5. Watch Stages 2-5 update status in real-time
6. View 5 opportunity cards on results page

**Total Demo Time:** ~3 minutes (15-30 min pipeline execution)

---

## Next Steps

1. Start with **Phase 1: Setup** (30 min)
2. Build **Homepage** using shadcn/ui MCP (2 hours)
3. Add **API Routes** for upload/run/status (1.5 hours)
4. Modify **Python pipeline** to accept file paths (1 hour)
5. Build **Pipeline Viewer UI** with 2-track Stage 1 (2.5 hours)
6. Create **Results Page** (1 hour)
7. **Deploy to Vercel** and test (30 min)

**Total: 8-9 hours** ✅

---

**Ready to start?** Begin with Phase 1 setup, then use shadcn/ui MCP to generate UI components quickly!
