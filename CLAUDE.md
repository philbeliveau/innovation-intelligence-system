# Innovation Intelligence System - Claude Configuration

## 🎯 Current Milestone: Gradio Experimentation System - Deployment Phase

**Status:** Stories 11.1-11.4 COMPLETE ✅ → Story 11.5 Railway Deployment
**Timeline:** Production-ready experimentation UI with database persistence
**Focus:** Deploy Gradio service to Railway for experimentation access
**Goal:** Enable innovation teams to upload trend reports, select brand profiles, run the 7-stage pipeline, review generated concepts, and persist experiments to database

**Completion Status:**
- ✅ **Story 11.1:** Gradio UI (1,518 lines, 95%+ test coverage)
- ✅ **Story 11.2:** 7-stage pipeline integration (Stage 0-6)
- ✅ **Story 11.3:** Few-shot learning system
- ✅ **Story 11.4:** Database persistence (PostgreSQL + psycopg2)
- 🚧 **Story 11.5:** Railway deployment (PORT fix required)

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

#### 7-Stage Production Pipeline (ACTIVE)

**IMPORTANT:** The system uses a 7-stage pipeline (Stage 0-6), NOT 5 stages.

**STAGE 0: BRAND CONTEXT** ✅ (NEW)
- Format brand profile data for UI display
- Output: Structured markdown with company name, industry, geography, product portfolio
- Implementation: `backend/pipeline/stages/stage0_brand_context.py`

**STAGE 1: TREND DECOMPOSITION**
- Extract structured trend objects from report
- Output: Reusable trend JSON (lifecycle, evidence, emotional drivers, aspirations)
- Implementation: `backend/pipeline/stages/stage1.py`

**STAGE 2: CONSUMER INSIGHT SYNTHESIS**
- Map general trend → brand/industry-specific consumer want
- Example: "Witherwill" (general) → "I'm overwhelmed by bread choices" (industry-specific)
- Output: Consumer wants/needs grounded in brand context
- Implementation: `backend/pipeline/stages/stage2.py`

**STAGE 3: SIT TECHNIQUE MATCHING**
- Analyze consumer want + brand resources
- Match to one of 5 SIT techniques:
  - **Subtraction**: Remove essential component
  - **Task Unification**: Assign new task to existing resource
  - **Multiplication**: Copy component with variation
  - **Attribute Dependency**: Correlate two attributes
  - **Division**: Separate in space/time
- Output: Selected SIT technique + rationale
- Implementation: `backend/pipeline/stages/stage3.py`

**STAGE 4: INITIATIVE CONCEPT GENERATION**
- Apply SIT technique → directional concept
- Output: Product/service/marketing initiative concept
- Implementation: `backend/pipeline/stages/stage4.py`

**STAGE 5: COMPETITIVE POSITIONING**
- Analyze competitive landscape and differentiation
- Output: Competitive analysis and positioning strategy
- Implementation: `backend/pipeline/stages/stage5.py`

**STAGE 6: EXECUTIVE SUMMARY** ✅ (NEW)
- Generate executive summary with packaging/opportunity card
- Structure: Trend → Consumer Insight → SIT Technique → Initiative Concept → Competitive Edge
- Output: Final packaged opportunity card
- Implementation: `backend/pipeline/stages/stage6_packaging.py`

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

**CRITICAL:** There are TWO pipeline implementations in the codebase:

1. **PRODUCTION PIPELINE** (ACTIVE - wired to Gradio UI)
   - Location: `backend/pipeline/stages/stage0-6.py`
   - Status: ✅ Complete and functional (7 stages)
   - Used by: Gradio UI via `/run/local` endpoint

2. **EXPERIMENTAL PIPELINE** (RESEARCH ONLY - NOT wired)
   - Location: `backend/experimentation/stages/`
   - Status: Research prototypes, not integrated with UI
   - Purpose: Testing alternative stage implementations

**Current Architecture Status:**
- ✅ Gradio UI implementation (1,518 lines at `backend/experimentation/gradio_lab.py`)
- ✅ FastAPI backend integration (`/run/local`, `/status/{run_id}`, `/experiments/*`)
- ✅ PostgreSQL database with psycopg2 (direct connection, bypassing Prisma for Gradio)
- ✅ Few-shot learning with auto-export of "Good" tagged experiments
- ✅ Markdown formatting for all 7 stages via `output_formatters.py`
- 🚧 Railway deployment pending (PORT configuration fix required)

**Brand Profiles Available:**
- `/data/brand-profiles/lactalis-canada.yaml` - Dairy/Food & Beverage (Canada)
- `/data/brand-profiles/decathlon.yaml` - Sporting Goods Retail (Global)
- `/data/brand-profiles/columbia-sportswear.yaml` - Outdoor Apparel (USA)
- `/data/brand-profiles/mccormick-usa.yaml` - Spices & Seasonings (USA)

