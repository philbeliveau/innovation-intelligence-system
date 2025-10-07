# Story 4.3: Complete 20-Test Batch Execution

## Status
Approved

## Story
**As a** product manager,
**I want** the full pipeline executed on all 20 test scenarios (5 inputs × 4 brands) with batch automation,
**so that** I have complete dataset of 100 opportunity cards for validation.

## Acceptance Criteria
1. Batch execution script updated: `python run_pipeline.py --batch` runs all 20 scenarios sequentially
2. Execution monitoring: Progress displayed with timestamps (e.g., "Test 5/20: premium-fast-food → mccormick - Stage 3/5 complete")
3. Error resilience: If one test scenario fails, log error and continue to next scenario (don't abort entire batch)
4. Batch execution completes and produces outputs:
   - 20 test output directories (one per scenario)
   - 100 opportunity cards total (5 per scenario)
   - Batch summary report: `data/test-outputs/batch-summary.md` with execution times, success/failure per scenario
5. Execution time tracking: Total batch runtime, average per scenario, average per stage
6. Success metric: ≥19 out of 20 scenarios complete successfully (95% success rate per NFR2)
7. All outputs committed to git for analysis
8. Batch execution can be re-run with `--batch --retry-failed` flag to retry only failed scenarios

## Tasks / Subtasks
- [ ] Update batch execution script (AC: 1)
  - [ ] Update `run_pipeline.py` with `--batch` flag
  - [ ] Configure all 20 scenarios (5 inputs × 4 brands)
  - [ ] Implement sequential execution
  - [ ] Add execution coordination logic
- [ ] Implement progress monitoring (AC: 2, 5)
  - [ ] Display test number and total (e.g., "Test 5/20")
  - [ ] Show current input and brand
  - [ ] Display stage progress (e.g., "Stage 3/5 complete")
  - [ ] Add timestamps to progress output
  - [ ] Track execution time per scenario and per stage
- [ ] Implement error resilience (AC: 3)
  - [ ] Wrap each scenario in try/except
  - [ ] Log errors with full context
  - [ ] Continue to next scenario on failure
  - [ ] Track failed scenarios for retry
- [ ] Generate batch summary report (AC: 4)
  - [ ] Create `data/test-outputs/batch-summary.md`
  - [ ] List all 20 scenarios with status (success/failure)
  - [ ] Include execution times
  - [ ] Count total opportunity cards generated (target: 100)
  - [ ] Calculate success rate
- [ ] Implement retry functionality (AC: 8)
  - [ ] Add `--retry-failed` flag
  - [ ] Track failed scenarios during batch execution
  - [ ] Implement retry logic for failed scenarios only
  - [ ] Update batch summary after retry
- [ ] Execute and validate batch (AC: 6, 7)
  - [ ] Run full batch execution
  - [ ] Verify ≥19 out of 20 scenarios succeed (95%)
  - [ ] Verify 100 opportunity cards generated (or close)
  - [ ] Commit all outputs to git

## Dev Notes

**Epic:** Epic 4 - Opportunity Generation & Complete Testing (Stage 5)

**Dependencies:**
- Story 4.2 (Stage 5 - Opportunity Generation Chain)
- Story 1.5 (Basic Pipeline Execution Script Scaffolding)

**Technical Requirements:**
- 20 scenarios = 5 inputs × 4 brands = 100 total opportunities
- Error resilience critical (don't fail entire batch on single error)
- Progress monitoring for transparency during long-running batch
- Performance tracking for speed validation

**Key Implementation Notes:**
- Batch execution validates pipeline scalability
- Error resilience ensures complete dataset collection
- Progress monitoring provides visibility during long runs
- Retry functionality enables efficient recovery

**Performance Targets:**
- 95% success rate (≥19/20 scenarios)
- Complete batch execution time reasonable for testing
- Per-scenario execution time tracked for optimization

### Testing
**Test file location:** Root directory (`run_pipeline.py`)
**Test standards:** Complete batch execution with monitoring
**Testing frameworks:** LangChain, batch automation
**Specific requirements:**
- Execute all 20 scenarios (5 inputs × 4 brands)
- Achieve ≥95% success rate (19/20 scenarios)
- Generate ~100 opportunity cards total
- Track execution times
- Test error resilience (continue on failure)
- Test retry functionality with failed scenarios

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
