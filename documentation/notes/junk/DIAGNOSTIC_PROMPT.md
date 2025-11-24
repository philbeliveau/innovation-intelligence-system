# Epic 8 Pipeline Visualization Critical Issues - Diagnostic Investigation Required

## Context
The Innovation Intelligence System's frontend pipeline visualization (Epic 8) has been partially implemented but is experiencing multiple critical UI/UX and data flow issues. The user has provided screenshots showing specific problems at each stage of the pipeline execution flow.

## Your Mission
Investigate and fix **5 critical issues** affecting the pipeline visualization user experience. These issues span the entire user journey from document upload through pipeline completion.

---

## Issue 1: Missing Document Preview Card Before Launch
**Screenshot:** `/docs/stories/wrong.png`

**Current Behavior:**
- After uploading a document, user sees a centered card with:
  - Document filename: "sacred-sync-trend.pdf"
  - Text: "Ready to analyze this document with your Board of Ideators"
  - "Preview Document" button (white/outlined)
  - "Launch" button (black, below the card, centered)
- The card is centered on the page with large white space

**Expected Behavior (from Epic 8 spec):**
- Document preview card should appear on the LEFT side of the screen
- Launch button should be UNDER the card (integrated into the card UI)
- Card should show document metadata: filename, file size, upload date
- Card should remain visible on left AFTER launch (next to extraction animation)

**File to Investigate:**
- `/innovation-web/app/analyze/[uploadId]/page.tsx`
- Look for the pre-launch UI state (before `launching` or `isPipelineRunning` is true)
- Search for where the document card and Launch button are rendered
- Check CSS/Tailwind classes for centering vs left-aligned layout

**Hypothesis:**
- The pre-launch UI was never updated to match Epic 8 spec
- Card is using center-aligned flex/grid instead of left-side layout
- Launch button is outside the card instead of integrated

---

## Issue 2: Missing Document Card After Pipeline Launch
**Screenshot:** `/docs/stories/wrong2.png`

**Current Behavior:**
- State 1 shows two side-by-side boxes:
  - LEFT: Extraction animation (beaker/flask) - ✅ WORKING
  - RIGHT: Workflow illustration (document → gears → lightbulb) - ✅ WORKING
- Document preview card that WAS visible before launch has DISAPPEARED

**Expected Behavior (from Epic 8 spec):**
- Document preview card should REMAIN visible on the left
- Extraction animation should be NEXT TO the document card
- Layout should be: [Document Card | Extraction Animation | Workflow Illustration]
- Or: Document card overlays the left side, extraction animation is primary focus

**File to Investigate:**
- `/innovation-web/components/pipeline/PipelineStateMachine.tsx` (lines 163-179, State 1 rendering)
- `/innovation-web/app/analyze/[uploadId]/page.tsx` (check if card is conditionally hidden when pipeline runs)
- Look for `isPipelineRunning` or `launching` state that might hide the document card

**Hypothesis:**
- Document card is only shown in pre-launch state
- State 1 rendering doesn't include the document card component
- Conditional rendering hides card when `isPipelineRunning === true`

---

## Issue 3: State 2 Layout Collapse - Three-Column Boxes Pushed to Bottom
**Screenshot:** `/docs/image/issue/issue1.png`

**Current Behavior:**
- When Stage 2 completes, the three-column layout appears AT THE BOTTOM of the page
- Massive white space above the columns (entire viewport height)
- Only column headers visible: "Signals" and "Transferable Insights"
- Columns appear cut off at bottom of viewport

**Expected Behavior:**
- Three-column layout should fill the viewport from top to bottom
- No large white space above the columns
- Columns should be prominently displayed, taking full available height
- Layout: [Signals Column | Transferable Insights Column | Sparks Preview Column]

**File to Investigate:**
- `/innovation-web/components/pipeline/PipelineStateMachine.tsx` (lines 181-240, State 2 rendering)
- `/innovation-web/components/pipeline/ThreeColumnLayout.tsx`
- `/innovation-web/app/analyze/[uploadId]/page.tsx` (check parent container CSS)
- Look for CSS classes that might cause layout collapse: `absolute`, `fixed`, `bottom-0`, or missing `min-h-screen`

**Hypothesis:**
- FadeTransition component has positioning issue (absolute/fixed)
- Parent container has `space-y-4` or `space-y-6` causing vertical gap
- ThreeColumnLayout is missing `min-h-screen` or proper height constraints
- State 1 and State 2 are both rendering simultaneously, causing layout stacking

---

## Issue 4: Empty Column Content - No Data in State 2 Cards
**Related to Issue 3**

