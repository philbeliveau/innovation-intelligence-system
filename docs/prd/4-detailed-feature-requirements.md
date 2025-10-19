# 4. Detailed Feature Requirements

## 4.0 Onboarding/Landing Page - Company Selection (Priority: P0)

### 4.0.1 Visual Design

**Reference:** `docs/image/Landing-page.png`

**Purpose:** Combined onboarding and landing page where users type company name to access their innovation board

**Layout:**
```
┌──────────────────────────────────────────────────────────────────┐
│                          [Everything] [Spaces] [Serendipity]     │
│                                                                   │
│                    ●  (teal circle)                              │
│                                                                   │
│         ●  (blue)                         ●  (yellow)            │
│                                                                   │
│                                                                   │
│    ●  (orange)      My Board of Ideators       ●  (orange)       │
│                                                                   │
│                    ┌──────────────────────────────┐              │
│                    │ Lactalis, Columbia, Decath...│              │
│                    │ (Type company name)          │              │
│                    └──────────────────────────────┘              │
│                                                                   │
│         ●  (yellow)                       ●  (blue)              │
│                                                                   │
│                    ●  (teal)                                     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 4.0.2 Functional Requirements

**FR-ON-1: Visual Elements**
- **Title:** "My Board of Ideators" centered, with "My" in teal italics
- **Colored Circles:** 8 circles arranged in circular pattern
  - Colors: Teal, Blue, Yellow, Orange (2 of each)
  - Equal spacing around center
- **Central Input:** White rectangular text input field
  - Placeholder: "Lactalis, Columbia, Decathlon, McCormick..."
  - Width: 400-500px
  - Height: 50-60px
- **Background:** Light gray/off-white with subtle texture

**FR-ON-2: Top Navigation**
- **Tabs:** "Everything" | "Spaces" | "Serendipity"
- **Position:** Top-right of page
- **Active Tab:** "Everything" by default (underlined or highlighted)
- **Phase 1:** Tabs are visual only (no functionality)
- **Phase 2:** Enable different board views per tab

**FR-ON-3: Company Input & Validation**
- **Input Behavior:**
  - User types company name into central input
  - Case-insensitive matching
  - Accepts partial matches (e.g., "lact" → "Lactalis")
- **Accepted Companies:**
  - "Lactalis" → `lactalis-canada`
  - "Columbia" → `columbia-sportswear`
  - "Decathlon" → `decathlon`
  - "McCormick" → `mccormick-usa`
- **Validation:**
  - On Enter key or input blur
  - If valid: Load brand profile YAML
  - If invalid: Show error message below input ("Company not found. Please try: Lactalis, Columbia, Decathlon, or McCormick")

**FR-ON-4: Company Profile Loading**
- **API Call:** POST to `/api/onboarding/set-company` with company name
- **Backend:**
  - Maps company name to company ID
  - Loads `/data/brand-profiles/{company-id}.yaml`
  - Saves company ID to HTTP-only cookie (7-day expiry)
  - Returns company name and profile data
- **Redirect:** On success, navigate to `/upload` page
- **Error Handling:** Display validation error, keep user on page

**FR-ON-5: Additional Interactions**
- **Circle Hover:** Optional subtle scale (1.05x) or glow effect
- **Input Focus:** Border color change (teal accent)
- **Loading State:** Show spinner in input during API call

### 4.0.3 Technical Specifications

**Components:**
- `app/page.tsx` - Combined onboarding/landing page (root route) with "My Board of Ideators" design
- `components/OnboardingHero.tsx` - Central title and circles
- `components/TopNav.tsx` - Top navigation tabs
- `components/CompanyInput.tsx` - Text input with validation

**API Integration:**
```typescript
'use client'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function OnboardingPage() {
  const router = useRouter()
  const [companyInput, setCompanyInput] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const companyMapping: Record<string, string> = {
    'lactalis': 'lactalis-canada',
    'columbia': 'columbia-sportswear',
    'decathlon': 'decathlon',
    'mccormick': 'mccormick-usa'
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const normalizedInput = companyInput.toLowerCase().trim()
    const companyId = companyMapping[normalizedInput]

    if (!companyId) {
      setError('Company not found. Try: Lactalis, Columbia, Decathlon, or McCormick')
      setLoading(false)
      return
    }

    try {
      const response = await fetch('/api/onboarding/set-company', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_id: companyId })
      })

      if (response.ok) {
        router.push('/upload')
      } else {
        setError('Failed to load company profile')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    // Onboarding UI with circles and company input
  )
}
```

---

## 4.1 Upload Page (Priority: P0)

### 4.1.1 Visual Design

**Purpose:** File upload interface for trend reports (accessed after company selection at root `/`)

**Layout:**
```
┌────────────────────────────────────────────────────────┐
│                                                        │
│              Select Your Company                       │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │                                               │    │
│  │  Company: [Select a company... ▼]            │    │
│  │                                               │    │
│  │  Options:                                     │    │
│  │  - Lactalis Canada                            │    │
│  │  - McCormick USA                              │    │
│  │  - Columbia Sportswear                        │    │
│  │  - Decathlon                                  │    │
│  │                                               │    │
│  │              [Continue →]                     │    │
│  │                                               │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 4.0.2 Functional Requirements

