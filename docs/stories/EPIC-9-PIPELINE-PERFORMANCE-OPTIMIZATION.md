# EPIC 9: Pipeline Performance Optimization

**Epic Owner:** Product Manager
**Architect:** Winston
**Created:** 2025-10-28
**Target:** Reduce pipeline execution time from 90-130s to 18-40s with real-time user feedback

---

## Epic Overview

The current 5-stage Innovation Intelligence Pipeline takes 90-130 seconds to complete with zero user feedback during execution. Users experience this as a "black box" where they upload a document and wait nearly 2 minutes with no indication of progress.

This epic addresses both **actual performance** (reduce wall-clock time) and **perceived performance** (provide real-time feedback) through 4 optimization tracks.

---

## Business Value

- **User Experience:** 70-80% improvement in perceived speed through real-time streaming
- **Operational Efficiency:** 50-70% reduction in actual pipeline execution time
- **Competitive Advantage:** Industry-leading response times for AI-powered innovation analysis
- **Cost Optimization:** 30-40% reduction in LLM API costs through parallel execution and token reduction

---

## Current State Analysis

### Pipeline Architecture
```
Stage 1 (12-18s) → Stage 2 (15-22s) → Stage 3 (18-25s) → Stage 4 (20-30s) → Stage 5 (22-35s)
Total: 87-130 seconds sequential execution
```

### Technical Bottlenecks
1. **Sequential Execution:** Stages run one-at-a-time despite some having no dependencies
2. **No Streaming:** Users see zero feedback until all 5 stages complete
3. **Suboptimal LLM Provider:** DeepSeek Chat is cost-effective but slower than alternatives
4. **Excessive Token Generation:** 17,000 total tokens requested across stages (some unnecessary)

### User Pain Points
- "Is it broken?" - No feedback during 90+ second wait
- "Should I refresh?" - Uncertainty about pipeline progress
- "Too slow for iteration" - Cannot rapidly test multiple documents

---

## User Stories for PM to Write

### Story 9.2: Parallel Stage Execution
**Priority:** 🔥 HIGH
**Impact:** 30 seconds actual time saved (33% faster)
**Complexity:** High
**Time Saved:** 30s reduction in wall-clock time

**PM Instructions:**
Write a user story that covers:
- **User Need:** As a user, I want the pipeline to process my document as fast as possible, so that I can iterate quickly and analyze multiple documents per session
- **Acceptance Criteria:**
  - Pipeline completes in 60 seconds or less (down from 90s)
  - Stages 3 and 4 execute concurrently (currently sequential)
  - Error handling preserves individual stage failure detection
  - Database updates correctly reflect parallel execution state
  - No race conditions in opportunity card generation
- **Technical Context:** Refactor `execute_pipeline_background()` to use Python `asyncio` with `asyncio.gather()`
- **Dependency Analysis:**
  - Stage 1 → Stage 2 (must remain sequential)
  - Stage 2 → Stage 3 (must remain sequential)
  - **Stage 3 + Stage 4 can run in parallel** ⚡
  - Stage 5 depends only on Stage 4 (not Stage 3)
- **Risk:** Race conditions in database writes, requires careful testing

**Dependencies:** None (can implement independently of other stories)

---

### Story 9.3: Switch to Groq LLM Provider
**Priority:** 🔥 QUICK WIN
**Impact:** 40-60 seconds actual time saved
**Complexity:** Low (1 environment variable change)
**Time Saved:** 40-60s reduction in wall-clock time

**PM Instructions:**
Write a user story that covers:
- **User Need:** As a user, I want the pipeline to execute faster without sacrificing output quality, so that I can analyze more documents in less time
- **Acceptance Criteria:**
  - Pipeline completes in 30-50 seconds (down from 90-130s)
  - Output quality remains equivalent to current DeepSeek Chat results
  - No code changes required (environment variable only)
  - Staging environment tested before production rollout
  - Cost analysis confirms acceptable budget impact
- **Technical Context:**
  - Change `LLM_MODEL` environment variable from `deepseek/deepseek-chat` to `groq/llama-3.1-70b-versatile`
  - Update `OPENROUTER_BASE_URL` to `https://api.groq.com/openai/v1`
  - Groq provides 2-3x faster inference with comparable quality
- **Testing Requirements:**
  - Run 5 test documents comparing DeepSeek vs Groq output
  - Verify JSON parsing still works (Groq may format differently)
  - Measure actual latency improvement
  - Validate opportunity card quality with business stakeholders

**Dependencies:** None (can implement in 5 minutes)

---

### Story 9.4: Token Count Reduction
**Priority:** Medium
**Impact:** 10-15 seconds time saved
**Complexity:** Low
**Time Saved:** 10-15s reduction in wall-clock time

**PM Instructions:**
Write a user story that covers:
- **User Need:** As a product owner, I want to optimize LLM token usage to reduce costs and improve speed without losing output quality
- **Acceptance Criteria:**
  - Total token count reduced from 17,000 to 12,300 (28% reduction)
  - Pipeline saves 10-15 seconds end-to-end
  - Output quality maintained (no truncated insights)
  - Stage 5 still generates all 5 opportunity cards
- **Technical Changes:**
  - Stage 1: 2,500 → 1,800 tokens (extractive task needs less)
  - Stage 2: 3,000 → 2,200 tokens (focused amplification)
  - Stage 5: 4,000 → 3,200 tokens (structured JSON output)
  - Total saved: 4,700 tokens
