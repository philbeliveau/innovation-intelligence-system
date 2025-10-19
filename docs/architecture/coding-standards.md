# 11. Coding Standards

## Overview

This document defines the coding standards and conventions for the Innovation Intelligence System web application. All developers MUST follow these standards to ensure consistency, maintainability, and code quality.

---

## TypeScript & React Standards

### Component Architecture

**React Server Components (RSC) vs Client Components:**

```typescript
// ✅ CORRECT: Server Component (default in Next.js 15 App Router)
// app/components/OpportunityCard.tsx
export default function OpportunityCard({ opportunity }: { opportunity: Opportunity }) {
  return <div>{opportunity.title}</div>
}

// ✅ CORRECT: Client Component (interactive, uses hooks)
// app/components/FileUploadZone.tsx
'use client'

import { useState } from 'react'

export default function FileUploadZone() {
  const [file, setFile] = useState<File | null>(null)
  // ... interactive logic
}
```

**Rules:**
- Default to Server Components unless you need interactivity
- Use `'use client'` directive ONLY when needed (hooks, event handlers, browser APIs)
- Client components should be leaf components where possible
- Never fetch data in client components - pass props from server components

### File Naming Conventions

**Components:**
```
✅ CORRECT:
components/FileUploadZone.tsx      # PascalCase for React components
components/ui/button.tsx           # lowercase for shadcn/ui primitives

❌ INCORRECT:
components/file-upload-zone.tsx   # kebab-case
components/FileUploadZone.jsx     # Use .tsx, not .jsx
```

**Pages & Routes:**
```
✅ CORRECT:
app/page.tsx                       # lowercase for route files
app/analyze/[uploadId]/page.tsx   # Dynamic routes in brackets
app/api/upload/route.ts           # API routes use route.ts

❌ INCORRECT:
app/Page.tsx                       # PascalCase for routes
app/analyze/uploadId/page.tsx     # Missing brackets for dynamic
```

**Utilities & Libraries:**
```
✅ CORRECT:
lib/utils.ts                       # lowercase for utilities
lib/pipeline-client.ts             # kebab-case for multi-word

❌ INCORRECT:
lib/Utils.ts                       # PascalCase
lib/pipeline_client.ts             # snake_case
```

### Import Organization

**Order:**
1. External dependencies (React, Next.js, libraries)
2. Internal components
3. Internal utilities
4. Types/interfaces
5. Styles (if any)

```typescript
// ✅ CORRECT:
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'

import FileUploadZone from '@/components/FileUploadZone'
import CompanyBadge from '@/components/CompanyBadge'

import { uploadToBlob } from '@/lib/blob-client'
import { cn } from '@/lib/utils'

import type { Opportunity } from '@/types/pipeline'

// ❌ INCORRECT: Random order, mixing internal and external
import { Button } from '@/components/ui/button'
import { useState } from 'react'
import type { Opportunity } from '@/types/pipeline'
import FileUploadZone from '@/components/FileUploadZone'
```

**Path Aliases:**
- Use `@/` for absolute imports from project root
- Never use relative imports beyond one level (`../../` is forbidden)

```typescript
// ✅ CORRECT:
import { Button } from '@/components/ui/button'
import { uploadToBlob } from '@/lib/blob-client'

// ❌ INCORRECT:
import { Button } from '../../components/ui/button'
import { uploadToBlob } from '../../../lib/blob-client'
```

### TypeScript Conventions

**Type Definitions:**

```typescript
// ✅ CORRECT: Use interfaces for objects, types for unions/primitives
interface Opportunity {
  id: string
  title: string
  description: string
}

type PipelineStatus = 'idle' | 'running' | 'completed' | 'error'

// ❌ INCORRECT: Using type for simple objects
type Opportunity = {
  id: string
  title: string
}
```

**Strict Typing:**
```typescript
// ✅ CORRECT: Explicit types, no any
function analyzeDocument(file: File): Promise<AnalysisResult> {
  // implementation
}

// ❌ INCORRECT: Using any, implicit types
function analyzeDocument(file: any) {
  // implementation
}
```

**Null Safety:**
```typescript
// ✅ CORRECT: Optional chaining and nullish coalescing
const title = opportunity?.title ?? 'Untitled'
const count = opportunities?.length ?? 0

// ❌ INCORRECT: Unsafe access
const title = opportunity.title || 'Untitled'  // Fails if title is empty string
```

### Function Conventions

**Naming:**
- Use descriptive, verb-based names
- Boolean functions start with `is`, `has`, `should`, `can`
- Event handlers start with `handle` or `on`

