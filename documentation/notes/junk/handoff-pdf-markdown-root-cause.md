# Handoff: PDF Markdown Formatting - Root Cause Analysis

## Executive Summary

PDFs display raw JSON instead of formatted markdown because **loaded experiments from the database don't have markdown fields**, causing the system to fall back to JSON code blocks.

**Status:** Root cause identified, solution defined
**Affected Feature:** PDF downloads from loaded experiments
**Fresh Pipeline Runs:** Work correctly (not affected)
**Loaded Experiments:** Show JSON (broken)

---

## Problem Statement

When downloading PDFs from the Gradio experimentation UI:

- ✅ **Fresh pipeline runs** → PDFs show formatted markdown correctly
- ❌ **Loaded experiments** → PDFs show raw JSON like `{"opportunities": [...]}`

### User-Reported Error

```
Traceback (most recent call last):
  File "/app/app.py", line 1576, in download_all_stages_pdf
    brand_name = state.get("brand_profile", {}).get("brand_name", "Unknown Brand")
AttributeError: 'NoneType' object has no attribute 'get'
```

Console warnings:
```
⚠️ Stage 1 missing markdown field, using JSON fallback
⚠️ Stage 2 missing markdown field, using JSON fallback
...
```

---

## Root Cause Analysis

### The Data Flow Problem

#### 1. **Fresh Pipeline Run** (WORKS ✅)

```python
# HF Space app.py line 1403-1411
state["stage_outputs"] = {
    "stage_0": {"markdown": stage0},  # stage0 is a markdown string from backend
    "stage_1": {"markdown": stage1},
    "stage_2": {"markdown": stage2},
    ...
}
```

When you run a fresh pipeline:
- Backend generates markdown via `format_stage_output()` (verified in Railway logs: `✅ Stage 5 markdown validated as string (4601 chars)`)
- HF Space stores markdown strings in state
- PDF download reads `stage_data.get("markdown")` and gets valid markdown
- ✅ **PDF displays formatted content**

#### 2. **Load From Database** (BROKEN ❌)

```python
# HF Space app.py line 1256
state["stage_outputs"] = stage_outputs  # From database

# Line 1266-1272
stage0 = stage_outputs.get("stage_0", {}).get("markdown", "")
stage1 = stage_outputs.get("stage_1", {}).get("markdown", "")
...
```