**FR-OB-1: Company Selection**
- **Input:** Dropdown with 4 company options
- **Data Source:** List companies from `/data/brand-profiles/*.yaml` files
- **Validation:** Must select company before proceeding
- **Action:** Load brand profile YAML and save to cookie

**FR-OB-2: Brand Profile Loading**
- **Source:** `/data/brand-profiles/{company-id}.yaml`
- **Fields Loaded:**
  - `brand_name` - Display on homepage
  - `country`, `industry`, `positioning` - Context for pipeline
  - `product_portfolio`, `target_customers` - Used in Stage 4
  - `strategic_priorities`, `brand_values` - Used in Stage 5
- **Storage:** Save `company_id` to HTTP-only cookie (7-day expiry)

**FR-OB-3: Navigation**
- **Continue Button:** Disabled until company selected
- **Redirect:** Navigate to `/` (homepage) after successful save
- **Error Handling:** Display error if YAML file not found

### 4.0.3 Technical Specifications (Deprecated - See Section 4.0 for Correct Implementation)

**Note:** This section describes an outdated separate onboarding route. The current architecture uses a combined onboarding/landing page at root (`/`). See Section 4.0 for the correct implementation.

**Components (Deprecated):**
- ~~`app/onboarding/page.tsx`~~ - Use `app/page.tsx` instead (combined onboarding/landing)
- `components/CompanySelector.tsx` - Dropdown (shadcn/ui Select)

**Current Implementation:** Company selection happens at root route (`/`) with text input, not separate `/onboarding` route. See Architecture document Section 5.0 for details.

---

## 4.1 Homepage (Priority: P0)

### 4.1.1 Visual Design

**Reference:** `docs/image/main-page.png`

**Layout:**
```
┌────────────────────────────────────────────────────────┐
│                 My Board of Ideators                   │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │              📤 Upload Icon                   │    │
│  │                                               │    │
│  │     Drag & drop or choose file to upload     │    │
│  │                                               │    │
│  │  Supported types: PDF, txt, Markdown, Audio  │    │
│  │                                               │    │
│  │  [Link] [Website] [YouTube]  [Paste text]   │    │
│  │                                               │    │
│  │            Brand: [Dropdown ▼]               │    │
│  │                                               │    │
│  │        [Generate Opportunities]              │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│          or Select a Starting Points                   │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │Food & Bev│  │Food & Bev│  │Food & Bev│          │
│  │Update    │  │Update    │  │Update    │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└────────────────────────────────────────────────────────┘
```

### 4.1.2 Functional Requirements

**FR-HP-0: Company Display**
- **Source:** Read `company_id` from cookie (set in onboarding)
- **Display:** Company name at top-right corner (e.g., "Lactalis Canada 🏢")
- **Redirect:** If no cookie found, redirect to `/onboarding`
- **Styling:** Subtle, non-intrusive (badge component)

**FR-HP-1: File Upload**
- **Input:** PDF, TXT, MD files via drag-and-drop or click
- **Max Size:** 25MB (Vercel Blob limit)
- **Validation:** Display error if unsupported file type or oversized
- **Feedback:** Show file name, size, and upload progress bar
- **Action:** After successful upload, redirect to `/analyze/{uploadId}`