**Test Dataset:**
- `WGSN - FC27-Emotions - Report.pdf` (Emotional trends: Witherwill, Strategic Joy, etc.)

---

## 🧪 Gradio Experimentation Workflow

### User Journey

1. **Upload Trend Report** - Drag-and-drop PDF (Mintel/WGSN, max 50MB)
2. **Select Brand Profile** - Choose from dropdown or enter manually
3. **Run Pipeline** - Click "Run Pipeline" button (triggers 7-stage extraction: Stage 0-6)
4. **Review Outputs** - Tabbed interface showing all 7 stages with markdown formatting
5. **Tag Quality** - Mark as Good/Needs Work/Failed with notes
6. **Save to Database** - Persist to PostgreSQL experiments table
7. **Auto-Export** - "Good" examples auto-exported to `/backend/experimentation/successful_examples/` for few-shot learning

### File Structure

```
backend/experimentation/
├── gradio_lab.py              # Main Gradio application (Story 11.1) - 1,518 lines
├── enhanced_gradio_lab.py     # Enhanced version with advanced features
├── few_shot_manager.py        # Few-shot learning system (Story 11.3)
├── prompt_template_library.py # Prompt templates for pipeline stages
├── quality_scorer.py          # Quality assessment logic
├── trend_filter.py            # Trend filtering utilities
├── requirements.txt           # Gradio + dependencies
└── successful_examples/       # Curated "Good" examples for few-shot learning

backend/tests/experimentation/
└── test_gradio_lab.py         # Gradio UI tests (Story 11.1)

data/brand-profiles/
├── lactalis-canada.yaml       # Lactalis brand profile
├── decathlon.yaml             # Decathlon brand profile
├── columbia-sportswear.yaml   # Colombia brand profile
├── mccormick-usa.yaml         # McCormick brand profile
└── [brand-name]/              # Supporting documentation folders
```

### Integration Architecture

```
┌─────────────────────────────┐
│  Gradio UI                  │ (Port 7860 - localhost or Railway)
│  backend/experimentation/   │
│  gradio_lab.py (1,518 lines)│
└──────────┬──────────────────┘
           │
           │ HTTP POST (httpx AsyncClient, 120s timeout)
           ▼
┌─────────────────────────────┐
│  FastAPI Backend            │ (Railway: innovation-backend-production.up.railway.app)
│  backend/app/               │
│                             │
│  Key Endpoints:             │
│  POST /run/local            │ ← Start pipeline with PDF text + brand profile
│  GET  /status/{run_id}      │ ← Poll every 2s for stage progress (Gradio gr.Progress)
│  POST /experiments/save     │ ← Save experiment to database
│  GET  /experiments/list     │ ← Retrieve experiment history
│                             │
│  Pipeline Execution:        │
│  - background thread        │
│  - /tmp/runs/{run_id}/      │ ← status.json updated per stage
│  - markdown formatting      │ ← via output_formatters.py
└──────────┬──────────────────┘
           │
           │ psycopg2 (direct connection, bypassing Prisma for Gradio)
           ▼
┌─────────────────────────────┐
│  PostgreSQL Database        │ (Railway)
│                             │
│  Table: Experiment          │
│  - id (String)              │
│  - runId (String)           │
│  - reportText (String)      │
│  - brandProfile (Json)      │ ← JSONB field
│  - stageOutputs (Json)      │ ← JSONB field (stages 0-6)
│  - qualityTag (String)      │ ← Good/Needs Work/Failed
│  - experimentNotes (String) │
│  - pipelineVersion (String) │
│  - createdAt (DateTime)     │
└─────────────────────────────┘
```

**Integration Flow:**

1. **PDF Upload** → `extract_pdf_text()` (PyPDF2, 50MB limit) → Cached in `gr.State()`
2. **Run Pipeline** → `POST /run/local` with `{pdf_text, brand_profile, run_id}`
3. **Backend Execution** → Background thread executes Stages 0-6, updates `/tmp/runs/{run_id}/status.json`
4. **Progress Polling** → Gradio polls `GET /status/{run_id}` every 2s, displays via `gr.Progress()`
5. **Markdown Rendering** → Backend adds `markdown` field to each stage via `format_stage_output()`
6. **Database Save** → User tags quality → `POST /experiments/save` → PostgreSQL Experiment table
7. **Auto-Export** → "Good" tagged experiments → `/backend/experimentation/successful_examples/`

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
- Follow Story 11.5 (`docs/stories/11.5.railway-deployment.md`) for Gradio Railway deployment

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
