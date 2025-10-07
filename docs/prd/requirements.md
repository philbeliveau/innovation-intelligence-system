# Requirements

## Functional

- **FR1:** System shall create and store structured brand context profiles for 4 test brands (Lactalis Canada, McCormick USA, Columbia Sportswear, Decathlon) including positioning, portfolio, target customers, recent innovations, and strategic priorities
- **FR2:** System shall ingest 5 different input types (case study PDFs, trend reports, spotted innovations) and extract content for pipeline processing
- **FR3:** System shall execute Stage 1 (Input Processing) to review content, identify inspiration elements, and conduct initial research
- **FR4:** System shall execute Stage 2 (Signal Amplification) to extract trend patterns from input document content (no external social media data)
- **FR5:** System shall execute Stage 3 (General Translation) to generate brand-agnostic universal insights and lessons from processed input
- **FR6:** System shall execute Stage 4 (Brand Contextualization) by loading brand profile, accessing pre-existing research data on the brand, and generating brand-specific strategic insights
- **FR7:** System shall execute Stage 5 (Opportunity Generation) to produce exactly 5 distinct, actionable innovation opportunities per test run
- **FR8:** System shall generate visual opportunity cards with descriptions for each generated opportunity
- **FR9:** System shall create follow-up prompts for further development of each opportunity
- **FR10:** System shall execute single test run (1 input + 1 brand) through all 5 pipeline stages
- **FR11:** System shall support batch execution of multiple test runs (up to 20 scenarios: 5 inputs × 4 brands)
- **FR12:** System shall store intermediate outputs between pipeline stages for debugging and validation
- **FR13:** System shall organize test outputs in structured directory format: `/data/test-outputs/{test-id}/`
- **FR14:** System shall generate execution logs tracking pipeline flow, stage completion, and errors
- **FR15:** System shall provide manual review checklist for opportunity quality assessment using scoring rubric (novelty, actionability, relevance, specificity)
- **FR16:** System shall enable side-by-side comparison of opportunities generated from same input across different brands
- **FR17:** System shall load and access pre-existing brand research data in Stage 4 from local files (current brand news, innovations, strategy, positioning)
- **FR18:** System shall define and document trend extraction methodology for Stage 2 (pattern recognition from document content without external social data)

## Non Functional

- **NFR1:** Pipeline shall complete single test run (1 input + 1 brand, all 5 stages) in under 30 minutes of active execution time
- **NFR2:** Pipeline shall achieve 95%+ success rate across all 20 test scenarios without fatal errors
- **NFR3:** System shall generate exactly 5 opportunities in 95%+ of test runs
- **NFR4:** Opportunity cards shall follow consistent structured format (markdown with frontmatter metadata)
- **NFR5:** Brand profiles shall be reusable data files (YAML or JSON) ingestible by pipeline without modification
- **NFR6:** All outputs shall be version-controlled and comparable across pipeline iterations
- **NFR7:** System shall operate within Claude Code CLI local execution environment without external services (except OpenRouter API for LLM access)
- **NFR8:** OpenRouter API costs for complete 20-test run batch shall remain under $50
- **NFR9:** Documentation shall be sufficient for another PM/developer to create productionization user stories
- **NFR10:** Pipeline stages shall be independently testable without requiring full end-to-end execution

---
