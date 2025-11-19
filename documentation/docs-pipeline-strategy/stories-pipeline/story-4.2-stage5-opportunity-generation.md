# Story 4.2: Stage 5 - Opportunity Generation Chain

## Status
Ready for Review

## Story
**As a** pipeline developer,
**I want** Stage 5 implemented to generate exactly 5 distinct opportunity cards from brand-specific insights,
**so that** the pipeline delivers its core value proposition: actionable innovation opportunities.

## Acceptance Criteria
1. File created: `pipeline/stages/stage5_opportunity_generation.py` with `Stage5Chain` class
2. LangChain PromptTemplate defined in `pipeline/prompts/stage5_prompt.py` with instructions:
   - Review brand-specific insights from Stage 4
   - Generate exactly 5 distinct, actionable innovation opportunities
   - Each opportunity must: address brand needs, leverage insights, be implementable (not science fiction), provide customer value
   - For each opportunity: create title, write description (2-3 paragraphs), list actionable next steps (3-5 bullets), describe suggested visual, generate 2-3 follow-up prompts
   - Opportunities should span different innovation types: product, service, marketing, experience, partnership
3. Output parsing: LangChain StructuredOutputParser extracts 5 opportunities into structured format
4. Stage 5 chain uses ChatOpenAI configured for OpenRouter (Claude Sonnet 4.5 via anthropic/claude-sonnet-4.5) with temperature=0.7 (higher creativity for opportunity generation)
5. For each opportunity, render opportunity card using Jinja2 template
6. Stage 5 integrated into `run_pipeline.py`:
   - Outputs saved to `stage5/opportunity-{1-5}.md` (5 separate markdown files)
   - Summary file created: `stage5/opportunities-summary.md` listing all 5 titles with one-line descriptions
7. Test execution: Run full pipeline on Savannah Bananas → Lactalis, verify exactly 5 opportunity cards generated
8. Quality check: Opportunities are distinct (not variations of same idea), actionable (have concrete next steps), and brand-relevant (mention Lactalis products/context)

## Tasks / Subtasks
- [x] Create Stage 5 implementation file (AC: 1)
  - [x] Create `pipeline/stages/stage5_opportunity_generation.py`
  - [x] Implement `Stage5Chain` class
  - [x] Set up Stage 4 output parsing
- [x] Create and configure prompt template (AC: 2, 3, 4)
  - [x] Create `pipeline/prompts/stage5_prompt.py`
  - [x] Define PromptTemplate for opportunity generation
  - [x] Add instructions for exactly 5 distinct opportunities
  - [x] Specify innovation type diversity requirement
  - [x] Configure StructuredOutputParser for 5 opportunities
  - [x] Set temperature to 0.7 for creativity
- [x] Implement opportunity card rendering (AC: 5)
  - [x] Load Jinja2 template for each opportunity
  - [x] Populate template with parsed opportunity data
  - [x] Render 5 individual markdown files
  - [x] Generate metadata (opportunity_id, timestamp, tags)
- [x] Create summary file generation (AC: 6)
  - [x] Create `stage5/opportunities-summary.md`
  - [x] List all 5 opportunity titles
  - [x] Add one-line descriptions for each
  - [x] Format for quick scanning
- [x] Integrate into pipeline execution (AC: 6)
  - [x] Add Stage 5 to `run_pipeline.py`
  - [x] Configure Stage 4 → Stage 5 data flow
  - [x] Save 5 opportunity cards to `stage5/opportunity-{1-5}.md`
  - [x] Generate summary file
- [x] Test and validate (AC: 7, 8)
  - [x] Run full pipeline Savannah Bananas → Lactalis
  - [x] Verify exactly 5 opportunity cards generated
  - [x] Check opportunities are distinct (not variations)
  - [x] Validate actionability (concrete next steps present)
  - [x] Confirm brand relevance (Lactalis-specific content)

## Dev Notes

**Epic:** Epic 4 - Opportunity Generation & Complete Testing (Stage 5)

**Dependencies:**
- Story 3.2 (Stage 4 - Brand Contextualization Chain)
- Story 4.1 (Opportunity Card Format and Template Design)

