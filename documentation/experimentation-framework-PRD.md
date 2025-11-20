# Innovation Intelligence System: Experimentation Framework PRD

**Version:** 1.0
**Date:** November 19, 2025
**Status:** Final
**Author:** Product Management Team

---

## Executive Summary

### Problem Statement

CPG innovation teams at companies like Lactalis, McCormick, and Decathlon invest $50,000 annually in Mintel/WGSN trend reports, yet struggle to extract actionable value. These abstract emotional trends remain locked as PDF insights rather than transformed into concrete product initiatives. Teams lack the operational "muscle" to:

- **Generalize insights** to their specific industry and operations
- **Extract actionable value** from trend data beyond surface-level observation
- **Apply global trends** to their unique product categories and geographies
- **Generate concrete initiative concepts** from abstract emotional trends

### Solution Overview

The Innovation Intelligence System's Experimentation Framework is a **simple 7-stage pipeline** for testing whether we can extract value from trend reports. The system:

- **Processes trend reports** to generate 3-5 directional concepts per brand
- **Uses human judgment** to identify what works (no complex scoring)
- **Iterates on prompts** based on manual review
- **Provides a simple Gradio UI** for experimentation
- **Focuses on proving the concept** before adding complexity

### Success Metrics

**Primary KPI:** Generate **3-5 directional concepts per brand** from a single trend report, packaged as opportunity cards
**Quality Target:** **80% of outputs score > 0.8** on automatic quality assessment
**Time Reduction:** From **3 days of manual analysis to 30 minutes** per brand
**ROI Demonstration:** **1 report × 5 brands = 15-25 directional concepts** from $50K investment

---

## System Architecture

### 7-Stage Pipeline Overview

The pipeline transforms WGSN/Mintel trend reports through systematic stages, each building upon the previous to create increasingly specific, actionable insights.

#### Stage 0: Brand Profile Enrichment
**Purpose:** Transform minimal brand input (4 fields) into enriched context
**Input:** Brand name, industry, geography, product portfolio
**Processing:** Perplexity search enrichment for category context, positioning, competitors
**Output:** `enriched_brand_context.json` with confidence scores
**Execution:** ONCE per brand (cached for reuse)

#### Stage 1: Multi-Trend Decomposition
**Purpose:** Extract all trends with 4-level abstraction ladder (L1-L4)
**Input:** WGSN/Mintel PDF report
**Processing:** Trend identification, abstraction ladder extraction, lifecycle mapping
**Output:** `trend_objects_array.json` (reusable across brands)
**Execution:** ONCE per report (brand-agnostic)

#### Stage 2: Consumer Insight Synthesis
**Purpose:** Discover brand-specific insights through multi-trend convergence
**Input:** Trend array + enriched brand context
**Processing:** JSON-based convergence enumeration, semantic matching to brand challenges
**Output:** `consumer_insights_array.json` with functional/emotional/social needs
**Execution:** PER (report × brand) combination

#### Stage 3: Technique Library Matching
**Purpose:** Validate insights against 55 innovation patterns (SIT: 5, TRIZ: 40, Doblin: 10)
**Input:** Consumer insights + technique libraries
**Processing:** SIT matching, conditional TRIZ application, Doblin type mapping
**Output:** `validated_techniques.json` with defensibility assessment
**Execution:** PER (report × brand) combination

#### Stage 4: Directional Concept Generation
**Purpose:** Generate brand-specific directional concepts (NOT full product specs, NOT business plans)
**Input:** Validated techniques + brand context
**Processing:** Concept formulation, narrative framework, NO financial projections
**Output:** `directional_concepts.json` with explicit no-hallucination boundaries
**Execution:** PER (report × brand) combination
**Key Constraint:** STOPS at directional concept - no validation, no business case

#### Stage 5: Competitive Intelligence
**Purpose:** Search-based validation to identify existing similar concepts
**Input:** Directional concepts
**Processing:** Multi-query search (direct, analogous, competitive)
**Output:** `competitive_validation.json` with honesty constraints
**Execution:** PER concept

#### Stage 6: Opportunity Card Packaging
**Purpose:** Create retail-ready opportunity cards with complete decision context
**Input:** All previous stage outputs
**Processing:** 30-second pitch structure, decision-ready artifacts
**Output:** `opportunity_cards.md` (markdown format)
**Execution:** PER concept

### Data Flow Architecture

```
[WGSN PDF + Brand Profile]
         ↓
    [Stage 0-1]
         ↓
[Trend Graph + Brand Context]
         ↓
    [Stage 2]
         ↓
[Consumer Insights]
         ↓
    [Stage 3]
         ↓
[Validated Techniques]
         ↓
    [Stage 4]
         ↓
[Directional Concepts]
         ↓
    [Stage 5]
         ↓
[Competitive Intel]
         ↓
    [Stage 6]
         ↓
[3-5 Opportunity Cards]
```

