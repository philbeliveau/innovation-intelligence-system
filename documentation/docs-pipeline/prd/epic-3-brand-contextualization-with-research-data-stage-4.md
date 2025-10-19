# Epic 3: Brand Contextualization with Research Data (Stage 4)

**Expanded Goal:** Implement Stage 4 that transforms brand-agnostic universal lessons into brand-specific strategic insights using pre-existing research data. This is the critical differentiation stage - same input must generate meaningfully different outputs for each brand. Epic delivers proof that contextualization works and research data integration is functional.

## Story 3.1: Pre-Existing Research Data Integration

As a **pipeline developer**,
I want **to load and access pre-existing research data from local files**,
so that **Stage 4 can use completed brand research without live web searches**.

### Acceptance Criteria

1. Research data loader created in `pipeline/utils.py`: `load_research_data(brand_id)` function that reads from `docs/web-search-setup/{brand-id}-research.md`
2. Function loads single comprehensive markdown file per brand containing 8 strategic sections (~550-720 lines, 35-48KB):
   - Brand Overview & Positioning
   - Product Portfolio & Innovation
   - Recent Innovations (Last 18 Months)
   - Strategic Priorities & Business Strategy
   - Target Customers & Market Positioning
   - Sustainability & Social Responsibility
   - Competitive Context & Market Trends
   - Recent News & Market Signals (Last 6 Months)
3. Function returns complete research content as string for injection into Stage 4 prompt
4. Test script created: `test_research_loader.py` that:
   - Lists all 4 available research files (lactalis-canada, mccormick-usa, columbia-sportswear, decathlon)
   - Loads each research file and verifies successful parsing (UTF-8 encoding)
   - Validates file statistics: line count, size, confirms 8 sections present
   - Tests graceful handling of missing files
5. Error handling implemented: If research file missing or unreadable, log warning and return empty string (non-fatal)
6. Logging added: Log file path, line count, and size (KB) when research data loaded
7. Documentation: `docs/brand-research-data-structure.md` documents the 8-section format, file naming convention (`{brand-id}-research.md`), and Stage 4 integration pattern

## Story 3.2: Stage 4 - Brand Research and Contextualization Chain

As a **pipeline developer**,
I want **Stage 4 implemented as LangChain LLMChain using pre-existing research data**,
so that **universal lessons are customized for specific brand context using completed brand research**.

### Acceptance Criteria

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

## Story 3.3: Multi-Brand Testing and Differentiation Validation

As a **pipeline developer**,
I want **Stage 4 tested across all 4 brands with the same input to validate differentiation**,
so that **we can prove brand contextualization generates meaningfully different outputs**.

### Acceptance Criteria

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

## Story 3.4: Complete Pipeline (Stages 1-4) Integration Testing

As a **pipeline developer**,
I want **full Stages 1-4 pipeline tested on multiple input/brand combinations**,
so that **the end-to-end flow is validated before building Stage 5**.

### Acceptance Criteria

1. Integration test runs 8 scenarios:
   - Savannah Bananas → All 4 brands
   - Premium Fast Food → All 4 brands
2. Test execution time measured per scenario (target: <30 minutes)
3. All 8 scenarios complete successfully with no fatal errors
4. Output quality spot-check: Manual review of 2 randomly selected outputs confirms:
   - Stage 1 inspirations are relevant
   - Stage 2 trends are document-derived
   - Stage 3 lessons are universal
   - Stage 4 insights are brand-specific
5. Error handling validation: Intentionally remove research file for one run, verify pipeline completes with degraded output and logged warning
6. Documentation: `docs/pipeline-execution-guide.md` created with troubleshooting tips based on integration testing findings
7. Performance baseline established: Average execution time per scenario documented

---
