# Experimentation Pipeline - State Analysis

**Generated:** 2025-11-25
**Branch:** `fix/pdf-export-backend-generation`
**Status:** CRITICAL ISSUES IDENTIFIED

---

## Executive Summary

The experimentation pipeline has **5 critical systemic issues** that prevent it from functioning as designed:

| Issue | Severity | Impact |
|-------|----------|--------|
| **1. Wrong Pipeline Connected** | CRITICAL | Gradio uses 5-stage legacy pipeline instead of 7-stage |
| **2. Custom Prompts Partially Working** | HIGH | Stages 0 & 6 custom prompts validated but never executed |
| **3. PDF Export Outputs JSON** | HIGH | Type validation missing in experimentation export module |
| **4. Few-Shot Learning Broken** | HIGH | Examples never saved, never injected |
| **5. HF Spaces Out of Sync** | MEDIUM | Separate git repo, diverged codebase |

---

## Issue #1: WRONG PIPELINE CONNECTED

### The Problem

Gradio UI is connected to the **LEGACY 5-STAGE PIPELINE**, not the 7-stage experimentation pipeline.

### Architecture Discrepancy

```
WHAT EXISTS:
├── /backend/pipeline/stages/           ← 5 STAGES (ACTIVE - Used by Gradio)
│   ├── stage1_input_processing.py      ✅ Executed
│   ├── stage2_signal_amplification.py  ✅ Executed
│   ├── stage3_general_translation.py   ✅ Executed
│   ├── stage4_brand_contextualization.py ✅ Executed
│   ├── stage5_opportunity_generation.py  ✅ Executed
│   ├── stage0_brand_context.py         ❌ EXISTS BUT NEVER EXECUTED
│   └── stage6_packaging.py             ❌ EXISTS BUT NEVER EXECUTED
│
└── /backend/experimentation/stages/    ← 7 STAGES (UNUSED - Test only)
    ├── stage_0_enrichment.py           ❌ Never called
    ├── stage_1_decomposition.py        ❌ Never called
    ├── stage_2_insights.py             ❌ Never called
    ├── stage_3_techniques.py           ❌ Never called
    ├── stage_4_concepts.py             ❌ Never called
    ├── stage_5_competitive.py          ❌ Never called
    └── stage_6_packaging.py            ❌ Never called
```

### Execution Path

```
Gradio UI (gradio_lab.py)
    ↓ HTTP POST /run/local
FastAPI (routes.py:271)
    ↓ Thread spawn
pipeline_runner.py:execute_pipeline_background()
    ↓ IMPORTS ONLY 5 STAGES
from pipeline.stages.stage1_input_processing import Stage1Chain
from pipeline.stages.stage2_signal_amplification import Stage2Chain
from pipeline.stages.stage3_general_translation import Stage3Chain
from pipeline.stages.stage4_brand_contextualization import Stage4Chain
from pipeline.stages.stage5_opportunity_generation import Stage5Chain
    ↓ EXECUTES
Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → DONE
    ↓
(Stage 0 and Stage 6 NEVER execute)
```

### Key Files

| File | Line | Issue |
|------|------|-------|
| `backend/app/pipeline_runner.py` | 19-23 | Only imports 5 stages |
| `backend/app/routes.py` | 358-364 | Spawns `execute_pipeline_background()` |
| `backend/experimentation/pipeline_orchestrator.py` | ALL | Complete 7-stage implementation, **NEVER WIRED** |

### The Unused 7-Stage Orchestrator

`backend/experimentation/pipeline_orchestrator.py` is a **complete, tested implementation** that:
- Executes all 7 stages (0-6)
- Supports custom prompts for all stages
- Has few-shot injection integration
- **But is NEVER called by any endpoint**

---

## Issue #2: CUSTOM PROMPTS PARTIALLY WORKING

### What Works

| Component | File | Status |
|-----------|------|--------|
| UI Upload | `gradio_lab.py` | ✅ Working |
| Validation | `prompt_file_validator.py` | ✅ Working |
| API Endpoint | `routes.py:283-317` | ✅ Validates stages 0-6 |
| Stage Constructor Injection | `pipeline_runner.py` | ✅ Stages 1-5 only |

### What's Broken

| Component | Issue |
|-----------|-------|
| **Stage 0 Custom Prompt** | Validated by API but never executed (stage not run) |
| **Stage 6 Custom Prompt** | Validated by API but never executed (stage not run) |
| **Response Metadata** | `custom_prompts_used` field missing from status |

### Code Flow