---

## Experimentation Features

### 1. Few-Shot Learning (Manual Curation)

**File:** `/backend/experimentation/successful_examples/`
**Purpose:** Store and learn from manually validated successful outputs

**Simple Approach:**
- **Manual selection:** Review outputs and save good examples to folder
- **Example injection:** Add 1-2 best examples to prompts when relevant
- **Folder structure:** One folder per stage with JSON examples
- **No automatic scoring:** Human judgment determines quality

**Expected Impact:** Improved consistency after 5-10 good examples

### 2. Prompt Templates

**Location:** `/backend/experimentation/prompts/`
**Purpose:** Maintain and iterate on prompt templates

**Simple Structure:**
```
prompts/
├── stage_1_trend_extraction.md
├── stage_2_convergence.md
├── stage_3_technique_matching.md
├── stage_4_concept_generation.md
├── stage_5_competitive_search.md
└── stage_6_packaging.md
```

**Usage:** Load markdown file, inject into pipeline, edit and iterate

### 3. Manual Quality Review

**Purpose:** Human evaluation of pipeline outputs

**Simple Tagging System:**
- ✅ **Good** - Save as few-shot example
- ⚠️ **Needs Work** - Note what's missing
- ❌ **Failed** - Debug what went wrong

**Storage:** Add tags and notes to experiment record

---

## User Workflows

### Simple Experimentation Workflow

1. **Upload and Run**
   - Upload WGSN/Mintel PDF
   - Enter brand details (name, industry, geography, portfolio)
   - Click "Run Pipeline"
   - Wait ~5 minutes

2. **Review Outputs**
   - See all 7 stage outputs in sequence
   - Focus on Stage 4 (directional concepts) and Stage 6 (opportunity cards)
   - Add notes about what worked/didn't work

3. **Tag Quality**
   - ✅ **Good** → Save to `successful_examples/` folder
   - ⚠️ **Needs Work** → Note improvements needed
   - ❌ **Failed** → Debug the issue

4. **Iterate**
   - Edit prompts in `prompts/` folder
   - Add good examples to few-shot folder
   - Run again with same or different brand
   - Compare results

### Learning Loop (Manual)

```
Run Pipeline → Review Output → Tag Quality → Save Good Examples
                      ↓
              Update Prompts Based on Patterns
```

**No automatic scoring, no A/B testing infrastructure, just human judgment and iteration.**

---

## Technical Specifications

### Frontend: Gradio Interface

**Technology:** Gradio 4.44.0
**File:** `/backend/experimentation/gradio_lab.py`
**Access:** `http://localhost:7860` (local) or Railway URL

**Core Features:**
- PDF upload with PyPDF2 processing
- Run full 7-stage pipeline
- View all stage outputs
- Add experiment notes
- Tag outputs (Good/Needs Work/Failed)
- Export successful examples
- Shareable link via `GRADIO_SHARE=true`

**Simple UI Flow:**
1. Upload trend report PDF
2. Enter brand details (4 fields)
3. Click "Run Pipeline"
4. Review outputs
5. Tag and save results

### Backend: FastAPI Service

**Technology:** FastAPI 0.104+
**Main Application:** `/backend/app/main.py`
**Deployment:** Railway (shared or separate service)

**Core Pipeline Endpoints:**
- `/pipeline/run` - Execute full pipeline
- `/pipeline/status/{run_id}` - Check execution status
- `/pipeline/stage/{stage_num}` - Run individual stage
- `/brands/list` - Available brand profiles

**Stage Implementations:** `/backend/experimentation/pipeline_integration.py`
- Each stage has multiple swappable versions
- Async execution with OpenRouter client
- Configuration via environment variables

### LLM Integration: OpenRouter

**Provider:** OpenRouter API
**Models:** Claude-3, GPT-4 (configurable)
**Features:**
- Model selection per stage
- Token tracking
- Cost optimization
- Fallback handling

### Data Storage: Simple Database

**Development:** SQLite or JSON files
**Production:** Railway PostgreSQL (when scale requires it)

