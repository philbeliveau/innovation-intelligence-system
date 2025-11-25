# HANDOFF: Persistent PDF 404 Error After run_id Fix

**Date:** 2025-11-24
**Agent:** Claude Code
**Status:** BLOCKED - Root cause identified, requires deeper investigation
**Priority:** CRITICAL - PDF download completely broken

---

## Problem Statement

PDF downloads continue to fail with 404 errors even after fixing the run_id mismatch bug. The issue persists with a new pattern.

### Latest Failure Evidence

**Logs from 2025-11-24 16:51:**

```
2025-11-24 16:51:08,569 - app.pipeline_runner - INFO - [f3cf35b7] Successfully notified frontend of completion
2025-11-24 16:51:08,570 - app.pipeline_runner - INFO - Cleaned up PDF file: /tmp/runs/f3cf35b7/input.txt

INFO:     100.64.0.3:28228 - "GET /status/f3cf35b7 HTTP/1.1" 200 OK
INFO:     100.64.0.4:43740 - "GET /status/f3cf35b7 HTTP/1.1" 200 OK

2025-11-24 16:51:27,047 - app.routes - INFO - [PDF_DOWNLOAD] Request for experiment f3cf35b7
2025-11-24 16:51:27,147 - app.routes - ERROR - [PDF_DOWNLOAD] Experiment f3cf35b7 not found
INFO:     100.64.0.9:46094 - "GET /experiments/f3cf35b7/download-pdf HTTP/1.1" 404 Not Found
```

**Key Observations:**
1. Pipeline completes successfully with run_id `f3cf35b7`
2. Frontend webhook notification succeeds
3. Status endpoint returns 200 OK for run_id `f3cf35b7`
4. User clicks "Download PDF" 18 seconds later
5. HF Space sends request for experiment `f3cf35b7` (CORRECT run_id!)
6. Backend database query returns 404: "Experiment f3cf35b7 not found"

---

## Previous Fix (Commit 7025237)

**What Was Fixed:**
- Modified `run_pipeline()` to return `actual_run_id` as 9th tuple element
- Updated `run_pipeline_wrapper()` to use returned run_id instead of generating new random UUID
- Fixed data flow bug where state contained different run_id than backend execution

**Impact:**
- HF Space now correctly uses the same run_id that backend executed with
- But experiments are STILL not found in database

---

## Root Cause Analysis

### The Critical Gap: Experiment Was Never Saved

Looking at the timeline:
1. Pipeline executes with run_id `f3cf35b7`
2. User clicks "Download PDF" immediately after completion
3. PDF download endpoint queries database for experiment `f3cf35b7`
4. **But the experiment was NEVER saved to the database!**

### Why Experiments Aren't Saved

**User Flow:**
1. User uploads PDF
2. User clicks "Run Pipeline"
3. Pipeline completes (run_id stored in Gradio state)
4. User sees results in UI tabs
5. **User must MANUALLY click "Save Experiment" button**
6. Only THEN is experiment saved to database via `POST /experiments/save`

**The Problem:**
- PDF download endpoint expects experiment to exist in database
- But users can download PDF BEFORE saving the experiment
- There's no automatic save-on-completion

---

## Database Query Issue

**Location:** `backend/app/routes.py` lines 1014-1061

```python
@router.get("/experiments/{experiment_id}/download-pdf")
async def download_experiment_pdf(experiment_id: str):
    # Load experiment from database
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Support both full UUID and short ID (last 8 chars)
            if len(experiment_id) == 8:
                cur.execute('SELECT * FROM "Experiment" WHERE "id" LIKE %s LIMIT 1', (f'%{experiment_id}',))
            else:
                cur.execute('SELECT * FROM "Experiment" WHERE "id" = %s', (experiment_id,))

            experiment = cur.fetchone()
            if not experiment:
                logger.error(f"[PDF_DOWNLOAD] Experiment {experiment_id} not found")
                raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")
```

**The Issue:**
- Query looks for experiment with ID ending in `f3cf35b7`
- Experiment IDs have format: `exp-{timestamp}-{run_id[:8]}`
- Example: `exp-1732464485-f3cf35b7`
- Query SHOULD match, but returns no results

### Why Database Query Fails

**Hypothesis 1: Experiment Not Saved Yet**
- User clicks "Download PDF" before clicking "Save Experiment"
- No database record exists to query

**Hypothesis 2: ID Mismatch in Save Process**
- `POST /experiments/save` generates experiment_id: `exp-{timestamp}-{run_id[:8]}`
- If run_id in state is different from what's sent to PDF download, query fails
- But logs show same run_id `f3cf35b7` used consistently

**Hypothesis 3: Database Write Delay**
- Experiment saved but database replication lag causes 404
- Unlikely given 18-second gap between completion and download

