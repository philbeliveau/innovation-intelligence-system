# 5. UI Specifications

## 5.0 Onboarding/Landing Page - Company Selection

**Reference:** `docs/image/Landing-page.png`

**Purpose:** Combined onboarding and landing page where users enter company name to access their board

**Layout:**
```
┌──────────────────────────────────────────────────────────────┐
│                                    [Everything] [Spaces] [Serendipity]
│                                                               │
│                  ●  (teal)                                   │
│                                                               │
│         ●  (blue)                      ●  (yellow)           │
│                                                               │
│                                                               │
│    ●  (orange)     My Board of Ideators    ●  (orange)       │
│                                                               │
│                  ┌────────────────────────────────────┐      │
│                  │  Lactalis, Columbia, Decathlon...  │      │
│                  │  (Type company name)               │      │
│                  └────────────────────────────────────┘      │
│                                                               │
│         ●  (yellow)                    ●  (blue)             │
│                                                               │
│                  ●  (teal)                                   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Visual Elements:**
- **Title:** "My Board of Ideators" with "My" in teal/green italics
- **Colored Circles:** 8 circles in circular arrangement (teal, blue, yellow, orange)
- **Central Input:** White rectangular text input with placeholder text
  - Placeholder: "Lactalis, Columbia, Decathlon, McCormick..."
  - On focus: Placeholder text fades
- **Top Navigation:** Three tabs aligned to right (Everything, Spaces, Serendipity)
- **Background:** Light gray/off-white with subtle texture

**Interactions:**
- **Type company name** → Validates against available companies
- **Press Enter or blur** → If valid, loads company profile and redirects to `/upload`
- **Invalid company** → Show error message below input
- **Hover over circles** → Optional: Slight scale/glow effect
- **Navigation tabs** → Visual only (Phase 1)

**Validation Logic:**
- Accepts: "Lactalis", "Columbia", "Decathlon", "McCormick" (case-insensitive)
- Maps to: `lactalis-canada`, `columbia-sportswear`, `decathlon`, `mccormick-usa`
- Loads corresponding YAML from `/data/brand-profiles/{company-id}.yaml`

**shadcn/ui Components Used:**
- `Tabs` - Top navigation
- `Input` - Central company name input
- Custom SVG circles or div elements for colored dots

---

## 5.1 Homepage Design

**Reference:** `docs/image/main-page.png`

**Layout:**
```
┌──────────────────────────────────────────────────────────────┐
│              Company: Lactalis Canada 🏢                      │
│                 (top-right corner, subtle)                    │
│                                                               │
│                   My Board of Ideators                        │
│                   (centered, large heading)                   │
│                                                               │
│   ┌───────────────────────────────────────────────────────┐  │
│   │              📤 Upload sources                         │  │
│   │                                                        │  │
│   │      Drag & drop or choose file to upload             │  │
│   │                                                        │  │
│   │   Supported file types: PDF, .txt, Markdown, Audio    │  │
│   │   Trend Report, Article, etc.                         │  │
│   │                                                        │  │
│   │   ┌──────────────┐  ┌──────────────┐                 │  │
│   │   │  🔗 Link     │  │  📋 Paste    │                 │  │
│   │   │  Website     │  │  Copied text │                 │  │
│   │   │  YouTube     │  │              │                 │  │
│   │   └──────────────┘  └──────────────┘                 │  │
│   └───────────────────────────────────────────────────────┘  │
│                                                               │
│            or Select a Starting Point                         │
│                                                               │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│   │ Food & Bev   │  │ Food & Bev   │  │ Food & Bev   │     │
│   │ Sept 2025    │  │ Sept 2025    │  │ Sept 2025    │     │
│   │ SERENDIPITY  │  │ SERENDIPITY  │  │ SERENDIPITY  │     │
│   │ SEEKERS      │  │ SEEKERS      │  │ SEEKERS      │     │
│   └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

