# Epic 4: Opportunity Generation & Complete Testing (Stage 5)

**Expanded Goal:** Implement Stage 5 that transforms brand-specific insights into 5 actionable opportunity cards with descriptions, visuals, and follow-up prompts. Execute complete 20-test validation run (5 inputs × 4 brands), conduct quality assessment, and validate business hypothesis. Epic delivers final validation of whether the pipeline produces opportunities worth paying for.

## Story 4.1: Opportunity Card Format and Template Design

As a **product manager**,
I want **a defined opportunity card format with Jinja2 template**,
so that **Stage 5 generates consistent, visually structured outputs**.

### Acceptance Criteria

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

## Story 4.2: Stage 5 - Opportunity Generation Chain

As a **pipeline developer**,
I want **Stage 5 implemented to generate exactly 5 distinct opportunity cards from brand-specific insights**,
so that **the pipeline delivers its core value proposition: actionable innovation opportunities**.

### Acceptance Criteria

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

## Story 4.3: Complete 20-Test Batch Execution

As a **product manager**,
I want **the full pipeline executed on all 20 test scenarios (5 inputs × 4 brands) with batch automation**,
so that **I have complete dataset of 100 opportunity cards for validation**.

### Acceptance Criteria

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

## Story 4.4: Quality Assessment and Business Hypothesis Validation

As a **product manager**,
I want **structured quality assessment of all 100 opportunity cards using scoring rubric**,
so that **I can validate whether pipeline outputs justify customer payment**.

### Acceptance Criteria

1. Quality scoring rubric created in `docs/opportunity-quality-rubric.md`:
   - **Novelty (1-5):** Is this a fresh idea, or obvious/generic?
   - **Actionability (1-5):** Are next steps concrete and implementable?
   - **Relevance (1-5):** Does this authentically fit the brand's context and capabilities?
   - **Specificity (1-5):** Is this detailed enough to act on, or too vague?
   - **Overall Score:** Average of 4 dimensions
2. Sampling strategy: Review 20 randomly selected opportunity cards (20% of total) using rubric
3. Quality assessment spreadsheet created: `data/quality-assessment.csv` with columns: opportunity_id, brand, input_source, novelty, actionability, relevance, specificity, overall_score, notes
4. Manual scoring completed by PM on 20 sampled opportunities
5. Results analysis:
   - Average overall score calculated (target: ≥3.5 per KPI table)
   - % of opportunities scoring ≥3.0 (target: ≥70%)
   - Breakdown by dimension: which dimensions are strong/weak?
6. Differentiation validation: Select 5 opportunities generated from same input across different brands, verify they are meaningfully different (qualitative assessment)
7. Business hypothesis validation documented in `docs/validation-results.md`:
   - **Transformation works?** Can pipeline systematically generate opportunities from signals? (Yes/No + evidence)
   - **Quality sufficient?** Would innovation teams pay for these opportunities? (Yes/No + rationale)
   - **Differentiation proven?** Do outputs vary meaningfully by brand? (Yes/No + examples)
   - **Speed feasible?** Can we deliver daily opportunities? (Yes/No + execution time data)
   - **Recommendation:** Proceed to productionization, pivot, or iterate? (Decision + reasoning)

## Story 4.5: Documentation and Handoff for Productionization

As a **future product manager/developer**,
I want **complete documentation of pipeline architecture, findings, and recommendations**,
so that **I can build production version based on validated demo**.

### Acceptance Criteria

1. Architecture documentation updated:
   - `docs/architecture.md` with LangChain chain diagrams, data flow, stage descriptions
   - `docs/prompt-engineering-decisions.md` documenting rationale for each stage's prompt design
2. Test results package created in `data/validation-package/`:
   - Batch summary report
   - Quality assessment results
   - Differentiation analysis examples
   - Validation results document
   - 5 "best of" opportunity cards showcasing high-quality outputs
3. Lessons learned documented in `docs/lessons-learned.md`:
   - What worked well (e.g., LangChain reduced dev time)
   - What was challenging (e.g., Stage 2 trend extraction without social data)
   - Recommendations for production (e.g., add automated quality scoring, improve visual generation)
4. Productionization recommendations in `docs/productionization-roadmap.md`:
   - What to keep (architecture, stage structure)
   - What to improve (error handling, output quality, execution speed)
   - What to add (automated scheduling, real-time data sources, feedback loop)
   - Estimated effort for production build (epic breakdown)
5. Setup and execution guide: `README.md` fully updated with installation, configuration, running pipeline, interpreting outputs
6. Code quality: All Python code includes docstrings, type hints where appropriate, inline comments for complex logic
7. Handoff meeting prep: Slide deck summarizing findings, recommendations, and demo of pipeline execution

---
