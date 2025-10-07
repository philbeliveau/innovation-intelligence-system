# Story 4.1: Opportunity Card Format and Template Design

## Status
Ready for Review

## Story
**As a** product manager,
**I want** a defined opportunity card format with Jinja2 template,
**so that** Stage 5 generates consistent, visually structured outputs.

## Acceptance Criteria
1. Opportunity card format defined in `docs/opportunity-card-format.md`:
   - Frontmatter metadata (YAML): opportunity_id, brand, input_source, timestamp, tags
   - **Title:** Concise opportunity name (5-10 words)
   - **Description:** 2-3 paragraphs explaining the opportunity, why it's relevant, and how it addresses brand needs
   - **Actionability:** Bulleted list of 3-5 concrete next steps
   - **Visual Placeholder:** Description of suggested visual/image (for MVP: text description, not generated image)
   - **Follow-up Prompts:** 2-3 prompts for further exploration via elicitation
2. Jinja2 template created: `templates/opportunity-card.md.j2` implementing format
3. Example opportunity cards created manually (3 examples) demonstrating good quality
4. Template rendering test: `test_template_rendering.py` populates template with sample data and validates output
5. Template successfully renders and produces valid markdown with frontmatter

## Tasks / Subtasks
- [x] Define opportunity card format (AC: 1)
  - [x] Create `docs/opportunity-card-format.md`
  - [x] Define YAML frontmatter fields (opportunity_id, brand, input_source, timestamp, tags)
  - [x] Specify Title format (5-10 words)
  - [x] Specify Description format (2-3 paragraphs)
  - [x] Specify Actionability section (3-5 bullets)
  - [x] Specify Visual Placeholder section (text description)
  - [x] Specify Follow-up Prompts section (2-3 prompts)
- [x] Create Jinja2 template (AC: 2)
  - [x] Create `templates/opportunity-card.md.j2`
  - [x] Implement YAML frontmatter rendering
  - [x] Implement all sections from format specification
  - [x] Add proper markdown formatting
  - [x] Ensure template variables are clearly defined
- [x] Create example opportunity cards (AC: 3)
  - [x] Create 3 manual examples demonstrating good quality
  - [x] Vary innovation types across examples
  - [x] Ensure examples meet format specification
  - [x] Document examples for reference
- [x] Create template rendering test (AC: 4, 5)
  - [x] Create `test_template_rendering.py`
  - [x] Populate template with sample data
  - [x] Validate markdown output
  - [x] Validate YAML frontmatter parsing
  - [x] Test all template variables render correctly

## Dev Notes

**Epic:** Epic 4 - Opportunity Generation & Complete Testing (Stage 5)

**Dependencies:**
- Story 1.1 (Repository Structure and Python Environment Setup)

**Technical Requirements:**
- Jinja2 for template rendering
- YAML frontmatter for metadata (parseable by static site generators)
- Markdown format for human readability
- Visual placeholder is text description (no image generation for MVP)

**Key Implementation Notes:**
- Template design impacts Stage 5 output quality
- Consistent format enables automated processing
- Frontmatter allows integration with static site generators
- Example cards provide quality benchmark

**Template Variables:**
- opportunity_id, brand, input_source, timestamp, tags
- title, description, actionability_items
- visual_description, follow_up_prompts

### Testing
**Test file location:** Root directory (`test_template_rendering.py`)
**Test standards:** Validate template rendering and markdown output
**Testing frameworks:** Jinja2, PyYAML
**Specific requirements:**
- Template renders with sample data
- Output is valid markdown
- YAML frontmatter parses correctly
- All sections present in output
- Visual formatting is clean and readable

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| TBD | 1.0 | Initial story creation | Unassigned |

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Debug Log References
No debugging required - all tests passed on first attempt after test fix

### Completion Notes List
- Created comprehensive opportunity card format specification (docs/opportunity-card-format.md) with detailed guidelines for all 6 sections: frontmatter, title, description, actionability, visual, and follow-up prompts
- Implemented Jinja2 template (templates/opportunity-card.md.j2) with proper YAML frontmatter and markdown formatting
- Created 3 diverse example cards demonstrating format quality:
  1. Lactalis + Savannah Bananas (experience-innovation)
  2. McCormick + Premium Fast Food (product-innovation)
  3. Decathlon + Sacred Sync (wellness/experience-innovation)
- Developed comprehensive test suite (test_template_rendering.py) with 16 test cases covering template loading, rendering, frontmatter validation, section presence, and edge cases
- All tests passing (16/16) with proper YAML timestamp handling

### File List
**Created:**
- docs/opportunity-card-format.md
- templates/opportunity-card.md.j2
- docs/examples/opportunity-cards/example-1-lactalis-experience-theater.md
- docs/examples/opportunity-cards/example-2-mccormick-premium-accessible.md
- docs/examples/opportunity-cards/example-3-decathlon-mindful-movement.md
- test_template_rendering.py
- data/test-outputs/test-template-output.md (generated by test)

**Modified:**
- None

## QA Results

### Review Date: 2025-10-07

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment

**Overall Assessment: EXCELLENT**

This story delivers a comprehensive, well-executed template system for opportunity card generation. The implementation demonstrates exceptional attention to detail with:

