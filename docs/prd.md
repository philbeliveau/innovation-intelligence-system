# Innovation Intelligence Pipeline Testing System - Product Requirements Document (PRD)

**Version:** 1.0
**Date:** 2025-10-03
**Author:** Product Management
**Status:** Draft - In Development
**Data Sources:** `documentation/document/`

---

## Goals and Background Context

### Goals

- Validate that automated pipeline can systematically transform market signals into brand-specific, actionable innovation opportunities
- Establish baseline quality threshold for "actionable opportunity" that justifies customer payment ($149-$1,500/month tiers)
- Prove differentiation capability by generating meaningfully different outputs across 4 brands from identical inputs
- Benchmark pipeline execution speed to determine feasibility of "daily opportunities" delivery tier
- Generate 100 opportunity cards across 20 test scenarios (5 inputs × 4 brands × 5 opportunities each) for empirical validation
- Build rapid demo to validate core hypothesis with minimal development time
- Document complete pipeline process to enable future productionization by development team
- Identify pipeline bottlenecks, failure modes, and data source requirements through systematic testing

### Background Context

The Innovation Intelligence System business concept proposes delivering "freshly baked" innovation opportunities to CPG companies, but the core value proposition remains unvalidated. The fundamental question is whether an automated system can systematically convert generic market signals (trend reports, case studies, spotted innovations) into high-value, brand-specific opportunities that innovation teams will pay for.

This PRD defines an MVP testing pipeline that will validate or invalidate the business hypothesis. The pipeline processes inputs through 5 stages: (1) Input Processing, (2) Signal Amplification, (3) General Translation, (4) Brand Contextualization, and (5) Opportunity Generation. By testing across 4 diverse brands (Lactalis Canada, McCormick USA, Columbia Sportswear, Decathlon) with 5 different input types, we can empirically measure quality, differentiation, speed, and consistency—the critical unknowns blocking business validation.

The system leverages existing BMAD agent orchestration framework and innovation intelligence research (TRIZ, SIT, biomimicry, SPECTRE validation) documented in `documentation/document/`. Success means proving the transformation works; failure means identifying why contextualization or opportunity generation breaks down, enabling informed pivot decisions.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-03 | 1.0 | Initial PRD creation from Project Brief | Product Management |

---

## Requirements

### Functional

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

### Non Functional

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

## Technical Assumptions

### Repository Structure: Monorepo

The system will be built within the existing `innovation-intelligence-system` monorepo with clear separation of concerns:
- `/pipeline/` - Main pipeline code (Python modules)
  - `/pipeline/stages/` - Stage 1-5 LangChain implementations
  - `/pipeline/chains.py` - SequentialChain setup
  - `/pipeline/prompts/` - PromptTemplate definitions
  - `/pipeline/utils.py` - Helper functions
- `/data/brand-profiles/` - Brand context YAML files
- `/data/test-outputs/{test-id}/` - Test execution results (intermediate + final outputs)
- `/documentation/document/` - Input source documents (5 test inputs as PDFs/markdown)
- `/templates/` - Jinja2 templates for opportunity card generation
- `run_pipeline.py` - Main execution script
- `requirements.txt` - Python dependencies

**Rationale:** Monorepo keeps all testing artifacts, pipeline code, and documentation co-located for easy access during validation phase. No need for polyrepo complexity when building single-purpose testing tool.

### Service Architecture

**Pipeline Orchestration Framework:** LangChain (Python-based LLM application framework)

**Why LangChain:**
- Purpose-built for sequential LLM chains (exactly our use case)
- Built-in PDF parsing and state management
- Rapid development: 1-2 days to working pipeline vs 3-5 days custom solution
- Industry-standard framework with extensive documentation
- Automatic context passing between pipeline stages

**LLM Provider:** OpenRouter (Unified API gateway for multiple LLM providers)

**Why OpenRouter:**
- Single API interface for accessing multiple LLM providers including Anthropic Claude
- Simplified API key management and billing across providers
- Flexible provider switching without code changes (future-proofing)
- Competitive pricing with transparent rate limits
- Compatible with OpenAI SDK, enabling use of langchain-openai package
- No vendor lock-in: can switch between Claude, GPT, or other models by changing model parameter