**Current Behavior:**
- State 2 three-column layout renders but appears empty
- Column headers show ("Signals", "Transferable Insights") but no content inside
- User reports "no info appearing on the actual cards"

**Expected Behavior:**
- **Signals Column:** Should show trend title, optional trend image, and extracted signal data
- **Transferable Insights Column:** Should show core mechanism, business impact, pattern transfers
- **Sparks Preview Column:** Should show generating state OR partial spark cards (if Stage 5 started)

**File to Investigate:**
- `/innovation-web/components/pipeline/PipelineStateMachine.tsx` (lines 185-238, data parsing logic)
- `/innovation-web/components/pipeline/SignalsColumn.tsx`
- `/innovation-web/components/pipeline/TransferableInsightsColumn.tsx`
- `/innovation-web/components/pipeline/SparksPreviewColumn.tsx`
- Check what props are being passed to each column component
- Verify `hasStage1Data` is evaluating to `true`
- Check if column components are receiving empty strings/undefined values

**Recent Fix Attempted:**
- Changed from `stage1Data ? <Column /> : <Skeleton />` to `hasStage1Data ? <Column /> : <Skeleton />`
- Added fallback mapping: `stage1Data?.inspiration_1_title || 'Analyzing Document Signal...'`
- Still showing skeletons or empty content

**Hypothesis:**
- Skeleton loaders are still rendering instead of actual columns
- `hasStage1Data` is evaluating to `false` even when data exists
- Column components are receiving props but not rendering them
- CSS issue hiding the content (white text on white background, overflow hidden, etc.)

---

## Issue 5: No Opportunity Cards at Pipeline Completion (State 3 Never Appears)
**Screenshot:** `/docs/image/issue/no-cards.png`

**Current Behavior:**
- Pipeline completes (URL: `http://localhost:3001/analyze/upload-1761681438836`)
- Page shows blank white screen with:
  - "My Board of Ideators" header at top
  - "Download All (0)" button (bottom left) - showing 0 cards
  - "New Pipeline" button (bottom right)
  - NO opportunity cards/sparks grid visible
  - Completely empty middle section

