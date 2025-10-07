# Story 3.2: Stage 4 - Brand Research and Contextualization Chain

## Status
Approved

## Story
**As a** pipeline developer,
**I want** Stage 4 implemented as LangChain LLMChain using pre-existing research data,
**so that** universal lessons are customized for specific brand context using completed brand research.

## Acceptance Criteria
1. File created: `pipeline/stages/stage4_brand_contextualization.py` with `Stage4Chain` class
2. Brand profile loaded from YAML using `load_brand_profile(brand_id)` helper function
3. Brand research data retrieved using `get_brand_research(brand_name)` from pre-existing files in `docs/web-search-setup/`
4. LangChain PromptTemplate defined in `pipeline/prompts/stage4_prompt.py` with instructions:
   - Review brand profile (injected from YAML)
   - Review pre-existing research data (loaded from local files)
   - Review universal lessons from Stage 3
   - Customize each lesson for this specific brand: how does it apply to their products, customers, strategy?
   - Generate brand-specific strategic insights (5-7 insights)
5. Stage 4 chain uses ChatOpenAI configured for OpenRouter (Claude Sonnet 4.5 via anthropic/claude-sonnet-4.5) with temperature=0.5 (slightly higher creativity for contextualization)
6. Output format: Structured markdown with sections: "Brand Context Summary" (from profile + research data), "Brand-Specific Strategic Insights" (numbered list)
7. Stage 4 integrated into `run_pipeline.py` with output saved to `stage4/brand-contextualization.md`
8. Test execution: Run Stages 1-3-4 on Savannah Bananas → Lactalis, verify brand-specific insights reference dairy products and Lactalis context
9. Graceful degradation: If brand research data is missing, Stage 4 proceeds using only brand profile data with logged warning

## Tasks / Subtasks
- [ ] Create Stage 4 implementation file (AC: 1)
  - [ ] Create `pipeline/stages/stage4_brand_contextualization.py`
  - [ ] Implement `Stage4Chain` class
  - [ ] Set up multi-input parsing (Stage 3, brand profile, research data)
- [ ] Implement data loading functions (AC: 2, 3, 9)
  - [ ] Create `load_brand_profile(brand_id)` helper
  - [ ] Create `get_brand_research(brand_name)` helper
  - [ ] Implement graceful degradation for missing research data
  - [ ] Add logging for missing data warnings
- [ ] Create and configure prompt template (AC: 4, 5)
  - [ ] Create `pipeline/prompts/stage4_prompt.py`
  - [ ] Define PromptTemplate with brand profile injection
  - [ ] Add research data injection
  - [ ] Add Stage 3 universal lessons input
  - [ ] Configure brand-specific customization instructions
  - [ ] Set temperature to 0.5 for contextualization creativity
- [ ] Implement output formatting (AC: 6)
  - [ ] Structure markdown with Brand Context Summary
  - [ ] Format Brand-Specific Strategic Insights as numbered list (5-7 items)
  - [ ] Ensure brand-specific language and references
- [ ] Integrate into pipeline execution (AC: 7)
  - [ ] Add Stage 4 to `run_pipeline.py`
  - [ ] Configure Stage 3 → Stage 4 data flow
  - [ ] Integrate brand profile and research data loading
  - [ ] Save output to `stage4/brand-contextualization.md`
- [ ] Test and validate (AC: 8, 9)
  - [ ] Run Stages 1-3-4 on Savannah Bananas → Lactalis
  - [ ] Verify dairy product and Lactalis-specific references
  - [ ] Test graceful degradation with missing research data
  - [ ] Validate output quality and brand specificity

## Dev Notes

**Epic:** Epic 3 - Brand Contextualization with Research Data (Stage 4)

**Dependencies:**
- Story 2.3 (Stage 3 - General Translation)
- Story 3.1 (Pre-Existing Research Data Integration)
- Story 1.3 (Brand Profile Creation)

**Technical Requirements:**
- Temperature=0.5 for more creative contextualization
- Critical differentiation stage - quality is paramount
- Must integrate both brand profile (YAML) and research data (markdown)
- Graceful degradation if research data unavailable

**Key Implementation Notes:**
- Stage 4 is the critical differentiation layer
- Quality of contextualization determines business value
- Must balance brand profile structure with research data richness
- Higher temperature (0.5) allows creative brand-specific application

**Data Integration:**
- Brand Profile: Structured YAML data (name, industry, positioning, etc.)
- Research Data: Comprehensive markdown (8 sections, 35-48KB)
- Stage 3 Output: Universal lessons from previous stage

### Testing
**Test file location:** Integration with `run_pipeline.py`
**Test standards:** Manual quality review for brand-specific insights
**Testing frameworks:** LangChain, manual review
**Specific requirements:**
- Test Savannah Bananas → Lactalis full pipeline (Stages 1-4)
- Verify brand-specific insights (dairy products, Lactalis context)
- Test graceful degradation with missing research data
- Validate 5-7 strategic insights generated
- Confirm insights are actionable and brand-relevant

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