**Single Table Schema:**
```sql
CREATE TABLE experiments (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP,
    report_text TEXT,
    brand_profile JSONB,
    stage_outputs JSONB,  -- All 7 stage outputs
    experiment_notes TEXT,
    quality_tag VARCHAR(20), -- 'good', 'needs_work', 'failed'
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Why Simple:**
- One table handles everything
- JSONB stores flexible stage outputs
- Manual tagging replaces complex scoring
- Easy to query and export

**File Processing:** PyPDF2
- PDF text extraction from trend reports
- Layout preservation
- Table handling

### Infrastructure Requirements

**Development Environment:**
- Python 3.11+
- 8GB RAM minimum
- SQLite for local storage

**Production Deployment:**
- Add Gradio to existing Railway backend service
- Use existing DATABASE_URL when ready for PostgreSQL
- Single deployment, no separate services needed

---

## Success Criteria

### Simple Success Metrics

**Core Functionality:**
- ✅ Pipeline runs end-to-end without errors
- ✅ Generates 3-5 directional concepts per brand
- ✅ Processing time < 10 minutes per brand
- ✅ Outputs are readable and understandable

**Quality Indicators (Manual Review):**
- ✅ Stage 1 extracts all major trends from report
- ✅ Stage 2 produces brand-specific insights (not generic)
- ✅ Stage 4 concepts are directional (not prescriptive)
- ✅ Stage 6 cards enable go/no-go decisions

**Business Value:**
- ✅ 1 report × 5 brands = 15-25 directional concepts
- ✅ Time saved vs manual analysis
- ✅ Concepts spark innovation discussions

### Qualitative Criteria

**User Reaction:** Innovation teams respond with "Woah, okay, THIS is what this report is signaling and these are directional concepts we could explore"

**Concept Clarity:** Directional concepts provide clear innovation direction without prescriptive implementation

**Decision Readiness:** Opportunity cards enable go/no-go decisions on which concepts to pursue

**Trust:** No-hallucination boundaries maintain credibility

**Adoption:** Teams request access after demo

---

## Implementation Approach

### Week 1: Get Pipeline Working

**Goal:** End-to-end execution with real data

**Tasks:**
- Set up single Gradio interface
- Create `prompts/` folder with initial templates
- Test with 1 real WGSN report + 1 brand
- Debug any stage failures

**Success:** Pipeline completes without errors

### Week 2: Test & Refine

**Goal:** Validate output quality

**Tasks:**
- Run 3 different brands through same report
- Manually review all outputs
- Tag quality (Good/Needs Work/Failed)
- Identify pattern failures
- Refine prompts based on issues

**Success:** 50% of outputs tagged as "Good"

### Week 3: Build Consistency

**Goal:** Improve reliability

**Tasks:**
- Add 2-3 best examples to prompts
- Test with different report
- Document what works/doesn't work
- Save successful examples

**Success:** 70% outputs are usable

### Week 4: Demo Ready

**Goal:** Prove value to stakeholders

**Tasks:**
- Process 2 reports × 3 brands each
- Create presentation of best outputs
- Show time savings vs manual analysis
- Get feedback from innovation team

**Success:** Team wants to continue using system

---

## Risk Management

### Technical Risks

**LLM Hallucination:**
- **Mitigation:** Explicit no-hallucination boundaries
- **Controls:** Source citation, confidence scoring

**API Rate Limits:**
- **Mitigation:** Queuing system, retry logic
- **Backup:** Multiple API keys, model fallbacks

**Data Quality:**
- **Mitigation:** Input validation, error handling
- **Recovery:** Manual override options

### Business Risks

**Adoption Resistance:**
- **Mitigation:** Pilot with innovation champions
- **Strategy:** Show ROI through concrete examples

**Competitive Replication:**
- **Mitigation:** Focus on learning system (hard to copy)
- **Moat:** Accumulated examples + templates

---

## Metrics & Monitoring

### Pipeline Metrics

**Per Stage:**
- Execution time
- Token usage
- Quality score
- Error rate

**End-to-End:**
- Total processing time
- Opportunity cards generated
- Average quality score
- Cost per brand

### Learning Metrics

**Few-Shot System:**
- Examples collected
- Injection success rate
- Quality improvement curve

**Template Library:**
- Template usage frequency
- Performance by template
- Evolution patterns

### Business Metrics

**Value Demonstration:**
- Directional concepts per $50K report
- Time saved per analysis
- Adoption rate by team

**ROI Tracking:**
- Directional concepts → Further exploration conversion
- Exploration → Pilots conversion
- Pilots → Launch conversion
- Revenue from launched initiatives

---

## No-Hallucination Boundaries

### What the System DOES

✅ **Synthesizes trends** from actual report text
✅ **Generates directional concepts** based on patterns (NOT detailed plans)
✅ **Packages concepts** into opportunity cards for decisions
✅ **Searches for competition** with transparency about limitations
✅ **Scores quality** based on explicit criteria
✅ **Learns from examples** to improve over time

### What the System DOES NOT Do

❌ **Invent market statistics** (TAM, growth rates, market share)
❌ **Claim competitive advantages** without evidence
❌ **Generate financial projections** or ROI predictions
❌ **Create detailed business plans** beyond directional concepts
❌ **Assert certainty** where data doesn't exist

### Transparency Requirements

Every opportunity card includes:
- **"What we know"** - Facts from reports and search
- **"What we infer"** - Concepts based on patterns
- **"What we DON'T claim"** - Explicit limitations

---

## Appendix A: Example Opportunity Card (Stage 6 Output)

### Le Guide St-Méthode

**Directional Concept:** In-aisle curated selection tool

**Tagline:** Rediscover bread joy without choice overwhelm

**Consumer Insight:** Bread buyers overwhelmed by 47 SKUs want purchasing to feel like rediscovering childhood simplicity

**Innovation Mechanism:** SIT Task Unification - Assign simplification task to shelf/packaging via QR code

**Concept Direction:** Tool that divides 47 SKUs into 3 simple categories with expert recommendations (Note: This is a DIRECTIONAL concept, not a detailed implementation plan)

**Why Now:** Witherwill trend ACCELERATING (WGSN 2027 forecast)

**Why This Brand:** Traditional craft expert positioning provides curation credibility

**Estimated Investment Range:** $40-60K pilot (rough estimate for decision-making)

**Potential Success Indicators:**
- Scan rate engagement
- New SKU trial behavior
- Repeat purchase patterns

**No-Hallucination Disclosure:** This is a directional concept based on trend synthesis. Specific metrics and implementation details require further validation.

---

## Appendix B: Technology Stack & Deployment

### Required Environment Variables

```bash
# Database (Railway PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/railway  # Railway provides this

