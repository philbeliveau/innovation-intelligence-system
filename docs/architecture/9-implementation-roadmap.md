# 9. Implementation Roadmap

## ⚠️ CRITICAL PRE-IMPLEMENTATION REQUIREMENTS

**READ FIRST:** Before starting Hour 1, complete these prerequisite tasks:

1. **Review Integration Test Plan** (Architecture Section 13)
   - Understand regression test requirements
   - Prepare test fixtures for baseline validation

2. **Review Database Migration Strategy** (Architecture Section 14)
   - Understand dual-write approach (database + file fallback)
   - Review rollback procedures

3. **Review Rollback Strategy** (Architecture Section 15)
   - Understand feature flag system
   - Know how to revert to file-based mode

4. **Set up development environment:**
   - Local PostgreSQL running OR Railway PostgreSQL connection string
   - Python 3.11 environment with pipeline dependencies
   - Node.js 20+ with Next.js dependencies

---

## Hour -2 to 0: Pre-Implementation Setup (MUST COMPLETE BEFORE HOUR 1)

### Hour -2: Railway PostgreSQL Deployment

**🔴 BLOCKER:** Database must exist before any frontend API routes work.

```bash
# 1. Create Railway project
railway login
railway init
railway link

# 2. Add PostgreSQL database
railway add --database postgres

# 3. Get DATABASE_URL
railway variables
# Copy DATABASE_URL value

# 4. Set local environment variable
echo "DATABASE_URL=<railway-postgres-url>" >> .env

# 5. Verify connection
psql $DATABASE_URL -c "SELECT 1"
# Expected: (1 row)
```

**✅ Validation:** Database accessible from local machine

---

### Hour -1: Prisma Schema Deployment

**🔴 BLOCKER:** Schema must be deployed before API routes can query database.

```bash
# 1. Install Prisma CLI
npm install -D prisma @prisma/client

# 2. Generate Prisma Client
npx prisma generate

# 3. Deploy migrations to Railway PostgreSQL
npx prisma migrate deploy

# 4. Verify schema
npx prisma studio
# Opens browser → Check tables: User, Run, OpportunityCard, etc.

# 5. Create test user (optional)
npx prisma db seed
```

**File:** `.env` (required)

```bash
DATABASE_URL="postgresql://user:pass@railway.app:5432/railway?pgbouncer=true&connection_limit=1"
DATABASE_URL_NON_POOLING="postgresql://user:pass@railway.app:5432/railway"  # For migrations
OPENROUTER_API_KEY="sk-or-v1-xxxxx"
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
ENABLE_DATABASE_WRITES=true
ENABLE_FILE_FALLBACK=true  # Dual-write mode for safety
```

**✅ Validation:**
- Prisma Studio shows all 5 tables
- `npx prisma db pull` shows no drift

---

### Hour 0: Integration Test Baseline

**🔴 BLOCKER:** Must capture baseline pipeline outputs before modifications.

```bash
# 1. Run existing pipeline (file-based) to create baseline
python scripts/run_pipeline.py \
  --input-file tests/fixtures/sample-report.pdf \
  --brand lactalis-canada \
  --run-id baseline-test-001

# 2. Copy outputs to expected-outputs directory
mkdir -p tests/fixtures/expected-outputs/
cp -r data/test-outputs/baseline-test-001/ tests/fixtures/expected-outputs/

# 3. Verify baseline
ls tests/fixtures/expected-outputs/baseline-test-001/stage5/
# Should see: opportunity-1.md through opportunity-5.md

# 4. Run initial regression test
pytest tests/test_pipeline_stages.py::TestStage1Regression::test_stage1_output_structure

# Expected: PASS (baseline captured)
```

**✅ Validation:**
- Existing pipeline runs successfully
- Baseline outputs saved in `tests/fixtures/expected-outputs/`
- At least 1 regression test passes

---

## Hour 1-2: Next.js Project Setup + Clerk Auth
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
