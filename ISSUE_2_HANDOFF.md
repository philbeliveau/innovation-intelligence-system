# Issue #2 Handoff: Sparks Preview Column Empty During Stages 2-5

## Quick Summary
The Sparks Preview column (rightmost column in State 2) remains empty with skeleton loader during pipeline stages 2-5. It should show preview cards as sparks are generated.

## Root Cause
**Architecture mismatch between design and implementation:**
- **Mockup expectation:** Sparks appear incrementally during stages 2-5
- **Current implementation:** Backend generates all 5 sparks in batch at Stage 5 completion, saves atomically to database
- **Result:** Frontend has no intermediate data to display

## Location
- **Component:** `innovation-web/components/pipeline/PipelineStateMachine.tsx` lines 205-241
- **Backend:** Stage 5 generates all opportunities at once in `backend/pipeline/stages/stage5_opportunity_generation.py`

## Two Solution Options

### Option A: Frontend Placeholder Cards (Quick Fix - 1 hour)
**Add placeholder "generating" cards during stages 2-5:**

```typescript
// In PipelineStateMachine.tsx around line 237
const sparks = pipelineData.opportunityCards?.map((card) => ({
  number: card.number,
  title: card.title,
  summary: card.summary,
  heroImageUrl: undefined,
})) || []

// ADD THIS: Show placeholder cards when stage >= 2
const displaySparks = sparks.length > 0
  ? sparks
  : (currentStage >= 2 && currentStage < 5)
    ? Array.from({ length: 5 }, (_, i) => ({
        number: i + 1,
        title: "Generating spark...",
        summary: "Innovation opportunity being created based on your insights",
        heroImageUrl: undefined,
        isPlaceholder: true
      }))
    : []

return (
  <ThreeColumnLayout>
    {displaySparks.length > 0 ? (
      <SparksPreviewColumn sparks={displaySparks} isGenerating={currentStage < 5} />
    ) : (
      <SparksPreviewColumnSkeleton />
    )}
  </ThreeColumnLayout>
)
```

**Update `SparksPreviewColumn` to style placeholder cards differently (grayed out, pulsing animation).**

**Pros:** No backend changes, quick implementation, aligns with current batch architecture
**Cons:** Doesn't show actual spark titles during generation

### Option B: Backend Streaming (Proper Fix - 8-12 hours)
**Modify backend to generate and save sparks incrementally:**

1. Change Stage 5 to generate opportunities one-at-a-time
2. Save each opportunity to database immediately after generation
3. Send webhook for each card: `POST /api/pipeline/[runId]/opportunity-card` (singular)
4. Frontend polls and appends new cards as they arrive

**Pros:** Matches mockup design, better UX, more interactive
**Cons:** Significant backend refactor, changes pipeline architecture

## Recommendation
**Go with Option A (placeholder cards)** for now. It's fast, safe, and doesn't break the existing batch pipeline architecture. Option B can be revisited later if needed.

## Files to Modify (Option A)
1. `innovation-web/components/pipeline/PipelineStateMachine.tsx` - Add placeholder logic
2. `innovation-web/components/pipeline/SparksPreviewColumn.tsx` - Style placeholder cards with gray/pulsing effect

## Testing
After implementing, test:
1. Upload document and launch pipeline
2. When Stage 2 starts, verify 5 placeholder cards appear in Sparks column
3. Verify cards show "Generating spark..." text and pulsing animation
4. When Stage 5 completes, verify real cards replace placeholders
5. Verify no console errors

## Reference
- Full analysis: `EPIC8_CRITICAL_ISSUES_REPORT.md` lines 277-428
- Mockup: `docs/front-end-spec.md` page 5 (State 2 with spark previews)