**Technical Requirements:**
- Temperature=0.7 for high creativity in opportunity generation
- StructuredOutputParser to ensure consistent output format
- Must generate exactly 5 opportunities (no more, no less)
- Opportunities should span different innovation types for diversity

**Key Implementation Notes:**
- Stage 5 delivers the core value proposition
- Quality of opportunities determines product viability
- Diversity of innovation types increases value
- Higher temperature (0.7) encourages creative thinking

**Innovation Types to Span:**
- Product innovation
- Service innovation
- Marketing innovation
- Experience innovation
- Partnership innovation

### Testing
**Test file location:** Integration with `run_pipeline.py`
**Test standards:** Manual quality review of opportunity cards
**Testing frameworks:** LangChain, Jinja2, manual review
**Specific requirements:**
- Test full pipeline Savannah Bananas → Lactalis
- Verify exactly 5 opportunities generated
- Validate distinction between opportunities
- Check actionability (concrete next steps)
- Confirm brand relevance (Lactalis context)
- Verify innovation type diversity

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| TBD | 1.0 | Initial story creation | Unassigned |
| 2025-10-07 | 2.0 | Stage 5 implementation complete - all acceptance criteria met | James (Dev Agent) |

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Debug Log References
None - no debugging required

### Completion Notes List
- Stage 5 implementation complete with temperature=0.7 for creative opportunity generation
- StructuredOutputParser successfully extracts exactly 5 opportunities from LLM output
- Jinja2 template rendering generates properly formatted opportunity cards with metadata
- Integration into run_pipeline.py complete with Stage 4 → Stage 5 data flow
- Test execution successful: Savannah Bananas → Lactalis generated 5 distinct opportunities spanning all innovation types (Product, Service, Marketing, Experience, Partnership)
- Quality validation passed: All opportunities are distinct, actionable (3-4 concrete next steps each), and brand-relevant (reference Olympic Organic, Oshawa facility, Lactalis Canada ESG leadership)

### File List
**Created:**
- pipeline/prompts/stage5_prompt.py
- pipeline/stages/stage5_opportunity_generation.py

**Modified:**
- run_pipeline.py (added Stage 5 import and execution)

## QA Results

### Review Date: 2025-10-07

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment

**Overall Assessment: GOOD IMPLEMENTATION, CRITICAL TEST COVERAGE GAP**

The Stage 5 implementation demonstrates solid engineering with:

**Strengths:**
- **Well-structured class design** - Stage5Chain class with clear separation of concerns (chain creation, opportunity rendering, summary generation)
- **Comprehensive prompt engineering** - Excellent prompt template with detailed instructions for opportunity generation, innovation type diversity, and quality criteria
- **Robust error handling** - Explicit validation of Stage 4 output, structured output parsing, and informative error messages
- **Production-quality logging** - Appropriate log levels throughout with context-rich messages
- **Type hints and docstrings** - All functions properly annotated following Google-style conventions
- **Manual test execution verified** - Evidence of successful pipeline runs generating exactly 5 opportunities spanning all innovation types

**Critical Gap:**
- **ZERO AUTOMATED TESTS** - No test file exists for Stage 5 (test_stage5.py missing)
- Story claims "Test execution: Run full pipeline Savannah Bananas → Lactalis, verify exactly 5 opportunity cards generated" but this was manual verification only
- No regression test capability for this critical "core value delivery" stage
- Stark contrast with Story 4.1 (dependency) which had 16 comprehensive automated tests

### Refactoring Performed

**None.** Implementation code is production-quality as delivered. However, test coverage must be added.

### Compliance Check

- **Coding Standards**: ✓ PASS
  - Type hints on all functions (Stage5Chain.__init__, run, render_opportunity_cards, generate_summary_file)
  - Google-style docstrings with Args/Returns/Raises
  - Proper import organization (standard lib, third-party, local)
  - PEP 8 compliant naming and structure
  - Explicit error handling with informative messages
  - Logging at appropriate levels

- **Project Structure**: ✓ PASS
  - Stage implementation in `pipeline/stages/stage5_opportunity_generation.py`
  - Prompt in `pipeline/prompts/stage5_prompt.py`
  - Template in `templates/opportunity-card.md.j2`
  - Integration in `run_pipeline.py`