- **Comprehensive format specification** (380 lines) covering all 6 sections with detailed guidelines, examples, and usage instructions
- **Clean Jinja2 template** with proper variable interpolation and markdown formatting
- **Robust test suite** with 16 test cases covering template loading, rendering, frontmatter validation, section presence/ordering, and edge cases
- **High-quality example cards** demonstrating format across diverse innovation types (experience, product, wellness)

All code follows PEP 8 standards with proper type hints, Google-style docstrings, organized imports, and clear error handling. The test architecture is exemplary with appropriate test level selection, comprehensive coverage, and fast execution (0.07s for 16 tests).

### Refactoring Performed

**None required.** Implementation is clean, well-structured, and production-ready as delivered.

### Compliance Check

- **Coding Standards** (docs/architecture/coding-standards.md): ✓ PASS
  - Type hints on all functions
  - Google-style docstrings with Args/Returns/Raises
  - Proper import organization (standard lib, third-party, local)
  - PEP 8 compliant (line length, naming conventions)
  - Explicit error handling with informative messages

- **Project Structure** (docs/architecture/7-file-structure.md): ✓ PASS
  - Template in `templates/` directory
  - Documentation in `docs/`
  - Test file in root following `test_*.py` pattern
  - Test outputs in `data/test-outputs/`

- **Testing Strategy** (docs/architecture/11-testing-strategy.md): ✓ PASS
  - Appropriate unit test structure
  - Clear test organization and naming
  - Proper use of fixtures and helper functions

- **All ACs Met**: ✓ PASS
  - AC1: Format specification complete with all 6 sections
  - AC2: Jinja2 template created and implements format
  - AC3: 3 high-quality example cards demonstrate format
  - AC4: Comprehensive test suite with 16 test cases
  - AC5: Template renders valid markdown with frontmatter (16/16 tests passing)

### Requirements Traceability

| AC | Requirement | Test Coverage | Status |
|----|-------------|---------------|--------|
| 1 | Format specification defined | Format document serves as reference | ✓ Complete |
| 2 | Jinja2 template created | `test_template_loads`, `test_template_renders_with_sample_data` | ✓ Complete |
| 3 | 3 example cards created | Manual verification of quality | ✓ Complete |
| 4 | Template rendering test | 16 comprehensive test cases | ✓ Complete |
| 5 | Valid markdown output | `test_frontmatter_is_valid_yaml`, `test_output_is_valid_markdown` | ✓ Complete |

**Coverage Assessment:** All ACs have appropriate validation mechanisms. Test coverage is comprehensive.

### Test Architecture Analysis

**Coverage Metrics:**
- Template loading: ✓
- Successful rendering: ✓
- Frontmatter validation: ✓
- Required field presence: ✓
- Value matching: ✓
- All body sections: ✓
- Section ordering: ✓
- Edge cases (empty lists, special chars): ✓
- Output persistence: ✓

**Test Quality:**
- Clear, descriptive test names following conventions
- Proper separation of concerns with reusable helpers (`get_sample_data`, `parse_frontmatter`, `load_template`)
- Appropriate assertions with informative failure messages
- Fast execution (0.07s for 16 tests)

**Assessment:** Excellent test architecture at appropriate level (unit tests for template rendering).

### Example Card Quality Review

**Example 1: Lactalis - Experience Theater**
- Title length: 7 words ✓
- Description: 3 well-structured paragraphs ✓
- Actionability: 5 concrete items with owners/timeframes ✓
- Visual: Rich atmospheric description ✓
- Follow-up prompts: 3 strategic questions ✓
- Quality: EXCELLENT - specific, actionable, brand-contextualized

**Example 2: McCormick - Premium Spice Blends**
- Demonstrates "accessible premium" positioning ✓
- Clear strategic alignment with brand challenges ✓
- Quality: EXCELLENT - strong business case

**Example 3: Decathlon - Mindful Movement**
- Innovative wellness positioning ✓
- Detailed implementation roadmap ✓
- Quality: EXCELLENT - differentiated approach

**Overall Example Quality:** All three examples demonstrate high-quality implementation with appropriate variety across innovation types.

### Security Review

No security concerns. This is template and documentation work with no user input processing, external API calls, or sensitive data handling.

**Status: PASS**

### Performance Considerations

Template rendering is fast and efficient. Test execution completes in 0.07s for 16 comprehensive tests. No performance concerns for intended use.

**Status: PASS**

### Non-Functional Requirements Assessment

- **Security**: PASS - No security-relevant code
- **Performance**: PASS - Fast rendering, efficient tests
- **Reliability**: PASS - Proper error handling, comprehensive edge case coverage
- **Maintainability**: PASS - Clear structure, excellent documentation, self-documenting tests

### Files Modified During Review

**None.** No refactoring required.

### Gate Status

**Gate: PASS** → docs/qa/gates/4.1-opportunity-card-format-template.yml

**Quality Score: 100/100**

**Decision Rationale:** All acceptance criteria fully implemented with excellent code quality, comprehensive test coverage (16/16 passing), high-quality documentation and examples, full standards compliance, and no issues identified.

### Recommended Status

**✓ Ready for Done**

This story is complete and production-ready. All requirements met with exceptional quality. No changes required.