**Execution Model:**
- Sequential 5-stage pipeline using LangChain SequentialChain
- Stage 1-3: LLMChain components for document analysis (offline)
- Stage 4: LLMChain with pre-existing research data integration (offline)
- Stage 5: LLMChain for opportunity generation
- Each stage defined as LangChain PromptTemplate + LLMChain
- Stages 1-3 execute once per input (brand-agnostic)
- Stages 4-5 execute per brand (4× per input) using brand profile variables and research data

**LangChain Components:**
- **Document Loading:** PyPDFLoader for PDF ingestion from `documentation/document/` and research data files
- **LLM:** ChatOpenAI (Claude Sonnet 4.5) via OpenRouter API
- **Chains:** SequentialChain for automatic stage orchestration
- **Data Loading:** File system access for pre-existing brand research from `docs/web-search-setup/`
- **Output Parsers:** StructuredOutputParser for opportunity card formatting
- **Memory:** ConversationBufferMemory for context preservation across stages

**Research Data Integration:**
- Stage 4 loads pre-existing brand research files from `docs/web-search-setup/` directory
- **Research File Structure:** Each brand has a comprehensive markdown file (~550-720 lines, 35-48KB) with 8 strategic dimensions:
  1. Brand Overview & Positioning (brand values, heritage, campaigns, target audience)
  2. Product Portfolio & Innovation (product categories, flagship products, recent launches)
  3. Recent Innovations - Last 18 Months (new products, packaging, technology, sustainability, partnerships)
  4. Strategic Priorities & Business Strategy (growth plans, digital transformation, sustainability targets)
  5. Target Customers & Market Positioning (demographics, psychographics, purchase behaviors)
  6. Sustainability & Social Responsibility (ESG commitments, certifications, initiatives)
  7. Competitive Context & Market Trends (competitors, industry dynamics, consumer trends)
  8. Recent News & Market Signals - Last 6 Months (press releases, market moves, media coverage)
- **Research Depth:** ~46 subsections per brand with cited sources (45+ sources per brand)
- **Available Brands:** Lactalis Canada, McCormick USA, Columbia Sportswear, Decathlon
- **File Location:** `docs/web-search-setup/{brand-id}-research.md`
- Research content loaded and injected into Stage 4 prompt context for brand-specific contextualization

**LLM Integration:**
- Claude API (Sonnet 4.5) via OpenRouter using langchain-openai package
- OpenRouter provides unified API access to multiple LLM providers including Anthropic Claude
- Temperature/top_p tuning per stage for creativity vs consistency balance
- Token limit management and chunking for large document inputs

**Data Processing:**
- PDF parsing via LangChain PyPDFLoader (case studies, trend reports from `documentation/document/`)
- Markdown generation for opportunity cards using Jinja2 templates
- YAML for brand profiles (loaded via PyYAML)
- JSON for structured outputs (opportunity metadata, intermediate stage results)
- Local file system storage (no database required for MVP)

**Rationale:** LangChain provides purpose-built components for sequential LLM pipelines, dramatically reducing development time. Built-in PDF parsing and state management eliminate need for custom infrastructure. Industry-standard framework means future teams can maintain/extend easily. OpenRouter provides flexible LLM provider management with access to Claude Sonnet 4.5, which offers sufficient reasoning capability for multi-stage analysis.

### Testing Requirements

**Testing Strategy:**
- **Manual execution initially** - Command-line driven pipeline invocation
- **Stage-level testing** - Each pipeline stage independently testable with mock inputs
- **Integration testing** - Full pipeline run (1 input + 1 brand) validates end-to-end flow
- **Batch testing** - All 20 scenarios (5 inputs × 4 brands) executed sequentially
- **Manual quality validation** - Human review using scoring rubric (no automated QA for MVP)

**Test Execution Methods:**
- Single test run: `python run_pipeline.py --input {input-id} --brand {brand-id}`
- Batch execution: `python run_pipeline.py --batch` (runs all 20 test scenarios)
- Stage testing: `python test_stage.py --stage {1-5} --mock-input {file}` for isolated validation
- Development mode: `python run_pipeline.py --input {input-id} --brand {brand-id} --verbose` for debugging