```typescript
// ✅ CORRECT:
function uploadFile(file: File): Promise<string> { }
function isValidPDF(file: File): boolean { }
function handleUploadClick(): void { }

// ❌ INCORRECT:
function upload(f: any) { }           // Unclear, implicit types
function validPDF(file: File) { }     // Missing verb
function clickUpload(): void { }      // Wrong convention
```

**Async Functions:**
```typescript
// ✅ CORRECT: Always use async/await, never mix with .then()
async function uploadAndAnalyze(file: File): Promise<AnalysisResult> {
  const blobUrl = await uploadToBlob(file)
  const analysis = await analyzeDocument(blobUrl)
  return analysis
}

// ❌ INCORRECT: Mixing async/await with .then()
async function uploadAndAnalyze(file: File) {
  const blobUrl = await uploadToBlob(file)
  return analyzeDocument(blobUrl).then(result => result)
}
```

---

## Next.js 15 Patterns

### App Router Conventions

**Route Handlers (API Routes):**

```typescript
// ✅ CORRECT: app/api/upload/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File

    // ... processing logic

    return NextResponse.json({ success: true, data })
  } catch (error) {
    console.error('Upload error:', error)
    return NextResponse.json(
      { error: 'Upload failed' },
      { status: 500 }
    )
  }
}

// ❌ INCORRECT: Missing error handling, implicit types
export async function POST(request) {
  const formData = await request.formData()
  return NextResponse.json({ data: formData.get('file') })
}
```

**Dynamic Routes:**
```typescript
// ✅ CORRECT: app/pipeline/[runId]/page.tsx
interface PageProps {
  params: { runId: string }
}

export default function PipelinePage({ params }: PageProps) {
  const { runId } = params
  // ... implementation
}

// ❌ INCORRECT: Implicit params type
export default function PipelinePage({ params }) {
  const runId = params.runId
}
```

### Data Fetching

**Server Components (Fetch Data Directly):**
```typescript
// ✅ CORRECT: Direct async fetch in server component
export default async function ResultsPage({ params }: PageProps) {
  const results = await fetch(`/api/results/${params.runId}`)
  const data = await results.json()

  return <ResultsDisplay data={data} />
}
```

**Client Components (Use SWR or React Query):**
```typescript
// ✅ CORRECT: Client-side polling
'use client'

import useSWR from 'swr'

export default function PipelineStatus({ runId }: { runId: string }) {
  const { data, error } = useSWR(
    `/api/status/${runId}`,
    fetcher,
    { refreshInterval: 2000 }
  )

  if (error) return <div>Error loading status</div>
  if (!data) return <div>Loading...</div>

  return <StatusDisplay status={data} />
}
```

---

## Error Handling Standards

### API Routes

```typescript
// ✅ CORRECT: Comprehensive error handling
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      )
    }

    if (file.type !== 'application/pdf') {
      return NextResponse.json(
        { error: 'Only PDF files are supported' },
        { status: 415 }
      )
    }

    const result = await processFile(file)
    return NextResponse.json({ success: true, data: result })

  } catch (error) {
    console.error('File processing error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

### Client Components

```typescript
// ✅ CORRECT: User-friendly error states
'use client'

export default function FileUpload() {
  const [error, setError] = useState<string | null>(null)

  const handleUpload = async (file: File) => {
    try {
      setError(null)
      const result = await uploadFile(file)
      // ... success handling
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      console.error('Upload error:', err)
    }
  }

  return (
    <div>
      {error && <ErrorMessage message={error} />}
      {/* ... upload UI */}
    </div>
  )
}
```

---

## Styling Standards

### Tailwind CSS Conventions

**Class Ordering (Tailwind Plugin Recommended):**
1. Layout (display, position, flex, grid)
2. Sizing (width, height, padding, margin)
3. Typography (font, text-align, color)
4. Decorative (background, border, shadow)
5. Interactive (hover, focus, transition)

```typescript
// ✅ CORRECT: Logical grouping
<div className="flex items-center justify-between w-full p-4 text-lg font-semibold bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">

// ❌ INCORRECT: Random order
<div className="shadow-sm hover:shadow-md bg-white flex text-lg w-full p-4 border-gray-200 rounded-lg items-center font-semibold border justify-between transition-shadow">
```

**Use `cn()` Utility for Conditional Classes:**
```typescript
import { cn } from '@/lib/utils'

// ✅ CORRECT:
<div className={cn(
  "px-4 py-2 rounded-lg",
  isActive && "bg-blue-500 text-white",
  isDisabled && "opacity-50 cursor-not-allowed"
)}>

