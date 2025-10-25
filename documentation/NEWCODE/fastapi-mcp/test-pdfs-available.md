# Test PDFs Available for Pipeline Testing

## Overview

The Innovation Intelligence System repository includes **6 real-world PDF documents** for testing the pipeline. These are trend reports and case studies suitable for CPG innovation analysis.

**Location:** `data/document/`

---

## Available Test Documents

### 1. **cat-dad-campaign.pdf** (133 KB)
- **Topic:** Cat Dad marketing campaign
- **Type:** Marketing case study
- **Best for:** Testing campaign analysis and consumer insights
- **Recommended brands:** All brands (general marketing innovation)

### 2. **nonalcoholic-beverage-trend.pdf** (1.3 MB)
- **Topic:** Non-alcoholic beverage market trends
- **Type:** Industry trend report
- **Best for:** Testing beverage innovation analysis
- **Recommended brands:**
  - lactalis-canada (dairy-based non-alcoholic drinks)
  - mccormick-usa (flavor innovations for beverages)

### 3. **premium-fast-food-trend.pdf** (2.2 MB)
- **Topic:** Premium fast food trends
- **Type:** Industry analysis
- **Best for:** Testing food service innovation
- **Recommended brands:**
  - mccormick-usa (spice/seasoning for premium food)
  - lactalis-canada (premium dairy products for food service)

### 4. **qr-garment-resale.pdf** (590 KB)
- **Topic:** QR code technology for garment resale
- **Type:** Technology trend report
- **Best for:** Testing sustainability and tech innovation
- **Recommended brands:**
  - decathlon (sustainable sports equipment)
  - columbia-sportswear (outdoor apparel resale)

### 5. **sacred-sync-trend.pdf** (1.3 MB)
- **Topic:** Sacred synchronization trend (wellness/mindfulness)
- **Type:** Consumer trend report
- **Best for:** Testing wellness innovation analysis
- **Recommended brands:**
  - decathlon (mindful movement, accessible sports)
  - All brands (wellness positioning)

### 6. **savannah-bananas.pdf** (143 KB)
- **Topic:** Savannah Bananas experiential baseball
- **Type:** Experience innovation case study
- **Best for:** Testing experiential marketing concepts
- **Recommended brands:**
  - lactalis-canada (experience theater positioning)
  - All brands (fan engagement innovation)

---

## How to Use These PDFs with MCP Tools

### Option 1: Upload to Vercel Blob (Required for Pipeline)

Since `run_pipeline` requires a Vercel Blob URL, you need to:

**Step 1: Upload via Frontend**
```bash
# Navigate to the upload page
open https://innovation-web-rho.vercel.app/upload

# Or locally if running dev server
open http://localhost:3000/upload
```

**Step 2: Select a PDF from `data/document/`**
- Choose one of the 6 PDFs listed above
- Upload through the web interface
- Copy the resulting blob URL

**Step 3: Use the blob URL with MCP**
```
Ask Claude: "Run the pipeline with this blob URL: [paste URL] using lactalis-canada"

Claude will call: run_pipeline(blob_url="https://blob.vercel-storage.com/...", brand_id="lactalis-canada")
```

---

### Option 2: Direct API Testing (For Development)

For testing the API directly without MCP:

```bash
# 1. First, upload a PDF to get a blob URL
# (Use the frontend or direct Vercel Blob API)

# 2. Then test the pipeline
curl -X POST https://innovation-backend-production.up.railway.app/run \
  -H "Content-Type: application/json" \
  -d '{
    "blob_url": "https://blob.vercel-storage.com/your-file-abc123.pdf",
    "brand_id": "lactalis-canada",
    "run_id": "test-run-001"
  }'
```

---

## Recommended Test Scenarios

### Scenario 1: Quick Test (Small File)
**PDF:** `cat-dad-campaign.pdf` (133 KB)
**Brand:** Any
**Why:** Fastest processing, good for verifying pipeline works

**Test command:**
```
"Upload cat-dad-campaign.pdf and run the pipeline with mccormick-usa"
```

---

### Scenario 2: Beverage Innovation
**PDF:** `nonalcoholic-beverage-trend.pdf` (1.3 MB)
**Brand:** `lactalis-canada` or `mccormick-usa`
**Why:** Perfect alignment with dairy/flavor innovation

**Test command:**
```
"Upload nonalcoholic-beverage-trend.pdf and run with lactalis-canada"
```

**Expected Output:** Opportunities related to:
- Dairy-based non-alcoholic alternatives
- Health-conscious beverage innovations
- Premium positioning strategies

---

### Scenario 3: Sustainability Focus
**PDF:** `qr-garment-resale.pdf` (590 KB)
**Brand:** `decathlon` or `columbia-sportswear`
**Why:** Aligns with outdoor/sports equipment sustainability

