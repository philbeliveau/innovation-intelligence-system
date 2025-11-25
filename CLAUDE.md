# Innovation Intelligence System - Claude Configuration

## 🎯 Current Milestone: Critical Architecture Fixes Required

**Status:** Stories 11.1-11.4 MARKED COMPLETE but with CRITICAL INTEGRATION GAPS
**Timeline:** Architecture consolidation required before production deployment
**Focus:** Fix 5 critical issues blocking proper pipeline execution
**Goal:** Enable innovation teams to upload trend reports, select brand profiles, run the ACTUAL 7-stage pipeline, review generated concepts, and persist experiments to database

**⚠️ CRITICAL STATE ANALYSIS (2025-11-25):**
See `docs/architecture/EXPERIMENTATION-PIPELINE-STATE-ANALYSIS.md` for full details.

| Issue | Severity | Status |
|-------|----------|--------|
| **Wrong Pipeline Connected** | CRITICAL | Gradio uses 5-stage legacy, not 7-stage orchestrator |
| **Custom Prompts Stage 0/6** | HIGH | Validated but never executed |
| **PDF Export Outputs JSON** | HIGH | Missing type validation in experimentation export |
| **Few-Shot Learning Broken** | HIGH | Import fails silently, injection never called |
| **HF Spaces Out of Sync** | MEDIUM | Separate git repo, diverged from main |

**Actual Completion Status:**
- ⚠️ **Story 11.1:** Gradio UI (2,022 lines) - UI complete but connected to WRONG pipeline
- ❌ **Story 11.2:** 7-stage pipeline - BUILT but NEVER WIRED to `/run/local` endpoint
- ❌ **Story 11.3:** Few-shot learning - Import fails silently, 0 examples saved
- ✅ **Story 11.4:** Database persistence (PostgreSQL + psycopg2) - Working
- 🚧 **Story 11.5:** Railway deployment - Blocked by above issues
- ⚠️ **Story 11.6.1:** Custom prompts UI - Working for stages 1-5 only
- ❌ **Story 11.6.2:** Custom prompts backend - Stage 0/6 validated but never executed

### Problem Statement

**Core Hypothesis:** CPG innovation teams at companies like Lactalis, McCormick, and Decathlon pay $50K/year for trend reports (Mintel, WGSN) but lack the "muscle" to:
- Generalize insights to their specific industry and operations
- Extract actionable value from trend data
- Apply global trends to their product categories
- Generate concrete initiative concepts from emotional trends

### Pipeline Architecture: SIT-Based Extraction Framework

**Core Innovation:** Transform general emotional trends into industry-specific initiative concepts using **Systematic Inventive Thinking (SIT)** framework.

#### Two-Input Extraction Model

**INPUT 1: Trend Report (WGSN/Mintel)**
- Emotional trends (e.g., "Strategic Joy," "Witherwill," "Suspicious Optimism")
- Lifecycle stage (EMERGING → ACCELERATING → PEAKING)
- Evidence and weak signals
- Timeline predictions
- General consumer behavior shifts

**INPUT 2: Brand Profile (YAML Structure)**

**Required Fields:**
1. **brand_name**: Company/brand identifier
2. **country**: Geographic market
3. **industry**: Sector classification
4. **product_portfolio**: List of product lines/SKUs

**Optional Enrichment:**
- **positioning**: Brand positioning statement
- **target_customers**: Customer segments
- **recent_innovations**: Recent product launches
- **strategic_priorities**: Business priorities
- **brand_values**: Core values

**Available via Dropdown in UI:**
- Lactalis Canada (Dairy/Food & Beverage)
- Decathlon (Sporting Goods Retail)
- Colombia Sportswear (Outdoor Apparel)
- McCormick (Spices & Seasonings)

#### 7-Stage Production Pipeline (INTENDED BUT NOT ACTIVE)

**⚠️ CRITICAL:** The system INTENDS to use 7 stages but ACTUALLY executes only 5.

**TWO PARALLEL IMPLEMENTATIONS EXIST:**

