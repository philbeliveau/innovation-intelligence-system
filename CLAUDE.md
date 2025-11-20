# Innovation Intelligence System - Claude Configuration

## 🎯 Current Milestone: Gradio Experimentation UI Development

**Status:** Pipeline Architecture Complete → Implementation Phase (Story 11.1)
**Timeline:** 1 month to demo
**Focus:** Build Gradio web interface for rapid experimentation with trend extraction pipeline
**Goal:** Enable innovation teams to upload trend reports, select brand profiles, run the 5-stage pipeline, and review generated concepts without technical expertise

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

#### 5-Stage LLM Pipeline

**STAGE 1: TREND DECOMPOSITION**
- Extract structured trend objects from report
- Output: Reusable trend JSON (lifecycle, evidence, emotional drivers, aspirations)

**STAGE 2: CONSUMER INSIGHT SYNTHESIS**
- Map general trend → brand/industry-specific consumer want
- Example: "Witherwill" (general) → "I'm overwhelmed by bread choices" (industry-specific)
- Output: Consumer wants/needs grounded in brand context

**STAGE 3: SIT TECHNIQUE MATCHING**
- Analyze consumer want + brand resources
- Match to one of 5 SIT techniques:
  - **Subtraction**: Remove essential component
  - **Task Unification**: Assign new task to existing resource
  - **Multiplication**: Copy component with variation
  - **Attribute Dependency**: Correlate two attributes
  - **Division**: Separate in space/time
- Output: Selected SIT technique + rationale

**STAGE 4: INITIATIVE CONCEPT GENERATION**
- Apply SIT technique → directional concept
- Output: Product/service/marketing initiative concept
- **STOPS HERE**: No financial projections, no business plans, no validation steps

**STAGE 5: PACKAGING**
- Format into opportunity card
- Structure: Trend → Consumer Insight → SIT Technique → Initiative Concept

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

### Current Development Sprint (Story 11.1)

**Active Story:** `docs/stories/11.1.gradio-experimentation-ui.md`

**Implementation Priorities:**
1. ✅ Pipeline architecture defined (5-stage SIT-based extraction)
2. ✅ Brand profile YAML structure established (4 profiles ready)
3. **IN PROGRESS:** Build Gradio experimentation UI
   - PDF upload interface (Mintel/WGSN reports)
   - Brand profile dropdown (Lactalis, Decathlon, Colombia, McCormick)
   - Pipeline execution with real-time status
   - Output display (7-stage tabbed interface)
   - Quality tagging system (Good/Needs Work/Failed)
   - Database persistence for experiments

**Brand Profiles Available:**
- `/data/brand-profiles/lactalis-canada.yaml` - Dairy/Food & Beverage (Canada)
- `/data/brand-profiles/decathlon.yaml` - Sporting Goods Retail (Global)
- `/data/brand-profiles/columbia-sportswear.yaml` - Outdoor Apparel (USA)
- `/data/brand-profiles/mccormick-usa.yaml` - Spices & Seasonings (USA)

**Test Dataset:**
- `WGSN - FC27-Emotions - Report.pdf` (Emotional trends: Witherwill, Strategic Joy, etc.)

### Next Milestones

1. **Story 11.1:** Gradio UI (current sprint)
2. **Story 11.2:** Pipeline implementation (5 stages)
3. **Story 11.3:** Few-shot learning system
4. **Story 11.4:** Experiment database & analytics
5. **Demo Preparation:** Multi-brand validation with real trend report

---

## 🧪 Gradio Experimentation Workflow

### User Journey

1. **Upload Trend Report** - Drag-and-drop PDF (Mintel/WGSN, max 50MB)
2. **Select Brand Profile** - Choose from dropdown or enter manually
3. **Run Pipeline** - Click "Run Pipeline" button (triggers 5-stage extraction)
4. **Review Outputs** - Tabbed interface showing all 7 stages (5 pipeline + 2 enrichment)
5. **Tag Quality** - Mark as Good/Needs Work/Failed with notes
6. **Auto-Save** - "Good" examples exported to `/backend/experimentation/successful_examples/`

### File Structure

```
backend/experimentation/
├── gradio_lab.py              # Main Gradio application (Story 11.1)
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
┌─────────────────┐
│  Gradio UI      │ (Port 7860)
│  localhost:7860 │
└────────┬────────┘
         │
         │ HTTP POST
         ▼
┌─────────────────┐
│  FastAPI        │ (Railway deployment)
│  /pipeline/run  │
│  /pipeline/     │
│  status/{id}    │
└────────┬────────┘
         │
         │ JSONB Storage
         ▼
┌─────────────────┐
│  PostgreSQL     │ (Railway)
│  experiments    │
│  table          │
└─────────────────┘
```

### Running Gradio Locally

```bash
# From project root
cd backend/experimentation
python gradio_lab.py

# Access at http://localhost:7860
# Optional: Set GRADIO_SHARE=true for public link
```

---

## Deployment to Railway

### Backend Deployment

The Python FastAPI backend is deployed to Railway. The service is configured with:
- **Root Directory**: `backend` (configured in Railway dashboard)
- **Build**: Dockerfile-based build
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Deploying from CLI:**

```bash
# Deploy from PROJECT ROOT (not from backend directory)
# Railway is configured with root directory as 'backend'
railway deploy

# Or using Railway MCP tool
# Must provide absolute path to PROJECT ROOT
/Users/your-username/path/to/innovation-intelligence-system
```

**Important Notes:**
-  Deploy from the **project root** directory (`innovation-intelligence-system/`)
- L Do NOT deploy from `backend/` subdirectory
- The Railway service has `backend` configured as the root directory in the dashboard
- This means Railway expects to find the `backend/` folder relative to where you deploy from

**Environment Variables:**
- Set in Railway dashboard under Settings � Variables
- Required: `DATABASE_URL`, `OPENROUTER_API_KEY`, `WEBHOOK_SECRET`, `VERCEL_BLOB_READ_WRITE_TOKEN`

**Monitoring Deployment:**
- Build logs are available in Railway dashboard
- Or access via CLI: `railway logs`

---

## 🛠️ Development Guidelines for Current Phase

### Story-Driven Development

- **Active Story:** Follow `docs/stories/11.1.gradio-experimentation-ui.md` precisely
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
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://backend-url/pipeline/run",
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
- Follow Story 11.1 (`docs/stories/11.1.gradio-experimentation-ui.md`) for Gradio UI implementation
