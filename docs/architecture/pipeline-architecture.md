# Pipeline Architecture Guide

## Overview

This guide defines the technical architecture for the 7-stage Innovation Intelligence Pipeline. Extracted from Story 11.2 to separate requirements from implementation specifications.

**Target Story:** 11.2 - Pipeline Implementation
**Purpose:** Transform trend reports into directional innovation concepts using SIT-based extraction framework

---

## Pipeline Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    INPUT LAYER                                │
├──────────────────────────────────────────────────────────────┤
│ PDF Report (WGSN/Mintel)  +  Brand Profile YAML             │
└────────────────┬──────────────────────────────────┬──────────┘
                 │                                   │
                 ▼                                   ▼
         ┌───────────────┐                  ┌────────────────┐
         │ PDF Extraction│                  │ Stage 0:       │
         │ (PyPDF2)      │                  │ Brand          │
         └───────┬───────┘                  │ Enrichment     │
                 │                          └────────┬───────┘
                 │                                   │
                 ▼                                   │
         ┌───────────────┐                          │
         │ Stage 1:      │◄─────────────────────────┘
         │ Trend         │
         │ Decomposition │
         │ (L1-L4)       │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ Stage 2:      │
         │ Consumer      │
         │ Insights      │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ Stage 3:      │
         │ Technique     │
         │ Matching      │
         │ (SIT/TRIZ)    │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ Stage 4:      │
         │ Concept       │
         │ Generation    │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ Stage 5:      │
         │ Competitive   │
         │ Intelligence  │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ Stage 6:      │
         │ Opportunity   │
         │ Cards         │
         └───────┬───────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│           OUTPUT: Markdown Cards               │
└────────────────────────────────────────────────┘
```

---

## Stage 0: Brand Profile Enrichment

**Purpose:** Transform 4 basic brand inputs into comprehensive context for downstream stages

**Inputs:**
```yaml
brand_name: "Company Name"
industry: "Industry Category"
country: "Geography"
product_portfolio:
  - "Product Line 1"
  - "Product Line 2"