**Expected Behavior (State 3):**
- When pipeline completes, State 3 (Sparks Grid) should render
- Should show:
  - Icon navigation at top (Signals, Insights, Sparks icons with "Sparks" active)
  - 2-column grid of spark cards (numbered overlays #1, #2, #3, etc.)
  - Each card shows: number, title, summary, optional hero image
  - Download All and New Pipeline buttons at bottom
- If NO cards were generated, should show error message or empty state

**File to Investigate:**
- `/innovation-web/components/pipeline/PipelineStateMachine.tsx` (lines 240-260, State 3 rendering)
- `/innovation-web/components/pipeline/SparksGrid.tsx`
- `/innovation-web/app/api/pipeline/[runId]/opportunity-cards/route.ts` (check if endpoint returns cards)
- `/innovation-web/app/analyze/[uploadId]/page.tsx` (check if `opportunityCards` state is populated)
- Backend: `/backend/app/routes.py` and `/backend/app/pipeline_runner.py` (verify cards are being saved)

**Diagnostic Steps:**
1. Check browser console for errors when pipeline completes
2. Check Network tab: Does `/api/pipeline/[runId]/opportunity-cards` return data?
3. Check Prisma database: Are OpportunityCard records created for this runId?
4. Check backend logs: Did Stage 5 complete successfully? Did it call the complete webhook?
5. Check `pipelineData.opportunityCards` in PipelineViewer state
6. Check if State 3 condition is met: `status === 'COMPLETED' && !selectedCardId`

**Hypothesis:**
- Opportunity cards are not being saved to database (Stage 5 issue or webhook issue)
- Frontend is not fetching opportunity cards correctly
- State machine is not transitioning to State 3 (still stuck in State 2)
- `status` is not being set to 'COMPLETED' properly
- `opportunityCards` array is empty, and SparksGrid doesn't handle empty state

---

## System Architecture Context

**Tech Stack:**
- Next.js 15.5.6 with App Router
- TypeScript strict mode
- React 19.0.0
- Tailwind CSS + shadcn/ui components
- Prisma ORM with PostgreSQL database
- Python FastAPI backend on Railway
- Webhook-based state updates

**Key Files:**
- `/innovation-web/app/analyze/[uploadId]/page.tsx` - Main page component
- `/innovation-web/components/pipeline/PipelineViewer.tsx` - Wrapper component with polling logic
- `/innovation-web/components/pipeline/PipelineStateMachine.tsx` - 4-state orchestrator
- `/innovation-web/app/api/pipeline/[runId]/status/route.ts` - Status endpoint
- `/innovation-web/app/api/pipeline/[runId]/opportunity-cards/route.ts` - Cards endpoint
- `/backend/app/pipeline_runner.py` - Python pipeline executor
- `/backend/app/routes.py` - Backend API endpoints

**State Machine Logic:**
```typescript
function determineCurrentState(currentStage: number, status: PipelineStatus, selectedCardId: string | null): PipelineState {
  if (status === 'COMPLETED' && selectedCardId !== null && selectedCardId !== undefined) {
    return PipelineState.State4 // Detail view
  }
  if (status === 'COMPLETED') {
    return PipelineState.State3 // Grid view
  }
  if (currentStage >= 2 && status === 'PROCESSING') {
    return PipelineState.State2 // 3-column progress
  }
  return PipelineState.State1 // Extraction animation
}
```

**Polling Logic:**
- PipelineViewer polls `/api/pipeline/[runId]/status` every 5 seconds
- On first poll, waits 2 seconds before starting (allow backend to initialize)
- Updates `currentStage`, `status`, `pipelineStages`, `opportunityCards` state
- Continues polling until `status === 'completed'`
- Auto-redirect to `/results` was REMOVED in last commit (706f0f7)

---

## Debugging Protocol

For each issue, follow this systematic approach:

### 1. Console Investigation
```bash
# Open browser DevTools Console
# Look for errors, warnings, or relevant log messages
# Search for: "Pipeline", "Stage", "State", "opportunity", "cards"
```

### 2. Network Tab Analysis
```bash
# Check these requests:
- POST /api/blob/upload (document upload)
- POST /api/analyze (pipeline launch)
- GET /api/pipeline/[runId]/status (polling)
- GET /api/pipeline/[runId]/opportunity-cards (on completion)
# Verify response status codes and payloads
```

### 3. React DevTools
```bash
# Inspect component tree
# Check PipelineViewer state: status, currentStage, opportunityCards
# Check PipelineStateMachine props: currentState, pipelineData
# Verify conditional rendering logic
```

### 4. Database Verification
```bash
# Use Prisma Studio or direct SQL query
SELECT * FROM "PipelineRun" WHERE id = '[runId]';
SELECT * FROM "StageOutput" WHERE "runId" = '[runId]' ORDER BY "stageNumber";
SELECT * FROM "OpportunityCard" WHERE "runId" = '[runId]' ORDER BY number;
```

### 5. Backend Logs
```bash
# Check Railway logs for backend
railway logs
# Look for: Stage completion messages, webhook calls, errors
```

---

## Expected Deliverables

1. **Root Cause Analysis** for each of the 5 issues
2. **Code Fixes** with clear explanations
3. **Testing Verification** showing before/after behavior
4. **Commit Message** following project conventions

---

## Important Notes

- Do NOT implement new features - fix existing broken functionality only
- Do NOT refactor unrelated code
- Do NOT change the 4-state architecture (State 1-4)
- DO verify fixes with actual pipeline execution (upload → launch → completion)
- DO check both frontend AND backend if data flow is involved
- DO update this diagnostic document with findings

---

## Recent Changes (Context)

**Commit 706f0f7 (2 hours ago):**
- Removed auto-redirect to `/results` page on completion
- Fixed State 2 data parsing (added fallback mappings)
- Changed `stage1Data` check to `hasStage1Data`

**Known Working:**
- State 1 extraction animation ✅
- State 1 workflow illustration ✅
- Document upload flow ✅
- Pipeline launch (backend execution) ✅

**Known Broken:**
- Pre-launch document card layout ❌
- Post-launch document card visibility ❌
- State 2 layout positioning ❌
- State 2 column content rendering ❌
- State 3 opportunity cards display ❌

---

## Success Criteria

All 5 issues resolved when:

1. ✅ Document card appears on LEFT before launch with integrated Launch button
2. ✅ Document card REMAINS visible on left during State 1 (next to extraction animation)
3. ✅ State 2 three-column layout fills viewport with no white space above
4. ✅ State 2 columns show actual content (trend title, mechanisms, insights)
5. ✅ State 3 displays opportunity cards grid after pipeline completion

User should be able to:
- Upload document → see left-aligned preview card with Launch button
- Click Launch → card stays visible, extraction animation starts on right
- See State 1 → State 2 transition smoothly with three-column layout filling screen
- See Stage 2-5 data populate in the three columns in real-time
- See State 3 sparks grid appear when pipeline completes with "Download All (5)" showing count

**End of Diagnostic Prompt**