```
LEGACY 5-STAGE (CURRENTLY ACTIVE):
backend/pipeline/stages/
├── stage1_input_processing.py      ✅ EXECUTED
├── stage2_signal_amplification.py  ✅ EXECUTED
├── stage3_general_translation.py   ✅ EXECUTED
├── stage4_brand_contextualization.py ✅ EXECUTED
├── stage5_opportunity_generation.py  ✅ EXECUTED
├── stage0_brand_context.py         ❌ FILE EXISTS, NEVER IMPORTED
└── stage6_packaging.py             ❌ FILE EXISTS, NEVER IMPORTED

EXPERIMENTATION 7-STAGE (BUILT BUT UNUSED):
backend/experimentation/stages/
├── stage_0_enrichment.py           ❌ NEVER CALLED (has few-shot integration)
├── stage_1_decomposition.py        ❌ NEVER CALLED (has few-shot integration)
├── stage_2_insights.py             ❌ NEVER CALLED (has few-shot integration)
├── stage_3_techniques.py           ❌ NEVER CALLED (has few-shot integration)
├── stage_4_concepts.py             ❌ NEVER CALLED (has few-shot integration)
├── stage_5_competitive.py          ❌ NEVER CALLED (has few-shot integration)
└── stage_6_packaging.py            ❌ NEVER CALLED (has few-shot integration)
```

**STAGE 0: BRAND CONTEXT** ❌ (EXISTS BUT NEVER EXECUTED)
- Format brand profile data for UI display
- Output: Structured markdown with company name, industry, geography, product portfolio
- Legacy file: `backend/pipeline/stages/stage0_brand_context.py` (never imported)
- Experimentation file: `backend/experimentation/stages/stage_0_enrichment.py` (never called)

**STAGE 1: TREND DECOMPOSITION** ✅ (ACTIVE via legacy)
- Extract structured trend objects from report
- Output: Reusable trend JSON (lifecycle, evidence, emotional drivers, aspirations)
- Active: `backend/pipeline/stages/stage1_input_processing.py`

**STAGE 2: CONSUMER INSIGHT SYNTHESIS** ✅ (ACTIVE via legacy)
- Map general trend → brand/industry-specific consumer want
- Example: "Witherwill" (general) → "I'm overwhelmed by bread choices" (industry-specific)
- Output: Consumer wants/needs grounded in brand context
- Active: `backend/pipeline/stages/stage2_signal_amplification.py`

**STAGE 3: SIT TECHNIQUE MATCHING** ✅ (ACTIVE via legacy)
- Analyze consumer want + brand resources
- Match to one of 5 SIT techniques:
  - **Subtraction**: Remove essential component
  - **Task Unification**: Assign new task to existing resource
  - **Multiplication**: Copy component with variation
  - **Attribute Dependency**: Correlate two attributes
  - **Division**: Separate in space/time
- Output: Selected SIT technique + rationale
- Active: `backend/pipeline/stages/stage3_general_translation.py`

**STAGE 4: INITIATIVE CONCEPT GENERATION** ✅ (ACTIVE via legacy)
- Apply SIT technique → directional concept
- Output: Product/service/marketing initiative concept
- Active: `backend/pipeline/stages/stage4_brand_contextualization.py`

**STAGE 5: COMPETITIVE POSITIONING** ✅ (ACTIVE via legacy)
- Analyze competitive landscape and differentiation
- Output: Competitive analysis and positioning strategy
- Active: `backend/pipeline/stages/stage5_opportunity_generation.py`

**STAGE 6: EXECUTIVE SUMMARY** ❌ (EXISTS BUT NEVER EXECUTED)
- Generate executive summary with packaging/opportunity card
- Structure: Trend → Consumer Insight → SIT Technique → Initiative Concept → Competitive Edge
- Output: Final packaged opportunity card
- Legacy file: `backend/pipeline/stages/stage6_packaging.py` (never imported)
- Experimentation file: `backend/experimentation/stages/stage_6_packaging.py` (never called)

**Pipeline Boundaries:**
- ✅ Synthesize trend + brand context
- ✅ Generate consumer insights via reasoning
- ✅ Match SIT techniques and create concepts
- ❌ NO financial projections, market statistics, or business plans

#### Structural Mechanism Definition

**"Structural Mechanism" = SIT Technique + Application Context**

Stored as transferable, domain-agnostic building blocks for latent space ideation engine:

