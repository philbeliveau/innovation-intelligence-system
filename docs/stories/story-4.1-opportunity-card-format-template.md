# Story 4.1: Opportunity Card Format and Template Design

## Status
Approved

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
- [ ] Define opportunity card format (AC: 1)
  - [ ] Create `docs/opportunity-card-format.md`
  - [ ] Define YAML frontmatter fields (opportunity_id, brand, input_source, timestamp, tags)
  - [ ] Specify Title format (5-10 words)
  - [ ] Specify Description format (2-3 paragraphs)
  - [ ] Specify Actionability section (3-5 bullets)
  - [ ] Specify Visual Placeholder section (text description)
  - [ ] Specify Follow-up Prompts section (2-3 prompts)
- [ ] Create Jinja2 template (AC: 2)
  - [ ] Create `templates/opportunity-card.md.j2`
  - [ ] Implement YAML frontmatter rendering
  - [ ] Implement all sections from format specification
  - [ ] Add proper markdown formatting
  - [ ] Ensure template variables are clearly defined
- [ ] Create example opportunity cards (AC: 3)
  - [ ] Create 3 manual examples demonstrating good quality
  - [ ] Vary innovation types across examples
  - [ ] Ensure examples meet format specification
  - [ ] Document examples for reference
- [ ] Create template rendering test (AC: 4, 5)
  - [ ] Create `test_template_rendering.py`
  - [ ] Populate template with sample data
  - [ ] Validate markdown output
  - [ ] Validate YAML frontmatter parsing
  - [ ] Test all template variables render correctly

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
Not yet implemented

### Debug Log References
Not yet implemented

### Completion Notes List
Not yet implemented

### File List
Not yet implemented

## QA Results
Not yet completed