- **Testing Strategy**: ✗ FAIL
  - **NO AUTOMATED TESTS** for Stage 5 chain
  - Manual testing only via `run_pipeline.py`
  - No unit tests for StructuredOutputParser
  - No integration tests for Jinja2 rendering
  - No edge case testing (empty opportunities, missing fields, invalid data)
  - No validation of exactly 5 opportunities constraint
  - No test for innovation type diversity requirement

- **All ACs Met**: ⚠ PARTIAL
  - AC1-6: ✓ Implementation complete
  - AC7: ⚠ "Test execution" completed manually, but no automated test artifact
  - AC8: ⚠ "Quality check" completed manually, but no automated validation

### Requirements Traceability

| AC | Requirement | Test Coverage | Status |
|----|-------------|---------------|--------|
| 1 | Stage5Chain class created | ✗ No test_stage5_chain_creation | ⚠ Untested |
| 2 | Prompt template with instructions | ✗ No test_prompt_template_structure | ⚠ Untested |
| 3 | StructuredOutputParser extracts 5 opps | ✗ No test_parser_validates_count | ⚠ Untested |
| 4 | OpenRouter/Claude Sonnet 4.5, temp=0.7 | ✗ No test_llm_configuration | ⚠ Untested |
| 5 | Jinja2 rendering for each opportunity | ✗ No test_render_opportunity_cards | ⚠ Untested |
| 6 | Integration into run_pipeline.py | ✓ Manual verification (stage5/ outputs exist) | ✓ Verified |
| 7 | Test execution generates 5 cards | ⚠ Manual only (no automated test) | ⚠ Manual |
| 8 | Quality check (distinct, actionable, relevant) | ⚠ Manual only (no automated validation) | ⚠ Manual |

**Coverage Assessment:** Implementation verified manually through pipeline execution. However, **NO AUTOMATED TESTS** means:
- No regression testing capability
- No edge case validation
- No fast feedback loop for future changes
- Higher risk of breaking changes

### Test Architecture Analysis

**Current State: CRITICAL GAP**

**Missing Test Coverage:**
1. **Unit Tests for Stage5Chain:**
   - `test_stage5_chain_creation()` - Verify chain initializes with correct config
   - `test_stage5_requires_stage4_output()` - Validate input validation
   - `test_stage5_rejects_empty_stage4_output()` - Edge case handling
   - `test_stage5_validates_exactly_5_opportunities()` - Core constraint testing
   - `test_stage5_handles_parser_errors()` - Error handling validation

2. **Unit Tests for StructuredOutputParser:**
   - `test_parser_extracts_5_opportunities()` - Verify parser configuration
   - `test_parser_rejects_wrong_count()` - Constraint validation
   - `test_parser_validates_required_fields()` - Schema validation

3. **Unit Tests for Jinja2 Rendering:**
   - `test_render_opportunity_cards_validates_count()` - Input validation
   - `test_render_creates_5_files()` - Output verification
   - `test_render_populates_frontmatter()` - Template variable validation
   - `test_generate_summary_file()` - Summary generation validation

4. **Integration Tests:**
   - `test_stage5_end_to_end()` - Full Stage 4 → Stage 5 flow
   - `test_stage5_innovation_type_diversity()` - Validate all 5 types present
   - `test_stage5_output_quality()` - Validate actionability items, follow-up prompts

**Recommendation:** Create `test_stage5_opportunity_generation.py` with minimum 12-15 test cases covering:
- Chain creation and configuration
- Input validation and error handling
- StructuredOutputParser validation
- Jinja2 template rendering
- Edge cases (empty data, invalid formats)
- Integration with Stage 4 output

**Comparison:** Story 4.1 (template design) had **16 comprehensive tests**. Story 4.2 (core value delivery stage) has **0 tests**. This is backwards.

### Manual Verification Results

I reviewed test output from `data/test-outputs/savannah-bananas-lactalis-canada-20251007-145233/stage5/`:

**✓ Verified:**
- Exactly 5 opportunity cards generated (opportunity-1.md through opportunity-5.md)
- Summary file created (opportunities-summary.md)
- Innovation type diversity confirmed:
  1. Product (Zero-Carbon Organic Yogurt Subscription)
  2. Service (Flexitarian Meal Planning App)
  3. Marketing (Sustainability Storytelling Campaign)
  4. Experience (Interactive Dairy Discovery Hub)
  5. Partnership (Regenerative Agriculture Partnership)