```python
# routes.py:284-317 - VALIDATES all 7 stages
for key, content in request.custom_prompts.items():
    stage_num = int(key.split("_")[1])  # stage_0 → 0, stage_6 → 6
    result = PromptFileValidator.validate(stage_num, content)  # ✅ Validates

# pipeline_runner.py:483-699 - EXECUTES only 5 stages
custom_stage1_prompt = custom_prompts.get("stage_1")  # ✅ Used
custom_stage2_prompt = custom_prompts.get("stage_2")  # ✅ Used
custom_stage3_prompt = custom_prompts.get("stage_3")  # ✅ Used
custom_stage4_prompt = custom_prompts.get("stage_4")  # ✅ Used
custom_stage5_prompt = custom_prompts.get("stage_5")  # ✅ Used
# stage_0 and stage_6 custom prompts: ❌ NEVER RETRIEVED
```

---

## Issue #3: PDF EXPORT OUTPUTS JSON

### Root Cause

**TWO VERSIONS** of `pdf_export.py` exist with different quality levels:

| Version | Location | Type Validation |
|---------|----------|-----------------|
| Backend | `backend/app/pdf_export.py` | ✅ Has type check (lines 160-165) |
| Gradio | `backend/experimentation/export/pdf_export.py` | ❌ NO type check |

### The Bug

**Gradio's pdf_export.py (lines 251-255):**
```python
# NO TYPE VALIDATION - passes dict directly to markdown2
for stage_num in sorted(stage_markdowns.keys()):
    markdown_content = stage_markdowns[stage_num]
    if markdown_content:
        combined_markdown.append(markdown_content)  # ← If dict, becomes JSON
```

**Backend's pdf_export.py (lines 160-165):**
```python
# HAS TYPE VALIDATION
if not isinstance(markdown_content, str):
    logger.error(f"markdown_content is not a string")
    import json
    markdown_content = f"```json\n{json.dumps(markdown_content, indent=2)}\n```"
```

### Impact

When `markdown_content` is a dict (not string):
- Backend version: Wraps in JSON code block (readable but ugly)
- Gradio version: Converts dict to string representation `{'key': 'value'}` (broken)

### Files Affected

| File | Line | Issue |
|------|------|-------|
| `backend/experimentation/export/pdf_export.py` | 251-255 | Missing type validation |
| `backend/experimentation/gradio_lab.py` | 978-1033 | Uses broken export module |
| `backend/pipeline/output_formatters.py` | 322-333 | Stage 5 can return dict |

---

## Issue #4: FEW-SHOT LEARNING BROKEN

### The Problem

"Good" tagged experiments are saved to database but:
1. **Never exported to filesystem** (import fails silently)
2. **Never injected into prompts** (wrong pipeline used)

### Import Chain Failure

**gradio_lab.py (lines 27-41):**
```python
try:
    from few_shot_manager import FileSystemExampleStorage  # HF Spaces style
except ImportError:
    try:
        from backend.experimentation.few_shot_manager import FileSystemExampleStorage
    except ImportError:
        FileSystemExampleStorage = None  # ← SILENT FAILURE
```

When both imports fail, `FileSystemExampleStorage = None`, and:
```python
# Line 836-840
if FileSystemExampleStorage is None:
    return 0, 7  # 0 saved, 7 failed - USER SEES THIS
```

### Evidence of Failure

```bash
$ cat backend/experimentation/successful_examples/stage_*/metadata.json
# ALL show: {"total_examples": 0, "last_updated": null, ...}
```

### Why Injection Never Happens

Even if examples were saved, the **legacy pipeline doesn't call few-shot injection**:

```python
# pipeline_runner.py - NO FEW-SHOT IMPORTS
# Search for: PromptInjector, ExampleSelector, inject_examples → NOT FOUND

# The experimentation stages HAVE few-shot integration:
# stage_1_decomposition.py line 12: from few_shot_integration import inject_examples_into_stage_prompt
# BUT these stages are NEVER EXECUTED
```

### System Flow (Broken)

```
User tags "Good" in Gradio
    ↓
POST /experiments/save → PostgreSQL ✅
    ↓
_export_few_shot_examples() called
    ↓
FileSystemExampleStorage is None → FAILS SILENTLY
    ↓
successful_examples/ remains empty
    ↓
Next pipeline run uses legacy stages (no few-shot import)
    ↓
No improvement from saved examples
```

---

## Issue #5: HF SPACES OUT OF SYNC

### Two Separate Codebases