**FR-HP-4: Starting Points (Phase 2 - Out of Scope)**
- Display 3 pre-loaded example reports
- Click to auto-populate upload with example
- **Hackathon:** Static cards with no functionality

### 4.1.3 Technical Specifications

**Components:**
- `app/page.tsx` - Main homepage component
- `components/FileUpload.tsx` - Drag & drop zone (use `react-dropzone`)
- `components/CompanyBadge.tsx` - Display company name (shadcn/ui Badge)
- `components/GenerateButton.tsx` - CTA button (shadcn/ui Button)

**API Integration:**
```typescript
'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const [companyName, setCompanyName] = useState<string>('')
  const [blobUrl, setBlobUrl] = useState<string>('')
  const router = useRouter()

  // Check if company is set, redirect to root if not
  useEffect(() => {
    fetch('/api/onboarding/current-company')
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          router.push('/')  // Redirect to root onboarding/landing page
        } else {
          setCompanyName(data.company_name)
        }
      })
  }, [])

  // File upload flow
  const handleFileUpload = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    })

    const { blob_url, upload_id } = await response.json()

    // Redirect to intermediary card page for analysis
    router.push(`/analyze/${upload_id}`)
  }

  return (
    // ... UI with company badge at top-right
  )
}
```

---

## 4.2 Intermediary Card Page (Priority: P0)

### 4.2.1 Visual Design

**Reference:** `docs/image/intermediary-card.png` and `docs/image/track-division.png`

**Purpose:** Display LLM-extracted document summary with ideation track selection before launching horizontal pipeline

**Layout:**
```
┌────────────────────────────────────────────────────────────────────────┐
│                     My Board of Ideators                               │
│                                                                         │
│  Left: Document Summary             Right: Ideation Tracks             │
│  ┌────────────────────────┐         ┌─────────────────────────┐       │
│  │                         │         │ Track 1: ✓ (Selected)  │       │
│  │  [Hero Image]           │         │ [Track Icon]            │       │
│  │                         │         │ Summary of this track.  │       │
│  │  Ad-generating QR...   │         │ Summary of this track.  │       │
│  │                         │         │ Summary of this track.  │       │
│  │  Source: [tw...com]     │         └─────────────────────────┘       │
│  │  Industry: [fashion]    │         ┌─────────────────────────┐       │
│  │  Theme: [marketing]     │         │ Track 2: ✓ (Selected)  │       │
│  │                         │         │ [Track Icon]            │       │
│  │  Most people only...   │         │ Summary of this track.  │       │
│  │                         │         │ Summary of this track.  │       │
│  │      • • •              │         └─────────────────────────┘       │
│  └────────────────────────┘                                            │
│                                                                         │
│                           [Launch]                                      │
│                 (Start horizontal pipeline flow)                       │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.2.2 Functional Requirements

**FR-IC-1: Document Analysis**
- **Trigger:** On page load with `uploadId` parameter
- **API Call:** POST to `/api/analyze-document` with blob URL
- **Loading State:** Display "Analyzing document..." with spinner
- **Processing Time:** 30-60 seconds (LLM extraction + track identification)

**FR-IC-2: Data Display - Left Card (Document Summary)**
- **Title:** LLM-generated compelling headline (10-15 words)
- **Hero Image:** Placeholder gradient or generic image
- **Source Badges:** Dark gray pills showing document sources
- **Industry Badge:** Orange pill with single-word industry
- **Theme Badge:** Red pill with 2-3 word theme
- **Summary:** 2-3 sentences (~50 words) explaining the document

**FR-IC-3: Data Display - Right Section (Ideation Tracks)**
- **Reference UI:** Must match `docs/image/track-division.png` exactly
- **Track Cards:** Display 2 ideation tracks identified by LLM
- **Selection:** Both tracks shown as selected (highlighted with checkmark)
- **Visual Style:** Icon + title + 2-3 sentence summary per track

**FR-IC-4: Launch Action**
- **Button:** "Launch" at bottom center
- **Behavior:**
  1. Call `/api/run` with blob URL, upload ID, and selected track IDs ([1, 2])
  2. Transition animation from vertical card to horizontal pipeline
  3. Redirect to `/pipeline/{runId}` with horizontal flow layout
- **Loading State:** Show spinner on button during API call

### 4.2.3 Technical Specifications

**Components:**
- `app/analyze/[uploadId]/page.tsx` - Main intermediary card page
- `components/DocumentCard.tsx` - Card component matching design
- `components/BadgePill.tsx` - Source/industry/theme badges

**API Integration:**
```typescript
'use client'
import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'

