# Story 4.2: Stage 5 - Opportunity Generation Chain

## Status
Approved

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
- [ ] Create Stage 5 implementation file (AC: 1)
  - [ ] Create `pipeline/stages/stage5_opportunity_generation.py`
  - [ ] Implement `Stage5Chain` class
  - [ ] Set up Stage 4 output parsing
- [ ] Create and configure prompt template (AC: 2, 3, 4)
  - [ ] Create `pipeline/prompts/stage5_prompt.py`
  - [ ] Define PromptTemplate for opportunity generation
  - [ ] Add instructions for exactly 5 distinct opportunities
  - [ ] Specify innovation type diversity requirement
  - [ ] Configure StructuredOutputParser for 5 opportunities
  - [ ] Set temperature to 0.7 for creativity
- [ ] Implement opportunity card rendering (AC: 5)
  - [ ] Load Jinja2 template for each opportunity
  - [ ] Populate template with parsed opportunity data
  - [ ] Render 5 individual markdown files
  - [ ] Generate metadata (opportunity_id, timestamp, tags)
- [ ] Create summary file generation (AC: 6)
  - [ ] Create `stage5/opportunities-summary.md`
  - [ ] List all 5 opportunity titles
  - [ ] Add one-line descriptions for each
  - [ ] Format for quick scanning
- [ ] Integrate into pipeline execution (AC: 6)
  - [ ] Add Stage 5 to `run_pipeline.py`
  - [ ] Configure Stage 4 → Stage 5 data flow
  - [ ] Save 5 opportunity cards to `stage5/opportunity-{1-5}.md`
  - [ ] Generate summary file
- [ ] Test and validate (AC: 7, 8)
  - [ ] Run full pipeline Savannah Bananas → Lactalis
  - [ ] Verify exactly 5 opportunity cards generated
  - [ ] Check opportunities are distinct (not variations)
  - [ ] Validate actionability (concrete next steps present)
  - [ ] Confirm brand relevance (Lactalis-specific content)

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