# LLM Integration
OPENROUTER_API_KEY=your_key_here

# Optional enrichment
PERPLEXITY_API_KEY=your_key_here  # For Stage 0 brand enrichment

# Webhook for frontend updates
WEBHOOK_SECRET=your_secret
VERCEL_BLOB_READ_WRITE_TOKEN=your_token  # For PDF storage

# Gradio Configuration (optional)
GRADIO_SERVER_PORT=7860
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SHARE=true  # Creates public shareable URL
```

### Python Dependencies

**Core Requirements:** `/backend/requirements.txt`
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
httpx==0.25.1
```

**Experimentation Requirements:** `/backend/experimentation/requirements.txt`
```
gradio==4.44.0
PyPDF2==3.0.1
pandas==2.1.3
sqlite3  # Fallback for local dev
```

### Railway Deployment

**Simple Approach:** Add to existing backend service
```bash
# Add Gradio to requirements.txt
echo "gradio==4.44.0" >> backend/requirements.txt

# Deploy
railway up

# Access at your Railway URL on port 7860
```

**For Production:** Use PostgreSQL when you have >100 experiments
```sql
-- Single table is all you need
CREATE TABLE experiments (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP,
    data JSONB,
    notes TEXT,
    tag VARCHAR(20)
);
```

---

## Appendix C: Simplified File Structure

### What You Actually Need

```
backend/experimentation/
├── gradio_lab.py                # Single UI interface
├── pipeline.py                  # 7-stage implementation
├── prompts/                     # Prompt templates (markdown files)
│   ├── stage_1_extraction.md
│   ├── stage_2_convergence.md
│   └── ...
├── successful_examples/         # Manually curated good outputs
│   ├── stage_1/
│   ├── stage_2/
│   └── ...
└── experiments.db              # SQLite for local storage
```

### Reference Documentation

```
documentation/
├── experimentation-framework-PRD.md  # This document
└── docs-pipeline-strategy/
    └── google-docs/
        └── simplified.md             # 7-stage pipeline specification
```

---

## Appendix D: Glossary

**SIT:** Systematic Inventive Thinking (5 techniques)
**TRIZ:** Theory of Inventive Problem Solving (40 principles)
**Doblin:** Ten Types of Innovation framework
**L1-L4:** Abstraction ladder levels (domain-specific to universal)
**Few-Shot Learning:** Learning from examples to improve performance
**Directional Concept:** Innovation direction without prescriptive implementation
**Opportunity Card:** Decision-ready packaging of directional concepts
**Convergence:** Multi-trend intersection creating innovation opportunities
**JSONB:** PostgreSQL JSON Binary format for flexible data storage
**Railway:** Cloud platform for deployment with integrated PostgreSQL

---

## Document Control

**Version History:**
- v1.0 - Initial PRD (November 19, 2025)

**Review Cycle:** Quarterly

**Distribution:** Innovation Teams, Engineering, Executive Leadership

**Confidentiality:** Internal Use Only

---

*End of Document*