// ❌ INCORRECT: String concatenation
<div className={`px-4 py-2 rounded-lg ${isActive ? 'bg-blue-500 text-white' : ''} ${isDisabled ? 'opacity-50' : ''}`}>
```

**Responsive Design:**
```typescript
// ✅ CORRECT: Mobile-first approach
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// ❌ INCORRECT: Desktop-first
<div className="grid grid-cols-3 md:grid-cols-2 sm:grid-cols-1">
```

### shadcn/ui Component Usage

**Never Modify Primitive Components:**
```typescript
// ✅ CORRECT: Wrap shadcn components
import { Button } from '@/components/ui/button'

export default function UploadButton({ onClick }: { onClick: () => void }) {
  return (
    <Button onClick={onClick} variant="default" size="lg">
      Upload PDF
    </Button>
  )
}

// ❌ INCORRECT: Directly editing ui/button.tsx
// NEVER edit files in components/ui/
```

---

## Comments & Documentation

### When to Comment

**DO Comment:**
- Complex business logic
- Non-obvious workarounds
- API contracts
- Magic numbers
- TODO items with context

```typescript
// ✅ CORRECT: Explains WHY, not WHAT
// Vercel Blob URLs expire after 1 hour, so we must download immediately
const pdfBuffer = await fetch(blobUrl).then(r => r.arrayBuffer())

// Poll every 2 seconds - pipeline stages can take 2-5 minutes each
const { data } = useSWR(`/api/status/${runId}`, fetcher, { refreshInterval: 2000 })

// TODO(philippe): Replace with WebSocket when we move off Vercel free tier
```

**DON'T Comment:**
- Self-explanatory code
- Obvious variable names
- Framework conventions

```typescript
// ❌ INCORRECT: States the obvious
// Get the file from form data
const file = formData.get('file')

// Create a new Date object
const now = new Date()

// Loop through opportunities
opportunities.forEach(opp => { })
```

### JSDoc for Public APIs

```typescript
// ✅ CORRECT: Document public functions
/**
 * Uploads a PDF file to Vercel Blob storage
 * @param file - The PDF file to upload
 * @returns The public URL of the uploaded file
 * @throws {Error} If file is not a PDF or upload fails
 */
export async function uploadPDF(file: File): Promise<string> {
  // implementation
}
```

---

## Testing Standards

### File Naming
```
src/components/FileUploadZone.tsx
src/components/FileUploadZone.test.tsx     ✅ CORRECT

tests/FileUploadZone.test.tsx              ❌ INCORRECT: Keep tests next to source
```

### Test Structure
```typescript
// ✅ CORRECT: Descriptive test names using BDD style
describe('FileUploadZone', () => {
  it('should accept PDF files via drag and drop', () => {
    // Arrange
    const onUpload = jest.fn()
    const { getByTestId } = render(<FileUploadZone onUpload={onUpload} />)

    // Act
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    fireEvent.drop(getByTestId('dropzone'), { dataTransfer: { files: [file] } })

    // Assert
    expect(onUpload).toHaveBeenCalledWith(file)
  })

  it('should reject non-PDF files', () => {
    // ... test implementation
  })
})
```

---

## Git Commit Standards

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling

**Examples:**
```bash
# ✅ CORRECT:
feat(upload): add drag-and-drop file upload with validation

- Implement FileUploadZone component using react-dropzone
- Add PDF validation and file size limits
- Display upload progress indicator

Closes #123

# ❌ INCORRECT:
updated file upload stuff
```

---

## Security Standards

### XSS Prevention
```typescript
// ✅ CORRECT: Use react-markdown for user-generated markdown
import ReactMarkdown from 'react-markdown'

<ReactMarkdown>{opportunityDescription}</ReactMarkdown>

// ❌ INCORRECT: Never use dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: opportunityDescription }} />
```

### Environment Variables
```typescript
// ✅ CORRECT: Validate environment variables
if (!process.env.BLOB_READ_WRITE_TOKEN) {
  throw new Error('BLOB_READ_WRITE_TOKEN is required')
}

// ❌ INCORRECT: Silent failures
const token = process.env.BLOB_READ_WRITE_TOKEN || ''
```

### API Route Protection
```typescript
// ✅ CORRECT: Validate inputs
export async function POST(request: NextRequest) {
  const { runId } = await request.json()

  // Validate runId format (UUIDs only)
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(runId)) {
    return NextResponse.json({ error: 'Invalid runId' }, { status: 400 })
  }

  // ... process request
}
```

---

## Performance Standards

### Bundle Size Optimization
```typescript
// ✅ CORRECT: Dynamic imports for heavy components
const PipelineViewer = dynamic(() => import('@/components/PipelineViewer'), {
  loading: () => <Skeleton />,
  ssr: false
})

// ❌ INCORRECT: Importing heavy libraries at top level
import * as d3 from 'd3'  // Imports entire d3 library
```

### Image Optimization
```typescript
// ✅ CORRECT: Use Next.js Image component
import Image from 'next/image'