**Test command:**
```
"Upload qr-garment-resale.pdf and run with decathlon"
```

**Expected Output:** Opportunities related to:
- Circular economy for sports equipment
- Technology-enabled resale programs
- Sustainability positioning

---

### Scenario 4: Experiential Innovation
**PDF:** `savannah-bananas.pdf` (143 KB)
**Brand:** `lactalis-canada`
**Why:** Tests "experience theater" positioning alignment

**Test command:**
```
"Upload savannah-bananas.pdf and run with lactalis-canada"
```

**Expected Output:** Opportunities related to:
- Fan engagement strategies
- Experiential marketing for CPG
- Community building through experiences

---

### Scenario 5: Wellness Trend
**PDF:** `sacred-sync-trend.pdf` (1.3 MB)
**Brand:** `decathlon`
**Why:** Aligns with "mindful movement" positioning

**Test command:**
```
"Upload sacred-sync-trend.pdf and run with decathlon"
```

**Expected Output:** Opportunities related to:
- Wellness-focused product development
- Mindful sports experiences
- Accessible meditation/movement programs

---

### Scenario 6: Premium Positioning
**PDF:** `premium-fast-food-trend.pdf` (2.2 MB)
**Brand:** `mccormick-usa`
**Why:** Tests premium/accessible innovation balance

**Test command:**
```
"Upload premium-fast-food-trend.pdf and run with mccormick-usa"
```

**Expected Output:** Opportunities related to:
- Premium ingredient positioning
- Accessible premium offerings
- Flavor innovation for food service

---

## Testing Workflow with Claude Code

### Full End-to-End Test

```
User: "I want to test the pipeline with a real PDF"

Claude: [Calls list_brands]
"Available brands:
- lactalis-canada
- mccormick-usa
- decathlon
- columbia-sportswear

I see you have 6 test PDFs in data/document/:
1. cat-dad-campaign.pdf (133 KB) - Marketing case
2. nonalcoholic-beverage-trend.pdf (1.3 MB) - Beverage trends
3. premium-fast-food-trend.pdf (2.2 MB) - Food service
4. qr-garment-resale.pdf (590 KB) - Sustainability tech
5. sacred-sync-trend.pdf (1.3 MB) - Wellness trends
6. savannah-bananas.pdf (143 KB) - Experiential marketing

Which PDF and brand would you like to test?"

User: "Let's use nonalcoholic-beverage-trend.pdf with lactalis-canada"

Claude: "Great choice! This aligns well with Lactalis Canada's dairy focus.

To run the pipeline, you need to:
1. Upload the PDF at: https://innovation-web-rho.vercel.app/upload
2. Copy the blob URL from the response
3. Then I can call run_pipeline with that URL

Would you like me to guide you through the upload process?"
```

---

## Alternative: Create Test Mode (Future Enhancement)

If you want to bypass blob URL validation for testing, we could add:

```python
# backend/app/routes.py

@router.post("/test/run-local-pdf", operation_id="test_run_local_pdf")
async def test_run_local_pdf(pdf_name: str, brand_id: str):
    """Test pipeline with local PDF from data/document/ (development only)"""

    # Map PDF name to local path
    local_pdf = Path(__file__).parent.parent / "data" / "document" / pdf_name

    if not local_pdf.exists():
        raise HTTPException(404, f"PDF not found: {pdf_name}")

    run_id = generate_run_id()

    # Copy to /tmp for processing
    pdf_path = f"/tmp/{run_id}.pdf"
    shutil.copy(local_pdf, pdf_path)

    # Load brand and execute
    brand_profile = load_brand_profile(brand_id)
    thread = Thread(target=execute_pipeline_background, args=(run_id, pdf_path, brand_profile))
    thread.start()

    return {"run_id": run_id, "status": "running", "test_mode": True}
```

**Benefits:**
- No need to upload to Vercel Blob for testing
- Faster iteration during development
- Can test with local PDFs directly

**Drawbacks:**
- Only works in development/testing
- Doesn't test the full upload flow
- Security risk if exposed in production

---

## Summary

**6 Test PDFs Available:**
- ✅ Located in `data/document/`
- ✅ Range from 133 KB to 2.2 MB
- ✅ Cover various CPG innovation topics
- ✅ Aligned with different brand profiles

**To Use Them:**
1. Upload via frontend to get Vercel Blob URL
2. Use blob URL with `run_pipeline` MCP tool
3. Monitor with `get_status` and `list_all_runs`
4. Debug with `get_stage_output` if needed

**Best for Testing:**
- Start with `cat-dad-campaign.pdf` (fastest)
- Match PDF topic to brand positioning
- Use `list_brands` and `get_brand_profile` to understand alignment

**Next Steps:**
1. Upload one of the PDFs via frontend
2. Get the blob URL
3. Test the complete pipeline with MCP tools
4. Use `get_stage_output` to inspect results