```json
{
  "trend": "Witherwill",
  "consumer_need": "Simplify decision-making",
  "sit_technique": "Task Unification",
  "component": "Shelf/Packaging",
  "new_task": "Choice simplification",
  "transferable_pattern": "Unify decision-support with existing customer touchpoints"
}
```

### No-Hallucination Boundaries

**What LLM CANNOT Do:**
- ❌ Fabricate market statistics (TAM, market share, growth rates)
- ❌ Invent competitive intelligence ("NO brand does X")
- ❌ Generate financial projections or ROI predictions
- ❌ Create detailed business plans or validation steps
- ❌ Infer data not present in source documents

**What LLM DOES:**
- ✅ Synthesize trend report + brand context
- ✅ Generate consumer insights via reasoning
- ✅ Match SIT techniques to problems
- ✅ Create directional initiative concepts
- ✅ Use ONLY explicitly provided data

### Example Output (Boulangerie St-Méthode)

```
TREND: Witherwill (EMERGING → ACCELERATING, peaks 2027)
EVIDENCE: "Longing to be free from responsibility, decision fatigue, ping minimalism"

CONSUMER INSIGHT: "I'm overwhelmed by bread choices - just tell me THE ONE bread for my family"

SIT TECHNIQUE: Task Unification
MECHANISM: Assign choice-simplification task to existing shelf/packaging resource

INITIATIVE: Le Guide St-Méthode (The Bread Finder Tool)
CONCEPT: Decision-support tool where consumers answer 3 questions and receive ONE
St-Méthode bread recommendation. Delivered via QR code on shelf and online.

BRAND CONTEXT (PROVIDED): St-Méthode operates in Quebec, manufactures bread,
has 25 SKUs with healthy bread focus.
```

### Success Criteria

Innovation teams see the demo and react with: **"Woah, okay, THIS is what this report is signaling and these are concrete initiatives we could explore for our brand"**

### System Architecture Overview

**CRITICAL ARCHITECTURE DISCREPANCY:** There are TWO pipeline implementations with INCOMPLETE INTEGRATION:

#### 1. LEGACY 5-STAGE PIPELINE (CURRENTLY ACTIVE)

**Used by BOTH Gradio + Next.js apps**

| Component | File | Line |
|-----------|------|------|
| Entry Point | `backend/app/routes.py` | 271-368 (`/run/local`) |
| Executor | `backend/app/pipeline_runner.py` | 434-740 (`execute_pipeline_background()`) |
| Stage 1 | `backend/pipeline/stages/stage1_input_processing.py` | Imported at line 19 |
| Stage 2 | `backend/pipeline/stages/stage2_signal_amplification.py` | Imported at line 20 |
| Stage 3 | `backend/pipeline/stages/stage3_general_translation.py` | Imported at line 21 |
| Stage 4 | `backend/pipeline/stages/stage4_brand_contextualization.py` | Imported at line 22 |
| Stage 5 | `backend/pipeline/stages/stage5_opportunity_generation.py` | Imported at line 23 |

**Missing:** Stage 0 and Stage 6 files exist but are NEVER imported in `pipeline_runner.py`

#### 2. EXPERIMENTATION 7-STAGE ORCHESTRATOR (NEVER WIRED)

**Complete implementation but NOT integrated with any endpoint**

| Component | File | Status |
|-----------|------|--------|
| Orchestrator | `backend/experimentation/pipeline_orchestrator.py` | Complete, tested, UNUSED |
| Stage 0-6 | `backend/experimentation/stages/stage_*.py` | Complete with few-shot, UNUSED |
| Tests | `test_orchestrator.py`, `test_end_to_end.py` | Pass but test-only |

**WHY IT'S UNUSED:** No code in `routes.py` or anywhere else instantiates `PipelineOrchestrator`.

#### Current Architecture Status

| Component | Status | Issue |
|-----------|--------|-------|
| Gradio UI | ✅ 2,022 lines | Connected to wrong pipeline |
| `/run/local` endpoint | ✅ Working | Uses legacy 5-stage |
| PostgreSQL persistence | ✅ Working | - |
| Few-shot export | ❌ Broken | Import fails silently |
| Few-shot injection | ❌ Broken | Legacy pipeline has no injection code |
| PDF export | ❌ Broken | JSON in PDF (type validation missing) |
| HF Spaces | ⚠️ Diverged | Separate git repo, out of sync |