**Quality Assurance:**
- Schema validation for stage outputs (ensure expected structure)
- Manual review checklist execution after test runs
- Version control all outputs for comparison across iterations
- Logging at each stage for debugging pipeline failures

**Rationale:** MVP prioritizes speed of validation over test automation sophistication. Manual testing is acceptable for 20 test scenarios. Automated unit/integration tests would delay validation without proportional value at this stage. If pipeline proves viable, production version can add comprehensive automated testing.

### Additional Technical Assumptions and Requests

**Programming Language:**
- Python 3.10+ for all pipeline code
- LangChain framework for LLM orchestration
- YAML for brand profiles and configuration
- Markdown for opportunity card outputs

**External Dependencies:**
- **Python packages:**
  - `langchain` - Core LangChain framework
  - `langchain-openai` - OpenRouter integration (compatible with OpenAI-style APIs)
  - `langchain-community` - PDF loaders and document processing
  - `openai` - OpenAI-compatible API SDK for OpenRouter
  - `pypdf` - PDF parsing backend
  - `pyyaml` - Brand profile and data loading
  - `jinja2` - Template rendering for outputs
- **API Keys:**
  - OpenRouter API key (access to Claude via OpenRouter)
- **Local file system access required for Stage 4** (pre-existing brand research data)

**Performance Considerations:**
- Pipeline execution primarily limited by LLM API latency (sequential stages)
- Intermediate output persistence enables stage restart without full re-run
- No parallelization required for MVP (20 tests can run sequentially)

**Documentation Requirements:**
- Each LangChain stage documented with: PromptTemplate, expected inputs/outputs, configuration details
- Brand profile YAML schema documented with examples
- Opportunity card markdown format documented with example outputs
- LangChain chain architecture diagram showing data flow
- Complete test results archived for analysis and productionization planning
- Setup instructions: Python environment, package installation, OpenRouter API key configuration

**Data Source Integration:**
- Test inputs stored in `documentation/document/` directory (all 5 input sources as PDFs or markdown)
- Input loading via LangChain PyPDFLoader or UnstructuredMarkdownLoader
- Stage 1-3: Process inputs from `documentation/document/` only (offline analysis)
- Stage 2 Trend Extraction: Analyze document content for patterns, recurring themes, industry signals - NO social media API access
- Stage 4 Brand Research: Load pre-existing comprehensive research files from `docs/web-search-setup/` directory
- Research data structure: Each brand has 8-section markdown file (~550-720 lines) covering positioning, portfolio, innovations, strategy, customers, sustainability, competitive context, and recent news with 45+ cited sources
- Research files: `lactalis-canada-research.md`, `mccormick-usa-research.md`, `columbia-sportswear-research.md`, `decathlon-research.md`

**Error Handling:**
- Log all errors to stage-specific log files
- Continue pipeline execution on non-fatal errors (record degraded output)
- Fatal errors halt pipeline and require manual intervention

**Demo Build Philosophy:**
- **Speed over perfection** - This is a rapid validation demo, not production software
- **Leverage existing frameworks** - LangChain provides 80% of infrastructure out-of-the-box
- **Hardcode where appropriate** - Brand profiles as simple YAML, fixed 5-stage sequence, no dynamic configuration
- **Manual intervention acceptable** - If a stage fails, manual retry is fine for 20 test runs
- **"Make it work, then make it better"** - Get end-to-end pipeline running first, optimize second
- **Copy-paste patterns** - Use LangChain cookbook examples rather than building custom abstractions

**Rationale:** These assumptions minimize external dependencies, leverage existing infrastructure, and prioritize validation speed over production quality. The "simple but effective" approach enables rapid hypothesis testing (target: buildable in 1-2 weeks) without over-engineering. This is a throwaway demo to validate business assumptions, not a foundation for production system.

---

## Epic List

### Epic 1: Foundation & Data Setup
**Goal:** Establish repository structure, organize test inputs, create brand profiles, and set up basic pipeline infrastructure to enable pipeline development.

### Epic 2: Document Processing Pipeline (Stages 1-3)
**Goal:** Build offline document analysis stages that transform raw input documents from `documentation/document/` into brand-agnostic universal insights and lessons.

