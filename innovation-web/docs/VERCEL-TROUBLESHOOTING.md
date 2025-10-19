# Vercel Deployment Troubleshooting Guide

This document captures all deployment errors encountered and their solutions during the Innovation Intelligence System web application deployment to Vercel.

## Table of Contents
- [Error 1: DOMMatrix is not defined](#error-1-dommatrix-is-not-defined)
- [Error 2: ESM Import Issues with pdf-parse](#error-2-esm-import-issues-with-pdf-parse)
- [Error 3: Missing TypeScript Declarations](#error-3-missing-typescript-declarations)
- [Error 4: Build Failures from Uncommitted Changes](#error-4-build-failures-from-uncommitted-changes)
- [Error 5: 504 Gateway Timeout](#error-5-504-gateway-timeout)
- [Best Practices](#best-practices)

---

## Error 1: DOMMatrix is not defined

### Symptom
```
[analyze-document] PDF parsing error: ReferenceError: DOMMatrix is not defined
at 75555 (.next/server/chunks/555.js:2:118173)
Failed to load resource: the server responded with a status of 500 ()
/api/analyze-document:1
```

### Root Cause
The `pdfjs-dist` library requires browser-specific APIs (DOMMatrix, Canvas) that are not available in Node.js serverless environments like Vercel Edge/Node runtime.

**Why it happened:**
- pdfjs-dist is designed for browser environments
- Vercel serverless functions run in Node.js runtime without DOM APIs
- Canvas rendering APIs (DOMMatrix) do not exist server-side

### Initial Misdiagnosis
Initially suspected Vercel Hobby plan's 10-second timeout was the issue. Applied optimizations:
- Changed LLM model to `gpt-4o-mini` (faster)
- Reduced context from 4000 to 2000 characters
- Set timeout to 8 seconds
- Added `maxDuration = 10`

**This did not solve the problem** - the actual issue was browser API incompatibility, not timeout.

### Solution
Replace `pdfjs-dist` with `pdf-parse-fork`, a pure Node.js PDF parsing library.

**File: `app/api/analyze-document/route.ts`**

Before (BROKEN):
```typescript
import * as pdfjs from 'pdfjs-dist/legacy/build/pdf.mjs'

// Lazy load pdfjs
const pdfjs = await loadPdfJs()
const pdf = await pdfjs.getDocument({ data: arrayBuffer }).promise

// Extract text from all pages
const textParts: string[] = []
for (let i = 1; i <= pdf.numPages; i++) {
  const page = await pdf.getPage(i)
  const textContent = await page.getTextContent()
  const pageText = textContent.items
    .map((item) => ('str' in item ? item.str : ''))
    .join(' ')
  textParts.push(pageText)
}
```

After (WORKING):
```typescript
import pdf from 'pdf-parse-fork'

const arrayBuffer = await pdfResponse.arrayBuffer()
const buffer = Buffer.from(arrayBuffer)

// Parse PDF with pdf-parse-fork (Node.js compatible)
const data = await pdf(buffer)
documentText = data.text
```

**Dependencies:**
```bash
npm uninstall pdfjs-dist
npm install pdf-parse-fork
```

---

## Error 2: ESM Import Issues with pdf-parse

### Symptom
```
Attempted import error: 'pdf-parse' does not contain a default export
```

### Root Cause
The `pdf-parse` package has ESM/CommonJS compatibility issues with Next.js 15 App Router.

### Attempted Solutions (Failed)
```typescript
import pdf from 'pdf-parse'              // FAILED
import * as pdfParse from 'pdf-parse'    // FAILED
import { parsePdf } from 'pdf-parse'     // FAILED
```

### Solution
Switch to `pdf-parse-fork` which has proper ESM exports:

```bash
npm uninstall pdf-parse
npm install pdf-parse-fork
```

```typescript
import pdf from 'pdf-parse-fork'  // WORKS
```

---

## Error 3: Missing TypeScript Declarations

### Symptom
```
Type error: Could not find a declaration file for module 'pdf-parse-fork'.
Try `npm i --save-dev @types/pdf-parse-fork` if it exists or add a new
declaration (.d.ts) file containing `declare module 'pdf-parse-fork';`
```

### Root Cause
The `pdf-parse-fork` package does not include TypeScript type definitions, and no community types (`@types/pdf-parse-fork`) exist.

### Solution
Create manual TypeScript declaration file.

**File: `pdf-parse-fork.d.ts`** (root of innovation-web/)

```typescript
declare module 'pdf-parse-fork' {
  interface PDFData {
    numpages: number
    numrender: number
    info: any
    metadata: any
    text: string
    version: string
  }

  function pdf(dataBuffer: Buffer): Promise<PDFData>
  export default pdf
}
```

**Why this works:**
- TypeScript compiler finds `.d.ts` files in project root
- Declares module shape for type checking
- Provides IntelliSense for `PDFData` interface

---

## Error 4: Build Failures from Uncommitted Changes

### Symptom
```
./app/pipeline/[runId]/page.tsx:167:31
Type error: Cannot find name 'getStageStatus'.
```

### Root Cause
Local files were modified (by user/linter/prettier) but not committed to git. Vercel deploys from git repository, not local filesystem.

**Common causes:**
- VS Code auto-format on save
- ESLint auto-fix
- Manual file edits during testing
- Prettier running on commit hooks

### Solution
Always commit all changes before deploying:

```bash
git add -A
git commit -m "fix: description of fix"
git push
vercel --prod --yes
```

**Best Practice:**
```bash
# Check git status before deployment
git status

# Review uncommitted changes
git diff

# Ensure working directory is clean
# (nothing in "Changes not staged for commit")
```

---

## Error 5: 504 Gateway Timeout

### Symptom
```
Vercel Runtime Timeout Error: Task timed out after 10 seconds
Failed to load resource: the server responded with a status of 504 ()
/api/analyze-document:1
```

### Root Cause
Vercel Hobby plan has a **10-second maximum execution time** for serverless functions. The original implementation was performing synchronous LLM analysis which took 12-15 seconds:

1. Download PDF from Blob (~1-2s)
2. Parse PDF with pdf-parse-fork (~1-2s)
3. **LLM analysis with gpt-4o-mini (~8-12s)** ← Timeout
4. JSON parsing and validation (~0.5s)

Even with optimizations (fast model, reduced context), LLM calls are unpredictable and often exceed 10 seconds.

### Solution
**Architectural change:** Remove LLM analysis from API route, return placeholder data immediately.

**Before (TIMED OUT):**
```typescript
// This took 12-15 seconds total
const llm = new ChatOpenAI({
  model: 'openai/gpt-4o-mini',
  timeout: 8000,
  maxRetries: 1,
})

const result = await llm.invoke(analysisPrompt)  // 8-12 seconds
const analysis = JSON.parse(result.content)
return NextResponse.json({ analysis })
```

**After (< 3 seconds):**
```typescript
// Quick PDF validation only (1-2 seconds)
const data = await pdf(buffer)
const preview = data.text.slice(0, 200)

// Return placeholder immediately
const analysis = {
  title: 'Document Preview',
  summary: `Document uploaded successfully. Preview: ${preview}...`,
  industry: 'pending',
  theme: 'Analysis in progress',
  tracks: [
    {
      title: 'Track 1 - Analyzing...',
      summary: 'Full analysis will be available after pipeline execution.',
    },
    {
      title: 'Track 2 - Analyzing...',
      summary: 'Click "Launch Innovation Pipeline" to begin.',
    }
  ]
}

return NextResponse.json({ analysis })  // Returns in ~2 seconds
```

**Benefits:**
- API route completes in 2-3 seconds (well under 10s limit)
- User sees immediate feedback
- Real LLM analysis happens during pipeline execution (no timeout limits)
- Pipeline Stage 1 has unlimited execution time

**File: `app/api/analyze-document/route.ts`**

Key changes:
1. Removed `ChatOpenAI` import
2. Removed LLM invocation
3. Extract only 500 characters for validation
4. Return placeholder data with preview text
5. Guide user to launch pipeline for full analysis

---

## Best Practices

### 1. Vercel Deployment Workflow
```bash
# Always follow this sequence:
git status              # Check for uncommitted changes
git add -A              # Stage all changes
git commit -m "msg"     # Commit with clear message
git push                # Push to GitHub
vercel --prod --yes     # Deploy to production

# Wait for deployment to complete
# Test in production environment
```

### 2. Serverless Function Constraints

**Vercel Hobby Plan Limits:**
- Maximum execution time: 10 seconds
- No browser APIs (DOM, Canvas, DOMMatrix)
- Cold start adds 1-2 seconds
- Must return before timeout or get 504

**Design Principles:**
- Keep API routes fast (< 5 seconds target)
- Move long operations to background jobs
- Use Edge Runtime for ultra-fast responses
- Return immediately, process asynchronously

### 3. PDF Processing in Serverless

**Do:**
- Use `pdf-parse-fork` for Node.js compatibility
- Extract only needed text (first N characters)
- Validate PDF quickly, analyze later
- Return early with placeholder data

**Don't:**
- Use `pdfjs-dist` (requires browser APIs)
- Parse entire multi-page PDFs synchronously
- Perform LLM analysis in API routes
- Block on external API calls > 5 seconds

### 4. TypeScript in Next.js

**For untyped packages:**
1. Check for `@types/package-name` on npm
2. If not available, create `.d.ts` file in project root
3. Use minimal typing (`any`) if needed
4. Document why manual types were needed

**Example declaration:**
```typescript
// package-name.d.ts
declare module 'package-name' {
  export function method(arg: string): Promise<any>
}
```

### 5. Debugging Vercel Errors

**Access logs:**
```bash
# Real-time logs
vercel logs --follow

# Recent logs for specific deployment
vercel logs [deployment-url]

# Function-specific logs
vercel logs --filter=/api/analyze-document
```

**Common error patterns:**

| Error Code | Common Cause | Solution |
|------------|--------------|----------|
| 500 | Runtime error in function | Check function logs for stack trace |
| 504 | Function timeout (>10s) | Optimize or move to background job |
| 404 | Route not found | Check file-based routing structure |
| 405 | Wrong HTTP method | Verify GET/POST exports in route.ts |

### 6. Environment Variables

**Required for this project:**
```bash
# Vercel dashboard → Settings → Environment Variables
OPENROUTER_API_KEY=your_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-4o-mini
BLOB_READ_WRITE_TOKEN=vercel_blob_token
```

**Testing locally:**
```bash
# .env.local (NOT committed to git)
OPENROUTER_API_KEY=sk-or-...
BLOB_READ_WRITE_TOKEN=vercel_blob_...

# Verify with:
npm run dev
# Check process.env in API route console.log
```

---

## Summary of Fixes Applied

| Issue | Error Type | Solution | Time to Fix |
|-------|-----------|----------|-------------|
| DOMMatrix not defined | Runtime Error | Replace pdfjs-dist → pdf-parse-fork | 30 min |
| ESM import error | Build Error | Switch pdf-parse → pdf-parse-fork | 10 min |
| Missing TypeScript types | Build Error | Create pdf-parse-fork.d.ts | 5 min |
| Uncommitted changes | Build Error | git add -A && commit && push | 2 min |
| 504 Gateway Timeout | Runtime Error | Remove LLM from API route | 20 min |

**Total debugging time:** ~67 minutes

**Key Lesson:** Always verify Vercel runtime environment compatibility before choosing npm packages. Browser-dependent libraries will fail in serverless Node.js.

---

## Additional Resources

- [Vercel Serverless Function Limits](https://vercel.com/docs/functions/serverless-functions/runtimes#limits)
- [Next.js App Router API Routes](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)
- [pdf-parse-fork Documentation](https://www.npmjs.com/package/pdf-parse-fork)
- [TypeScript Declaration Files](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html)