export default function AnalyzePage() {
  const params = useParams()
  const router = useRouter()
  const [analysis, setAnalysis] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [blobUrl, setBlobUrl] = useState('')

  useEffect(() => {
    const analyzeDocument = async () => {
      // Get blob URL from upload ID (stored in sessionStorage or passed via query)
      const blob_url = sessionStorage.getItem(`upload_${params.uploadId}`)
      setBlobUrl(blob_url)

      const response = await fetch('/api/analyze-document', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ blob_url })
      })

      const data = await response.json()
      setAnalysis(data.analysis)
      setLoading(false)
    }

    analyzeDocument()
  }, [params.uploadId])

  const handleLaunch = async () => {
    const response = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        blob_url: blobUrl,
        upload_id: params.uploadId
      })
    })

    const { run_id } = await response.json()
    router.push(`/pipeline/${run_id}`)
  }

  if (loading) {
    return <div>Analyzing document...</div>
  }

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-3xl font-bold text-center mb-8">My Board of Ideators</h1>

      <Card className="p-6 mb-6">
        {/* Hero image placeholder */}
        <div className="w-full h-48 bg-gradient-to-r from-amber-200 to-amber-400 rounded-lg mb-4" />

        {/* Title */}
        <h2 className="text-xl font-semibold mb-4">{analysis.title}</h2>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mb-4">
          <Badge variant="secondary">Source: {analysis.sources[0]}</Badge>
          {analysis.sources.length > 1 && (
            <Badge variant="secondary">{analysis.sources.length - 1} others</Badge>
          )}
          <Badge className="bg-orange-500">Industry: {analysis.industry}</Badge>
          <Badge className="bg-red-600">Theme: {analysis.theme}</Badge>
        </div>

        {/* Summary */}
        <p className="text-sm text-gray-700">{analysis.summary}</p>

        {/* Pagination dots */}
        <div className="flex justify-center gap-2 mt-4">
          <span className="w-2 h-2 rounded-full bg-gray-400" />
          <span className="w-2 h-2 rounded-full bg-gray-400" />
          <span className="w-2 h-2 rounded-full bg-gray-400" />
        </div>
      </Card>

      <Button
        onClick={handleLaunch}
        className="w-full"
        size="lg"
      >
        Launch
      </Button>
    </div>
  )
}
```

---

## 4.3 Pipeline Viewer - Horizontal Flow (Priority: P0)

### 4.3.1 Visual Design - Horizontal Pipeline Layout

**Reference:** `docs/image/track-division.png` for track display at Stage 1

**Layout:** Pipeline flows horizontally from left to right
```
┌──────────────────────────────────────────────────────────────────────┐
│  ◀ Back              Innovation Pipeline          Company: Lactalis  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   │
│  │Stage 1 │ → │Stage 2 │ → │Stage 3 │ → │Stage 4 │ → │Stage 5 │   │
│  │Tracks  │   │Signals │   │Lessons │   │Context │   │Opport. │   │
│  │  ✓     │   │  ⏳    │   │  ⌛    │   │  ⌛    │   │  ⌛    │   │
│  └────────┘   └────────┘   └────────┘   └────────┘   └────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Current: Stage 2 - Signal Amplification                      │   │
│  │                                                               │   │
│  │ Extracting broader trends from selected inspiration tracks..│   │
│  │                                                               │   │
│  │ Progress: ████████████░░░░░ 75%      Est: 2 min remaining   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  Stage 1 Output (Completed):                                         │
│  ┌──────────────────────┐  ┌──────────────────────┐                │
│  │ Track 1 (Selected) ✓ │  │ Track 2 (Selected) ✓ │                │
│  │ [Track Icon]         │  │ [Track Icon]         │                │
│  │ Experience Theater   │  │ Community Building   │                │
│  │ Summary text...      │  │ Summary text...      │                │
│  └──────────────────────┘  └──────────────────────┘                │
└──────────────────────────────────────────────────────────────────────┘
```

### 4.3.2 Horizontal Pipeline Requirements

**FR-PV-1: Horizontal Stage Navigation**
- **Layout:** All 5 stages displayed in single horizontal row at top
- **Stage Boxes:** Each shows stage number, short name ("Tracks", "Signals", etc.), status icon
- **Active Stage:** Highlighted with border and pulse animation
- **Completed Stages:** Green checkmark (✓) indicator
- **Pending Stages:** Grayed out with hourglass icon (⌛)
- **Flow Direction:** Left-to-right with arrow connectors between stages

**FR-PV-2: Stage 1 - Track Division Display**
- **Reference:** Must match `docs/image/track-division.png` UI exactly
- **Display:** Show the 2 selected tracks from intermediary card
- **Track Cards:** Side-by-side layout matching track division design
- **Selection Indicator:** Both tracks shown with checkmark and "Selected" label
- **Data Source:** Read from `data/test-outputs/{run_id}/stage1/inspirations.json`:
  ```json
  {
    "selected_tracks": [1, 2],
    "track_1": {
      "title": "Track 1 Title",
      "summary": "Summary of first track...",
      "icon_url": ""
    },
    "track_2": {
      "title": "Track 2 Title",
      "summary": "Summary of second track...",
      "icon_url": ""
    },
    "completed_at": "2025-10-19T14:23:45.123Z"
  }
  ```

**FR-PV-3: Current Stage Detail Panel**
- **Position:** Below horizontal stage indicator row
- **Content:**
  - Stage name and full description
  - Progress bar showing estimated completion percentage
  - Status message (e.g., "Extracting trends from selected tracks...")
  - Estimated time remaining
- **Updates:** Refreshed every 5 seconds via polling

### 4.3.3 Stages 2-5: Horizontal Progress Indicators

**FR-PV-4: Horizontal Stage Boxes**
- **Layout:** All 5 stages in single horizontal row at page top
- **Each Stage Box:**
  - Stage number (1-5)
  - Short name ("Tracks", "Signals", "Lessons", "Context", "Opport.")
  - Status icon (✓ complete, ⏳ running, ⌛ pending)
- **Spacing:** Equal spacing with arrow/line connectors

**FR-PV-5: Stage Descriptions (Detail Panel)**
- **Stage 1:** "Track Division - Selected 2 inspiration tracks"
- **Stage 2:** "Signal Amplification - Extracting broader trends"
- **Stage 3:** "Universal Translation - Converting to brand-agnostic lessons"
- **Stage 4:** "Brand Contextualization - Applying to [Brand Name]"
- **Stage 5:** "Opportunity Generation - Creating 5 actionable innovations"

**FR-PV-6: Status Detection & Visual Updates**
- **Polling:** Call `/api/status/{run_id}` every 5 seconds
- **Visual States:**
  - Previous stages: Green checkmark (✓), solid background
  - Current stage: Animated pulse, progress bar in detail panel
  - Future stages: Grayed out, hourglass icon (⌛)
- **Transitions:** Smooth animation when stage completes (checkmark appears, next stage activates)

**FR-PV-7: Completion Action**
- When `current_stage === 5` and `status === "complete"`:
  - Final stage shows green checkmark
  - Detail panel shows "View Opportunities →" button
  - Button redirects to `/results/{run_id}`
  - Optional: Auto-redirect after 3 seconds with countdown

### 4.3.4 Technical Specifications

**Components:**
- `app/pipeline/[runId]/page.tsx` - Main pipeline viewer
- `components/InspirationTrack.tsx` - Stage 1 card component
- `components/StageBox.tsx` - Stages 2-5 status component

**API Polling:**
```typescript
useEffect(() => {
  const pollStatus = async () => {
    const response = await fetch(`/api/status/${runId}`)
    const data = await response.json()
    setStatus(data)

    // Continue polling if not complete
    if (data.status !== 'complete') {
      setTimeout(pollStatus, 5000)
    }
  }

  pollStatus()
}, [runId])
```

---

## 4.4 Results Page (Priority: P0)

### 4.4.1 Visual Design

**Layout:**
```
┌────────────────────────────────────────────────────────┐
│  ✓ Pipeline Complete - 5 Opportunities Generated      │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ Opportunity 1: [Title from markdown]         │    │
│  │                                               │    │
│  │ [Full markdown content rendered]             │    │
│  │                                               │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ Opportunity 2: [Title]                       │    │
│  │ ...                                          │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  [3 more opportunity cards]                           │
│                                                        │
│  [New Pipeline]  [Download All as PDF]               │
└────────────────────────────────────────────────────────┘
```

### 4.4.2 Functional Requirements

**FR-RS-1: Opportunity Display**
- Read 5 markdown files from `data/test-outputs/{run_id}/stage5/opportunity-{1-5}.md`
- Render each as a separate card using `react-markdown`
- Preserve markdown formatting (headings, lists, bold, etc.)

**FR-RS-2: Actions**
- **New Pipeline Button:** Redirect to `/` (homepage)
- **Download PDF Button:** (Phase 2 - Out of Scope) - Show as disabled for hackathon

**FR-RS-3: Error Handling**
- If opportunity files not found: Display error message
- If only some files exist: Display available opportunities + warning

### 4.4.3 Technical Specifications

**Component:**
- `app/results/[runId]/page.tsx` - Server component

**Data Loading:**
```typescript
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
      {opportunities.map(({ number, markdown }) => (
        <Card key={number} className="p-6 mb-6">
          <ReactMarkdown>{markdown}</ReactMarkdown>
        </Card>
      ))}
    </div>
  )
}
```

---

## 4.5 API Routes (Priority: P0)

### 4.5.1 POST /api/analyze-document

**Purpose:** Use LLM to extract summary and metadata from uploaded document

**Request:**
```typescript
{
  blob_url: string  // Vercel Blob URL
}
```

**Response:**
```typescript
{
  upload_id: string,
  analysis: {
    title: string,         // "Ad-generating QR codes incorporated into..."
    summary: string,       // "Most people only wear a fraction..."
    industry: string,      // "fashion"
    theme: string,         // "marketing strategies"
    sources: string[]      // ["trendwatching.com", "8 others"]
  },
  blob_url: string,
  analyzed_at: string
}
```

**Error Codes:**
- 400: Invalid blob URL
- 500: LLM analysis failed

**Implementation:**
```typescript
import { NextResponse } from 'next/server'
import { ChatOpenAI } from '@langchain/openai'
import { writeFile } from 'fs/promises'
import pdf from 'pdf-parse'