### Epic 3: Brand Contextualization with Web Research (Stage 4)
**Goal:** Implement web search integration and brand contextualization stage that transforms universal insights into brand-specific strategic recommendations using live brand research.

### Epic 4: Opportunity Generation & Complete Testing (Stage 5)
**Goal:** Build opportunity generation stage, create opportunity card format with visuals and follow-up prompts, and execute full 20-test validation run with quality assessment.

---

## Epic 1: Foundation & Data Setup

**Expanded Goal:** Establish complete repository infrastructure, organize all test input documents, create comprehensive brand profiles for 4 brands, set up Python environment with LangChain, and build basic execution scaffolding. This epic delivers a testable foundation where any subsequent stage implementation can immediately run and produce outputs.

### Story 1.1: Repository Structure and Python Environment Setup

As a **developer**,
I want **a clean repository structure with Python virtual environment and all LangChain dependencies installed**,
so that **I can immediately start building pipeline stages without configuration overhead**.

#### Acceptance Criteria

1. Directory structure created matching Technical Assumptions spec (`/pipeline/`, `/data/`, `/templates/`, `run_pipeline.py`, etc.)
2. Python 3.10+ virtual environment created with `requirements.txt` containing: `langchain`, `langchain-openai`, `langchain-community`, `openai`, `pypdf`, `pyyaml`, `jinja2`
3. `.env.template` file created documenting required environment variables (OPENROUTER_API_KEY, OPENROUTER_BASE_URL)
4. `.gitignore` configured to exclude virtual environment, `.env`, and test output files
5. Basic `README.md` created with setup instructions and quick-start commands
6. Successful test: `python -c "import langchain; from langchain_openai import ChatOpenAI; print('Environment ready')"` executes without errors

### Story 1.2: Test Input Document Organization

As a **pipeline developer**,
I want **all 5 test input documents organized in `documentation/document/` with standardized naming and metadata**,
so that **the pipeline can reliably load inputs for testing**.

#### Acceptance Criteria

1. All 5 input documents placed in `documentation/document/`:
   - `savannah-bananas.pdf` - Case study
   - `premium-fast-food-trend.pdf` - Trend report
   - `combined-trends-nonalcoholic-sacred-sync.pdf` - Combined trends
   - `cat-dad-campaign.pdf` - Spotted innovation
   - `qr-garment-resale.pdf` - Spotted innovation
2. Input manifest file created (`data/input-manifest.yaml`) listing each input with metadata: id, filename, type, description
3. Test script created (`test_input_loading.py`) that successfully loads each input using PyPDFLoader and prints character count
4. All inputs load without errors and contain minimum 100 characters of content
5. Documentation updated in `README.md` explaining how to add new test inputs

### Story 1.3: Brand Profile Creation for 4 Test Brands

As a **pipeline developer**,
I want **comprehensive YAML brand profiles for Lactalis Canada, McCormick USA, Columbia Sportswear, and Decathlon**,
so that **Stage 4 can contextualize opportunities with accurate brand information**.

#### Acceptance Criteria

1. Four brand profile YAML files created in `data/brand-profiles/`:
   - `lactalis-canada.yaml`
   - `mccormick-usa.yaml`
   - `columbia-sportswear.yaml`
   - `decathlon.yaml`
2. Each profile contains minimum fields:
   - `brand_name` (string)
   - `country` (string)
   - `industry` (string)
   - `positioning` (1-2 sentence string)
   - `product_portfolio` (list of strings)
   - `target_customers` (list of strings)
   - `recent_innovations` (list of strings, 2-3 examples)
   - `strategic_priorities` (list of strings)
   - `brand_values` (list of strings)
3. Brand profile schema documented in `docs/brand-profile-schema.md` with field descriptions and examples
4. Test script (`test_brand_profiles.py`) validates YAML syntax and required fields for all 4 profiles
5. All profiles load successfully with PyYAML without errors

### Story 1.4: Output Directory Structure and Logging Setup

As a **pipeline developer**,
I want **structured output directories and logging configuration**,
so that **test runs store results in organized fashion and execution is traceable**.

#### Acceptance Criteria

