# HANDOFF: PDF Export Showing JSON Instead of Markdown - Persistent Issue

## 🚨 CRITICAL CONTEXT

**Duration:** 2+ days of debugging
**Status:** UNSOLVED - Need fresh approach
**Impact:** Core feature (PDF downloads) completely broken
**Environment:** HuggingFace Spaces + Railway Backend

---

## Problem Statement

When users download PDFs from the Gradio experimentation UI, they see **raw JSON code blocks** instead of **formatted markdown with headings, bullets, and structure**.

### What We Know Works ✅

1. **Backend markdown generation:** Railway logs confirm all stages generate valid markdown strings
   ```
   ✅ Stage 5 markdown validated as string (4606 chars)
   ```

2. **Fresh pipeline runs in UI:** After running a pipeline, the Gradio tabs display formatted markdown correctly

3. **Backend formatters:** All 7 stages (0-6) have working markdown formatters in `backend/pipeline/output_formatters.py`

### What's Broken ❌

1. **PDF downloads from fresh runs:** Show JSON instead of markdown
2. **Loaded experiments:** State is None, causing `AttributeError: 'NoneType' object has no attribute 'get'`
3. **Database persistence:** Experiments are saved but markdown doesn't survive the round trip

---

## Root Cause Analysis (Current Understanding)

### Issue #1: State Management Breakdown

**File:** `backend/experimentation/hf-space-deploy/app.py`

**Line 342-362:** `download_all_stages_pdf()` function
```python
def download_all_stages_pdf(state):
    """Generate combined PDF with all stages"""
    if state is None:  # ❌ State is None when called
        return None

    brand_name = state.get("brand_profile", {}).get("brand_name", "Unknown Brand")
    stage_outputs = state.get("stage_outputs", {})

    # Collect markdown from all stages
    markdowns = {}
    for i in range(7):
        stage_key = f"stage_{i}"
        markdown = stage_outputs.get(stage_key, {}).get("markdown", "")
        if markdown:
            markdowns[i] = markdown
```

**Problem:** `state` is `None` when the download button is clicked, even after running a fresh pipeline.

### Issue #2: Database Doesn't Store Markdown

**File:** `backend/app/routes.py`

**Line 621-682:** `save_experiment()` endpoint saves `stage_outputs` to PostgreSQL JSONB field

**What's saved:**
```python
json.dumps(request.stage_outputs)  # From HF Space
```

**What HF Space sends (Line 1403-1411 in app.py):**
```python
state["stage_outputs"] = {
    "stage_0": {"markdown": stage0},  # stage0 is a markdown string
    "stage_1": {"markdown": stage1},
    ...
}
```

**Problem:** When loading experiments back from database, markdown field should exist but the state doesn't get populated correctly.

### Issue #3: Load Experiment State Mismatch

**File:** `backend/experimentation/hf-space-deploy/app.py`

**Line 1238-1280:** `load_saved_experiment()` function

```python
# Extract data (camelCase fields from Experiment table)
brand_profile = experiment.get("brandProfile", {})
stage_outputs = experiment.get("stageOutputs", {})

# Update state
state["pdf_text"] = experiment.get("reportText", "")
state["brand_profile"] = brand_profile
state["run_id"] = experiment.get("runId", "")
state["stage_outputs"] = stage_outputs  # ⚠️ This should contain markdown

# Extract stage markdown
stage0 = stage_outputs.get("stage_0", {}).get("markdown", "")  # ❌ Returns empty string
stage1 = stage_outputs.get("stage_1", {}).get("markdown", "")
...
```

**Problem:** Even though `stage_outputs` is loaded from database, the markdown extraction returns empty strings, suggesting the database either:
1. Doesn't contain markdown fields, OR
2. The structure is different than expected

---

## Evidence & Logs

### Backend Logs (Railway) - ✅ WORKING

```
2025-11-24 14:24:40,175 - app.pipeline_runner - INFO - [77dc3909] Stage 3 format_stage_output returned type: str
2025-11-24 14:24:40,175 - app.pipeline_runner - INFO - [77dc3909] ✅ Stage 3 markdown validated as string (5957 chars)
2025-11-24 14:24:40,175 - app.pipeline_runner - INFO - [77dc3909] Stage 4 format_stage_output returned type: str
2025-11-24 14:24:40,175 - app.pipeline_runner - INFO - [77dc3909] ✅ Stage 4 markdown validated as string (6489 chars)
2025-11-24 14:24:40,175 - app.pipeline_runner - INFO - [77dc3909] Stage 5 format_stage_output returned type: str
2025-11-24 14:24:40,175 - app.pipeline_runner - INFO - [77dc3909] ✅ Stage 5 markdown validated as string (4606 chars)
```

