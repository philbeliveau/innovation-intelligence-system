# Story 3.3: Multi-Brand Testing and Differentiation Validation

## Status
Approved

## Story
**As a** pipeline developer,
**I want** Stage 4 tested across all 4 brands with the same input to validate differentiation,
**so that** we can prove brand contextualization generates meaningfully different outputs.

## Acceptance Criteria
1. Test script created: `test_stage4_differentiation.py` runs Savannah Bananas input through Stages 1-3, then Stage 4 for all 4 brands
2. Four outputs generated: Lactalis, McCormick, Columbia, Decathlon strategic insights
3. Side-by-side comparison document created: `data/test-outputs/stage4-differentiation-test/comparison.md` with excerpts from each brand
4. Differentiation scoring rubric created in `docs/differentiation-rubric.md`:
   - **Unique insights per brand:** Are insights specific to brand's products/context? (Yes/No per insight)
   - **Differentiation index:** % of insights that are unique (not copy-pasted across brands)
   - **Target: 70%+ unique insights per brand**
5. Manual scoring completed using rubric, results documented in comparison document
6. If differentiation <70%: Refine Stage 4 prompt to emphasize brand-specific application, re-test
7. Success criteria: Differentiation index ≥70% for all 4 brands
8. Qualitative validation: Can a reviewer correctly match each output to its brand without seeing the brand name?

## Tasks / Subtasks
- [ ] Create differentiation test script (AC: 1, 2)
  - [ ] Create `test_stage4_differentiation.py`
  - [ ] Run Savannah Bananas through Stages 1-3 once
  - [ ] Run Stage 3 output → Stage 4 for all 4 brands
  - [ ] Generate 4 brand-specific outputs
  - [ ] Save all outputs to designated directory
- [ ] Create comparison document (AC: 3)
  - [ ] Create `data/test-outputs/stage4-differentiation-test/comparison.md`
  - [ ] Extract key excerpts from each brand output
  - [ ] Format side-by-side for easy comparison
  - [ ] Include full outputs as references
- [ ] Create differentiation rubric (AC: 4)
  - [ ] Create `docs/differentiation-rubric.md`
  - [ ] Define "Unique insights per brand" criteria
  - [ ] Define "Differentiation index" calculation method
  - [ ] Set 70% target threshold
  - [ ] Provide scoring examples
- [ ] Perform manual scoring (AC: 5, 8)
  - [ ] Score each insight as unique or generic
  - [ ] Calculate differentiation index per brand
  - [ ] Document results in comparison document
  - [ ] Perform blind matching test (output to brand)
- [ ] Iterate if needed (AC: 6, 7)
  - [ ] If <70% differentiation, identify issues
  - [ ] Refine Stage 4 prompt for better brand specificity
  - [ ] Re-run test with refined prompt
  - [ ] Verify ≥70% differentiation achieved

## Dev Notes

**Epic:** Epic 3 - Brand Contextualization with Research Data (Stage 4)

**Dependencies:**
- Story 3.2 (Stage 4 - Brand Contextualization Chain)

**Technical Requirements:**
- This is the critical validation test for business hypothesis
- 70% differentiation threshold validates value proposition
- Manual scoring required (no automation for MVP)
- May require multiple iterations of prompt refinement

**Key Implementation Notes:**
- This story validates the core business hypothesis
- Differentiation quality determines product viability
- 70% threshold ensures meaningful brand-specific value
- Blind matching test provides qualitative validation

**Success Metrics:**
- Quantitative: ≥70% differentiation index per brand
- Qualitative: Successful blind matching of outputs to brands
- Business validation: Proves brand contextualization adds value

### Testing
**Test file location:** Root directory (`test_stage4_differentiation.py`)
**Test standards:** Manual differentiation scoring with rubric
**Testing frameworks:** LangChain, manual quality assessment
**Specific requirements:**
- Run same input (Savannah Bananas) through all 4 brands
- Generate 4 distinct brand outputs
- Score each insight for uniqueness
- Calculate differentiation index per brand
- Achieve ≥70% differentiation for all brands
- Validate through blind matching test

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| TBD | 1.0 | Initial story creation | Unassigned |

## Dev Agent Record

### Agent Model Used
Not yet implemented

### Debug Log References
Not yet implemented

### Completion Notes List
Not yet implemented

### File List
Not yet implemented

## QA Results
Not yet completed
