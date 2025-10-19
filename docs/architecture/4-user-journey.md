# 4. User Journey

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ ONBOARDING: Company Selection (Team-Led)                        │
│ - Team member selects target company from dropdown              │
│ - System loads brand profile from YAML files                    │
│   (/data/brand-profiles/{company-id}.yaml)                      │
│ - Company context saved to session/cookie                       │
│ - User redirected to landing page                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ LANDING PAGE: My Board of Ideators                              │
│ - Clean visual design with "My Board of Ideators" heading       │
│ - Circular pattern of colored circles                           │
│ - Central search/input bar for file upload or search            │
│ - Top navigation: Everything | Spaces | Serendipity             │
│ - User can upload file or browse existing boards                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ HOMEPAGE: Upload Only (Brand Pre-Selected)                      │
│ - Display selected company name at top (e.g. "Lactalis Canada") │
│ - Drag & drop PDF (trend report)                                │
│ - File uploads to Vercel Blob                                   │
│ - Redirect to intermediary card page                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ INTERMEDIARY CARD: Document Analysis (LLM-Powered)              │
│ - Extract PDF text content                                      │
│ - LLM analyzes document to generate:                            │
│   • Concise summary (2-3 sentences)                             │
│   • Industry identification                                     │
│   • Source attribution                                          │
│   • Theme/topic categorization                                  │
│ - Display in card format matching design reference              │
│ - Show "Launch" button to start pipeline                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ PIPELINE VIEWER: Real-time Execution                            │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Stage 1: Extracting Inspirations                            │ │
│ │ ┌─────────────────────┐  ┌─────────────────────┐           │ │
│ │ │ Inspiration Track 1 │  │ Inspiration Track 2 │           │ │
│ │ │ "Experience Theater"│  │ "Community Building"│           │ │
│ │ │ Loading...          │  │ Loading...          │           │ │
│ │ └─────────────────────┘  └─────────────────────┘           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Stage 2: Amplifying Signals                                 │ │
│ │ Status: Waiting...                                          │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Stage 3: Translating to Lessons                             │ │
│ │ Status: Pending                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Stage 4: Brand Contextualization                            │ │
│ │ Status: Pending                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Stage 5: Generating Opportunities                           │ │
│ │ Status: Pending                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ RESULTS: Opportunity Cards                                       │
│ - 5 opportunity cards (markdown rendered)                       │
│ - Download all as PDF                                           │
│ - Start new pipeline run                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Steps

### Step 0: Onboarding/Landing - Company Selection via Visual Interface (30 seconds, Team-Led)
1. Team member navigates to `/` (root - landing page/onboarding combined)
2. Sees "My Board of Ideators" page matching `docs/image/Landing-page.png` design
3. **Central input bar** displays placeholder: "Enter company name (Lactalis, Columbia, Decathlon, McCormick)"
4. User types company name into central search bar
5. System validates company name against available profiles
6. On valid entry, loads brand profile from `/data/brand-profiles/{company-id}.yaml`
7. Company ID saved to cookie/session storage
8. Redirect to upload page (`/upload`) with company context pre-loaded

**Why This Design?**
- **Clean, minimalist interface** - No dropdown clutter
- **Direct text input** - Faster than selecting from dropdown
- **Visual brand experience** - Colored circles create welcoming aesthetic
- **Team-controlled** - Company name is known, direct entry
- **Scalable** - Easy to add more companies without UI changes

**Design Elements:**
- **Title:** "My Board of Ideators" with "My" in teal italics
- **8 Colored Circles:** Arranged in circular pattern (teal, blue, yellow, orange)
- **Central Input Bar:** White rectangular input with company name placeholder
- **Top Navigation:** "Everything" | "Spaces" | "Serendipity" (visual only)
- **Background:** Light gray/off-white with subtle texture

### Step 1: Homepage - Upload Only (1-2 minutes)
1. User lands on homepage matching `docs/image/main-page.png` design
2. **Company name displayed at top** (e.g. "Lactalis Canada")
3. **"My Board of Ideators"** title with brand styling
4. **Upload sources** card with drag & drop zone
5. User drags PDF trend report → file uploads to Vercel Blob
6. **No brand selector visible** (already selected in onboarding)
7. After successful upload → redirect to `/analyze/[uploadId]`

### Step 2: Intermediary Card - Document Analysis (30-60 seconds)
1. Display loading state: "Analyzing document..."
2. Backend calls LLM to extract:
   - **Summary:** 2-3 sentence concise description of document content
   - **Industry:** Primary industry/sector identified (e.g. "fashion", "food & beverage", "sports")
   - **Source:** Document source if identifiable (e.g. "trendwatching.com")
   - **Theme:** Main topic or category (e.g. "marketing strategies", "sustainability")
3. Display extracted information in card format matching `docs/image/intermediary-card.png`:
   - Hero image placeholder
   - Title (generated from summary)
   - Source badges (e.g. "trendwatching.com", "8 others")
   - Industry badge (orange pill)
   - Theme badge (red pill)
   - Summary text
4. Show "Launch" button at bottom
5. Click "Launch" → POST to `/api/run` → redirect to `/pipeline/[runId]`

### Step 3: Pipeline Execution (15-30 minutes)
**Stage 1: Special UI (2 Inspiration Tracks)**
- Displays 2 side-by-side cards
- Each card shows inspiration title + loading animation
- When complete: Shows extracted inspiration text (~2-3 paragraphs each)

**Stages 2-5: Minimal Box UI**
- Each stage = single box with:
  - Stage number + name
  - Status: "Running..." → "Complete ✓"
  - High-level description (1 sentence)
- No detailed output shown until complete

**Progress Polling:**
- Frontend polls `/api/status/:runId` every 5 seconds
- Updates stage status based on log file parsing
- Shows completion checkmarks as stages finish

### Step 3: Results Display (2-3 minutes)
- All stages complete → shows 5 opportunity cards
- Each card rendered from markdown (frontmatter + content)
- "Download All" button exports as PDF
- "New Pipeline" button returns to homepage

---