### HF Space Logs - ❌ BROKEN

```
[FETCH_EXPERIMENTS] Found 9 experiments (total: 9)
⚠️ Stage 1 missing markdown field, using JSON fallback
⚠️ Stage 2 missing markdown field, using JSON fallback
⚠️ Stage 3 missing markdown field, using JSON fallback
⚠️ Stage 4 missing markdown field, using JSON fallback
⚠️ Stage 5 missing markdown field, using JSON fallback

Traceback (most recent call last):
  File "/app/app.py", line 1576, in download_all_stages_pdf
    brand_name = state.get("brand_profile", {}).get("brand_name", "Unknown Brand")
AttributeError: 'NoneType' object has no attribute 'get'
```

---

## What We've Tried (Failed Attempts)

### Attempt #1: Add Stage 0 and Stage 6 Formatters ❌
- **Action:** Created `format_stage0_to_markdown()` and `format_stage6_to_markdown()`
- **Result:** Backend logs show they work, but PDFs still show JSON
- **Conclusion:** Formatters aren't the problem

### Attempt #2: Add Type Validation ❌
- **Action:** Added `isinstance(markdown, str)` checks everywhere
- **Result:** Confirmed markdown IS a string in backend, but still JSON in PDFs
- **Conclusion:** Type conversion happens somewhere between backend and PDF generation

### Attempt #3: Add Diagnostic Logging ❌
- **Action:** Added extensive logging to track markdown type at every stage
- **Result:** Logs show markdown is valid string, but user still sees JSON in PDF
- **Conclusion:** The problem is in state management, not markdown generation

### Attempt #4: Fix None State Handling ❌
- **Action:** Modified code (shown in system reminder) to handle None state
- **Result:** Still not working after 2 days
- **Conclusion:** The architectural approach is flawed

---

## Alternative Solutions to Consider

### Solution A: Bypass State - Direct Backend PDF Generation

**Concept:** Move PDF generation entirely to the backend, bypassing HF Space state management.

**Implementation:**
1. Add new backend endpoint: `POST /experiments/{experiment_id}/download-pdf`
2. Backend queries database, regenerates markdown using formatters, generates PDF
3. Returns PDF file directly to HF Space for download
4. HF Space becomes a thin UI layer, no state management needed

**Pros:**
- ✅ Eliminates state management issues
- ✅ Backend has all the data (database, formatters)
- ✅ Single source of truth
- ✅ Simpler architecture

**Cons:**
- ⚠️ Requires backend code changes
- ⚠️ Adds load to backend (PDF generation is CPU-intensive)

**Files to Modify:**
- `backend/app/routes.py` - Add PDF generation endpoint
- `backend/experimentation/hf-space-deploy/app.py` - Replace PDF download logic with backend API call
- `backend/experimentation/hf-space-deploy/export/pdf_export.py` - Move to backend or make importable

### Solution B: Store Markdown in Database

**Concept:** Explicitly save markdown to database when saving experiments, not just raw output.

**Implementation:**
1. Modify `save_experiment()` in HF Space to ensure markdown is in `stage_outputs`
2. Add database migration to include `markdown` field in `stageOutputs` JSONB
3. Backend `/run/local` already generates markdown - ensure it's saved to status.json
4. HF Space loads markdown directly from database, no regeneration needed

**Pros:**
- ✅ Markdown persists correctly
- ✅ No regeneration needed on load
- ✅ Simpler load logic

**Cons:**
- ⚠️ Database schema change required
- ⚠️ Need to backfill existing experiments
- ⚠️ Larger database storage (markdown strings are verbose)

**Files to Modify:**
- `backend/app/routes.py` - Ensure `stageOutputs` JSONB contains markdown
- `backend/experimentation/hf-space-deploy/app.py` - Load markdown from database correctly

### Solution C: Regenerate Markdown On-Demand

**Concept:** When loading experiments, call backend to regenerate markdown from stored `output` JSON.

**Implementation:**
1. Add backend endpoint: `POST /format-stage-output`
2. Accepts stage number + raw output JSON
3. Returns formatted markdown using existing formatters
4. HF Space calls this endpoint when loading experiments to populate markdown fields

**Pros:**
- ✅ No database schema changes
- ✅ Works with existing experiments
- ✅ Leverages existing formatters
- ✅ Separates concerns (backend formats, HF Space displays)

**Cons:**
- ⚠️ Adds latency when loading experiments (7 API calls per experiment)
- ⚠️ More complex load flow

**Files to Modify:**
- `backend/app/routes.py` - Add `/format-stage-output` endpoint
- `backend/pipeline/output_formatters.py` - Expose `format_stage_output()` via API
- `backend/experimentation/hf-space-deploy/app.py` - Call backend when loading experiments