#### Required Fix: Wire Orchestrator to /run/local

**Option A (Recommended):** Replace `execute_pipeline_background()` call in `routes.py:358-364`:
```python
# Current (BROKEN):
thread = Thread(target=execute_pipeline_background, args=(...))

# Fix: Use orchestrator instead
from backend.experimentation.pipeline_orchestrator import PipelineOrchestrator
orchestrator = PipelineOrchestrator()
# Note: Orchestrator is async, need to handle in thread or make endpoint async
```

**Option B:** Add Stage 0 and 6 imports to `pipeline_runner.py` and extend execution loop.

**Brand Profiles Available:**
- `/data/brand-profiles/lactalis-canada.yaml` - Dairy/Food & Beverage (Canada)
- `/data/brand-profiles/decathlon.yaml` - Sporting Goods Retail (Global)
- `/data/brand-profiles/columbia-sportswear.yaml` - Outdoor Apparel (USA)
- `/data/brand-profiles/mccormick-usa.yaml` - Spices & Seasonings (USA)

**Test Dataset:**
- `WGSN - FC27-Emotions - Report.pdf` (Emotional trends: Witherwill, Strategic Joy, etc.)

---

## 🧪 Gradio Experimentation Workflow

### User Journey (ACTUAL vs INTENDED)

| Step | User Sees | What Actually Happens |
|------|-----------|----------------------|
| 1. Upload PDF | ✅ Works | PDF extracted via PyPDF2 |
| 2. Select Brand | ✅ Works | YAML profile loaded |
| 3. Run Pipeline | UI shows 7 stages | ⚠️ Only 5 stages execute (Stage 0, 6 skipped) |
| 4. Review Outputs | 7 tabs displayed | ⚠️ Stage 0, 6 tabs empty or placeholder |
| 5. Tag Quality | ✅ Works | Tag saved to database |
| 6. Save to Database | ✅ Works | PostgreSQL insert succeeds |
| 7. Few-Shot Export | UI says "exported" | ❌ Import fails silently, 0 files saved |
| 8. Download PDF | Click download | ❌ PDF contains JSON instead of formatted markdown |

### File Structure

```
backend/experimentation/
├── gradio_lab.py              # Main Gradio application - 2,022 lines
├── pipeline_orchestrator.py   # 7-stage orchestrator (COMPLETE BUT UNUSED)
├── few_shot_manager.py        # Few-shot storage (import fails silently)
├── prompt_injection.py        # Few-shot injection (never called by active pipeline)
├── prompt_template_library.py # Prompt templates for pipeline stages
├── export/
│   └── pdf_export.py          # ❌ MISSING TYPE VALIDATION (line 251)
├── stages/                    # 7-stage implementations (UNUSED)
│   ├── stage_0_enrichment.py
│   ├── stage_1_decomposition.py
│   ├── stage_2_insights.py
│   ├── stage_3_techniques.py
│   ├── stage_4_concepts.py
│   ├── stage_5_competitive.py
│   └── stage_6_packaging.py
├── successful_examples/       # ❌ EMPTY (0 examples in all stage folders)
│   ├── stage_0/metadata.json  # {"total_examples": 0}
│   ├── stage_1/metadata.json  # {"total_examples": 0}
│   └── ...
└── hf-space-deploy/           # ⚠️ SEPARATE GIT REPO - OUT OF SYNC
    ├── app.py                 # Different from gradio_lab.py (2,116 vs 2,022 lines)
    ├── requirements.txt       # Pinned: gradio==4.44.1
    └── README.md              # HF Spaces metadata

backend/app/
├── routes.py                  # /run/local endpoint (line 271-368)
├── pipeline_runner.py         # LEGACY 5-stage executor (line 434-740)
├── pdf_export.py              # ✅ HAS type validation (line 160-165)
└── models.py                  # Request/response models

backend/pipeline/stages/       # LEGACY 5-STAGE (ACTIVE)
├── stage1_input_processing.py
├── stage2_signal_amplification.py
├── stage3_general_translation.py
├── stage4_brand_contextualization.py
├── stage5_opportunity_generation.py
├── stage0_brand_context.py    # ❌ EXISTS BUT NEVER IMPORTED
└── stage6_packaging.py        # ❌ EXISTS BUT NEVER IMPORTED
```