```

**Process:**
1. Load brand YAML from `/data/brand-profiles/{brand-name}.yaml`
2. Optional: Enrich with Perplexity API for recent news, competitive landscape
3. Structure into comprehensive context object

**Output Schema:**
```json
{
  "brand_name": "string",
  "industry": "string",
  "country": "string",
  "product_portfolio": ["string"],
  "enrichment": {
    "positioning": "optional string",
    "recent_news": ["optional"],
    "competitive_landscape": "optional",
    "confidence_score": 0.0-1.0
  }
}
```

**LLM Call:** Optional (if Perplexity enabled)
**Token Budget:** ~2,000 tokens

---

## Stage 1: Multi-Trend Decomposition with Abstraction Ladder

**Purpose:** Extract trends with L1-L4 abstraction levels for transferability

**Abstraction Ladder (L1 → L4):**
- **L1 (Domain-Specific):** "Gen Z consumers want dairy-free protein alternatives"
- **L2 (Category-Level):** "Health-conscious consumers seek plant-based nutrition"
- **L3 (Cross-Category):** "Consumers want to optimize health without sacrificing convenience"
- **L4 (Universal Principle):** "People seek control over personal well-being"

**Inputs:**
- PDF text (extracted report content)
- Trend format hints (WGSN, Mintel, etc.)

**Process:**
1. Identify all distinct trends in report
2. Extract for each trend:
   - **Name:** Trend identifier (e.g., "Witherwill", "Strategic Joy")
   - **Lifecycle Stage:** EMERGING | ACCELERATING | PEAKING | DECLINING
   - **Timeline:** Peak year prediction
   - **Evidence:** Market signals, stats, examples
   - **Weak Signals:** Early indicators
   - **Emotional Drivers:**
     - Current negative emotion (what consumers feel now)
     - Aspirational positive emotion (what they want to feel)
   - **Abstraction Levels:** L1, L2, L3, L4 descriptions

**Output Schema:**
```json
{
  "trends": [
    {
      "trend_id": "unique_id",
      "name": "Trend Name",
      "lifecycle_stage": "ACCELERATING",
      "timeline": {
        "emergence_year": 2024,
        "peak_year": 2027
      },
      "evidence": ["signal 1", "signal 2"],
      "weak_signals": ["early indicator 1"],
      "emotional_drivers": {
        "current_negative": "Decision fatigue, overwhelm",
        "aspirational_positive": "Clarity, simplicity, freedom"
      },
      "abstraction_ladder": {
        "L1_domain_specific": "Consumers overwhelmed by bread choices",
        "L2_category": "Shoppers want simplified product selection",
        "L3_cross_category": "People seek to reduce cognitive load in daily decisions",
        "L4_universal": "Humans desire mental freedom from trivial choices"
      }
    }
  ]
}
```

**LLM Call:** Required
**Token Budget:** ~10,000 tokens (input) + ~8,000 tokens (output)
**Model Recommendation:** Claude-3-Opus or GPT-4 (requires strong reasoning)

---

## Stage 2: Consumer Insight Synthesis

**Purpose:** Map general trends to brand-specific consumer wants/needs

**Inputs:**
- Trend objects array (from Stage 1)
- Enriched brand context (from Stage 0)

**Process:**
1. For each trend, identify **convergence patterns** (multi-trend intersections)
2. Generate brand-specific consumer insight using formula:
   ```
   "I'm a [brand's target customer] and I [current negative emotion]
   because [brand-relevant problem]. I want to [aspirational positive]
   through [brand's product category]."
   ```
3. Map insight across three dimensions:
   - **Functional Need:** What practical problem to solve?
   - **Emotional Need:** What feeling to achieve?
   - **Social Need:** What identity/belonging to signal?

**Output Schema:**
```json
{
  "insights": [
    {
      "insight_id": "unique_id",
      "source_trends": ["trend_id_1", "trend_id_2"],
      "consumer_statement": "I'm overwhelmed by bread choices - just tell me THE ONE bread for my family",
      "functional_need": "Simplify decision-making at point of purchase",
      "emotional_need": "Reduce cognitive load and decision fatigue",
      "social_need": "Feel confident I'm making the 'right' choice for my family",
      "brand_relevance_score": 0.0-1.0
    }
  ]
}
```

**LLM Call:** Required
**Token Budget:** ~12,000 tokens (input) + ~5,000 tokens (output)

---

## Stage 3: Innovation Technique Matching

**Purpose:** Match consumer insights to SIT/TRIZ/Doblin techniques

**Technique Libraries:**

### SIT (Systematic Inventive Thinking) - 5 Techniques
1. **Subtraction:** Remove essential component
   - Example: Headphones without wires (AirPods)

2. **Task Unification:** Assign new task to existing resource
   - Example: Shelf labels become decision-support tools

3. **Multiplication:** Copy component with variation
   - Example: Dual-blade razors, multi-camera phones

4. **Attribute Dependency:** Correlate two independent attributes
   - Example: Tires that change tread based on temperature

5. **Division:** Separate component in space/time
   - Example: Modular furniture, separable product lines

### TRIZ (40 Principles) - Conditional Application
Applied ONLY if SIT insufficient. Key principles:
- Segmentation, Extraction, Local Quality, Asymmetry, Merging, etc.

### Doblin (10 Innovation Types) - Strategic Layer
- Profit Model, Network, Structure, Process, Product Performance, Product System, Service, Channel, Brand, Customer Engagement

**Inputs:**
- Consumer insights array (from Stage 2)
- Brand context (from Stage 0)

**Process:**
1. Match each insight to 1-2 SIT techniques
2. Assess defensibility (can competitors easily copy?)
3. If SIT insufficient, conditionally apply TRIZ
4. Map to Doblin type for strategic classification

**Output Schema:**
```json
{
  "matched_techniques": [
    {
      "insight_id": "ref",
      "primary_technique": {
        "framework": "SIT",
        "technique": "Task Unification",
        "rationale": "Existing shelf/packaging can take on choice-simplification task",
        "defensibility_score": 0.0-1.0
      },
      "secondary_technique": {
        "framework": "TRIZ",
        "principle": "Segmentation (optional)",
        "rationale": "optional"
      },
      "doblin_type": "Service",
      "transferability": {
        "L1_domain": "Bakery decision support",
        "L4_universal": "Choice simplification mechanism"
      }
    }
  ]
}
```

**LLM Call:** Required
**Token Budget:** ~8,000 tokens (input) + ~4,000 tokens (output)

---

## Stage 4: Directional Concept Generation

**Purpose:** Generate 3-5 directional concepts (NOT detailed specs)

### No-Hallucination Boundaries (CRITICAL)

**What LLM CANNOT Do:**
- ❌ Generate market statistics (TAM, market share, growth rates)
- ❌ Invent competitive intelligence ("NO brand does this")
- ❌ Create financial projections (revenue, ROI, cost)
- ❌ Make unverified claims ("Studies show...", "Research indicates...")
- ❌ Generate detailed business plans or go-to-market strategies

**What LLM DOES:**
- ✅ Synthesize trend + insight + technique → directional concept
- ✅ Use ONLY data explicitly provided in inputs
- ✅ Focus on DIRECTION not implementation
- ✅ Generate creative application of SIT technique to brand problem

**Inputs:**
- Matched techniques (from Stage 3)
- Consumer insights (from Stage 2)
- Brand context (from Stage 0)

**Process:**
1. Apply SIT technique to consumer insight
2. Generate 3-5 directional concepts
3. For each concept:
   - What is it? (1 sentence)
   - How does it work? (mechanism only, not implementation)
   - Why does it address the insight?

**Output Schema:**
```json
{
  "concepts": [
    {
      "concept_id": "unique_id",
      "insight_id": "ref",
      "technique_id": "ref",
      "concept_name": "Le Guide St-Méthode (The Bread Finder Tool)",
      "concept_statement": "Decision-support tool where consumers answer 3 questions and receive ONE St-Méthode bread recommendation",
      "mechanism": "QR code on shelf → 3-question quiz → Personalized recommendation → Product location",
      "why_it_works": "Unifies choice-simplification task with existing shelf resource, reducing decision fatigue",
      "boundary_disclosure": "This is a directional concept. No financial projections, market validation, or implementation details included."
    }
  ]
}
```

**LLM Call:** Required
**Token Budget:** ~10,000 tokens (input) + ~6,000 tokens (output)
**Prompt Constraint:** Include explicit no-hallucination instructions

---

## Stage 5: Competitive Intelligence Search

**Purpose:** Search for similar concepts with honesty constraints

**Honesty Constraints:**
- ❌ Do NOT invent competitors or products
- ✅ Separate "What we know" vs "What we infer"
- ✅ Cite search queries and sources
- ✅ If no results found, say "No similar concepts found"

**Inputs:**
- Directional concepts (from Stage 4)
- Perplexity API access (optional)

**Process:**
1. For each concept, generate 3 search queries:
   - **Direct:** Exact concept search
   - **Analogous:** Similar solutions in different industries
   - **Competitive:** Brand's competitors with similar initiatives

2. Execute searches (Perplexity or web search API)
3. Classify findings:
   - **Direct Match:** Exact same concept exists
   - **Analogous:** Similar concept in different domain
   - **Novel:** No matches found

**Output Schema:**
```json
{
  "competitive_intel": [
    {
      "concept_id": "ref",
      "search_queries": [
        "bread recommendation quiz QR code",
        "decision simplification tool retail",
        "product finder grocery store"
      ],
      "findings": [
        {
          "match_type": "Analogous",
          "description": "Wine Finder quiz at Total Wine (USA retail)",
          "source_url": "optional",
          "what_we_know": "Tool exists for wine selection",
          "what_we_infer": "Similar mechanism could apply to bread"
        }
      ],
      "novelty_assessment": "Analogous solutions exist in other categories, but not in bakery/bread domain"
    }
  ]
}
```

**LLM Call:** Optional (for search query generation only)
**Token Budget:** ~3,000 tokens
**External API:** Perplexity or web search

---

## Stage 6: Opportunity Card Packaging

**Purpose:** Format concepts into 30-second pitch structure

**Card Structure:**
1. **Concept Name:** Clear, memorable name
2. **Consumer Insight:** The problem being solved
3. **Mechanism:** How it works (SIT technique application)
4. **Why Now:** Trend evidence + lifecycle stage
5. **Why This Brand:** Brand-specific fit
6. **No-Hallucination Disclosure:** Explicit boundary statement

**Inputs:**
- Concepts (from Stage 4)
- Competitive intel (from Stage 5)
- Trends (from Stage 1)
- Brand context (from Stage 0)

**Process:**
1. For each concept, generate markdown card
2. Use template below

**Output Format (Markdown):**

```markdown
# 💡 [Concept Name]

## 🎯 Consumer Insight
> "I'm a [target customer] and I [problem statement]."

**Functional Need:** [1 sentence]
**Emotional Need:** [1 sentence]
**Social Need:** [1 sentence]

---

## ⚙️ Mechanism (SIT: [Technique Name])
[2-3 sentences explaining how the concept works, with SIT technique applied]

**Example Application:**
- [Step 1]
- [Step 2]
- [Step 3]

---

## 📈 Why Now?
**Trend:** [Trend Name] ([Lifecycle Stage])
- **Evidence:** [Key signals from trend report]
- **Timeline:** Emerging [year], peaking [year]

---

## 🏢 Why [Brand Name]?
[2-3 sentences on brand-specific fit using brand context]

**Brand Assets:**
- [Asset 1 from brand profile]
- [Asset 2]

---

## 🔍 Competitive Landscape
[Summary from Stage 5 competitive intel]
- **Direct Matches:** [Yes/No + details]
- **Analogous Solutions:** [Examples from other industries]

---

## ⚠️ Boundary Disclosure
This is a **directional concept** generated from trend analysis and systematic innovation techniques. It does NOT include:
- Financial projections or ROI estimates
- Detailed implementation plans
- Market validation or customer research
- Competitive claims beyond documented search results

**Next Steps:** Validate with customer research, financial modeling, and feasibility assessment.

---

**Generated:** [Timestamp]
**Pipeline Version:** [Version]
**Source Trend Report:** [Report Name]
```

**LLM Call:** Required
**Token Budget:** ~15,000 tokens (input) + ~3,000 tokens per card (output)

---

## Environment Variables

```bash
# LLM Configuration
OPENROUTER_API_KEY=required
OPENROUTER_MODEL=anthropic/claude-3-opus-20240229  # or openai/gpt-4-turbo
PERPLEXITY_API_KEY=optional  # For Stage 0 enrichment and Stage 5 search

# Pipeline Configuration
PIPELINE_TIMEOUT=600  # 10 minutes total
STAGE_TIMEOUT=120     # 2 minutes per stage
MAX_RETRIES=3         # Retry attempts per stage
RETRY_DELAY=2         # Seconds between retries

# Webhooks
WEBHOOK_URL=optional  # Vercel frontend webhook for progress updates
WEBHOOK_SECRET=required_if_webhook_url_set

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Feature Flags
STAGE_0_ENRICHMENT_ENABLED=true   # Enable Perplexity enrichment
STAGE_5_SEARCH_ENABLED=true       # Enable competitive search
FEW_SHOT_ENABLED=true             # Enable few-shot example injection
```

---

## Token Management

### Total Token Budget per Run:
- **Input:** ~50,000 tokens
- **Output:** ~30,000 tokens
- **Total:** ~80,000 tokens (~$0.80 at Claude-3-Opus pricing)

### Token Tracking:
```python
class PipelineRun:
    def __init__(self):
        self.tokens_by_stage = {
            "stage_0": {"input": 0, "output": 0},
            "stage_1": {"input": 0, "output": 0},
            # ... for all stages
        }
        self.total_tokens = 0
        self.estimated_cost_usd = 0.0

    def track_stage_tokens(self, stage, input_tokens, output_tokens):
        self.tokens_by_stage[stage] = {
            "input": input_tokens,
            "output": output_tokens
        }
        self.total_tokens += (input_tokens + output_tokens)
        self.estimate_cost()

    def estimate_cost(self):
        # Claude-3-Opus pricing (example)
        input_cost = (self.total_tokens / 1_000_000) * 15.00   # $15/1M input
        output_cost = (self.total_tokens / 1_000_000) * 75.00  # $75/1M output
        self.estimated_cost_usd = input_cost + output_cost
```

---

## Error Handling & Retry Strategy

### Stage-Level Retry:
```python
async def execute_stage_with_retry(stage_func, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await stage_func()
            return result
        except OpenRouterRateLimitError:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
        except Exception as e:
            # Log error, classify via pipeline_errors.py
            if attempt < max_retries - 1:
                continue
            raise
```

### Resume from Failure:
```python
class PipelineState:
    def __init__(self, run_id):
        self.run_id = run_id
        self.completed_stages = []
        self.stage_outputs = {}

    def save_checkpoint(self, stage_num, output):
        self.completed_stages.append(stage_num)
        self.stage_outputs[f"stage_{stage_num}"] = output
        # Save to database via PrismaAPIClient

    def resume_from_checkpoint(self):
        last_completed = max(self.completed_stages) if self.completed_stages else -1
        return last_completed + 1  # Next stage to run
```

---

## Technique Library Files

### SIT Techniques (`/backend/experimentation/technique_libraries/sit_techniques.json`)
```json
{
  "techniques": [
    {
      "id": "subtraction",
      "name": "Subtraction",
      "description": "Remove an essential component",
      "prompt_hint": "What happens if we remove [component]?",
      "examples": ["AirPods (removed wires)", "Netflix (removed physical media)"]
    },
    {
      "id": "task_unification",
      "name": "Task Unification",
      "description": "Assign new task to existing resource",
      "prompt_hint": "Can [existing resource] perform [new task]?",
      "examples": ["Shelf labels → decision support", "Packaging → entertainment"]
    }
    // ... 3 more techniques
  ]
}
```

---

## References

- **Story 11.2:** `/docs/stories/11.2.pipeline-implementation.md`
- **PRD Section:** "7-Stage Pipeline Overview" (lines 43-123)
- **Example Output:** PRD Appendix A (lines 495-520)
- **No-Hallucination Boundaries:** PRD lines 467-491