- **Testing Requirements:**
  - Run regression tests on 10 existing test documents
  - Verify all 5 opportunity cards still generate completely
  - Check for truncated descriptions or missing actionability items

**Dependencies:** Should be tested AFTER Story 9.3 (Groq switch) to isolate variables

---

## Implementation Sequencing

### Phase 1: Quick Wins (Week 1)
1. **Story 9.3** - Switch to Groq (1 hour implementation, 1 day testing)
2. **Story 9.4** - Token Reduction (2 hours implementation, 1 day testing)
3. **Combined Testing** - Validate Groq + Token Reduction together

**Deliverable:** 50-70 second pipeline (40-50% faster than baseline)

---

### Phase 2: Real-Time Experience (Week 2-3)
1. **Story 9.1** - Streaming SSE (2-3 days implementation, 2 days testing)
2. **Frontend Integration** - EventSource API, real-time UI updates
3. **User Testing** - Validate perceived performance improvement

**Deliverable:** Real-time feedback + 50-70 second pipeline

---

### Phase 3: Parallel Optimization (Week 4-5)
1. **Story 9.2** - Parallel Execution (3-4 days implementation, 3 days testing)
2. **Concurrency Testing** - Race condition validation, load testing
3. **Production Rollout** - Gradual rollout with monitoring

**Deliverable:** 30-40 second pipeline with real-time feedback

---

## Success Metrics

### Performance Metrics
- **Baseline:** 90-130s end-to-end execution
- **Target (Phase 1):** 50-70s execution (Quick wins)
- **Target (Phase 2):** 50-70s execution + real-time streaming (Perceived instant)
- **Target (Phase 3):** 30-40s execution + real-time streaming (Final state)

### User Experience Metrics
- **Time to First Feedback:** 0s (instant streaming vs 90s currently)
- **User Abandonment Rate:** Reduce by 50%+ (users won't refresh/leave)
- **Session Documents Analyzed:** Increase by 2-3x (faster iteration)

### Cost Metrics
- **Token Usage:** Reduce by 28% (17,000 → 12,300 tokens)
- **API Costs:** Model-dependent (Groq may be cheaper than DeepSeek)
- **Infrastructure:** No additional costs (same Railway deployment)

---

## Technical Architecture Changes

### Backend (Python/FastAPI)
```
Current: Sequential LangChain execution
↓
Phase 1: Groq provider + reduced tokens
↓
Phase 2: + Streaming SSE endpoint
↓
Phase 3: + asyncio parallel execution
```

### Frontend (Next.js)
```
Current: Polling /api/pipeline/[runId]/status every 5s
↓
Phase 2: EventSource /api/pipeline/[runId]/stream (real-time)
↓
Phase 3: Handle parallel stage updates (no change needed)
```

---

## Risks and Mitigations

### Risk 1: Groq Output Format Changes
**Impact:** High - Could break JSON parsing
**Mitigation:** Extensive testing with 20+ documents before production rollout

### Risk 2: Race Conditions in Parallel Execution
**Impact:** Medium - Could cause opportunity cards to not save
**Mitigation:** Add database transaction locks, comprehensive concurrency testing

### Risk 3: Streaming Increases Server Load
**Impact:** Low - More concurrent connections
**Mitigation:** Monitor Railway resource usage, scale horizontally if needed

### Risk 4: Token Reduction Truncates Output
**Impact:** Medium - Could lose important insights
**Mitigation:** A/B testing with current token counts, gradual reduction

---

## Dependencies

### External Dependencies
- Groq API access (assume already have OpenRouter account)
- Railway supports SSE (yes, confirmed)
- Browser EventSource API support (98%+ browsers)

### Internal Dependencies
- Prisma database schema (no changes needed)
- Webhook endpoints (no changes needed)
- Frontend PipelineStateMachine component (minor updates for streaming)

---

## PM Action Items

**For each story above (9.1-9.4), please write:**

1. **Full user story** in standard format:
   ```
   As a [user type]
   I want [goal]
   So that [business value]
   ```

2. **Detailed acceptance criteria** (Given/When/Then format)

3. **Definition of Done** (what must be true to close the story)

4. **Technical notes** for the development team (not for users)

5. **Testing requirements** (unit, integration, E2E)

6. **Story points** estimate (Fibonacci: 1, 2, 3, 5, 8, 13)

7. **Dependencies** on other stories (if any)

---

## Questions for PM to Answer

1. **Priority Confirmation:** Do you agree with the priority ranking (9.1 → 9.3 → 9.2 → 9.4)?
2. **Phasing Strategy:** Should we do all Quick Wins first, or interleave with Streaming?
3. **Quality vs Speed:** What's acceptable quality threshold for Groq vs DeepSeek?
4. **User Testing:** Should we beta test streaming UI with select users first?
5. **Rollback Plan:** What's the rollback strategy if Groq degrades quality?

---

## References

- **Current Pipeline Code:** `backend/app/pipeline_runner.py`
- **LLM Configuration:** `backend/pipeline/utils.py:16-64`
- **Stage Implementations:** `backend/pipeline/stages/stage{1-5}_*.py`
- **Frontend Pipeline Page:** `innovation-web/app/pipeline/[runId]/page.tsx`
- **Architecture Review:** This document created by Winston (Architect) on 2025-10-28