### Integration Architecture

```
┌─────────────────────────────┐
│  Gradio UI                  │ (Port 7860 - localhost or HF Spaces)
│  backend/experimentation/   │
│  gradio_lab.py (2,022 lines)│
└──────────┬──────────────────┘
           │
           │ HTTP POST /run/local (httpx, 120s timeout)
           ▼
┌─────────────────────────────┐
│  FastAPI Backend            │ (Railway: innovation-backend-production.up.railway.app)
│  backend/app/routes.py:271  │
│                             │
│  Key Endpoints:             │
│  POST /run/local            │ ← Spawns execute_pipeline_background() thread
│  GET  /status/{run_id}      │ ← Returns status.json content
│  POST /experiments/save     │ ← Insert to PostgreSQL
│  GET  /experiments/list     │ ← Query PostgreSQL
│                             │
│  ⚠️ PROBLEM: routes.py:358  │
│  Calls legacy pipeline_runner.py (5 stages only)
│  NOT pipeline_orchestrator.py (7 stages)
└──────────┬──────────────────┘
           │
           │ execute_pipeline_background() - pipeline_runner.py:434
           ▼
┌─────────────────────────────┐
│  LEGACY 5-STAGE PIPELINE    │ (WHAT ACTUALLY RUNS)
│  backend/app/pipeline_runner.py
│                             │
│  Imports (lines 19-23):     │
│  - Stage1Chain              │ ✅ Executed
│  - Stage2Chain              │ ✅ Executed
│  - Stage3Chain              │ ✅ Executed
│  - Stage4Chain              │ ✅ Executed
│  - Stage5Chain              │ ✅ Executed
│  ❌ Stage0 NOT IMPORTED     │
│  ❌ Stage6 NOT IMPORTED     │
└──────────┬──────────────────┘
           │
           │ psycopg2 (bypassing Prisma)
           ▼
┌─────────────────────────────┐
│  PostgreSQL Database        │ (Railway)
│                             │
│  Table: Experiment          │
│  - stageOutputs (Json)      │ ← Contains only stages 1-5
│  - qualityTag (String)      │ ← Good/Needs Work/Failed
└─────────────────────────────┘
```

**Integration Flow (ACTUAL):**

1. **PDF Upload** → `extract_pdf_text()` (PyPDF2, 50MB limit) → Cached in `gr.State()` ✅
2. **Run Pipeline** → `POST /run/local` with `{pdf_text, brand_profile, run_id}` ✅
3. **Backend Execution** → `execute_pipeline_background()` runs **STAGES 1-5 ONLY** ⚠️
4. **Progress Polling** → Gradio polls `GET /status/{run_id}` every 2s ✅
5. **Markdown Rendering** → `format_stage_output()` called for stages 1-5 only ⚠️
6. **Database Save** → User tags quality → `POST /experiments/save` → PostgreSQL ✅
7. **Few-Shot Export** → `_export_few_shot_examples()` → **IMPORT FAILS, 0 FILES SAVED** ❌
8. **PDF Download** → `generate_all_stages_pdf()` → **JSON IN PDF (no type validation)** ❌

### Running Gradio Locally

```bash
# From project root
cd backend/experimentation
python gradio_lab.py

# Access at http://localhost:7860
# Optional: Set GRADIO_SHARE=true for public link
```

---

## 🚀 Deployment to Railway

### Backend Service (DEPLOYED ✅)

**Service:** `innovation-backend-production`
**URL:** `https://innovation-backend-production.up.railway.app`
**Status:** Production-ready

**Configuration:**
- **Root Directory**: `backend` (configured in Railway dashboard)
- **Build**: Dockerfile-based build
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**: `DATABASE_URL`, `OPENROUTER_API_KEY`, `WEBHOOK_SECRET`, `VERCEL_BLOB_READ_WRITE_TOKEN`

**Deploying Backend Updates:**