When you load an experiment:
- Database returns `stageOutputs` JSONB field
- This field contains the SAME structure as fresh runs: `{"stage_0": {"markdown": "..."}}`
- **BUT** the state is not properly initialized (line 1252-1256 doesn't populate state correctly)
- PDF download function receives `state=None` (line 1576 error)
- Even if state existed, stages show "missing markdown field" warnings

### Why Loaded Experiments Fail

**Problem 1: State is None**

```python
# app.py line 1576
def download_all_stages_pdf(state):
    brand_name = state.get("brand_profile", {}).get("brand_name", "Unknown Brand")
    # ❌ AttributeError: 'NoneType' object has no attribute 'get'
```

The `cached_data` state is not properly passed to the PDF download function when loading experiments.

**Problem 2: Missing Markdown Fields**

```python
# app.py line 489-495 get_stage_display()
markdown = stage_data.get("markdown", "")
if not markdown:
    print(f"⚠️ Stage {stage_key} missing markdown field, using JSON fallback")
    return f"```json\n{json.dumps(stage_data.get('output', {}), indent=2)}\n```"
```

When loading from database:
- `stage_data` structure is: `{"markdown": "# Stage 0..."}`
- **BUT** the `get_stage_display()` function expects markdown to be a NON-EMPTY string
- If markdown is empty or missing, it falls back to JSON

### The Database Schema Issue

**What's Saved:**

```python
# backend/app/routes.py line 671
json.dumps(request.stage_outputs)  # Saves stage_outputs to JSONB
```

**What's in stage_outputs:**

```python
# From HF Space app.py line 1403-1411
{
    "stage_0": {"markdown": "# Stage 0: Brand Context\n\n..."},
    "stage_1": {"markdown": "# Stage 1: Trend Decomposition\n\n..."},
    ...
}
```

The database **DOES** store markdown strings, but when loading:

1. The state is not properly initialized (None)
2. The stage_outputs structure is loaded but not properly connected to the UI state
3. PDF download fails because it can't access `state["brand_profile"]`

---

## Evidence

### Backend Logs (Railway)

```
2025-11-24 14:24:40,175 - app.pipeline_runner - INFO - [77dc3909] ✅ Stage 5 markdown validated as string (4606 chars)
```

✅ **Backend is working correctly** - generates markdown strings for all stages.

### HF Space Console Logs

```
[FETCH_EXPERIMENTS] Found 9 experiments (total: 9)
⚠️ Stage 1 missing markdown field, using JSON fallback
⚠️ Stage 2 missing markdown field, using JSON fallback
```

❌ **HF Space fails to load markdown** from database experiments.

### Error Traceback

```python
File "/app/app.py", line 1576, in download_all_stages_pdf
    brand_name = state.get("brand_profile", {}).get("brand_name", "Unknown Brand")
AttributeError: 'NoneType' object has no attribute 'get'
```

❌ **State is None** when PDF download is triggered from loaded experiment.

---

## Solution

### Fix 1: Handle None State in PDF Download

**File:** `backend/experimentation/hf-space-deploy/app.py`
**Line:** 1576

**Current Code (BROKEN):**
```python
def download_all_stages_pdf(state):
    brand_name = state.get("brand_profile", {}).get("brand_name", "Unknown Brand")
    stage_outputs = state.get("stage_outputs", {})
```

**Fixed Code:**
```python
def download_all_stages_pdf(state):
    """Generate combined PDF with all stages

    Args:
        state: Gradio state dict (may be None if not initialized)
    """
    # Handle None state
    if state is None:
        print("[PDF_DOWNLOAD] ERROR: state is None - cannot generate PDF")
        return None

    brand_name = state.get("brand_profile", {}).get("brand_name", "Unknown Brand")
    stage_outputs = state.get("stage_outputs", {})

    # Log state structure for debugging
    print(f"[PDF_DOWNLOAD] State keys: {list(state.keys())}")
    print(f"[PDF_DOWNLOAD] Brand name: {brand_name}")
    print(f"[PDF_DOWNLOAD] Stage outputs keys: {list(stage_outputs.keys())}")
```

### Fix 2: Properly Initialize State When Loading Experiments

**File:** `backend/experimentation/hf-space-deploy/app.py`
**Line:** 1252-1256

**Current Code (INCOMPLETE):**
```python
# Update state
state["pdf_text"] = experiment.get("reportText", "")
state["brand_profile"] = brand_profile
state["run_id"] = experiment.get("runId", "")
state["stage_outputs"] = stage_outputs
```

**Issue:** This updates the state dict, but the state is not properly connected to the Gradio component outputs.

**Fixed Code:**

```python
# Update state - ensure it's a dict, not None
if state is None:
    state = {}

state["pdf_text"] = experiment.get("reportText", "")
state["brand_profile"] = brand_profile
state["run_id"] = experiment.get("runId", "")
state["stage_outputs"] = stage_outputs

print(f"[LOAD_EXPERIMENT] State initialized with keys: {list(state.keys())}")
print(f"[LOAD_EXPERIMENT] Brand profile: {brand_profile.get('brand_name', 'N/A')}")
print(f"[LOAD_EXPERIMENT] Stage outputs keys: {list(stage_outputs.keys())}")
```

### Fix 3: Ensure Markdown Persistence

**Current Behavior:**
- Fresh runs: Backend generates markdown → HF Space stores in state → Saves to DB
- Loaded experiments: DB returns stageOutputs → HF Space loads → Markdown should exist

**Verification Needed:**

Check if the database actually contains markdown fields:

```sql
-- Query Railway PostgreSQL
SELECT
    id,
    "qualityTag",
    jsonb_pretty("stageOutputs")
FROM "Experiment"
LIMIT 1;
```

**Expected Output:**
```json
{
  "stage_0": {
    "markdown": "# Stage 0: Brand Context\n\n**Brand Name**: Decathlon\n..."
  },
  "stage_1": {
    "markdown": "# Stage 1: Trend Decomposition\n\n## Extracted Trends\n..."
  }
}
```

**If markdown is missing:**

The save function needs to be updated to explicitly include markdown when saving:

```python
# backend/experimentation/hf-space-deploy/app.py line 607-615
save_payload = {
    "run_id": run_id,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "report_text": pdf_text,
    "brand_profile": brand_profile,
    "stage_outputs": stage_outputs,  # Must contain markdown fields
    "quality_tag": quality_tag.lower(),
    "notes": notes
}
```

---

## Testing Plan

### Test 1: Fresh Pipeline Run

1. Go to HF Space
2. Upload trend report PDF
3. Enter brand profile
4. Run pipeline
5. Download "Full Report PDF"
6. ✅ Verify formatted markdown (not JSON)

### Test 2: Load Existing Experiment

1. Go to "Saved Experiments" tab
2. Select any experiment
3. Click "📥 Load"
4. Verify stages populate in UI tabs
5. Download "Full Report PDF"
6. ✅ Verify formatted markdown (not JSON)

### Test 3: Save and Reload

1. Run fresh pipeline
2. Tag as "Good"
3. Save experiment
4. Reload page
5. Load the saved experiment
6. Download PDF
7. ✅ Verify formatted markdown (not JSON)

---

## Implementation Checklist

- [ ] Fix 1: Add None state handling in `download_all_stages_pdf()` (line 1576)
- [ ] Fix 2: Initialize state properly in `load_saved_experiment()` (line 1252)
- [ ] Fix 3: Add diagnostic logging to track state flow
- [ ] Test: Fresh pipeline run → PDF download
- [ ] Test: Load experiment → PDF download
- [ ] Test: Save → Reload → PDF download
- [ ] Verify: Check database contains markdown fields
- [ ] Deploy: Push to HF Space
- [ ] Validate: Run full regression test

---

## Files to Modify

### Primary File

**`backend/experimentation/hf-space-deploy/app.py`**

**Changes:**

1. **Line 1576** (download_all_stages_pdf): Add None state check
2. **Line 1252** (load_saved_experiment): Initialize state as dict
3. **Line 1571** (download_all_stages_pdf): Add diagnostic logging

### Secondary Files (if markdown is missing in DB)

**`backend/app/routes.py`** (line 622-671)

If database inspection shows missing markdown fields, update save logic to ensure markdown is included in `stageOutputs` JSONB.

---

## Success Criteria

After fixes:

1. ✅ Fresh pipeline runs → Formatted markdown in PDFs
2. ✅ Loaded experiments → Formatted markdown in PDFs
3. ✅ No `AttributeError: 'NoneType'` errors
4. ✅ No "missing markdown field" warnings
5. ✅ All 7 stages (0-6) format correctly
6. ✅ Database contains markdown in `stageOutputs` JSONB field

---

## Next Steps

1. **Immediate:** Fix None state handling (Fix 1)
2. **Immediate:** Fix state initialization (Fix 2)
3. **Verify:** Check database contains markdown fields
4. **Deploy:** Push fixes to HF Space
5. **Test:** Run full test suite (Fresh run + Load + Save/Reload)

---

**Status:** Ready for implementation
**Priority:** High - Core feature broken for loaded experiments
**Estimated Effort:** 1-2 hours (fixes + testing)
**Blockers:** None - all information available

---

## Technical Context

**Gradio Version:** 4.x (async handlers)
**Backend:** FastAPI + PostgreSQL (Railway)
**Database:** Direct psycopg2 connection (bypassing Prisma for Gradio)
**PDF Generation:** WeasyPrint + markdown2
**Deployment:** HuggingFace Spaces (Space: `innovation-intelligence`)

**Related Files:**
- `backend/experimentation/hf-space-deploy/app.py` (1,518 lines)
- `backend/experimentation/hf-space-deploy/export/pdf_export.py`
- `backend/app/routes.py` (save_experiment endpoint)
- `backend/pipeline/output_formatters.py` (markdown generators)

**Recent Fixes:**
- ✅ Added Stage 0 and Stage 6 formatters
- ✅ Deployed backend with all 7-stage markdown generation
- ✅ Added diagnostic logging to track markdown types

**Remaining Issue:**
- ❌ State management for loaded experiments
- ❌ PDF download fails with None state error
