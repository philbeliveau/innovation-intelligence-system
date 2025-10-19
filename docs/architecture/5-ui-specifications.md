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
│            or Select a Starting Points                        │
│            (Story 1.4 - appears when upload history exists)  │
│                                                               │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│   │ 📄           │  │ 📄           │  │ 📄           │     │
│   │ Food & Bev   │  │ Food & Bev   │  │ Food & Bev   │     │
│   │ Sept 2025    │  │ Sept 2025    │  │ Sept 2025    │     │
│   │ SERENDIPITY  │  │ SERENDIPITY  │  │ SERENDIPITY  │     │
│   │ SEEKERS      │  │ SEEKERS      │  │ SEEKERS      │     │
│   │              │  │              │  │              │     │
│   │ report.pdf   │  │ trends.pdf   │  │ market.pdf   │     │
│   │ 2 hours ago  │  │ Yesterday    │  │ 3 days ago   │     │
│   └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

**After File Upload (Story 1.4 Behavior):**
```
┌──────────────────────────────────────────────────────────────┐
│              Company: Lactalis Canada 🏢                      │
│                                                               │
│   ✓ File uploaded: sustainable-packaging-2025.pdf             │
│   (User stays on page - no automatic redirect)               │
│                                                               │
│            or Select a Starting Points                        │
│                                                               │
│   [Upload history cards appear here - see above layout]      │
│   Click any card to navigate to /analyze/{uploadId}          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**shadcn/ui Components Used:**
- `Card` - Upload container + Upload history cards
- `Button` - Primary CTA
- `Badge` - File upload status + Company indicator
- Custom drag & drop zone (react-dropzone)

**Key Changes from Original Design:**
- ✅ No brand selector on homepage (moved to onboarding)
- ✅ Company name displayed at top-right corner
- ✅ Cleaner presentation for client demos
- ✅ **Story 1.4:** No automatic redirect after upload - user stays on page
- ✅ **Story 1.4:** Upload history cards appear dynamically below upload zone
- ✅ **Story 1.4:** Users can upload multiple documents in single session
- ✅ **Story 1.4:** Click history card to navigate to analysis page

---

## 5.2 Left Sidebar - Collapsible Home Menu with Ideation Tracks

**Hover Behavior:**
- Cursor moves to left edge → sidebar slides in (300ms transition)
- Shows home navigation and non-selected ideation track

**Layout:**
```
┌─────────────────────────────┐
│                             │
│   🏠 Home                   │
│                             │
│   Ideation Tracks           │
│   ┌───────────────────────┐ │
│   │ 2                     │ │
│   │ Track Title           │ │
│   │ Summary of this tra...│ │
│   └───────────────────────┘ │
│                             │
└─────────────────────────────┘
```

**Implementation:**
- Width: 240px (w-60) to accommodate track card
- Click "Home" → navigate to `/upload` (homepage)
- Collapsed by default (only visible on hover at left edge)
- Displays non-selected track from sessionStorage
- Track card shows: track number, title, truncated summary (100 chars)
- Dimmed styling (bg-gray-100, opacity-80)
- Allows user to return to upload page from any view
- Keeps context of non-selected track visible throughout pipeline

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
4. User selects exactly 1 track via radio button (Track 1 or Track 2)
5. Selected track displays with highlighted border/background (border-blue-500, bg-blue-50)
6. Non-selected track displays with dimmed appearance (opacity-60, border-gray-300)
7. User reviews selection and clicks "Launch"
8. Selected track data stored in sessionStorage for pipeline viewer
9. Non-selected track data stored in sessionStorage for sidebar display
10. Navigate to vertical pipeline viewer with selected track flowing downward
11. Non-selected track appears in left sidebar under "Ideation Tracks"

---

## 5.4 Pipeline Viewer - Vertical Flow Layout

**Reference:** `docs/image/track-division.png` for track UI at Stage 1

**Vertical Pipeline Layout:**

```
┌────────────────────────────────────────────────────────────────────────────┐
│  ◀ Back                  Innovation Pipeline             Company: Lactalis  │
├──┬─────────────────────────────────────────────────────────────────────────┤
│S │                                                                          │
│I │  ┌───────────────────────────────────────────────────────────────────┐  │
│D │  │ Stage 1 - Tracks                                              ✓  │  │
│E │  └───────────────────────────────────────────────────────────────────┘  │
│B │                                  ↓                                       │
│A │  ┌───────────────────────────────────────────────────────────────────┐  │
│R │  │ Stage 2 - Signals                                             ⏳ │  │
│  │  └───────────────────────────────────────────────────────────────────┘  │
│T │                                  ↓                                       │
│r │  ┌───────────────────────────────────────────────────────────────────┐  │
│a │  │ Stage 3 - Lessons                                             ⌛ │  │
│c │  └───────────────────────────────────────────────────────────────────┘  │
│k │                                  ↓                                       │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │
│2 │  │ Stage 4 - Context                                             ⌛ │  │
│  │  └───────────────────────────────────────────────────────────────────┘  │
│  │                                  ↓                                       │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  │ Stage 5 - Opportunities                                       ⌛ │  │
│  │  └───────────────────────────────────────────────────────────────────┘  │
│  │                                                                          │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  │ Current Stage: Stage 2 - Signal Amplification                     │  │
│  │  │                                                                    │  │
│  │  │ Extracting broader trends from selected inspiration track...      │  │
│  │  │                                                                    │  │
│  │  │ Progress: ████████████░░░░░ 75%     Est. time: 2 min remaining    │  │
│  │  └───────────────────────────────────────────────────────────────────┘  │
│  │                                                                          │
│  │  Stage 1 Output (Completed):                                            │
│  │  ┌──────────────────────────────────────────────┐                       │
│  │  │ Track 1 (Selected) ✓                         │                       │
│  │  │ [Track Icon/Image]                           │                       │
│  │  │ Experience Theater                           │                       │
│  │  │ Summary of this track...                     │                       │
│  │  │ More content about the selected track...     │                       │
│  │  └──────────────────────────────────────────────┘                       │
└──┴─────────────────────────────────────────────────────────────────────────┘
```

**Layout Features:**
1. **Left Sidebar:** Non-selected track displayed in collapsible sidebar (hover to reveal)
2. **Vertical Stage Column:** All 5 stages displayed in single vertical column flowing downward in main content area
3. **Active Stage Panel:** Below stages, shows current stage details and progress
4. **Completed Output:** Stage 1 shows only the selected track in main content area
5. **Flow Direction:** Top to bottom with downward arrow indicators between stages
6. **Track Division:** Stage 1 displays only the selected track (single card, not side-by-side)

**shadcn/ui Components:**
- `Card` - Stage boxes and track containers
- `Progress` - Progress bars for current stage
- `Badge` - Status indicators (✓, ⏳, ⌛)
- `Separator` - Between stages

---

## 5.5 Pipeline Viewer - Stages 2-5 (Vertical Progress)

**Vertical Stage Indicators:**

Each stage in the vertical column shows:
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