```bash
# Deploy from PROJECT ROOT (not from backend directory)
cd /Users/philippebeliveau/Desktop/Notebook/innovation-intelligence-system
railway deploy

# Monitor deployment
railway logs
```

**Important:** Railway service has `backend` configured as root directory in dashboard. Always deploy from project root.

---

### Gradio Service (PENDING 🚧 - Story 11.5)

**CRITICAL FIX REQUIRED BEFORE DEPLOYMENT:**

The Gradio service currently hardcodes port 7860, which will fail on Railway (requires dynamic `$PORT` env var).

**File:** `backend/experimentation/gradio_lab.py`
**Line:** 1510

**Current Code (BROKEN for Railway):**
```python
server_port=7860  # Hardcoded - fails on Railway
```

**Required Fix:**
```python
server_port=int(os.getenv("PORT", 7860))  # Dynamic port for Railway
```

**Deployment Steps (after PORT fix):**

1. **Fix PORT Configuration**
   ```bash
   # Edit backend/experimentation/gradio_lab.py line 1510
   # Change: server_port=7860
   # To: server_port=int(os.getenv("PORT", 7860))
   ```

2. **Create Railway Service**
   ```bash
   # From project root
   railway service create gradio-experimentation-ui
   ```

3. **Configure Service Settings**
   - Root Directory: `backend/experimentation`
   - Start Command: `python gradio_lab.py`
   - Environment Variables:
     - `BACKEND_URL=https://innovation-backend-production.up.railway.app`
     - `DATABASE_URL` (copy from backend service)
     - `PORT` (auto-injected by Railway)

4. **Deploy**
   ```bash
   railway deploy
   ```

5. **Verify Deployment**
   - Access Gradio UI at Railway-provided URL
   - Test PDF upload → pipeline execution → database save flow

**Reference:** See `docs/stories/11.5.railway-deployment.md` for complete deployment guide

---

## 🛠️ Development Guidelines for Current Phase

### Story-Driven Development

- **Active Story:** Follow `docs/stories/11.5.railway-deployment.md` for Gradio deployment
- **Task Checklist:** Complete subtasks in order specified in story
- **Testing:** Write tests in `/backend/tests/experimentation/` before implementation
- **Quality Gates:** All acceptance criteria must pass before story completion

### Brand Profile Integration

**YAML Loading Pattern:**
```python
import yaml
from pathlib import Path

def load_brand_profile(brand_name: str):
    """Load brand profile from /data/brand-profiles/"""
    profile_path = Path(f"data/brand-profiles/{brand_name}.yaml")
    with open(profile_path, 'r') as f:
        return yaml.safe_load(f)
```

**Available Profiles:**
- `lactalis-canada.yaml` → "Lactalis Canada"
- `decathlon.yaml` → "Decathlon"
- `columbia-sportswear.yaml` → "Colombia Sportswear"
- `mccormick-usa.yaml` → "McCormick"

### Gradio UI Development

**Key Components:**
- `gr.File()` - PDF upload with 50MB limit
- `gr.Dropdown()` - Brand profile selector
- `gr.Button()` - Pipeline execution trigger
- `gr.Tabs()` - 7-stage output display
- `gr.Radio()` - Quality tagging (Good/Needs Work/Failed)

**Backend Integration:**
```python
import httpx

async def run_pipeline(pdf_text: str, brand_profile: dict):
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://innovation-backend-production.up.railway.app/run/local",
            json={"report_text": pdf_text, "brand_profile": brand_profile}
        )
        return response.json()["run_id"]
```

### File Organization Rules

- ✅ **DO:** Save Gradio files to `/backend/experimentation/`
- ✅ **DO:** Save tests to `/backend/tests/experimentation/`
- ✅ **DO:** Reference brand profiles from `/data/brand-profiles/`
- ❌ **DON'T:** Create files in project root
- ❌ **DON'T:** Modify existing backend API unless required by story

### Important Reminders

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary for achieving your goal
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files (*.md) or README files
- **CRITICAL:** Do NOT modify Next.js app code when fixing Gradio issues - they share backend but are distinct products

---

## 🚨 CRITICAL BUGS - FIX LOCATIONS

### Bug #1: Wrong Pipeline Connected (CRITICAL)