---

## Recommended Approach: Solution A (Backend PDF Generation)

**Why this is best:**

1. **Eliminates root cause:** State management is fundamentally broken in HF Space. Bypassing it entirely removes the problem.

2. **Simpler architecture:** Backend has all the data (database, formatters, output_formatters.py). Moving PDF generation there creates a single source of truth.

3. **Already works:** Backend markdown generation is confirmed working. We're just moving PDF generation to where markdown already exists.

4. **Minimal changes:** Only need to add one new endpoint and update HF Space download buttons to call it.

### Implementation Plan

**Step 1: Create Backend PDF Endpoint**

**File:** `backend/app/routes.py`

Add new endpoint:
```python
@router.get("/experiments/{experiment_id}/download-pdf")
async def download_experiment_pdf(experiment_id: str):
    """Generate PDF for saved experiment

    Loads experiment from database, regenerates markdown using formatters,
    generates PDF, returns as file download.
    """
    import psycopg2
    import psycopg2.extras
    from pipeline.output_formatters import format_stage_output
    from pathlib import Path
    import tempfile

    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL not configured")

    # Load experiment from database
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Support both full UUID and short ID
            if len(experiment_id) == 8:
                cur.execute('SELECT * FROM "Experiment" WHERE "id" LIKE %s LIMIT 1', (f'%{experiment_id}',))
            else:
                cur.execute('SELECT * FROM "Experiment" WHERE "id" = %s', (experiment_id,))

            experiment = cur.fetchone()
            if not experiment:
                raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")
    finally:
        conn.close()

    # Extract data
    brand_profile = experiment.get("brandProfile", {})
    brand_name = brand_profile.get("brand_name", "Unknown Brand")
    stage_outputs = experiment.get("stageOutputs", {})

    # Regenerate markdown for all stages using backend formatters
    markdowns = {}
    for stage_num in range(7):
        stage_key = f"stage_{stage_num}"
        if stage_key in stage_outputs:
            stage_data = stage_outputs[stage_key]

            # Check if markdown already exists
            if "markdown" in stage_data and isinstance(stage_data["markdown"], str):
                markdown = stage_data["markdown"]
            else:
                # Regenerate markdown from output JSON
                output = stage_data.get("output", {})
                if output:
                    markdown = format_stage_output(stage_num, output)
                else:
                    markdown = ""

            if markdown:
                markdowns[stage_num] = markdown

    # Generate PDF using existing PDF export logic
    # Import from HF Space or recreate here
    from experimentation.hf_space_deploy.export.pdf_export import generate_all_stages_pdf

    pdf_path = generate_all_stages_pdf(
        stage_markdowns=markdowns,
        brand_name=brand_name
    )

    # Return PDF as file download
    from fastapi.responses import FileResponse
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{brand_name.replace(' ', '_')}_full_report.pdf"
    )
```

**Step 2: Update HF Space Download Button**

**File:** `backend/experimentation/hf-space-deploy/app.py`

Replace line 342-362 `download_all_stages_pdf()` function:

```python
def download_all_stages_pdf(state):
    """Generate combined PDF via backend API

    Calls backend to generate PDF from database, bypassing state management.
    """
    if state is None:
        print("[PDF_DOWNLOAD] ERROR: state is None")
        return None

    # Get experiment ID from state
    run_id = state.get("run_id")
    if not run_id:
        print("[PDF_DOWNLOAD] ERROR: No run_id in state")
        return None

    try:
        # Call backend PDF generation endpoint
        import httpx
        import tempfile

        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")

        with httpx.Client(timeout=60.0) as client:
            response = client.get(f"{backend_url}/experiments/{run_id}/download-pdf")

            if response.status_code != 200:
                print(f"[PDF_DOWNLOAD] Backend error: {response.status_code}")
                return None

            # Save PDF to temp file
            brand_name = state.get("brand_profile", {}).get("brand_name", "Unknown")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{brand_name.replace(' ', '_')}_report_{timestamp}.pdf"

            pdf_path = Path(tempfile.gettempdir()) / filename
            with open(pdf_path, 'wb') as f:
                f.write(response.content)

            print(f"[PDF_DOWNLOAD] PDF saved to {pdf_path}")
            return str(pdf_path)

    except Exception as e:
        print(f"[PDF_DOWNLOAD] Exception: {e}")
        import traceback
        traceback.print_exc()
        return None
```

**Step 3: Test Flow**

1. Run fresh pipeline in HF Space
2. Save experiment to database
3. Click "Download Full Report PDF" button
4. HF Space calls backend `/experiments/{run_id}/download-pdf`
5. Backend loads experiment, regenerates markdown, generates PDF, returns file
6. User receives formatted PDF (not JSON)