**After File Upload:**
```
┌──────────────────────────────────────────────────────────────┐
│              Company: Lactalis Canada 🏢                      │
│                                                               │
│   ✓ File uploaded: sustainable-packaging-2025.pdf             │
│                                                               │
│   [Generate Opportunities →]                                  │
│   (no brand selector - already set in onboarding)            │
└──────────────────────────────────────────────────────────────┘
```

**shadcn/ui Components Used:**
- `Card` - Upload container
- `Button` - Primary CTA
- `Badge` - File upload status + Company indicator
- Custom drag & drop zone (react-dropzone)

**Key Changes from Original Design:**
- ✅ No brand selector on homepage (moved to onboarding)
- ✅ Company name displayed at top-right corner
- ✅ Cleaner presentation for client demos

---

## 5.2 Left Sidebar - Collapsible Home Menu

**Hover Behavior:**
- Cursor moves to left edge → sidebar slides in (300ms transition)
- Shows minimal menu with home navigation

**Layout:**
```
┌─────────────────┐
│                 │
│   🏠 Home       │
│                 │
│                 │
└─────────────────┘
```

**Implementation:**
- Click "Home" → navigate to `/` (homepage)
- Collapsed by default (only visible on hover at left edge)
- Allows user to return to upload page from any view

---

## 5.3 Intermediary Card - Document Analysis Page with Track Division

**Reference:** `docs/image/intermediary-card.png` and `docs/image/track-division.png`

**Purpose:** Display LLM-extracted document summary with ideation track selection before launching pipeline

**Layout:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          My Board of Ideators                               │
│                                                                              │
│  Left: Document Summary                 Right: Ideation Tracks              │
│  ┌─────────────────────────────┐       ┌──────────────────────────┐        │
│  │                              │       │ Track 1: ✓ (Selected)   │        │
│  │  [Hero Image Placeholder]   │       │ [Track Icon]             │        │
│  │                              │       │ Summary of this track.   │        │
│  │  Ad-generating QR codes...  │       │ Summary of this track.   │        │
│  │                              │       │ Summary of this track.   │        │
│  │  Source: [trendwatching.com]│       └──────────────────────────┘        │
│  │  Industry: [fashion]         │       ┌──────────────────────────┐        │
│  │  Theme: [marketing]          │       │ Track 2: ✓ (Selected)   │        │
│  │                              │       │ [Track Icon]             │        │
│  │  Most people only wear...   │       │ Summary of this track.   │        │
│  │                              │       │ Summary of this track.   │        │
│  │          • • •               │       └──────────────────────────┘        │
│  └─────────────────────────────┘                                            │
│                                                                              │
│                              [Launch]                                        │
│                    (Start pipeline with top 2 tracks)                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. After file upload, call `/api/analyze-document` with blob URL
2. LLM extracts structured data from document AND identifies 2 key ideation tracks
3. Display document card (left) + track division showing 2 tracks (right)
4. Both tracks displayed as selected (matching `track-division.png` UI)
5. User reviews and clicks "Launch"
6. Navigate to horizontal pipeline viewer with selected tracks

---

## 5.4 Pipeline Viewer - Horizontal Flow Layout

**Reference:** `docs/image/track-division.png` for track UI at Stage 1

**Horizontal Pipeline Layout:**