export async function POST(request: Request) {
  const { blob_url } = await request.json()
  const upload_id = `upload-${Date.now()}`

  // Download PDF from Blob
  const response = await fetch(blob_url)
  const buffer = await response.arrayBuffer()
  const tmpPath = `/tmp/${upload_id}.pdf`
  await writeFile(tmpPath, Buffer.from(buffer))

  // Extract text from PDF
  const dataBuffer = Buffer.from(buffer)
  const data = await pdf(dataBuffer)
  const fullText = data.text

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
3. The primary industry (single word: fashion, food, technology, healthcare, sports, etc.)
4. The main theme or topic (2-3 words: e.g. "marketing strategies", "sustainability", "customer experience")
5. Any identifiable sources mentioned in the document (e.g. website names, publications)

Document text (first 4000 characters):
${fullText.slice(0, 4000)}

Respond ONLY with valid JSON in this exact format:
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

### 4.5.2 POST /api/upload

**Purpose:** Upload file to Vercel Blob storage

**Request:**
```typescript
// multipart/form-data
{
  file: File // PDF, TXT, or MD file
}
```

**Response:**
```typescript
{
  blob_url: string,      // "https://blob.vercel-storage.com/..."
  file_name: string,     // "savannah-bananas.pdf"
  file_size: number,     // 1234567 (bytes)
  uploaded_at: string    // "2025-10-19T14:23:45.123Z"
}
```

**Error Codes:**
- 400: Invalid file type or size exceeded
- 500: Blob upload failed

**Implementation:**
```typescript
import { put } from '@vercel/blob'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const formData = await request.formData()
  const file = formData.get('file') as File

  // Validation
  const allowedTypes = ['application/pdf', 'text/plain', 'text/markdown']
  if (!allowedTypes.includes(file.type)) {
    return NextResponse.json(
      { error: 'Invalid file type' },
      { status: 400 }
    )
  }

  if (file.size > 25 * 1024 * 1024) { // 25MB
    return NextResponse.json(
      { error: 'File too large (max 25MB)' },
      { status: 400 }
    )
  }

  // Upload to Blob
  const blob = await put(`uploads/${Date.now()}-${file.name}`, file, {
    access: 'public',
  })

  const upload_id = `upload-${Date.now()}`

  return NextResponse.json({
    upload_id,
    blob_url: blob.url,
    file_name: file.name,
    file_size: file.size,
    uploaded_at: new Date().toISOString()
  })
}
```

### 4.5.3 POST /api/run

**Purpose:** Execute pipeline with uploaded file and brand selection

**Request:**
```typescript
{
  blob_url: string,  // Vercel Blob URL
  brand_id: string   // "lactalis-canada" | "mccormick-usa" | "decathlon" | "columbia-sportswear"
}
```

**Response:**
```typescript
{
  run_id: string,    // "run-1729349025123"
  status: "running"
}
```

**Error Codes:**
- 400: Missing blob_url or brand_id
- 404: Brand profile not found
- 500: Pipeline execution failed to start

**Implementation:**
```typescript
import { exec } from 'child_process'
import { NextResponse } from 'next/server'
import { writeFile } from 'fs/promises'
import path from 'path'

export async function POST(request: Request) {
  const { blob_url, brand_id } = await request.json()
  const run_id = `run-${Date.now()}`

  // Download PDF from Blob
  const response = await fetch(blob_url)
  const buffer = await response.arrayBuffer()
  const tmpPath = `/tmp/${run_id}.pdf`
  await writeFile(tmpPath, Buffer.from(buffer))

  // Execute pipeline in background
  const cwd = process.cwd()
  const command = `cd ${cwd} && python scripts/run_pipeline.py --input-file ${tmpPath} --brand ${brand_id} --run-id ${run_id}`

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Pipeline error for ${run_id}:`, error)
    }
  })

  return NextResponse.json({ run_id, status: 'running' })
}
```

### 4.5.4 GET /api/status/[runId]

**Purpose:** Get current pipeline execution status and stage data

**Request:** None (runId in URL)

**Response:**
```typescript
{
  run_id: string,              // "run-1729349025123"
  status: "running" | "complete" | "error",
  current_stage: 0 | 1 | 2 | 3 | 4 | 5,
  stage1_data?: {
    inspiration_1: {
      title: string,
      content: string,
      key_elements: string[]
    },
    inspiration_2: {
      title: string,
      content: string,
      key_elements: string[]
    },
    completed_at: string
  }
}
```

**Error Codes:**
- 404: Run ID not found or not started yet

**Implementation:**
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
      try {
        const jsonPath = `data/test-outputs/${runId}/stage1/inspirations.json`
        const jsonContent = await readFile(jsonPath, 'utf-8')
        stage1Data = JSON.parse(jsonContent)
      } catch {
        // Stage 1 not complete yet
      }
    }

    return NextResponse.json({
      run_id: runId,
      status: currentStage === 5 ? 'complete' : 'running',
      current_stage: currentStage,
      stage1_data: stage1Data,
    })
  } catch (error) {
    return NextResponse.json(
      { run_id: runId, status: 'error' },
      { status: 404 }
    )
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

---

## 4.6 Pipeline Modifications (Priority: P0)

### 4.6.1 scripts/run_pipeline.py Changes

**FR-PM-1: New CLI Arguments**

Add support for direct file input and run ID:

```python
parser.add_argument('--input-file', type=str, help='Direct PDF file path')
parser.add_argument('--run-id', type=str, help='Unique run identifier')
```

**FR-PM-2: New Execution Mode**

```python
def main():
    args = parse_arguments()

    # NEW: Web app execution mode
    if args.input_file and args.brand and args.run_id:
        run_from_uploaded_file(args.input_file, args.brand, args.run_id)
        sys.exit(0)

    # Existing CLI modes...
    if args.batch:
        run_batch_testing()
    elif args.input and args.brand:
        run_single_test(args.input, args.brand)

