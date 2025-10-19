# 9. Dependencies & Prerequisites

## 9.1 External Services

**Vercel Account**
- Free tier supports Blob storage and deployments
- Required: `BLOB_READ_WRITE_TOKEN` (auto-generated on first deploy)

**OpenRouter Account**
- API key required for LLM access
- Model: `anthropic/claude-sonnet-4.5`
- Cost: ~$0.50 per pipeline run

**GitHub Repository**
- Code versioning
- Vercel auto-deploy on push to main

## 9.2 Existing Assets

**Pipeline Code (Python)**
- All 5 stages fully implemented in `/pipeline/stages/`
- Utilities in `/pipeline/utils.py`
- Execution script in `/scripts/run_pipeline.py`

**Brand Profiles (JSON)**
- Located in `/data/brand-profiles/`
- 4 brands: lactalis-canada, mccormick-usa, decathlon, columbia-sportswear

**Research Data (Markdown)**
- Located in `/data/brand-research/`
- Market intelligence per brand

**Test Inputs (PDF)**
- Located in `/data/test-inputs/`
- Example: `savannah-bananas.pdf`

---
