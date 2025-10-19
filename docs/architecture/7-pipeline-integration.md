# 7. Pipeline Integration

## 7.1 Python Pipeline Modifications

**Minimal changes to `scripts/run_pipeline.py`:**

```python
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

    # Run stages 1-5 (COMPLETELY UNCHANGED)
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