---

## Two Possible Solutions

### Solution A: Auto-Save on Pipeline Completion (Recommended)

**Approach:** Automatically save experiment to database when pipeline completes successfully.

**Implementation:**
1. Modify `execute_pipeline_background()` in `backend/app/pipeline_runner.py`
2. After final stage completes, automatically call `POST /experiments/save`
3. Use quality_tag="auto_saved" or "pending_review"
4. Store all stage outputs from status.json

**Advantages:**
- Experiments always available for PDF download
- No user action required
- Matches user expectation (pipeline complete = results saved)

**Disadvantages:**
- Saves ALL pipeline runs, including failures
- May clutter database with unwanted experiments
- Requires refactoring pipeline completion logic

**Files to Modify:**
- `backend/app/pipeline_runner.py` (add auto-save logic after line 270)
- `backend/app/routes.py` (ensure `/experiments/save` handles auto-save)

---

### Solution B: Generate PDF from Pipeline Status, Not Database (Alternative)

**Approach:** PDF download should use `/tmp/runs/{run_id}/status.json` instead of database.

**Implementation:**
1. Modify PDF download endpoint to check two sources:
   - First: Try loading from database (for saved experiments)
   - Fallback: Load from `/tmp/runs/{run_id}/status.json` (for unsaved pipelines)
2. Generate PDF from pipeline execution results directly

**Advantages:**
- PDF download works immediately after pipeline completion
- No need to save experiments to database first
- Simpler user flow

**Disadvantages:**
- `/tmp/runs/{run_id}/` may be cleaned up (see log: "Cleaned up PDF file")
- Status files may not persist long enough
- Depends on file system state, not database

**Files to Modify:**
- `backend/app/routes.py` lines 1014-1131 (add fallback logic)

---

## Recommended Implementation: Solution A

### Step 1: Verify Current Save Flow

**Check:** What happens when user clicks "Save Experiment" in HF Space?

**Files:**
- `backend/experimentation/hf-space-deploy/app.py` lines 1496-1513 (save_experiment_wrapper)
- `backend/experimentation/hf-space-deploy/app.py` lines 581-625 (save_experiment method)

**Expected Flow:**
```
User clicks "Save" → save_experiment_wrapper(state, quality, notes)
                   → self.save_experiment(run_id, pdf_text, brand_profile, ...)
                   → POST /experiments/save
                   → PostgreSQL INSERT with experiment_id: exp-{timestamp}-{run_id[:8]}
```

### Step 2: Implement Auto-Save in Pipeline Runner

**Location:** `backend/app/pipeline_runner.py`

**After line 270 (pipeline completion):**

```python
# Auto-save experiment to database (makes PDF download available immediately)
try:
    logger.info(f"[{run_id}] Auto-saving experiment to database...")

    import httpx
    from datetime import datetime, timezone

    # Load pipeline results from status.json
    with open(status_file, 'r') as f:
        final_status = json.load(f)

    # Extract stage outputs
    stage_outputs = final_status.get("stages", {})

    # Call save endpoint
    async with httpx.AsyncClient(timeout=30.0) as client:
        save_response = await client.post(
            f"{backend_url}/experiments/save",
            json={
                "run_id": run_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "report_text": pdf_text,
                "brand_profile": brand_profile,
                "stage_outputs": stage_outputs,
                "quality_tag": "auto_saved",  # User can update later
                "notes": "Automatically saved on pipeline completion"
            }
        )

        if save_response.status_code == 200:
            logger.info(f"[{run_id}] Experiment auto-saved successfully")
        else:
            logger.error(f"[{run_id}] Auto-save failed: {save_response.text}")

except Exception as e:
    logger.error(f"[{run_id}] Auto-save error (non-fatal): {e}")
    # Don't fail pipeline if auto-save fails
```

### Step 3: Update HF Space "Save" Button Behavior

**Location:** `backend/experimentation/hf-space-deploy/app.py`

**Modify save_experiment_wrapper() to UPDATE existing experiment instead of INSERT:**

```python
async def save_experiment_wrapper(state, quality, notes_text):
    run_id = state.get("run_id")

    # Check if experiment already exists (auto-saved)
    existing_exp = await check_experiment_exists(run_id)

    if existing_exp:
        # UPDATE existing experiment with user's quality tag and notes
        return await self.update_experiment(
            run_id=run_id,
            quality_tag=quality,
            notes=notes_text
        )
    else:
        # INSERT new experiment (fallback for old pipelines)
        return await self.save_experiment(...)
```

### Step 4: Create Update Endpoint

**Location:** `backend/app/routes.py`

**Add new endpoint:**

