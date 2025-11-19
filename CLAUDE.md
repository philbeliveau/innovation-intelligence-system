# Innovation Intelligence System - Claude Configuration

## 🎯 Current Milestone: Mintel Report Value Extraction (Architecture Phase)

**Status:** Discovery Complete → Pipeline Design
**Timeline:** 1 month to demo
**Goal:** Prove that we can unlock the $50K value trapped in Mintel/WGSN trend reports that innovation teams pay for but struggle to operationalize

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

**INPUT 2: Brand Profile (4 Required Fields)**
1. **Company Name**: e.g., "Boulangerie St-Méthode"
2. **Industry**: e.g., "Bread manufacturer"
3. **Geography**: e.g., "Quebec"
4. **Product Portfolio**: e.g., "25 SKUs, healthy bread focus"

**Optional Enrichment via Perplexity:**
- Market context (competitors, category trends)
- Distribution channels
- Brand positioning

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

### Next Steps

1. ✅ Complete discovery brainstorming (SIT framework identified)
2. Build Stage 1: Trend decomposition from WGSN report
3. Build Stage 2: Consumer insight synthesis with brand context
4. Build Stage 3: SIT technique matching logic
5. Build Stage 4: Initiative concept generation
6. Test with `WGSN - FC27-Emotions - Report.pdf` + multiple brand profiles

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
