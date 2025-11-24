# Agent Prompt: Diagnose PipelineStateMachine Rendering Failure

## Context

I am working on Epic 8 - Pipeline Visualization Refactor for a Next.js 15 application. The goal is to replace the old `DetailPanel` component with a new `PipelineStateMachine` component that shows 4 progressive UI states.

**Current Problem:** Despite making code changes to render `PipelineStateMachine`, the UI still shows the OLD interface with vertical stage boxes (see `/Users/philippebeliveau/Desktop/Notebook/innovation-intelligence-system/docs/stories/stages.png`).

## What Has Been Done

### Changes Made to `/app/pipeline/[runId]/page.tsx`:

1. **Removed feature flag** - Changed from:
   ```typescript
   {process.env.NEXT_PUBLIC_NEW_PIPELINE_UI === 'true' ? (
     <PipelineStateMachine ... />
   ) : (
     <DetailPanel ... />
   )}
   ```
   To:
   ```typescript
   <PipelineStateMachine
     currentStage={currentStage}
     status={status === 'completed' ? 'COMPLETED' : status === 'running' ? 'PROCESSING' : 'FAILED'}
     pipelineData={{
       runId,
       stages: pipelineStages,
       opportunityCards,
       brandName,
     }}
   />
   ```

2. **Removed DetailPanel import** - Line 11 no longer imports `DetailPanel`

3. **Added state for pipeline data**:
   ```typescript
   const [pipelineStages, setPipelineStages] = useState<Array<{ stageNumber: number; output?: string }>>([])
   const [opportunityCards, setOpportunityCards] = useState<Array<any>>([])
   ```

4. **Fetch real data from API** - Lines 118-138 parse stages and fetch opportunity cards

5. **Dev server is running** - http://localhost:3000 with Turbopack hot reload
6. **No build errors** - Next.js compiled successfully
7. **Pipeline is starting** - Backend is processing `run-1761680076456-6593`

## The Problem

**Expected:** When navigating to `/pipeline/[runId]`, should see NEW UI from `PipelineStateMachine`:
- State 1: Extraction animation + workflow illustration (2 boxes side-by-side)
- State 2: Three-column layout (signals → insights → sparks)
- State 3: Sparks grid view
- State 4: Detail view with collapsed sidebar

**Actual:** Still seeing OLD UI with:
- Vertical "Pipeline Stages" boxes (Stage 1: Tracks, Stage 2: Signals, etc.)
- Traditional layout with left sidebar
- No state-based progressive UI

## Key Files

### Component to Debug:
- **Main page:** `/Users/philippebeliveau/Desktop/Notebook/innovation-intelligence-system/innovation-web/app/pipeline/[runId]/page.tsx`
- **State machine:** `/Users/philippebeliveau/Desktop/Notebook/innovation-intelligence-system/innovation-web/components/pipeline/PipelineStateMachine.tsx`

### Component Dependencies:
```
PipelineStateMachine imports:
- ExtractionAnimation
- WorkflowIllustration
- ThreeColumnLayout
- SignalsColumn
- TransferableInsightsColumn
- SparksPreviewColumn
- SparksGrid
- CollapsedSidebar
- ExpandedSparkDetail
- FadeTransition
- StateAnnouncer
```

### Type Definitions:
- `/Users/philippebeliveau/Desktop/Notebook/innovation-intelligence-system/innovation-web/types/pipeline-state.ts`

## Hypotheses to Test

### 1. **Component Not Rendering (Most Likely)**
- PipelineStateMachine exists in JSX but returns null or empty
- Conditional logic inside PipelineStateMachine preventing render
- TypeScript errors causing silent failures

### 2. **Import/Module Issues**
- PipelineStateMachine not properly exported
- Circular dependency preventing load
- Missing dependency causing component to fail

### 3. **CSS/Layout Issue**
- Component IS rendering but hidden by CSS
- z-index or positioning issues
- Old UI overlaying new UI

### 4. **Data Shape Mismatch**
- pipelineData props not matching expected interface
- currentStage or status values causing early returns
- Empty arrays causing "no data" fallback

### 5. **Browser Cache**
- Old bundle cached in browser
- Service worker serving stale version
- Next.js Turbopack not hot-reloading properly

## Diagnostic Tasks