| Item | Main Project | HF Spaces |
|------|--------------|-----------|
| **File** | `backend/experimentation/gradio_lab.py` | `backend/experimentation/hf-space-deploy/app.py` |
| **Lines** | 2,022 | 2,116 |
| **Git Repo** | Main project | **Separate HF Spaces repo** |
| **MD5** | `5b78d10e565ad4e3b3836c27f21ffd8b` | `9ba81cd0e2b19f2c22fffa503d104997` |

### HF Spaces Deployment Structure

```
hf-space-deploy/
├── app.py                  # Different from main gradio_lab.py
├── requirements.txt        # Pinned: gradio==4.44.1, pydantic>=2.0,<2.9
├── README.md               # HF metadata (sdk_version: 4.44.1)
├── few_shot_manager.py     # Copied (may be outdated)
├── export/pdf_export.py    # Copied (may be outdated)
└── data/brand-profiles/    # Copied brand profiles
```

### Key Differences

1. **Logging**: Main uses `logging` module, HF Spaces uses `print()`
2. **Experiment ID display**: Main shows first 8 chars, HF shows last 8
3. **Git history**: Completely separate (6 commits in HF Space repo)

### Sync Requirement

Changes to these files need **MANUAL PUSH** to HF Spaces:
- `gradio_lab.py` → `hf-space-deploy/app.py`
- `few_shot_manager.py` → `hf-space-deploy/few_shot_manager.py`
- `export/pdf_export.py` → `hf-space-deploy/export/pdf_export.py`

---

## Recommended Fixes

### Priority 1: Wire 7-Stage Pipeline (CRITICAL)

**Option A: Replace pipeline_runner.py imports**
```python
# Change from:
from pipeline.stages.stage1_input_processing import Stage1Chain
# To:
from experimentation.stages.stage_0_enrichment import Stage0Enrichment
from experimentation.stages.stage_1_decomposition import Stage1Decomposition
# ... etc for all 7 stages
```

**Option B: Wire orchestrator to /run/local**
```python
# In routes.py, change execute_pipeline_background() call to:
orchestrator = PipelineOrchestrator()
await orchestrator.run_pipeline(run_id, pdf_text, brand_profile, custom_prompts)
```

### Priority 2: Fix PDF Export Type Validation

**File:** `backend/experimentation/export/pdf_export.py`

Add at line 251:
```python
# Validate markdown_content is string
if not isinstance(markdown_content, str):
    import json
    markdown_content = f"```json\n{json.dumps(markdown_content, indent=2)}\n```"
```

### Priority 3: Fix Few-Shot Import

**File:** `backend/experimentation/gradio_lab.py`

Replace lines 27-41 with robust import:
```python
import sys
from pathlib import Path

# Determine correct import path
experimentation_dir = Path(__file__).parent
if (experimentation_dir / "few_shot_manager.py").exists():
    sys.path.insert(0, str(experimentation_dir))
    from few_shot_manager import FileSystemExampleStorage
else:
    from backend.experimentation.few_shot_manager import FileSystemExampleStorage
```

### Priority 4: Sync HF Spaces

Create sync script or GitHub Action to push changes to HF Spaces repo when main changes.

---

## File Reference Table

| Component | File | Status |
|-----------|------|--------|
| **Gradio UI** | `backend/experimentation/gradio_lab.py` | Active (2,022 lines) |
| **HF Spaces App** | `backend/experimentation/hf-space-deploy/app.py` | Diverged (2,116 lines) |
| **Legacy Pipeline** | `backend/app/pipeline_runner.py` | Active (uses 5 stages) |
| **7-Stage Orchestrator** | `backend/experimentation/pipeline_orchestrator.py` | Complete but unused |
| **Route Handler** | `backend/app/routes.py` | Line 271-368 for `/run/local` |
| **PDF Export (Backend)** | `backend/app/pdf_export.py` | Has type validation |
| **PDF Export (Gradio)** | `backend/experimentation/export/pdf_export.py` | Missing type validation |
| **Few-Shot Manager** | `backend/experimentation/few_shot_manager.py` | Complete but import fails |
| **Prompt Validator** | `backend/pipeline/prompt_file_validator.py` | Working |
| **Output Formatters** | `backend/pipeline/output_formatters.py` | Working (Stage 5 edge case) |

---

## Next Steps

1. [ ] Decide: Wire orchestrator vs extend pipeline_runner
2. [ ] Fix PDF export type validation in experimentation module
3. [ ] Fix few-shot import chain
4. [ ] Add logging for few-shot export success/failure
5. [ ] Establish HF Spaces sync workflow
6. [ ] Add integration tests for full 7-stage flow