- Valid YAML frontmatter in all cards
- All required sections present (Title, Description, Actionability, Visual, Follow-up Prompts)
- Opportunities are distinct (not variations of same idea)
- Actionability items are concrete (3-4 per opportunity)
- Brand relevance confirmed (reference Lactalis products, Olympic Organic, Oshawa facility)

**Quality Assessment:** Manual review confirms AC7 and AC8 requirements met. However, this verification is not repeatable via automated tests.

### Security Review

No security concerns for this stage:
- No user input processing (internal pipeline data flow)
- No external API calls beyond LLM provider (handled by LangChain)
- No sensitive data handling in templates
- File system operations use proper Path handling and encoding

**Status: PASS**

### Performance Considerations

**Observed Performance:**
- Stage 5 execution time: ~15-30 seconds (LLM generation)
- Template rendering: <1 second for 5 cards
- No performance bottlenecks identified

**Considerations:**
- Temperature=0.7 increases creative output but may increase response time vs. lower temperatures
- StructuredOutputParser adds parsing overhead but provides critical validation

**Status: PASS**

### Non-Functional Requirements Assessment

- **Security**: PASS - No security-relevant concerns
- **Performance**: PASS - Acceptable execution time for creative generation task
- **Reliability**: CONCERNS - No automated tests to ensure consistent behavior
- **Maintainability**: CONCERNS - Lack of tests increases risk of regression when modifying code

### Improvements Required

**CRITICAL - Must Address Before Production:**

1. **Create automated test suite** - `test_stage5_opportunity_generation.py`
   - Minimum 12-15 test cases covering core functionality
   - Unit tests for Stage5Chain methods
   - Unit tests for StructuredOutputParser
   - Unit tests for Jinja2 rendering
   - Integration test for Stage 4 → Stage 5 flow
   - Edge case coverage

2. **Add test fixtures** for Stage 5 testing:
   - `get_sample_stage4_output()` - Valid Stage 4 output for testing
   - `get_sample_opportunities()` - Valid opportunity data structures
   - Mock LLM responses for fast test execution

3. **Add validation tests** for quality criteria:
   - Test innovation type diversity requirement
   - Test actionability items count (3-5)
   - Test follow-up prompts count (2-3)
   - Test distinct opportunities (not variations)

**RECOMMENDED - Future Improvements:**

- [ ] Add performance benchmarks for Stage 5 execution time
- [ ] Add tests for graceful degradation if template file missing
- [ ] Add tests for handling malformed LLM output
- [ ] Consider adding quality scoring for generated opportunities
- [ ] Add integration test validating full pipeline Stages 1-5

### Files Modified During Review

**None.** Implementation is production-quality. Test coverage must be added by Dev team.

### Gate Status

**Gate: CONCERNS** → docs/qa/gates/4.2-stage5-opportunity-generation.yml

**Quality Score: 70/100**
- Implementation quality: Excellent (90/100)
- Test coverage: Critical gap (0/100)
- Weighted average: 70/100

**Decision Rationale:**
Implementation code is production-quality with proper error handling, logging, and documentation. Manual verification confirms all acceptance criteria technically met. However, **ZERO AUTOMATED TESTS** for the "core value delivery" stage creates critical technical debt and regression risk. Story 4.1 (template) had 16 tests; Story 4.2 (pipeline core) has 0 tests - this is backwards prioritization.

**Risk Assessment:**
- **Probability of regression:** HIGH (no automated safeguards)
- **Impact of regression:** HIGH (core value delivery affected)
- **Overall risk:** HIGH

### Recommended Status

**✗ Changes Required - Add Automated Test Suite**

**Required Actions:**
1. Create `test_stage5_opportunity_generation.py` with comprehensive test coverage (12-15 tests minimum)
2. Add test fixtures for Stage 5 testing
3. Ensure all tests pass before marking Done
4. Update File List with test file

**Timeline Estimate:** 2-4 hours to implement comprehensive test suite

**Justification:** While implementation quality is excellent and manual testing confirms functionality, lack of automated tests creates unacceptable technical debt for the "core value delivery" stage. This stage must have the same test rigor as its dependencies (Story 4.1 had 16 tests).
