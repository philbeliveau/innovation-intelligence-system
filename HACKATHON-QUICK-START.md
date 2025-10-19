# Hackathon Quick Start Guide

**Time Budget:** 8-10 hours
**Goal:** Working web demo wrapping existing Python pipeline
**Status:** ✅ Architecture validated and ready

---

## ⚠️ CRITICAL FIRST STEP

**Before writing any code, validate Python on Vercel:**

```bash
# Create test project
npx create-next-app@latest test-python --app --typescript
cd test-python

# Create test route: app/api/test/route.ts
```

```typescript
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

```bash
# Deploy and test
vercel --prod
# Visit https://your-deployment.vercel.app/api/test
```

**If Python NOT available:** Use Railway, Render.com, or Docker instead of Vercel.

---

## 🚀 Implementation Steps

### Hour 0-1: Setup

```bash
# Create Next.js app
npx create-next-app@latest innovation-web --app --tailwind
cd innovation-web

# Install ALL dependencies (critical: pdf-parse and yaml)
npm install @vercel/blob react-dropzone react-markdown yaml pdf-parse
npm install -D @types/node

# Install shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add card button select badge skeleton separator

# Copy .env.example to .env.local and fill in values
cp ../.env.example .env.local
# Edit .env.local with your OPENROUTER_API_KEY
```

---

### Hour 1-2: Onboarding Page

**Create:** `app/onboarding/page.tsx`

```typescript
'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Select } from '@/components/ui/select'
import { Button } from '@/components/ui/button'

export default function Onboarding() {
  const [companyId, setCompanyId] = useState('')
  const router = useRouter()

  const companies = [
    { id: 'lactalis-canada', name: 'Lactalis Canada' },
    { id: 'mccormick-usa', name: 'McCormick USA' },
    { id: 'columbia-sportswear', name: 'Columbia Sportswear' },
    { id: 'decathlon', name: 'Decathlon' }
  ]

  const handleContinue = async () => {
    await fetch('/api/onboarding/set-company', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_id: companyId })
    })
    router.push('/')
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-96">
        <h1 className="text-2xl font-bold mb-4">Select Your Company</h1>
        <Select value={companyId} onValueChange={setCompanyId}>
          {companies.map(c => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </Select>
        <Button
          onClick={handleContinue}
          disabled={!companyId}
          className="mt-4 w-full"
        >
          Continue →
        </Button>
      </div>
    </div>
  )
}
```

**Create:** `app/api/onboarding/set-company/route.ts`

```typescript
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import { parse } from 'yaml'

export async function POST(request: Request) {
  const { company_id } = await request.json()

  // Load brand profile
  const profilePath = `data/brand-profiles/${company_id}.yaml`
  const yamlContent = await readFile(profilePath, 'utf-8')
  const brandProfile = parse(yamlContent)

  // Set cookie
  cookies().set('company_id', company_id, {
    maxAge: 60 * 60 * 24 * 7,
    httpOnly: true,
    sameSite: 'lax'
  })

  return NextResponse.json({
    success: true,
    company_id,
    company_name: brandProfile.brand_name
  })
}
```

---

### Hour 2-3: Homepage with Upload

**Create:** `app/page.tsx`

```typescript
'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useDropzone } from 'react-dropzone'
import { Card } from '@/components/ui/card'