**Symptom:** UI shows 7 stages but only 5 execute
**Root Cause:** `/run/local` calls legacy `execute_pipeline_background()` not `PipelineOrchestrator`

| Fix Location | File | Line |
|--------------|------|------|
| Thread spawn | `backend/app/routes.py` | 358-364 |
| Legacy executor | `backend/app/pipeline_runner.py` | 434-740 |
| Unused orchestrator | `backend/experimentation/pipeline_orchestrator.py` | ALL |

**Fix:** Replace `execute_pipeline_background()` call with `PipelineOrchestrator.run_pipeline()`

---

### Bug #2: PDF Export Outputs JSON (HIGH)

**Symptom:** Downloaded PDF contains `{'key': 'value'}` instead of formatted text
**Root Cause:** `experimentation/export/pdf_export.py` missing type validation

| Fix Location | File | Line |
|--------------|------|------|
| Missing validation | `backend/experimentation/export/pdf_export.py` | 251-255 |
| Working version | `backend/app/pdf_export.py` | 160-165 |

**Fix:** Add to `experimentation/export/pdf_export.py` line 251:
```python
if not isinstance(markdown_content, str):
    import json
    markdown_content = f"```json\n{json.dumps(markdown_content, indent=2)}\n```"
```

---

### Bug #3: Few-Shot Learning Broken (HIGH)

**Symptom:** "Good" experiments saved to DB but few-shot never improves output
**Root Cause:** (A) Import fails silently, (B) Legacy pipeline has no injection code

| Fix Location | File | Line |
|--------------|------|------|
| Silent import failure | `backend/experimentation/gradio_lab.py` | 27-41 |
| Missing injection | `backend/app/pipeline_runner.py` | N/A (no few-shot imports) |
| Empty examples | `backend/experimentation/successful_examples/*/metadata.json` | ALL show 0 |

**Fix A:** Make import path robust in `gradio_lab.py`:
```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from few_shot_manager import FileSystemExampleStorage
```

**Fix B:** Add few-shot injection to legacy pipeline OR wire orchestrator (has injection built-in)

---

### Bug #4: Custom Prompts Stage 0/6 Never Execute (HIGH)

**Symptom:** Custom prompts for Stage 0 and 6 validated but have no effect
**Root Cause:** Legacy pipeline only imports stages 1-5

| Fix Location | File | Line |
|--------------|------|------|
| Validation (works) | `backend/app/routes.py` | 283-317 |
| Missing imports | `backend/app/pipeline_runner.py` | 19-23 |

**Fix:** Add Stage0 and Stage6 imports to `pipeline_runner.py` OR wire orchestrator

---

### Bug #5: HF Spaces Out of Sync (MEDIUM)

**Symptom:** HF Spaces has different code than main Gradio
**Root Cause:** `hf-space-deploy/` is a separate git repository

| File Comparison | Main | HF Spaces |
|-----------------|------|-----------|
| App | `gradio_lab.py` (2,022 lines) | `hf-space-deploy/app.py` (2,116 lines) |
| Git | Main project repo | Separate HF Spaces repo |

**Fix:** Establish sync workflow - either git submodule or manual push script

---

## 📋 Quick Reference: Key File Locations

| Component | Path | Line(s) |
|-----------|------|---------|
| **Route Handler** | `backend/app/routes.py` | 271-368 |
| **Legacy Pipeline** | `backend/app/pipeline_runner.py` | 434-740 |
| **7-Stage Orchestrator** | `backend/experimentation/pipeline_orchestrator.py` | ALL |
| **Gradio UI** | `backend/experimentation/gradio_lab.py` | ALL |
| **PDF Export (Broken)** | `backend/experimentation/export/pdf_export.py` | 251 |
| **PDF Export (Working)** | `backend/app/pdf_export.py` | 160 |
| **Few-Shot Manager** | `backend/experimentation/few_shot_manager.py` | ALL |
| **Few-Shot Import** | `backend/experimentation/gradio_lab.py` | 27-41 |
| **Output Formatters** | `backend/pipeline/output_formatters.py` | 476-507 |
| **HF Spaces App** | `backend/experimentation/hf-space-deploy/app.py` | ALL |

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
