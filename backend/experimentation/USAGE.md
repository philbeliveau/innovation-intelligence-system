# Gradio Experimentation Lab - Usage Guide

## Overview

The Gradio Experimentation Lab provides a web-based interface for running the Innovation Intelligence pipeline. Non-technical innovation researchers can upload trend reports, configure brand profiles, and generate opportunity concepts without writing code.

## Quick Start

### 1. Install Dependencies

```bash
cd backend/experimentation
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export BACKEND_API_URL="http://localhost:8000"
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export OPENROUTER_API_KEY="your_api_key"
```

### 3. Launch Interface

```bash
python gradio_lab.py
```

Access at: `http://localhost:7860`

## Interface Guide

### PDF Upload

1. **Drag and drop** or **click** to upload trend report (PDF, max 50MB)
2. Wait for extraction confirmation: `✅ Extracted X characters from Y pages`
3. If extraction fails, check:
   - File is valid PDF (not image-based)
   - File size under 50MB
   - PDF not password-protected

### Brand Profile Selection

**Option 1: Pre-configured Brands (Dropdown)**
- Select from: Lactalis Canada, Decathlon, Colombia Sportswear, McCormick USA
- Fields auto-populate from YAML profiles

**Option 2: Upload Custom YAML**
- Drag and drop `.yaml` or `.yml` file
- Required fields: `brand_name`, `country`, `industry`, `product_portfolio`
- Example format:
  ```yaml
  brand_name: "My Brand"
  country: "USA"
  industry: "Food & Beverage"
  product_portfolio:
    - "Product A"
    - "Product B"
  ```

**Option 3: Manual Entry**
- Select "Custom (Manual Entry)" from dropdown
- Fill in fields manually:
  - Company Name (required)
  - Industry (required)
  - Geography (required)
  - Product Portfolio (one per line)

### Running Pipeline

1. Ensure PDF extracted and brand configured
2. Click **"▶️ Run Pipeline"**
3. Watch real-time progress:
   - Stage 0: Brand enrichment (14%)
   - Stage 1: Trend extraction (28%)
   - Stage 2: Consumer insights (42%)
   - Stage 3: Technique matching (57%)
   - Stage 4: Concept generation (71%)
   - Stage 5: Competitive intel (85%)
   - Stage 6: Opportunity cards (100%)
4. View outputs in tabbed interface

### Reviewing Outputs

**Stage 0-5 (JSON):**
- Syntax-highlighted JSON
- Expandable for readability
- Copy/paste for external analysis

**Stage 6 (Markdown):**
- Formatted opportunity cards
- Human-readable summaries
- Ready for presentation

### Quality Tagging

1. Review pipeline outputs
2. Select quality tag:
   - **Good**: High-quality, useful outputs (auto-exported for few-shot learning)
   - **Needs Work**: Acceptable but requires refinement
   - **Failed**: Poor quality or incorrect outputs
3. Add optional notes (observations, issues, feedback)
4. Click **"💾 Save Experiment"**
5. Confirmation: `✅ Experiment saved successfully!`

## Troubleshooting

### PDF Extraction Fails

**Issue:** `❌ PDF extraction failed`

**Solutions:**
- Verify file is valid PDF (not corrupted)
- Check if PDF is image-based (requires OCR)
- Ensure PyPDF2 installed: `pip install PyPDF2`

### Brand Profile Not Found

**Issue:** `⚠️ Brand profile not found`

**Solutions:**
- Verify YAML file exists in `/data/brand-profiles/`
- Check filename matches dropdown selection
- Validate YAML syntax

### Pipeline Execution Fails

**Issue:** `❌ Pipeline failed: [error message]`

**Solutions:**
- Check backend API running at `BACKEND_API_URL`
- Verify `OPENROUTER_API_KEY` environment variable set
- Ensure all required fields filled in
- Check network connectivity

### Database Save Fails

**Issue:** `❌ Save failed`

**Solutions:**
- Verify `DATABASE_URL` environment variable
- Check database connection
- Ensure PostgreSQL running
- Validate experiment data format

## Advanced Features

### Session Caching

- PDF text cached after first extraction
- Reload same PDF without re-extraction
- Clear cache by uploading new file

### Few-Shot Learning Export

- "Good" tagged experiments auto-exported
- Location: `/backend/experimentation/successful_examples/`
- Organized by stage: `stage_0/`, `stage_1/`, etc.
- Used for future prompt enhancement

### Public Sharing

Enable Gradio share link for remote access:

```python
# In gradio_lab.py, change:
lab.launch(share=True)
```

Generates public URL valid for 72 hours.

## Configuration

### Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `BACKEND_API_URL` | Yes | `http://localhost:8000` | FastAPI backend |
| `DATABASE_URL` | Yes | None | PostgreSQL connection |
| `OPENROUTER_API_KEY` | Yes | None | LLM API access |
| `GRADIO_SERVER_PORT` | No | `7860` | Port for interface |
| `GRADIO_SERVER_NAME` | No | `0.0.0.0` | Bind address |
| `GRADIO_SHARE` | No | `false` | Public share link |

### Queue Settings

Configured for concurrent usage:
- Max queue size: 10 users
- Max concurrent pipelines: 3
- Status update rate: Auto

Modify in `gradio_lab.py`:
```python
demo.queue(
    max_size=10,
    default_concurrency_limit=3
)
```

## Testing

Run test suite:

```bash
cd backend
pytest tests/experimentation/test_gradio_lab.py -v
```

Test coverage:
- PDF upload and extraction
- Brand profile loading (all 3 methods)
- Pipeline execution workflow
- Quality tagging and database save
- Error handling scenarios

## Next Steps

- **Story 11.2**: Pipeline implementation (7 stages)
- **Story 11.3**: Few-shot learning system
- **Story 11.4**: Experiment database operations

## Support

For issues or questions:
1. Check this usage guide
2. Review `/docs/architecture/gradio-implementation-guide.md`
3. Check Story 11.1: `/docs/stories/11.1.gradio-experimentation-ui.md`
4. Contact development team

---

**Last Updated:** 2025-11-20
**Version:** 1.0
**Story:** 11.1 - Gradio Experimentation UI