```
┌────────────────────────────────────────────────────────────────────────────┐
│  ◀ Back                  Innovation Pipeline             Company: Lactalis  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────┐
│  │ Stage 1  │ →  │ Stage 2  │ →  │ Stage 3  │ →  │ Stage 4  │ →  │Stage 5│
│  │ Tracks   │    │ Signals  │    │ Lessons  │    │ Context  │    │Opport.│
│  │   ✓      │    │   ⏳     │    │   ⌛     │    │   ⌛     │    │  ⌛   │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘    └───────┘
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Current Stage: Stage 2 - Signal Amplification                        │  │
│  │                                                                       │  │
│  │ Extracting broader trends from selected inspiration tracks...        │  │
│  │                                                                       │  │
│  │ Progress: ████████████░░░░░ 75%        Est. time: 2 min remaining   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Stage 1 Output (Completed):                                               │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐         │
│  │ Track 1 (Selected) ✓        │  │ Track 2 (Selected) ✓        │         │
│  │ [Track Icon/Image]          │  │ [Track Icon/Image]          │         │
│  │ Experience Theater          │  │ Community Building          │         │
│  │ Summary of this track...    │  │ Summary of this track...    │         │
│  └─────────────────────────────┘  └─────────────────────────────┘         │
└────────────────────────────────────────────────────────────────────────────┘
```

**Layout Features:**
1. **Horizontal Stage Row:** All 5 stages displayed in single horizontal row at top
2. **Active Stage Panel:** Below stages, shows current stage details and progress
3. **Completed Output:** Previous stage outputs shown below (e.g., Stage 1 tracks)
4. **Flow Direction:** Left to right with arrow indicators between stages
5. **Track Division:** Stage 1 displays the 2 selected tracks matching `track-division.png` UI

**shadcn/ui Components:**
- `Card` - Stage boxes and track containers
- `Progress` - Progress bars for current stage
- `Badge` - Status indicators (✓, ⏳, ⌛)
- `Separator` - Between stages

---

## 5.5 Pipeline Viewer - Stages 2-5 (Horizontal Progress)

**Horizontal Stage Indicators:**

Each stage in the horizontal row shows:
- Stage number (1-5)
- Short name
- Status icon

**Current Stage Detail Panel:**

```
┌──────────────────────────────────────────────────────────────┐
│ Stage 2: Signal Amplification                                 │
│                                                               │
│ Extracting broader trends from inspiration patterns          │
│                                                               │
│ ⏳ Running... (estimated 4-6 minutes)                         │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Stage 3: Universal Translation                                │
│                                                               │
│ Converting insights into brand-agnostic lessons               │
│                                                               │
│ ⌛ Pending                                                    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Stage 4: Brand Contextualization                              │
│                                                               │
│ Applying lessons to Lactalis Canada                          │
│                                                               │
│ ⌛ Pending                                                    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Stage 5: Opportunity Generation                               │
│                                                               │
│ Creating 5 actionable innovation opportunities                │
│                                                               │
│ ⌛ Pending                                                    │
└──────────────────────────────────────────────────────────────┘
```

**Status Icons:**
- ⌛ Pending (gray)
- ⏳ Running... (blue, animated spinner)
- ✓ Complete (green checkmark)

**When Complete:**
- Box turns green background
- Shows completion time: "Completed in 4m 23s"
- Next stage automatically starts

---

## 5.6 Results Page

**5 Opportunity Cards:**

```
┌──────────────────────────────────────────────────────────────┐
│ ✓ Pipeline Complete - 5 Opportunities Generated               │
│                                                               │
│ [Download All as PDF]  [Start New Pipeline]                  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Opportunity #1: Plant-Based Dairy Theater                     │
│                                                               │
│ Strategic Rationale                                           │
│ Lactalis can leverage experience theater principles...       │
│                                                               │
│ Implementation Approach                                       │
│ • Partner with local theaters for product launches           │
│ • Create immersive tasting experiences                       │
│ • Integrate social media sharing moments                     │
│                                                               │
│ Success Metrics                                               │
│ • 20% increase in event participation                        │
│ • 15% social media engagement lift                          │
│                                                               │
│ Timeline: 6-12 months  |  Investment: $500K-$1M              │
└──────────────────────────────────────────────────────────────┘

(4 more cards...)
```

**shadcn/ui Components:**
- `Card` - Opportunity containers
- `Accordion` - Collapsible sections
- `Button` - Download/New actions
- `Badge` - Timeline/Investment tags

---
