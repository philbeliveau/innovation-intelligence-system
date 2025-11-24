# Handoff: Fix Markdown Formatting in PDF Exports

## Problem Statement

When downloading PDFs from the Gradio experimentation UI, the pipeline stage outputs are displaying as **raw JSON** instead of **formatted markdown** with headings, bullet points, and proper structure.

**Example of Current Behavior (BROKEN):**
```
{'opportunities': [{'title': 'Concept Name', 'description': '...'}]}
```

**Expected Behavior:**
```
# Stage 5: Opportunity Cards

## Generated Opportunities (3)

### 1. **Concept Name**

**Type**: `Product Innovation`

#### Description
...
```

## Root Cause Analysis

The markdown formatting pipeline has multiple defensive type checks that were added to prevent dict objects from being treated as strings. However, these checks may be **too aggressive** or there's a point in the chain where markdown generation is failing silently.

**Data Flow: Backend → Gradio → PDF**

1. **Backend** (`backend/app/pipeline_runner.py`)
   - Line 80: Calls `format_stage_output(stage_num, stage_data["output"])`
   - Line 82-87: Validates returned markdown is a string
   - Line 83: Stores in `stage_data["markdown"]`

2. **Gradio** (`backend/experimentation/hf-space-deploy/app.py`)
   - Line 487-495: `get_stage_display()` extracts markdown from status response
   - Line 490: Type checks `isinstance(markdown, str)`
   - Line 1405: `download_stage_pdf()` extracts markdown from state

3. **PDF Generator** (`backend/experimentation/hf-space-deploy/export/pdf_export.py`)
   - Line 161-165: Final type check before `markdown2.markdown()`
   - Line 168: Converts markdown to HTML
   - Line 208: Generates PDF with WeasyPrint

## Known Issues

### Issue 1: Stage 5 Nested Structure
Stage 5 output has a nested structure where each opportunity may have its own `markdown` field:

```python
{
  "opportunities": [
    {
      "title": "Concept Name",
      "markdown": "### 1. **Concept Name**\n\n..."  # ← May be dict instead of string
    }
  ]
}
```

**Affected Code:** `backend/pipeline/output_formatters.py` line 259-271

### Issue 2: Silent Fallback to JSON
If `format_stage_output()` fails or returns non-string, the fallback creates JSON code blocks:
```python
stage_data["markdown"] = f"```json\n{json.dumps(stage_data['output'], indent=2)}\n```"
```

This creates **valid markdown** (code block), but displays as JSON instead of formatted content.

## Files Requiring Investigation

### Priority 1: Backend Formatters
**File:** `backend/pipeline/output_formatters.py`

**Focus Areas:**
- `format_stage5_to_markdown()` (line 235-322) - Most complex formatter
- Line 259-271: Type checking for `opp['markdown']` field
- Verify all formatters return strings, not dicts

**Diagnostic Steps:**
1. Add logging to see what type `format_stage_output()` returns
2. Check if `opp['markdown']` is actually a string in Stage 5 outputs
3. Verify Stage 1-4 formatters work correctly (simpler structure)

### Priority 2: Backend Pipeline Runner
**File:** `backend/app/pipeline_runner.py`

**Focus Areas:**
- Line 78-91: `update_status_file()` markdown generation
- Line 80: Call to `format_stage_output()`
- Line 84: Logs markdown length if successful

**Diagnostic Steps:**
1. Check Railway logs for: `"Stage {stage_num} markdown generated ({len(markdown)} chars)"`
2. Check for error logs: `"Stage {stage_num} format_stage_output returned non-string"`
3. Verify `stage_data["markdown"]` is set correctly before writing to status.json

### Priority 3: Stage Output Generation
**Files:** `backend/pipeline/stages/stage*.py`

**Focus Areas:**
- Check what structure Stage 5 actually returns
- Verify if `opportunities` array contains `markdown` fields
- Check if those `markdown` fields are strings or dicts

**Diagnostic Steps:**
1. Add logging in Stage 5 to show output structure before formatting
2. Check if stage returns pre-formatted markdown or raw data
3. Verify stage output matches what formatters expect

## Debugging Strategy

### Step 1: Enable Verbose Logging (Backend)
Add to `backend/app/pipeline_runner.py` line 80:

```python
markdown = format_stage_output(stage_num, stage_data["output"])
logger.info(f"[{run_id}] Stage {stage_num} format output type: {type(markdown)}")
logger.info(f"[{run_id}] Stage {stage_num} format output preview: {str(markdown)[:200]}")
```

### Step 2: Test Individual Formatter
Create test script `backend/tests/test_stage5_formatter.py`:

```python
from pipeline.output_formatters import format_stage5_to_markdown
import json

# Load actual Stage 5 output from recent run
with open('/tmp/runs/{run_id}/status.json', 'r') as f:
    status = json.load(f)
    stage5_output = status['stages']['5']['output']

# Test formatter
result = format_stage5_to_markdown(stage5_output)

print(f"Type: {type(result)}")
print(f"Length: {len(result)}")
print(f"Preview:\n{result[:500]}")
```

### Step 3: Check Railway Logs
```bash
railway logs | grep -E "markdown generated|format_stage_output|Stage 5"
```

Look for:
- ✅ `"Stage 5 markdown generated (1234 chars)"` ← Success
- ❌ `"Stage 5 format_stage_output returned non-string"` ← Type error
- ❌ `"Failed to format stage 5 markdown"` ← Exception

### Step 4: Test Gradio Flow
1. Run pipeline in Gradio UI
2. Check browser console for warnings: `"stage_5 markdown field is not a string"`
3. Try downloading Stage 5 PDF
4. If JSON appears, markdown field contains dict

## Hypothesis: Most Likely Issue

**Hypothesis 1:** Stage 5 opportunities have nested `markdown` fields that are **dicts** instead of **strings**.

**Why:** The type validation at line 259-262 checks `isinstance(opp['markdown'], str)` and logs a warning if false, but then falls through to the structured fallback (line 267-324). This fallback builds markdown from fields, but if those fields are also malformed, it could return JSON.

**Test:**
```python
# In format_stage5_to_markdown() line 260
opp_markdown = opp['markdown']
if isinstance(opp_markdown, str):
    print(f"✅ Opportunity markdown is string ({len(opp_markdown)} chars)")
else:
    print(f"❌ Opportunity markdown is {type(opp_markdown)}: {opp_markdown}")
```

**Hypothesis 2:** The Stage 5 chain output includes pre-formatted markdown that's being double-encoded.

**Why:** If Stage 5 returns `{"markdown": {"text": "..."}}` instead of `{"markdown": "..."}`, the formatter receives a dict.

**Test:**
Check Stage 5 output structure in Railway logs or status.json

## Success Criteria

After fix:
1. ✅ PDFs display formatted markdown with headings, bullets, and structure
2. ✅ No raw JSON `{'key': 'value'}` visible in PDFs
3. ✅ All 7 stages (0-6) format correctly
4. ✅ Railway logs show: `"Stage X markdown generated (N chars)"` for all stages
5. ✅ No warnings: `"markdown field is not a string"`

## Testing Checklist

- [ ] Run full pipeline with existing trend report
- [ ] Download individual stage PDFs (Stage 0-6)
- [ ] Download combined "All Stages" PDF
- [ ] Verify each PDF has:
  - [ ] Proper headings (# ## ###)
  - [ ] Bullet points render as lists
  - [ ] Code blocks formatted correctly
  - [ ] No raw JSON dicts visible
- [ ] Check Railway logs for markdown generation success
- [ ] Check Gradio console for type warnings

## Related Files

**Backend:**
- `backend/pipeline/output_formatters.py` (formatting logic)
- `backend/app/pipeline_runner.py` (markdown generation)
- `backend/pipeline/stages/stage5_opportunity_generation.py` (Stage 5 output)

**Gradio/HF Space:**
- `backend/experimentation/hf-space-deploy/app.py` (UI + PDF download)
- `backend/experimentation/hf-space-deploy/export/pdf_export.py` (PDF generation)

**Recent Fixes:**
- Commit `990f088` - Added type validation to prevent dict/JSON in markdown pipeline
- Commit `6246562` - Updated HF Space submodule with PDF type validation fixes

## Questions for Next Agent

1. What does Railway log show for `"Stage 5 markdown generated"`?
2. What is the actual structure of Stage 5 output in status.json?
3. Does `format_stage5_to_markdown()` return a string or dict?
4. Are there any logged warnings about markdown type mismatches?
5. Does the issue affect all stages or just Stage 5?

## Deployment After Fix

1. **Test locally:**
   ```bash
   cd backend
   pytest tests/test_stage5_formatter.py -v
   ```

2. **Deploy backend:**
   ```bash
   railway up --detach
   ```

3. **Deploy HF Space (if Gradio changes):**
   ```bash
   cd backend/experimentation/hf-space-deploy
   git add .
   git commit -m "fix: resolve markdown formatting in PDF exports"
   git push
   ```

4. **Verify:**
   - Upload trend report in Gradio
   - Run pipeline
   - Download Stage 5 PDF
   - Confirm formatted markdown appears (not JSON)

---

**Status:** Ready for investigation
**Priority:** High - Core feature broken
**Estimated Effort:** 2-4 hours (investigation + fix + testing)