1. Output directory structure created: `data/test-outputs/{input-id}-{brand-id}-{timestamp}/`
2. Each test run directory contains subdirectories: `stage1/`, `stage2/`, `stage3/`, `stage4/`, `stage5/`, `logs/`
3. Logging configuration implemented in `pipeline/utils.py`:
   - Console logging at INFO level
   - File logging at DEBUG level to `logs/pipeline.log` in test output directory
   - Separate error log at `logs/errors.log`
4. Helper function `create_test_output_dir(input_id, brand_id)` returns path to new test run directory
5. Test script validates directory creation and log file writing
6. Git commit includes `.gitkeep` files in empty directories to preserve structure

### Story 1.5: Basic Pipeline Execution Script Scaffolding

As a **pipeline developer**,
I want **a runnable `run_pipeline.py` script with argument parsing and basic flow**,
so that **I can execute test runs before pipeline stages are implemented**.

#### Acceptance Criteria

1. `run_pipeline.py` created with argparse configuration:
   - `--input` (required for single run): input document ID
   - `--brand` (required for single run): brand profile ID
   - `--batch`: flag to run all 20 test scenarios
   - `--verbose`: flag for debug-level logging
2. Script validates inputs: checks input file exists, checks brand profile exists, creates output directory
3. Placeholder execution: prints "Executing pipeline for {input} + {brand}" and creates empty stage output files
4. Batch mode iterates through all combinations of 5 inputs × 4 brands
5. Successful execution: `python run_pipeline.py --input savannah-bananas --brand lactalis` completes without errors and creates output directory
6. Help documentation: `python run_pipeline.py --help` displays usage instructions

---

## Epic 2: Document Processing Pipeline (Stages 1-3)

**Expanded Goal:** Implement the three offline document analysis stages that transform raw PDF/markdown inputs into brand-agnostic universal insights. Each stage is a LangChain LLMChain with specific prompting strategy. Epic delivers a functional pipeline that can process any input document and generate high-quality universal lessons without external dependencies.

### Story 2.1: Stage 1 - Input Processing and Inspiration Identification

As a **pipeline developer**,
I want **Stage 1 implemented as a LangChain LLMChain that reviews input documents and identifies key inspiration elements**,
so that **the pipeline can extract the most relevant insights from diverse input types**.

#### Acceptance Criteria

1. File created: `pipeline/stages/stage1_input_processing.py` with `Stage1Chain` class
2. LangChain PromptTemplate defined in `pipeline/prompts/stage1_prompt.py` with instructions:
   - Review input document thoroughly
   - Identify 3-5 key inspiration elements (innovations, strategies, successful tactics)
   - For each inspiration, note: what it is, why it's interesting, potential applicability
   - Summarize overall context and significance
3. Stage 1 chain uses ChatOpenAI configured for OpenRouter (Claude Sonnet 4.5 via anthropic/claude-sonnet-4.5) with temperature=0.3 for consistency
4. Output format: Structured markdown with sections: "Document Overview", "Key Inspirations" (numbered list), "Context Notes"
5. Stage 1 integrated into `run_pipeline.py` with output saved to `stage1/inspiration-analysis.md`
6. Test execution: Run on Savannah Bananas input, verify output contains 3-5 inspirations with descriptions
7. Stage output passes through to Stage 2 successfully

### Story 2.2: Stage 2 - Trend Extraction from Document Content

As a **pipeline developer**,
I want **Stage 2 implemented to extract trend patterns from document content without external social media data**,
so that **the pipeline can amplify signals using only the information present in input documents**.

#### Acceptance Criteria

1. File created: `pipeline/stages/stage2_signal_amplification.py` with `Stage2Chain` class
2. LangChain PromptTemplate defined in `pipeline/prompts/stage2_prompt.py` with methodology:
   - Analyze Stage 1 inspirations for recurring themes and patterns
   - Identify underlying trends: consumer behavior shifts, industry movements, emerging needs
   - Extract relevant broader context (industry trends mentioned in document)
   - Categorize trends by: behavioral, technological, cultural, economic