<Image
  src="/images/logo.png"
  alt="Company Logo"
  width={200}
  height={100}
  priority={true}  // For above-fold images
/>

// ❌ INCORRECT: Regular img tag
<img src="/images/logo.png" alt="Company Logo" />
```

---

## Accessibility Standards

### Semantic HTML
```typescript
// ✅ CORRECT: Semantic elements
<main>
  <header>
    <h1>Upload Innovation Report</h1>
  </header>
  <section>
    <FileUploadZone />
  </section>
</main>

// ❌ INCORRECT: Div soup
<div>
  <div>
    <div>Upload Innovation Report</div>
  </div>
  <div>
    <FileUploadZone />
  </div>
</div>
```

### ARIA Labels
```typescript
// ✅ CORRECT: Accessible interactive elements
<button
  onClick={handleUpload}
  aria-label="Upload PDF document"
  aria-busy={isUploading}
>
  {isUploading ? 'Uploading...' : 'Upload PDF'}
</button>

// ❌ INCORRECT: Missing accessibility attributes
<div onClick={handleUpload}>Upload</div>
```

---

## Python Standards (Pipeline Code)

### DO NOT Modify Python Pipeline Code
```python
# ⚠️ WARNING: Existing pipeline code in pipeline/ is FROZEN
# Only modify scripts/run_pipeline.py for integration

# ✅ CORRECT: Add new functionality via wrapper scripts
# scripts/run_pipeline.py - modified to accept new parameters

# ❌ INCORRECT: Editing stage implementations
# pipeline/stages/stage1_input_processing.py - DO NOT TOUCH
```

### Python Modifications (If Absolutely Necessary)
- Follow PEP 8 style guide
- Type hints for function signatures
- Docstrings for all functions
- Error handling with logging

```python
# ✅ CORRECT: Minimal changes with logging
import logging

logger = logging.getLogger(__name__)

def run_pipeline(input_file: str, brand: str, run_id: str) -> dict:
    """Run the 5-stage innovation pipeline.

    Args:
        input_file: Path to PDF document
        brand: Brand identifier from brand-profiles/
        run_id: Unique run identifier

    Returns:
        dict: Pipeline execution results
    """
    logger.info(f"Starting pipeline for {brand} (run_id: {run_id})")
    # ... implementation
```

---

## Code Review Checklist

Before submitting code, verify:

- [ ] All files follow naming conventions
- [ ] TypeScript strict mode passes (`npm run type-check`)
- [ ] ESLint passes with no warnings (`npm run lint`)
- [ ] All imports use `@/` path aliases
- [ ] No `any` types (except in type assertions)
- [ ] Error handling in all async functions
- [ ] Tailwind classes use logical ordering
- [ ] Comments explain WHY, not WHAT
- [ ] Accessibility attributes on interactive elements
- [ ] No modifications to `components/ui/` (shadcn primitives)
- [ ] No modifications to `pipeline/stages/` (Python pipeline)
- [ ] Security: No `dangerouslySetInnerHTML`, validated inputs
- [ ] Performance: Dynamic imports for heavy components

---

## Anti-Patterns (What NOT to Do)

### ❌ FORBIDDEN PATTERNS:

**1. Modifying shadcn/ui Primitives:**
```typescript
// ❌ NEVER EDIT components/ui/button.tsx
// Create wrapper components instead
```

**2. Relative Import Hell:**
```typescript
// ❌ NEVER USE
import { Button } from '../../../components/ui/button'

// ✅ USE
import { Button } from '@/components/ui/button'
```

**3. Mixing Async Patterns:**
```typescript
// ❌ NEVER MIX
async function fetchData() {
  const data = await fetch('/api/data')
  return data.json().then(result => result)
}

// ✅ CONSISTENT
async function fetchData() {
  const data = await fetch('/api/data')
  return await data.json()
}
```

**4. Props Drilling (3+ Levels):**
```typescript
// ❌ AVOID
<Parent prop={value}>
  <Child prop={value}>
    <GrandChild prop={value}>
      <GreatGrandChild prop={value} />
    </GrandChild>
  </Child>
</Parent>

// ✅ USE CONTEXT OR COMPOSITION
```

**5. Inline Styles:**
```typescript
// ❌ NEVER USE
<div style={{ padding: '16px', backgroundColor: 'blue' }}>

// ✅ USE TAILWIND
<div className="p-4 bg-blue-500">
```

---

## Questions?

For clarification on coding standards:
1. Check this document first
2. Review existing code in `innovation-web/` (once implemented)
3. Consult Next.js 15 documentation
4. Ask the architect agent (`/BMad:agents:architect`)

**Last Updated**: 2025-10-19
**Maintained By**: Winston (Architect Agent)