export default function Home() {
  const [companyName, setCompanyName] = useState('')
  const router = useRouter()

  useEffect(() => {
    fetch('/api/onboarding/current-company')
      .then(res => res.json())
      .then(data => {
        if (data.error) router.push('/onboarding')
        else setCompanyName(data.company_name)
      })
  }, [])

  const onDrop = async (files: File[]) => {
    const formData = new FormData()
    formData.append('file', files[0])

    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    })
    const { upload_id, blob_url } = await res.json()

    // Save blob_url for intermediary page
    sessionStorage.setItem(`upload_${upload_id}`, blob_url)
    router.push(`/analyze/${upload_id}`)
  }

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] }
  })

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-right text-sm text-gray-600 mb-4">
          🏢 {companyName}
        </div>
        <h1 className="text-3xl font-bold text-center mb-8">
          My Board of Ideators
        </h1>
        <Card className="p-8">
          <div {...getRootProps()} className="border-2 border-dashed p-12 text-center cursor-pointer">
            <input {...getInputProps()} />
            <p>📤 Drag & drop PDF or click to upload</p>
          </div>
        </Card>
      </div>
    </div>
  )
}
```

---

### Hour 3-4: API Routes

**All API route code is in `docs/architecture.md` Section 6:**

1. Copy `/api/upload/route.ts` (uses Vercel Blob)
2. Copy `/api/analyze-document/route.ts` (uses pdf-parse + LLM)
3. Copy `/api/run/route.ts` (**USE UUID VERSION**)
4. Copy `/api/status/[runId]/route.ts` (**WITH TIMEOUT DETECTION**)

**Critical: Use the UPDATED versions from architecture.md with:**
- ✅ `randomUUID()` for run_id
- ✅ Timeout detection in /api/status
- ✅ Error handling with try-catch

---

### Hour 5-6: Python Pipeline Mods

**Edit:** `scripts/run_pipeline.py`

Add CLI arguments:
```python
parser.add_argument('--input-file', type=str, help='Direct PDF file path')
parser.add_argument('--run-id', type=str, help='Unique run identifier')
```

Add new function (copy from architecture.md Section 7.1)

**Edit:** `pipeline/stages/stage1_input_processing.py`

Add JSON output for 2-track UI (copy from architecture.md Section 7.2)

---

### Hour 6-8: Pipeline Viewer

**Create:** `app/pipeline/[runId]/page.tsx`

**Use the polling code from architecture.md Section 9, Hour 6-8:**
- ✅ Includes 35-minute timeout
- ✅ Error handling
- ✅ 5-second polling interval

Create components:
- `components/InspirationTrack.tsx` - Stage 1 cards
- `components/StageBox.tsx` - Stages 2-5 status

---

### Hour 8-9: Results Page

**Create:** `app/results/[runId]/page.tsx`

```typescript
import ReactMarkdown from 'react-markdown'
import { readFile } from 'fs/promises'
import { Card } from '@/components/ui/card'

export default async function Results({ params }) {
  const outputDir = `data/test-outputs/${params.runId}/stage5`

  const opportunities = await Promise.all(
    [1, 2, 3, 4, 5].map(async (num) => {
      const markdown = await readFile(`${outputDir}/opportunity-${num}.md`, 'utf-8')
      return { number: num, markdown }
    })
  )

  return (
    <div className="max-w-4xl mx-auto p-8">
      {opportunities.map(({ number, markdown }) => (
        <Card key={number} className="p-6 mb-6">
          <ReactMarkdown
            disallowedElements={['script', 'iframe', 'object', 'embed']}
            unwrapDisallowed={true}
          >
            {markdown}
          </ReactMarkdown>
        </Card>
      ))}
    </div>
  )
}
```

**⚠️ CRITICAL: Use XSS protection (disallowedElements)**

---

### Hour 9-10: Polish & Deploy

```bash
# Test locally
npm run dev

# Deploy to Vercel
vercel --prod

# Set environment variables in Vercel dashboard:
# - OPENROUTER_API_KEY
# - LLM_MODEL
# - BLOB_READ_WRITE_TOKEN (auto-generated)

# Test end-to-end with real PDF
```

---

## 🎯 Success Checklist

- [ ] Company selection works (onboarding)
- [ ] File upload to Blob succeeds
- [ ] Intermediary card shows LLM analysis
- [ ] Pipeline starts on "Launch" click
- [ ] Stage 1 displays 2 inspiration tracks
- [ ] Stages 2-5 update status in real-time
- [ ] All 5 stages complete
- [ ] Results page shows 5 opportunity cards
- [ ] No console errors
- [ ] Deployed to Vercel with public URL

---

## 🐛 Common Issues

**"Cannot find module 'pdf-parse'"**
- Run: `npm install pdf-parse`

**"Cannot find module 'yaml'"**
- Run: `npm install yaml`

**Pipeline never starts**
- Check Python is available on Vercel (see pre-check)
- Check logs: `data/test-outputs/{run_id}/logs/pipeline.log`

**Pipeline timeout**
- Expected if > 35 minutes
- Check for Python errors in logs
- Verify OpenRouter API key is valid

**Blob upload fails**
- Set `BLOB_READ_WRITE_TOKEN` in Vercel env vars
- Check file is < 25MB

---

## 📚 Reference Documents

- **Complete Architecture:** `docs/architecture.md`
- **All Code Examples:** `docs/architecture.md` Section 6 (API Design)
- **Directory Structure:** `docs/architecture.md` Section 3.1
- **Critical Fixes Applied:** `CRITICAL-FIXES-APPLIED.md`
- **Environment Variables:** `.env.example`

---

**Good luck with your hackathon! 🚀**

**Questions?** All code is copy-paste ready from `docs/architecture.md`.