3. Trend extraction methodology documented in `docs/stage2-trend-methodology.md` explaining pattern recognition approach
4. Stage 2 chain receives Stage 1 output as input variable
5. Output format: Structured markdown with sections: "Identified Trends" (bulleted with categories), "Signal Strength Assessment" (high/medium/low per trend), "Trend Context"
6. Stage 2 integrated into `run_pipeline.py` with output saved to `stage2/trend-analysis.md`
7. Test execution: Run on Savannah Bananas → Stage 1 → Stage 2, verify trends extracted without requiring external data
8. Manual review confirms trends are derived from document content, not LLM general knowledge

### Story 2.3: Stage 3 - General Translation to Universal Lessons

As a **pipeline developer**,
I want **Stage 3 implemented to translate inspirations and trends into brand-agnostic universal principles**,
so that **Stage 4 can apply these principles to any brand context**.

#### Acceptance Criteria

1. File created: `pipeline/stages/stage3_general_translation.py` with `Stage3Chain` class
2. LangChain PromptTemplate defined in `pipeline/prompts/stage3_prompt.py` with instructions:
   - Synthesize Stage 1 inspirations + Stage 2 trends into universal lessons
   - De-contextualize: remove specific brand/industry references, extract underlying principles
   - Generate 5-7 universal lessons applicable across industries
   - For each lesson: principle statement + why it works + where it could apply
3. Optional: Integration with innovation frameworks from `documentation/document/` (TRIZ, SIT, biomimicry) - reference frameworks in prompt if helpful
4. Stage 3 chain receives Stage 1 + Stage 2 outputs as concatenated input
5. Output format: Structured markdown with section "Universal Lessons" (numbered list with sub-bullets for explanation and applicability)
6. Stage 3 integrated into `run_pipeline.py` with output saved to `stage3/universal-lessons.md`
7. Test execution: Run full pipeline Stages 1-3 on Savannah Bananas, verify lessons are brand-agnostic (no mention of baseball or specific brand)
8. Quality check: Manual review confirms lessons are actionable and truly universal (could apply to CPG, retail, services, etc.)

### Story 2.4: Stages 1-3 Integration Testing and Refinement

As a **pipeline developer**,
I want **integration testing across all 3 document processing stages with prompt refinement**,
so that **the offline pipeline produces high-quality universal insights consistently**.

#### Acceptance Criteria

1. Integration test script created: `test_stages_1_3.py` that runs full Stage 1-3 pipeline on all 5 inputs
2. Test execution generates 5 sets of outputs (one per input) in `data/test-outputs/integration-test-stages-1-3/`
3. Quality checklist created for manual review (`docs/stage-1-3-quality-checklist.md`):
   - Stage 1: Are inspirations specific and actionable?
   - Stage 2: Are trends derived from document (not hallucinated)?
   - Stage 3: Are lessons truly universal (de-contextualized)?
4. Manual quality review completed on all 5 outputs using checklist
5. Prompt refinements implemented based on quality review findings
6. Re-run integration test after prompt refinement, verify quality improvements
7. Documentation updated: Each stage's PromptTemplate documented with rationale for key instructions
8. Success metric: 4 out of 5 inputs produce "good quality" outputs (pass quality checklist)

---

## Epic 3: Brand Contextualization with Research Data (Stage 4)

**Expanded Goal:** Implement Stage 4 that transforms brand-agnostic universal lessons into brand-specific strategic insights using pre-existing research data. This is the critical differentiation stage - same input must generate meaningfully different outputs for each brand. Epic delivers proof that contextualization works and research data integration is functional.

### Story 3.1: Pre-Existing Research Data Integration

As a **pipeline developer**,
I want **to load and access pre-existing research data from local files**,
so that **Stage 4 can use completed brand research without live web searches**.

#### Acceptance Criteria

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

### Story 3.2: Stage 4 - Brand Research and Contextualization Chain

As a **pipeline developer**,
I want **Stage 4 implemented as LangChain LLMChain using pre-existing research data**,
so that **universal lessons are customized for specific brand context using completed brand research**.

#### Acceptance Criteria

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

### Story 3.3: Multi-Brand Testing and Differentiation Validation

As a **pipeline developer**,
I want **Stage 4 tested across all 4 brands with the same input to validate differentiation**,
so that **we can prove brand contextualization generates meaningfully different outputs**.

#### Acceptance Criteria

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

