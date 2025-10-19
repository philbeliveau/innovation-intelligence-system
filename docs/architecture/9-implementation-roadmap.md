# 9. Implementation Roadmap

## ⚠️ CRITICAL PRE-IMPLEMENTATION CHECK

**Before starting implementation, MUST validate Python execution on Vercel:**

```typescript
// Create test-python/api/test/route.ts
import { exec } from 'child_process'
import { NextResponse } from 'next/server'

export async function GET() {
  return new Promise((resolve) => {
    exec('python --version', (error, stdout, stderr) => {
      resolve(NextResponse.json({
        pythonAvailable: !error,
        version: stdout || 'Not available',
        error: error?.message || null
      }))
    })
  })
}
```

**Deploy this test to Vercel FIRST:**
1. Create minimal Next.js project with above route
2. Deploy to Vercel: `vercel --prod`
3. Visit `/api/test` endpoint
4. **If Python unavailable:** Use contingency plan (separate Python server or containerized deployment)

**Contingency Options if Python Not Available:**
- **Option A:** Deploy Python pipeline to Render.com, trigger via webhook from Next.js
- **Option B:** Use Railway or Fly.io with Docker (containerize entire stack)
- **Option C:** Use Replit or PythonAnywhere with Python support

---

## Hour 0-1: Project Setup
- [ ] Create Next.js 15 app: `npx create-next-app@latest innovation-web --app --tailwind`
- [ ] Install dependencies:
  ```bash
  npm install @vercel/blob react-dropzone react-markdown yaml pdf-parse
  npm install -D @types/node
  ```
- [ ] Install shadcn/ui:
  ```bash
  npx shadcn-ui@latest init
  npx shadcn-ui@latest add card button select badge skeleton separator
  ```
- [ ] Symlink brand profiles: `ln -s ../data ./data`

## Hour 1-2: Onboarding Page
- [ ] Create `app/onboarding/page.tsx`
- [ ] Company selector dropdown (4 options: Lactalis, McCormick, Columbia, Decathlon)
- [ ] POST to `/api/onboarding/set-company` on selection
- [ ] Redirect to homepage with company context
- [ ] Create `app/api/onboarding/set-company/route.ts` (loads YAML, sets cookie)
- [ ] Create `app/api/onboarding/current-company/route.ts` (reads cookie)

**Use MCP Tool:**
```typescript
// Use mcp__magic__21st_magic_component_builder
// Prompt: "Create an onboarding page with centered card,
// 'Select Your Company' heading, dropdown with 4 company options,
// and Continue button that redirects on selection"
```

## Hour 2-3: Homepage UI
- [ ] Create `app/page.tsx` matching reference design
- [ ] Display company name from cookie (top-right corner)
- [ ] Implement drag & drop with react-dropzone
- [ ] **NO brand selector** (already set in onboarding)
- [ ] Upload to Vercel Blob on drop
- [ ] Show file upload status
- [ ] After upload → redirect to `/analyze/[uploadId]`
- [ ] Redirect to `/onboarding` if no company cookie found

## Hour 3-4: Intermediary Card Page
- [ ] Create `app/analyze/[uploadId]/page.tsx`
- [ ] Call `/api/analyze-document` on page load
- [ ] Show loading state during analysis
- [ ] Display card matching `docs/image/intermediary-card.png`:
  - [ ] Hero image placeholder
  - [ ] Title from LLM analysis
  - [ ] Source badges
  - [ ] Industry badge (orange)
  - [ ] Theme badge (red)
  - [ ] Summary text
- [ ] "Launch" button → POST /api/run → redirect to `/pipeline/[runId]`

**Use MCP Tool:**
```typescript
// Use mcp__magic__21st_magic_component_builder
// Prompt: "Create a file upload dropzone component with drag and drop,
// styled like the reference image with a centered upload icon,
// 'Drag & drop or choose file' text, and supported file types list"
```

## Hour 4-5: API Routes
- [ ] Create `app/api/upload/route.ts` (Vercel Blob integration)
- [ ] Create `app/api/analyze-document/route.ts` (LLM extraction)
- [ ] Create `app/api/run/route.ts` (spawn Python subprocess, read brand from cookie)
- [ ] Create `app/api/status/[runId]/route.ts` (log parsing)
- [ ] Create `app/api/results/[runId]/route.ts` (read markdown files)

## Hour 5-6: Pipeline Modifications
- [ ] Add `--input-file` and `--run-id` CLI args to `run_pipeline.py`
- [ ] Add JSON output to Stage 1 for 2-track UI
- [ ] Test local execution with sample PDF

## Hour 6-8: Pipeline Viewer UI
- [ ] Create `app/pipeline/[runId]/page.tsx`
- [ ] Implement Stage 1 two-track visualization
- [ ] Add polling logic with timeout protection:
  ```typescript
  'use client'
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const startTime = Date.now()
    const MAX_RUNTIME = 35 * 60 * 1000 // 35 minutes

    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/status/${runId}`)
        const data = await response.json()
        setStatus(data)

        // Frontend timeout check
        const elapsed = Date.now() - startTime
        if (elapsed > MAX_RUNTIME && data.status === 'running') {
          setError('Pipeline timeout')
          return
        }

        // Backend error check
        if (data.status === 'error') {
          setError(data.error || 'Pipeline failed')
          return
        }

        // Continue polling if not complete
        if (data.status !== 'complete') {
          setTimeout(pollStatus, 5000)
        }
      } catch (e) {
        setError('Failed to fetch status')
      }
    }

    pollStatus()
  }, [runId])
  ```
- [ ] Implement Stages 2-5 minimal box UI
- [ ] Add status icons (pending/running/complete)
- [ ] Handle stage transitions

**Use MCP Tool:**
```typescript
// Use mcp__magic__21st_magic_component_builder
// Prompt: "Create two side-by-side cards for displaying inspiration tracks,
// each with a title, content area, bullet points, and loading skeleton state"
```

## Hour 8-9: Results Page
- [ ] Create `app/results/[runId]/page.tsx`
- [ ] Fetch opportunities from `/api/results/:runId`
- [ ] Render markdown cards with react-markdown (**with XSS protection**)
  ```typescript
  <ReactMarkdown
    disallowedElements={['script', 'iframe', 'object', 'embed']}
    unwrapDisallowed={true}
  >
    {markdown}
  </ReactMarkdown>
  ```
- [ ] Add "Download All" button (PDF export)
- [ ] Add "New Pipeline" button (redirect to homepage)

## Hour 9-10: Left Sidebar & Polish
- [ ] Create collapsible left sidebar component
- [ ] Hover-trigger at left edge
- [ ] Display "Home" button
- [ ] Click → navigate to `/` (homepage)
- [ ] Add basic error boundaries (optional but recommended):
  ```typescript
  // app/error.tsx
  'use client'

  export default function Error({
    error,
    reset,
  }: {
    error: Error & { digest?: string }
    reset: () => void
  }) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center">
        <h2 className="text-2xl font-bold mb-4">Something went wrong!</h2>
        <p className="text-gray-600 mb-4">{error.message}</p>
        <button
          onClick={() => reset()}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          Try again
        </button>
      </div>
    )
  }
  ```
- [ ] Final UI polish and testing

## Hour 10-11: Testing & Deployment
- [ ] Test full flow: upload → run → view results
- [ ] Deploy to Vercel: `vercel --prod`
- [ ] Set environment variables in Vercel dashboard
- [ ] Test deployed app with real PDF

---