```python
@router.put("/experiments/{run_id}/update", operation_id="update_experiment")
async def update_experiment(run_id: str, quality_tag: str, notes: str):
    """Update experiment quality tag and notes

    Allows users to refine auto-saved experiments with their assessment.
    """
    # Find experiment by run_id suffix
    # UPDATE quality_tag and notes
    # Return success
```

---

## Testing Checklist

After implementing Solution A:

1. **Test Auto-Save:**
   - [ ] Run pipeline in HF Space
   - [ ] Check Railway logs for "Experiment auto-saved successfully"
   - [ ] Query database: `SELECT * FROM "Experiment" WHERE "id" LIKE '%{run_id}'`
   - [ ] Verify experiment exists with quality_tag="auto_saved"

2. **Test PDF Download (Unsaved):**
   - [ ] Run pipeline
   - [ ] Immediately click "Download PDF" (before clicking "Save")
   - [ ] Verify PDF downloads successfully (no 404)

3. **Test Save Button (Update Flow):**
   - [ ] Run pipeline (auto-saved)
   - [ ] Select quality tag "Good"
   - [ ] Add notes
   - [ ] Click "Save"
   - [ ] Verify experiment updated (not duplicated)
   - [ ] Check quality_tag changed from "auto_saved" to "good"

4. **Test PDF Content:**
   - [ ] Download PDF for auto-saved experiment
   - [ ] Verify markdown formatting (not JSON code blocks)
   - [ ] Verify all 7 stages included

---

## Alternative Investigation: Why Wasn't Experiment Saved?

If user claims they DID click "Save Experiment":

### Debug Steps:

1. **Check HF Space Logs:**
   ```bash
   # Look for save_experiment_wrapper calls in HF Space stdout
   grep "SAVE_EXPERIMENT" hf_space.log
   ```

2. **Check Backend /experiments/save Logs:**
   ```bash
   # Check Railway logs for POST /experiments/save
   railway logs --filter "experiments/save"
   ```

3. **Verify Database Schema:**
   ```sql
   -- Check if Experiment table exists
   SELECT table_name FROM information_schema.tables WHERE table_name = 'Experiment';

   -- Check experiment ID format
   SELECT id, "runId" FROM "Experiment" ORDER BY "createdAt" DESC LIMIT 5;
   ```

4. **Test Database Query Directly:**
   ```sql
   -- Try to find experiment with run_id f3cf35b7
   SELECT * FROM "Experiment" WHERE "id" LIKE '%f3cf35b7';

   -- Check if any experiments exist at all
   SELECT COUNT(*) FROM "Experiment";
   ```

---

## Key Questions for Next Agent

1. **Did user actually click "Save Experiment" button?**
   - If no: Implement Solution A (auto-save)
   - If yes: Investigation needed - why didn't save work?

2. **Are experiments being saved to database successfully?**
   - Check: `SELECT COUNT(*) FROM "Experiment";`
   - If 0: Database connection issue
   - If >0: Query mismatch issue

3. **What is the actual experiment_id format in database?**
   - Check: `SELECT id FROM "Experiment" ORDER BY "createdAt" DESC LIMIT 5;`
   - Verify format matches: `exp-{timestamp}-{run_id[:8]}`

4. **Is the LIKE query working correctly?**
   - Test: `SELECT * FROM "Experiment" WHERE "id" LIKE '%f3cf35b7';`
   - If no results: ID format doesn't match expectation

---

## Files to Reference

### Key Backend Files:
- `backend/app/routes.py` (PDF download endpoint, lines 1014-1131)
- `backend/app/pipeline_runner.py` (pipeline execution, add auto-save after line 270)
- `backend/experimentation/hf-space-deploy/app.py` (HF Space UI, lines 1496-1513)

### Database Schema:
- Table: `Experiment`
- Key fields: `id`, `runId`, `stageOutputs`, `qualityTag`, `experimentNotes`

### Recent Commits:
- `7025237`: Fixed run_id mismatch (HF Space now uses correct run_id)
- Previous: Fixed markdown formatting in PDFs

---

## Success Criteria

Solution is successful when:
1. User can download PDF immediately after pipeline completion (no 404)
2. Experiments are auto-saved to database on completion
3. "Save Experiment" button allows users to refine quality tag and notes
4. PDF downloads work for both auto-saved and user-saved experiments
5. No duplicate experiments created when user clicks "Save"

---

## Notes for Next Agent

- This is an **extremely persistent** issue - approach with deep investigation
- User has high frustration - solution must be robust and permanent
- Consider both technical fix AND user flow improvement
- Test thoroughly before marking complete
- Check all three components: HF Space → Backend API → PostgreSQL

**DO NOT assume the previous fix solved anything. Start fresh with database verification.**