### Story 3.4: Complete Pipeline (Stages 1-4) Integration Testing

As a **pipeline developer**,
I want **full Stages 1-4 pipeline tested on multiple input/brand combinations**,
so that **the end-to-end flow is validated before building Stage 5**.

#### Acceptance Criteria

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

## Epic 4: Opportunity Generation & Complete Testing (Stage 5)

**Expanded Goal:** Implement Stage 5 that transforms brand-specific insights into 5 actionable opportunity cards with descriptions, visuals, and follow-up prompts. Execute complete 20-test validation run (5 inputs × 4 brands), conduct quality assessment, and validate business hypothesis. Epic delivers final validation of whether the pipeline produces opportunities worth paying for.

### Story 4.1: Opportunity Card Format and Template Design

As a **product manager**,
I want **a defined opportunity card format with Jinja2 template**,
so that **Stage 5 generates consistent, visually structured outputs**.

#### Acceptance Criteria

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

### Story 4.2: Stage 5 - Opportunity Generation Chain

As a **pipeline developer**,
I want **Stage 5 implemented to generate exactly 5 distinct opportunity cards from brand-specific insights**,
so that **the pipeline delivers its core value proposition: actionable innovation opportunities**.

#### Acceptance Criteria

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

### Story 4.3: Complete 20-Test Batch Execution

As a **product manager**,
I want **the full pipeline executed on all 20 test scenarios (5 inputs × 4 brands) with batch automation**,
so that **I have complete dataset of 100 opportunity cards for validation**.

#### Acceptance Criteria

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

### Story 4.4: Quality Assessment and Business Hypothesis Validation

As a **product manager**,
I want **structured quality assessment of all 100 opportunity cards using scoring rubric**,
so that **I can validate whether pipeline outputs justify customer payment**.

#### Acceptance Criteria

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

### Story 4.5: Documentation and Handoff for Productionization

As a **future product manager/developer**,
I want **complete documentation of pipeline architecture, findings, and recommendations**,
so that **I can build production version based on validated demo**.

#### Acceptance Criteria

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

## Checklist Results Report

*Checklist execution pending - run PM checklist to validate PRD completeness before handoff to architect.*

---

## Next Steps

### Architect Prompt

Now that the PRD is complete, please proceed with technical architecture design:

**Prompt for Solution Architect:**

> I need you to design the technical architecture for the Innovation Intelligence Pipeline Testing System based on the PRD at `docs/prd.md`.
>
> **Key Requirements:**
> - **LangChain-based pipeline** with 5 sequential stages (SequentialChain)
> - **Python 3.10+** implementation
> - **LLM Provider:** OpenRouter for Claude Sonnet 4.5 access (using langchain-openai)
> - **Stages 1-3:** Offline document processing (PDF input from `documentation/document/`)
> - **Stage 4:** Offline with pre-existing research data integration from local files
> - **Stage 5:** Opportunity generation with Jinja2 templating
> - **Execution:** Single test (`python run_pipeline.py --input X --brand Y`) and batch mode (`--batch` for all 20 tests)
> - **Output:** 100 opportunity cards total (20 tests × 5 opportunities each)
>
> **Focus Areas:**
> 1. LangChain chain architecture - how stages connect and pass context
> 2. OpenRouter integration with ChatOpenAI configuration
> 3. Brand profile YAML schema
> 4. Opportunity card output format (markdown with frontmatter)
> 5. Research data loading approach from local files
> 6. Error handling strategy for non-fatal failures
> 7. Logging and intermediate output storage
>
> **Deliverables:**
> - Architecture document (`docs/architecture.md`) with chain diagrams
> - Data models for brand profiles and opportunity cards
> - File structure specification
> - LangChain component specifications for each stage
> - OpenRouter configuration details
>
> **Constraints:**
> - This is a throwaway demo for validation (1-2 week build target)
> - Prioritize simplicity over production quality
> - No database - file-based storage only
> - Manual quality review acceptable
>
> Please create the architecture document based on the complete PRD.

---

**PRD Status:** ✅ Complete - Ready for Architecture Phase

**Document Version:** 1.0
**Last Updated:** 2025-10-03
**Next Owner:** Solution Architect
**Approval Status:** Awaiting stakeholder review