### Phase 1: Verify Component is Mounted
1. **Add console.log to PipelineStateMachine top level**:
   ```typescript
   export default function PipelineStateMachine({ currentStage, status, pipelineData }) {
     console.log('🎯 PipelineStateMachine MOUNTED', { currentStage, status, pipelineData })
     // ... rest of code
   ```

2. **Check browser console** - Navigate to `/pipeline/run-1761680076456-6593` and check:
   - Does "🎯 PipelineStateMachine MOUNTED" appear?
   - What are the prop values?
   - Any React errors in console?

3. **Check Network tab** - Look for:
   - 404s for component files
   - Failed module loads
   - API calls to `/api/pipeline/[runId]/status`

### Phase 2: Inspect Render Output
4. **Check React DevTools**:
   - Is `PipelineStateMachine` in component tree?
   - What state does `determineCurrentState()` return?
   - Are child components (ExtractionAnimation, etc.) present?

5. **Check DOM Inspector**:
   - Search for `data-testid="state-1"` in DOM
   - Is the component rendered but hidden?
   - What CSS is applied?

### Phase 3: Check Component Logic
6. **Review determineCurrentState function** (lines 44-59 in PipelineStateMachine.tsx):
   ```typescript
   const determineCurrentState = (
     currentStage: number,
     status: PipelineStatus,
     selectedCardId: string | null | undefined
   ): PipelineState => {
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
   - What state is being returned?
   - Are the conditionals matching expected values?

7. **Check FadeTransition visibility** (lines 164-179):
   ```typescript
   <FadeTransition isVisible={currentState === PipelineState.State1}>
     <div data-testid="state-1">
       {/* Extraction animation boxes */}
     </div>
   </FadeTransition>
   ```
   - Is `isVisible` prop true for current state?
   - Does FadeTransition have `display: none` when not visible?

### Phase 4: Check Data Flow
8. **Verify API response shape**:
   - Open browser DevTools → Network
   - Find request to `/api/pipeline/run-1761680076456-6593/status`
   - Check response JSON structure:
     - Does it have `current_stage`?
     - Does it have `status`?
     - Does it have `stages` object?

9. **Check state updates in page.tsx**:
   - Add console.log after line 102: `console.log('📊 Status update:', data)`
   - Add console.log after line 124: `console.log('📦 Stages array:', stagesArray)`
   - Verify state is being set correctly

### Phase 5: Nuclear Options
10. **Hard refresh browser** - Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
11. **Clear Next.js cache** - `rm -rf .next && npm run dev`
12. **Restart dev server** - Kill all processes and restart
13. **Check for competing components** - Search page.tsx for other render paths

## Expected Outcomes

### If Component IS Mounting:
- You'll see console.logs from PipelineStateMachine
- Component will be in React DevTools tree
- Issue is likely conditional logic or CSS

### If Component NOT Mounting:
- No console.logs appear
- Component missing from React tree
- Issue is likely import/module error or TypeScript failure

## Success Criteria

**Diagnostic is complete when you can answer:**
1. ✅ Is PipelineStateMachine mounting? (Yes/No)
2. ✅ What is the current state value? (State1/State2/State3/State4)
3. ✅ Are child components rendering? (ExtractionAnimation, etc.)
4. ✅ What is preventing the new UI from displaying?

## Additional Context

- **Project root:** `/Users/philippebeliveau/Desktop/Notebook/innovation-intelligence-system/innovation-web`
- **Story file:** `/Users/philippebeliveau/Desktop/Notebook/innovation-intelligence-system/docs/stories/8.6.state-transition-animations.md`
- **Spec file:** `/Users/philippebeliveau/Desktop/Notebook/innovation-intelligence-system/docs/front-end-spec.md`
- **Dev server:** http://localhost:3000
- **Current run ID:** `run-1761680076456-6593`

## Tools Available

- Chrome/Firefox DevTools
- React DevTools extension
- VS Code debugger
- Next.js error overlay
- Console.log debugging
- Browser Network inspector

## Request to Agent

**Please systematically work through Phases 1-5 to identify why PipelineStateMachine is not displaying.**

Prioritize:
1. Component mounting verification (Phase 1)
2. Render output inspection (Phase 2)
3. Conditional logic debugging (Phase 3)

**Document all findings and provide a root cause analysis with specific fix recommendation.**
