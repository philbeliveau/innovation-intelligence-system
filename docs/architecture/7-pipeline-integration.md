# 7. Pipeline Integration

**Last Updated:** 2025-10-25
**Status:** ✅ Prisma-First Architecture Implemented

## 7.1 Prisma-First Backend Integration

### Overview

The Python backend now writes pipeline status to **Prisma database via HTTP API** instead of file-based status management. This creates a single source of truth for pipeline execution state.

### Backend Architecture

```
Python Pipeline (Railway)
  ↓ Stage completion
PrismaAPIClient (HTTP)
  ↓ POST /api/pipeline/:runId/stage-update
Next.js API Route (Vercel)
  ↓ prisma.stageOutput.upsert()
PostgreSQL (Prisma)
```

### PrismaAPIClient Usage

**File:** `backend/app/prisma_client.py`

```python
from app.prisma_client import PrismaAPIClient

def execute_pipeline_background(run_id: str, pdf_path: str, brand_profile: dict):
    """Execute 5-stage pipeline with Prisma status updates."""

    # Initialize Prisma API client
    prisma_client = PrismaAPIClient()
    current_stage = 1

    try:
        # Initialize all stages (stage 1 = PROCESSING)
        prisma_client.initialize_pipeline_stages(run_id)

        # Extract PDF text
        input_text = extract_text_from_pdf(pdf_path)

        # Stage 1: Input Processing
        logger.info(f"[{run_id}] Starting Stage 1")
        stage1 = Stage1Chain()
        stage1_result = stage1.run(input_text)

        # Save locally for debugging
        save_stage_output(run_id, 1, stage1_result)

        # Mark complete in Prisma
        prisma_client.mark_stage_complete(run_id, 1, stage1_result)

        # Stage 2: Signal Amplification
        current_stage = 2
        prisma_client.mark_stage_processing(run_id, 2)

        stage2 = Stage2Chain()
        stage2_result = stage2.run(stage1_result['stage1_output'])

        save_stage_output(run_id, 2, stage2_result)
        prisma_client.mark_stage_complete(run_id, 2, stage2_result)

        # ... stages 3, 4, 5 follow same pattern

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        # Mark failed stage in Prisma (auto-marks PipelineRun as FAILED)
        prisma_client.mark_stage_failed(run_id, current_stage, str(e))
```

### PrismaAPIClient Methods

```python
class PrismaAPIClient:
    """HTTP client for Prisma API endpoints."""

    def initialize_pipeline_stages(run_id: str) -> bool:
        """Initialize stage 1 as PROCESSING."""

    def mark_stage_processing(run_id: str, stage_number: int) -> bool:
        """Mark stage as currently processing."""

    def mark_stage_complete(run_id: str, stage_number: int, output_data: Any) -> bool:
        """Mark stage as completed with output."""

    def mark_stage_failed(run_id: str, stage_number: int, error_message: str) -> bool:
        """Mark stage as failed with error."""
```

### Auto-Update Logic

**Stage 5 Completion:**
```python
prisma_client.mark_stage_complete(run_id, 5, stage5_result)
# → PipelineRun.status = COMPLETED
# → PipelineRun.completedAt = now()
```

**Any Stage Failure:**
```python
prisma_client.mark_stage_failed(run_id, 3, "LLM timeout")
# → PipelineRun.status = FAILED
# → PipelineRun.completedAt = now()
```

---

## 7.2 Python Pipeline Modifications (Legacy Reference)

**NOTE:** This section describes the original file-based approach. See section 7.1 for current Prisma-first implementation.

### Minimal changes to `scripts/run_pipeline.py` (OUTDATED):

```python
# OLD APPROACH - NO LONGER USED
# Files now only saved locally for debugging
# Status tracking done via Prisma API

# Add new CLI arguments
parser.add_argument('--input-file', type=str, help='Direct PDF file path')
parser.add_argument('--run-id', type=str, help='Unique run identifier')

def run_from_file(input_file_path: str, brand_id: str, run_id: str):
    """Execute pipeline from uploaded file."""

    # Create output directory with run_id
    output_dir = Path(f"data/test-outputs/{run_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup logging
    setup_pipeline_logging(output_dir)

    # Read PDF directly
    from pypdf import PdfReader
    reader = PdfReader(input_file_path)
    input_text = "".join(page.extract_text() for page in reader.pages)

    # Load brand data (UNCHANGED)
    brand_profile = load_brand_profile(brand_id)
    research_data = load_research_data(brand_id)

    # Run stages 1-5 (NOW WITH PRISMA API CALLS)
    logging.info("Starting Stage 1: Input Processing")
    stage1 = create_stage1_chain()
    result1 = stage1.run(input_text)
    stage1.save_output(result1['stage1_output'], output_dir)

    logging.info("Starting Stage 2: Signal Amplification")
    stage2 = create_stage2_chain()
    result2 = stage2.run(result1['stage1_output'])
    stage2.save_output(result2['stage2_output'], output_dir)

    # ... stages 3, 4, 5 (UNCHANGED)
```

**Stage 1 Output Modification:**

For the 2-track UI, Stage 1 must output structured JSON:

```python
# pipeline/stages/stage1_input_processing.py

def save_output(self, output: str, output_dir: Path) -> Path:
    """Save Stage 1 output with structured inspirations."""

    # Parse LLM output to extract 2 inspirations
    inspirations = parse_inspirations(output)

    # Save markdown (existing format)
    markdown_path = output_dir / "stage1" / "inspiration-analysis.md"
    markdown_path.write_text(output, encoding='utf-8')

    # Save JSON for API consumption
    json_path = output_dir / "stage1" / "inspirations.json"
    json_data = {
        "inspiration_1": {
            "title": inspirations[0]['title'],
            "content": inspirations[0]['content'],
            "key_elements": inspirations[0]['key_elements']
        },
        "inspiration_2": {
            "title": inspirations[1]['title'],
            "content": inspirations[1]['content'],
            "key_elements": inspirations[1]['key_elements']
        },
        "completed_at": datetime.now().isoformat()
    }
    json_path.write_text(json.dumps(json_data, indent=2), encoding='utf-8')

    return markdown_path
```

---

## 7.2 Stage Output Formats

**Stage 1: `inspirations.json`**
```json
{
  "inspiration_1": {
    "title": "Experience Theater",
    "content": "The Savannah Bananas have transformed...",
    "key_elements": ["Theatrical presentation", "Choreographed interactions", "Post-game experiences"]
  },
  "inspiration_2": {
    "title": "Community Building",
    "content": "Creating a sense of belonging...",
    "key_elements": ["Fan-first entertainment", "Social media integration", "Viral moment creation"]
  }
}
```

**Stages 2-5: Markdown only** (consumed by results page, not real-time UI)

---