**Step 4: Handle PDF Export Dependencies**

**Option A:** Move `pdf_export.py` to backend
```bash
# Move file
mv backend/experimentation/hf-space-deploy/export/pdf_export.py backend/app/pdf_export.py

# Update imports in backend/app/routes.py
from app.pdf_export import generate_all_stages_pdf
```

**Option B:** Make pdf_export.py a shared module
```bash
# Create shared module
mkdir backend/shared
mv backend/experimentation/hf-space-deploy/export/pdf_export.py backend/shared/

# Update imports in both HF Space and backend
```

---

## Testing Checklist

After implementing Solution A:

- [ ] Test fresh pipeline run → Save → Download PDF → Verify markdown (not JSON)
- [ ] Test load existing experiment → Download PDF → Verify markdown
- [ ] Test all 7 stages individually → Download each stage PDF
- [ ] Test combined "Full Report" PDF → Verify all stages formatted
- [ ] Verify backend logs show markdown generation
- [ ] Verify HF Space logs show successful backend API call
- [ ] Check PDF file size (should be reasonable, not massive JSON dumps)
- [ ] Test with multiple brand profiles (Lactalis, Decathlon, McCormick)

---

## Success Criteria

After fix is complete:

1. ✅ PDFs show formatted markdown with:
   - Proper headings (# ## ###)
   - Bullet points render as lists
   - Code blocks formatted correctly
   - No raw JSON `{'key': 'value'}` visible

2. ✅ Fresh pipeline runs → PDF download works

3. ✅ Loaded experiments → PDF download works

4. ✅ Backend logs show markdown generation for all stages

5. ✅ No `AttributeError: 'NoneType'` errors

6. ✅ No "missing markdown field" warnings

---

## Key Files & Locations

### Backend (Railway)
- `backend/app/routes.py` - API endpoints (ADD PDF endpoint here)
- `backend/pipeline/output_formatters.py` - Markdown formatters (ALREADY WORKING)
- `backend/app/pipeline_runner.py` - Pipeline execution (ALREADY WORKING)

### HF Space
- `backend/experimentation/hf-space-deploy/app.py` - Gradio UI (MODIFY download function)
- `backend/experimentation/hf-space-deploy/export/pdf_export.py` - PDF generation (MOVE to backend)

### Database
- Table: `Experiment`
- Field: `stageOutputs` (JSONB) - Contains stage output JSON
- Field: `brandProfile` (JSONB) - Contains brand data

---

## Environment Variables

**Backend (Railway):**
- `DATABASE_URL` - PostgreSQL connection string
- `OPENROUTER_API_KEY` - LLM API key
- `WEBHOOK_SECRET` - For frontend communication

**HF Space:**
- `BACKEND_API_URL` - Backend URL (e.g., `https://innovation-backend-production.up.railway.app`)
- `DATABASE_URL` - PostgreSQL connection string (same as backend)

---

## Final Notes

**Why 2 days of debugging failed:**
- We were trying to fix state management in HF Space (fundamentally broken architecture)
- We were debugging symptoms (JSON in PDFs) instead of root cause (state is None)
- We were adding more complexity (logging, type checks) instead of simplifying

**Why Solution A will work:**
- Eliminates the broken state management entirely
- Backend already generates correct markdown (confirmed in logs)
- PDF generation moves to where the data lives (backend + database)
- Simpler, cleaner architecture with single source of truth

**Next agent should:**
1. Implement Solution A (backend PDF endpoint)
2. Update HF Space to call backend API
3. Test thoroughly with fresh runs and loaded experiments
4. Deploy and verify in production

---

**Estimated Effort:** 3-4 hours (implementation + testing)
**Priority:** CRITICAL - Core feature broken
**Blockers:** None - all information available
**Success Metric:** User downloads PDF and sees beautiful formatted markdown, not JSON

---

## Quick Start for Next Agent

```bash
# 1. Add PDF endpoint to backend
code backend/app/routes.py  # Add /experiments/{id}/download-pdf endpoint

# 2. Update HF Space download function
code backend/experimentation/hf-space-deploy/app.py  # Replace download_all_stages_pdf()

# 3. Test locally
cd backend
python -m uvicorn app.main:app --reload  # Start backend
cd experimentation/hf-space-deploy
python app.py  # Start HF Space

# 4. Deploy to Railway
railway up

# 5. Deploy to HF Spaces
cd backend/experimentation/hf-space-deploy
git add . && git commit -m "fix: move PDF generation to backend API" && git push
```

Good luck! This should finally solve the persistent PDF markdown issue.
