# Epic 1: Foundation & Data Setup

**Expanded Goal:** Establish complete repository infrastructure, organize all test input documents, create comprehensive brand profiles for 4 brands, set up Python environment with LangChain, and build basic execution scaffolding. This epic delivers a testable foundation where any subsequent stage implementation can immediately run and produce outputs.

## Story 1.1: Repository Structure and Python Environment Setup

As a **developer**,
I want **a clean repository structure with Python virtual environment and all LangChain dependencies installed**,
so that **I can immediately start building pipeline stages without configuration overhead**.

### Acceptance Criteria

1. Directory structure created matching Technical Assumptions spec (`/pipeline/`, `/data/`, `/templates/`, `run_pipeline.py`, etc.)
2. Python 3.10+ virtual environment created with `requirements.txt` containing: `langchain`, `langchain-openai`, `langchain-community`, `openai`, `pypdf`, `pyyaml`, `jinja2`
3. `.env.template` file created documenting required environment variables (OPENROUTER_API_KEY, OPENROUTER_BASE_URL)
4. `.gitignore` configured to exclude virtual environment, `.env`, and test output files
5. Basic `README.md` created with setup instructions and quick-start commands
6. Successful test: `python -c "import langchain; from langchain_openai import ChatOpenAI; print('Environment ready')"` executes without errors

## Story 1.2: Test Input Document Organization

As a **pipeline developer**,
I want **all 5 test input documents organized in `documentation/document/` with standardized naming and metadata**,
so that **the pipeline can reliably load inputs for testing**.

### Acceptance Criteria

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

## Story 1.3: Brand Profile Creation for 4 Test Brands

As a **pipeline developer**,
I want **comprehensive YAML brand profiles for Lactalis Canada, McCormick USA, Columbia Sportswear, and Decathlon**,
so that **Stage 4 can contextualize opportunities with accurate brand information**.

### Acceptance Criteria

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

## Story 1.4: Output Directory Structure and Logging Setup

As a **pipeline developer**,
I want **structured output directories and logging configuration**,
so that **test runs store results in organized fashion and execution is traceable**.

### Acceptance Criteria

1. Output directory structure created: `data/test-outputs/{input-id}-{brand-id}-{timestamp}/`
2. Each test run directory contains subdirectories: `stage1/`, `stage2/`, `stage3/`, `stage4/`, `stage5/`, `logs/`
3. Logging configuration implemented in `pipeline/utils.py`:
   - Console logging at INFO level
   - File logging at DEBUG level to `logs/pipeline.log` in test output directory
   - Separate error log at `logs/errors.log`
4. Helper function `create_test_output_dir(input_id, brand_id)` returns path to new test run directory
5. Test script validates directory creation and log file writing
6. Git commit includes `.gitkeep` files in empty directories to preserve structure

## Story 1.5: Basic Pipeline Execution Script Scaffolding

As a **pipeline developer**,
I want **a runnable `run_pipeline.py` script with argument parsing and basic flow**,
so that **I can execute test runs before pipeline stages are implemented**.

### Acceptance Criteria

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
