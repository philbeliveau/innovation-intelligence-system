# Technical Assumptions

## Repository Structure: Monorepo

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

## Service Architecture

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

## Testing Requirements

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

## Additional Technical Assumptions and Requests

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