def run_from_uploaded_file(input_file_path: str, brand_id: str, run_id: str):
    """Execute pipeline from web-uploaded file."""

    # Create output directory with run_id
    output_dir = Path(f"data/test-outputs/{run_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup logging
    setup_pipeline_logging(output_dir)
    logger = logging.getLogger(__name__)
    logger.info(f"Starting pipeline for run_id: {run_id}")

    # Read PDF (add pypdf if needed)
    from pypdf import PdfReader
    reader = PdfReader(input_file_path)
    input_text = "".join(page.extract_text() for page in reader.pages)

    # Load brand data
    brand_profile = load_brand_profile(brand_id)
    research_data = load_research_data(brand_id)

    # Execute all 5 stages (UNCHANGED)
    logger.info("Starting Stage 1: Input Processing")
    stage1_chain = Stage1Chain()
    stage1_result = stage1_chain.run(input_text)
    stage1_output = stage1_result[stage1_chain.output_key]
    stage1_chain.save_output(stage1_output, output_dir)
    logger.info("Stage 1 execution completed")

    # Continue with stages 2-5...
```

### 4.6.2 pipeline/stages/stage1_input_processing.py Changes

**FR-PM-3: JSON Output for Two-Track UI**

Modify `save_output()` to generate both markdown and JSON:

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

    # Parse inspirations from LLM output
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
    """Extract 2 inspirations from LLM markdown output.

    Expected format:
    ## Track 1: [Title]
    [Content paragraph]

    **Key Elements:**
    - Element 1
    - Element 2

    ## Track 2: [Title]
    ...
    """
    import re

    # Extract Track 1
    track1_match = re.search(
        r'## Track 1: (.+?)\n\n(.+?)\n\n\*\*Key Elements:\*\*\n((?:- .+\n)+)',
        output,
        re.DOTALL
    )

    # Extract Track 2
    track2_match = re.search(
        r'## Track 2: (.+?)\n\n(.+?)\n\n\*\*Key Elements:\*\*\n((?:- .+\n)+)',
        output,
        re.DOTALL
    )

    if not track1_match or not track2_match:
        # Fallback if parsing fails
        return [
            {
                "title": "Inspiration Track 1",
                "content": "Unable to parse - see full markdown output",
                "key_elements": []
            },
            {
                "title": "Inspiration Track 2",
                "content": "Unable to parse - see full markdown output",
                "key_elements": []
            }
        ]

    return [
        {
            "title": track1_match.group(1).strip(),
            "content": track1_match.group(2).strip(),
            "key_elements": [
                line.strip('- ').strip()
                for line in track1_match.group(3).strip().split('\n')
            ]
        },
        {
            "title": track2_match.group(1).strip(),
            "content": track2_match.group(2).strip(),
            "key_elements": [
                line.strip('- ').strip()
                for line in track2_match.group(3).strip().split('\n')
            ]
        }
    ]
```

**FR-PM-4: Stage 1 Prompt Update**

Ensure LLM output follows parseable format for TOP 2 TRACKS ONLY:

```python
STAGE1_TEMPLATE = """
Analyze this innovation signal document and extract the TWO most compelling inspiration tracks.

IMPORTANT: Only extract the TOP 2 most impactful inspiration tracks. These will be displayed
in a horizontal pipeline UI and used for all subsequent analysis stages.

# Track 1: [Give it a descriptive title]

[Write 2-3 sentences summarizing the first main inspiration or pattern you identify]

# Track 2: [Give it a descriptive title]

[Write 2-3 sentences summarizing the second main inspiration or pattern you identify]

NOTE: The system will auto-select these top 2 tracks for the pipeline. Do not include
additional tracks beyond these two.

Input Document:
{input_text}
"""
```

---
