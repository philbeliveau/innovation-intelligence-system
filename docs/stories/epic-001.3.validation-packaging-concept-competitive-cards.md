# Story EPIC-001.3: Validation & Packaging - Concept Generation + Competitive Intel + Cards (Stages 4-6)

## Status

Draft

## Story

**As an** Innovation Intelligence System,
**I want** to generate directional CPG innovation concepts, validate them with competitive intelligence, and package them into retail-ready opportunity cards,
**so that** innovation teams receive actionable, defensible opportunities with transparent disclosure of limitations.

## Acceptance Criteria

### Functional Requirements

1. **Stage 4 (Directional Concept Generation)**:
   - Generates brand-specific directional concepts (NOT full product specs)
   - Combines consumer insight + innovation mechanism + lifecycle strategy + brand permission
   - Applies narrative framework: Customer Problem → Brand Solution → Emotional Payoff → Proof Points
   - Includes CPG feasibility assessment (capabilities, investment estimate, go-to-market)
   - Defines success metrics (trial rate, new SKU trial, repeat purchase)
   - Maintains no-hallucination boundary (what we know vs what we infer vs what we don't claim)

2. **Stage 5 (Competitive Intelligence Integration)**:
   - Executes 3 search queries per concept via Perplexity API: Direct, Analogous, Competitive
   - Triangulates results: Direct competitors (exact match) + Analogous competitors (transferable mechanism) + No evidence caveat
   - Applies honesty constraints (NEVER claim "zero competition", say "no evidence found in top 50 results")
   - Assesses competitive landscape: OPEN/CROWDED/EMERGING
   - Proposes differentiation angle if competitors found
   - Acknowledges search limitations in output

3. **Stage 6 (Opportunity Card Packaging)**:
   - Packages concepts into retail-ready markdown opportunity cards
   - Follows 30-second pitch structure: Headline → Problem → Solution → Strategy
   - Includes decision-ready sections: Strategic Fit, Concept Overview, Innovation Mechanism, Competitive Landscape, Execution Roadmap, Investment Required, Success Metrics
   - Adds transparency layer: No-Hallucination Disclosure in every card
   - Maintains full traceability from trend extraction to final card

4. **End-to-End Pipeline**:
   - Full 7-stage execution: Stage 0 → Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → Stage 6
   - Outputs 3-5 opportunity cards per WGSN report
   - Complete traceability: Trend → Convergence → Insight → Technique → Concept → Competitive Validation → Card

### Integration Requirements

5. **Stage 4 consumes Stage 3 outputs**:
   - Reads matched techniques (SIT/TRIZ/Doblin) from Stage 3
   - Reads consumer insights and brand context from Stage 2
   - Validates lifecycle strategy mapping

6. **Stage 5 consumes Stage 4 outputs**:
   - Reads directional concepts from Stage 4
   - Executes search queries with Perplexity API
   - Returns competitive validation ready for Stage 6

7. **Stage 6 consumes Stage 5 outputs**:
   - Reads concepts + competitive intelligence
   - Reads full derivation chain (Stage 1 → Stage 2 → Stage 3 → Stage 4)
   - Formats into final opportunity card markdown

8. **Existing frontend integration maintained**:
   - Opportunity cards output format compatible with frontend expectations
   - Webhook notifications work for all 7 stages
   - API endpoints `/api/pipeline/run` and `/api/pipeline/status` unchanged

### Quality Requirements

9. **Concept generation validation**:
   - Narrative framework answers all 4 questions (Problem, Solution, Payoff, Proof)
   - CPG feasibility includes specific capabilities required + investment estimate
   - Success metrics are measurable and realistic
   - No-hallucination boundary clearly defines what's known vs inferred vs not claimed

10. **Competitive intelligence validation**:
    - All 3 search queries executed (direct, analogous, competitive)
    - Honesty constraints enforced (no "zero competition" claims)
    - Analogous competitors include transferability assessment
    - No evidence caveat included in output

11. **Opportunity card validation**:
    - Card follows markdown template structure
    - No-Hallucination Disclosure section present in every card
    - Full traceability chain documented
    - Card is retail-ready (innovation team can present to stakeholders)

12. **Testing coverage**:
    - Unit tests for Stages 4, 5, 6 pass
    - Integration test: Full 7-stage pipeline with real WGSN report produces 3-5 cards
    - End-to-end test passes with traceability validation

13. **Performance meets targets**:
    - Stage 4 execution: < 40 seconds
    - Stage 5 execution: < 45 seconds (3 Perplexity searches)
    - Stage 6 execution: < 15 seconds
    - **Total end-to-end (Stages 0-6): < 3 minutes**

## Tasks / Subtasks

### Task 1: Stage 4 - Directional Concept Generation (AC: 1, 9)
- [ ] Refactor `/backend/pipeline/stages/stage4_brand_application.py` → `stage4_concept_generation.py`
  - [ ] Rename class to `ConceptGenerationStage`
  - [ ] Define input schema (consumer insights + matched techniques from Stages 2-3)
  - [ ] Define output schema (directional concepts per handoff doc lines 385-429)
- [ ] Create `/backend/pipeline/prompts/stage4_prompt.py`
  - [ ] Prompt for concept formulation (insight + mechanism + lifecycle + brand permission)
  - [ ] Prompt for narrative framework (Problem/Solution/Payoff/Proof)
  - [ ] Prompt for CPG feasibility assessment
  - [ ] Prompt for success metrics definition
  - [ ] Include no-hallucination boundary instructions
- [ ] Implement concept formulation logic
  - [ ] Combine consumer insight from Stage 2
  - [ ] Apply innovation mechanism from Stage 3 (SIT/TRIZ/Doblin)
  - [ ] Map lifecycle strategy from Stage 2 convergence
  - [ ] Validate brand permission from Stage 0 positioning
- [ ] Implement narrative framework generation
  - [ ] Customer Problem: What frustrates them? (from consumer insight)
  - [ ] Brand Solution: How does concept solve it? (from innovation mechanism)
  - [ ] Emotional Payoff: How will they feel? (from emotional needs)
  - [ ] Proof Points: Why will it work? (analogies + evidence)
- [ ] Implement CPG feasibility assessment
  - [ ] Capabilities required (list specific capabilities)
  - [ ] Estimated investment ($XXK-$XXK range based on concept scope)
  - [ ] Go-to-market approach (retail/DTC/foodservice)
  - [ ] Success metrics (trial rate, new SKU trial, repeat purchase with realistic %)
- [ ] Add no-hallucination boundary
  - [ ] What we know: Facts from WGSN report + brand context
  - [ ] What we infer: Directional concepts based on convergence + techniques
  - [ ] What we DON'T claim: Exact market size, zero competition, guaranteed ROI
- [ ] Create unit tests in `/backend/tests/test_stage4_concept_generation.py`
  - [ ] Test concept formulation from Stage 2-3 outputs
  - [ ] Test narrative framework generation
  - [ ] Test CPG feasibility logic
  - [ ] Mock OpenRouter LLM calls

### Task 2: Stage 5 - Competitive Intelligence Integration (AC: 2, 10)
- [ ] Create `/backend/pipeline/stages/stage5_competitive_intel.py`
  - [ ] Implement `CompetitiveIntelligenceStage` class
  - [ ] Define input schema (directional concepts from Stage 4)
  - [ ] Define output schema (competitive validation per handoff doc lines 464-492)
- [ ] Create `/backend/pipeline/prompts/stage5_prompt.py`
  - [ ] Prompt for search query generation (3 queries per concept)
  - [ ] Prompt for result triangulation (direct vs analogous vs no evidence)
  - [ ] Prompt for competitive landscape assessment
  - [ ] Include honesty constraint instructions
- [ ] Integrate Perplexity API for competitive search
  - [ ] Reuse Perplexity client from Stage 0 (already created in Story 1)
  - [ ] Generate 3 search queries per concept:
    - **Direct**: Same concept + same category (e.g., "curated bread selection tool bakery")
    - **Analogous**: Same mechanism + different category (e.g., "product curation system wine grocery")
    - **Competitive**: Brand's competitors + innovation type (e.g., "Whole Foods bakery innovation 2024")
  - [ ] Execute searches with exponential backoff
  - [ ] Parse and structure search results
- [ ] Implement result triangulation logic
  - [ ] Identify direct competitors (exact match to concept in same category)
  - [ ] Identify analogous competitors (transferable mechanism from different category)
  - [ ] Include transferability assessment for analogous competitors (HIGH/MEDIUM/LOW)
  - [ ] Calculate threat level per competitor (HIGH/MEDIUM/LOW)
- [ ] Apply honesty constraints
  - [ ] NEVER claim "zero competition" or "no competitors"
  - [ ] Say: "No evidence found in top 50 search results"
  - [ ] Add caveat: "Search has blind spots, absence of evidence ≠ evidence of absence"
  - [ ] If direct competitors found, acknowledge and propose differentiation
- [ ] Implement competitive landscape assessment
  - [ ] OPEN: No direct competitors, some analogous threats
  - [ ] EMERGING: Few direct competitors, growing interest
  - [ ] CROWDED: Multiple direct competitors, established market
  - [ ] Calculate first-mover opportunity (MEDIUM-HIGH/MEDIUM/LOW)
  - [ ] Generate differentiation angle if needed
- [ ] Create unit tests in `/backend/tests/test_stage5_competitive_intel.py`
  - [ ] Test search query generation (3 queries per concept)
  - [ ] Test result triangulation logic
  - [ ] Test honesty constraints enforcement
  - [ ] Mock Perplexity API responses

### Task 3: Stage 6 - Opportunity Card Packaging (AC: 3, 11)
- [ ] Rename `/backend/pipeline/stages/stage5_opportunity_generation.py` → `stage6_opportunity_packaging.py`
  - [ ] Update class name to `OpportunityPackagingStage`
  - [ ] Define input schema (concepts from Stage 4 + competitive intel from Stage 5 + full derivation chain)
  - [ ] Define output schema (markdown opportunity cards)
- [ ] Create `/backend/pipeline/prompts/stage6_prompt.py`
  - [ ] Prompt for 30-second pitch structure
  - [ ] Prompt for decision-ready sections formatting
  - [ ] Include markdown template structure
- [ ] Create opportunity card markdown template in `/backend/pipeline/templates/opportunity_card_template.md`
  - [ ] Use structure from handoff doc lines 526-568:
    ```markdown
    ## Opportunity Card: {Concept Name}
    **Tagline:** {Concept tagline}

    ### Strategic Fit
    - Consumer Insight
    - Trend Convergence
    - Lifecycle Stage
    - Strategic Posture

    ### Concept Overview
    [2-3 sentence description]

    ### Innovation Mechanism
    - Primary Technique (SIT/TRIZ/Doblin)
    - How It Works
    - Defensibility

    ### Competitive Landscape
    - Direct Competitors
    - Analogous Threats
    - Differentiation Angle

    ### Execution Roadmap
    - Phase 1 (Months 1-3): Pilot
    - Phase 2 (Months 4-6): Refine
    - Phase 3 (Months 7-12): Scale

    ### Investment Required
    - Budget: $XXK-$XXK
    - Timeline: X months

    ### Success Metrics
    - Trial Rate: X%
    - New SKU Trial: X%
    - Repeat Purchase: X%

    ### No-Hallucination Disclosure
    **What we know:** [Facts from reports]
    **What we infer:** [Directional concepts]
    **What we DON'T claim:** [Market size, zero competition, ROI]

    ### Derivation Traceability
    **Source Trends:** [Trend A + Trend B]
    **Convergence Pattern:** [Type + shared drivers]
    **Innovation Technique:** [SIT/TRIZ/Doblin]
    **Competitive Validation:** [Search queries executed]
    ```
- [ ] Implement card formatting logic
  - [ ] Populate template with Stage 4 concept data
  - [ ] Integrate Stage 5 competitive intelligence
  - [ ] Add full traceability chain (Stage 1 trends → Stage 2 convergence → Stage 3 technique → Stage 4 concept → Stage 5 validation)
  - [ ] Ensure No-Hallucination Disclosure section is complete
- [ ] Create unit tests in `/backend/tests/test_stage6_opportunity_packaging.py`
  - [ ] Test markdown template rendering
  - [ ] Test traceability chain inclusion
  - [ ] Test No-Hallucination Disclosure presence
  - [ ] Verify card is valid markdown format

### Task 4: Pipeline Orchestrator Updates (AC: 4, 8)
- [ ] Update `/backend/app/pipeline_runner.py` for 7-stage execution
  - [ ] Update `execute_v2_pipeline()` to include Stages 4, 5, 6
  - [ ] Ensure proper handoff: Stage 3 → Stage 4 → Stage 5 → Stage 6
  - [ ] Add JSON schema validation at each handoff
  - [ ] Maintain webhook notifications for each stage completion
- [ ] Update stage progress tracking
  - [ ] Stage count: 7 stages total (update from 5)
  - [ ] Stage names: Update in webhook payload
  - [ ] Progress percentage calculation: 100% / 7 stages
- [ ] Add parallel execution optimization (optional if time permits)
  - [ ] Stages 2-6 can run in parallel per brand if multiple brands processed
  - [ ] Stage 0 and Stage 1 remain sequential (cached, shared across brands)
- [ ] Update `/backend/app/routes.py` if needed
  - [ ] Verify `/api/pipeline/run` endpoint unchanged
  - [ ] Verify `/api/pipeline/status` returns correct stage progress
  - [ ] Add `/api/pipeline/cards/{run_id}` endpoint to retrieve opportunity cards

### Task 5: End-to-End Integration Testing (AC: 12, 13)
- [ ] Create comprehensive integration test in `/backend/tests/test_pipeline_v2_full_e2e.py`
  - [ ] Test: Real WGSN PDF (`/data/document/WGSN - FC27-Emotions - Report.pdf`)
  - [ ] Test: Test brand (Boulangerie St-Méthode from CLAUDE.md)
  - [ ] Test: Full 7-stage execution: Stage 0 → Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → Stage 6
  - [ ] Test: Verify 3-5 opportunity cards generated
  - [ ] Test: Validate full traceability chain in cards
  - [ ] Test: Verify No-Hallucination Disclosure present in all cards
- [ ] JSON schema validation tests
  - [ ] Validate Stage 0 → Stage 1 handoff
  - [ ] Validate Stage 1 → Stage 2 handoff
  - [ ] Validate Stage 2 → Stage 3 handoff
  - [ ] Validate Stage 3 → Stage 4 handoff
  - [ ] Validate Stage 4 → Stage 5 handoff
  - [ ] Validate Stage 5 → Stage 6 handoff
- [ ] Traceability validation tests
  - [ ] Verify each opportunity card includes source trends (from Stage 1)
  - [ ] Verify each card includes convergence pattern (from Stage 2)
  - [ ] Verify each card includes matched technique (from Stage 3)
  - [ ] Verify each card includes competitive searches (from Stage 5)
- [ ] Performance benchmarking (AC: 13)
  - [ ] Measure Stage 4 execution time (target: < 40 seconds)
  - [ ] Measure Stage 5 execution time (target: < 45 seconds for 3 searches)
  - [ ] Measure Stage 6 execution time (target: < 15 seconds)
  - [ ] Measure total end-to-end time (target: < 3 minutes)
  - [ ] Identify bottlenecks if target missed
- [ ] Regression testing (AC: 8)
  - [ ] Verify existing REST API endpoints work (`/api/pipeline/run`, `/api/pipeline/status`)
  - [ ] Verify webhook notifications sent for all 7 stages
  - [ ] Verify frontend can consume opportunity cards output
  - [ ] Verify feature flag toggle still works (v1 vs v2 pipeline)

### Task 6: Deployment and Documentation (AC: 8)
- [ ] Update API documentation
  - [ ] Document updated stage names (5 → 7 stages)
  - [ ] Document new `/api/pipeline/cards/{run_id}` endpoint (if added)
  - [ ] Document opportunity card markdown format
- [ ] Update deployment guide
  - [ ] Add `PERPLEXITY_API_KEY` environment variable requirement (from Story 1)
  - [ ] Add `PIPELINE_VERSION=v2_7stage` activation instructions
  - [ ] Document rollback procedure (set `PIPELINE_VERSION=v1_5stage`)
- [ ] Create migration checklist
  - [ ] Database migration run (new tables from Stories 1-3)
  - [ ] Environment variables configured (PERPLEXITY_API_KEY, PIPELINE_VERSION)
  - [ ] Technique library data seeded (from Story 2)
  - [ ] Cache system initialized (from Story 1)
- [ ] Deploy to Railway staging environment
  - [ ] Run database migrations
  - [ ] Set environment variables
  - [ ] Deploy backend with `PIPELINE_VERSION=v2_7stage`
  - [ ] Run end-to-end smoke test
  - [ ] Verify opportunity cards generated successfully
- [ ] Production deployment (after validation)
  - [ ] Create git tag: `v2.0.0-7stage-pipeline`
  - [ ] Deploy to Railway production
  - [ ] Monitor first 10 pipeline runs
  - [ ] Verify performance meets < 3 minute target

## Dev Notes

### Existing System Integration

**Technology Stack**: Python 3.11+, FastAPI, Prisma (PostgreSQL), OpenRouter (LLM API), Perplexity API (competitive search)

**Integration Points**:
- **Stage 4 (REFACTOR)**: Replaces `stage4_brand_application.py` with lifecycle-aware concept generation
- **Stage 5 (NEW)**: New competitive intelligence stage using Perplexity API
- **Stage 6 (UPDATE)**: Renames `stage5_opportunity_generation.py` to reflect packaging focus
- **Orchestrator**: Updates pipeline runner to execute all 7 stages sequentially
- **Dependencies**: Stories 1 and 2 must be completed first

**Existing Patterns to Follow**:

1. **Stage Class Structure** (same as Stories 1-2):
```python
class ConceptGenerationStage:
    async def execute(self, input_data: dict, run_id: str) -> dict:
        # 1. Load consumer insights from Stage 2
        # 2. Load matched techniques from Stage 3
        # 3. Load brand context from Stage 0
        # 4. Generate directional concept via LLM
        # 5. Apply narrative framework
        # 6. Assess CPG feasibility
        # 7. Define success metrics
        # 8. Add no-hallucination boundary
        # 9. Store to database
        return directional_concepts
```

2. **Perplexity API Reuse** (from Story 1):
```python
# Reuse client from Stage 0
from backend.app.api_clients import PerplexityClient

perplexity = PerplexityClient()

# Execute competitive search queries
direct_results = await perplexity.search(
    query="curated bread selection tool bakery",
    return_citations=True
)

analogous_results = await perplexity.search(
    query="product curation system wine grocery",
    return_citations=True
)

competitive_results = await perplexity.search(
    query="Whole Foods bakery innovation 2024",
    return_citations=True
)
```

3. **Markdown Template Rendering** (Jinja2):
```python
from jinja2 import Template

template = Template(open('/backend/pipeline/templates/opportunity_card_template.md').read())

card_markdown = template.render(
    concept_name=concept['concept_name'],
    tagline=concept['concept_tagline'],
    consumer_insight=insight['insight_statement'],
    trend_convergence=convergence['primary_trend'] + ' + ' + convergence['secondary_trend'],
    # ... all template variables
)
```

**Source Tree Updates** (from Stories 1-2):
```
/backend/
├── pipeline/
│   ├── stages/
│   │   ├── stage0_brand_enrichment.py      # From Story 1
│   │   ├── stage1_trend_decomposition.py   # From Story 1
│   │   ├── stage2_insight_synthesis.py     # From Story 2
│   │   ├── stage3_technique_matching.py    # From Story 2
│   │   ├── stage4_concept_generation.py    # REFACTOR - Story 3
│   │   ├── stage5_competitive_intel.py     # NEW - Story 3
│   │   └── stage6_opportunity_packaging.py # RENAME from stage5_opportunity_generation.py
│   ├── prompts/
│   │   ├── stage4_prompt.py                # UPDATE - Story 3
│   │   ├── stage5_prompt.py                # NEW - Story 3
│   │   └── stage6_prompt.py                # UPDATE - Story 3
│   ├── templates/
│   │   └── opportunity_card_template.md    # NEW - Story 3
│   └── executor.py                         # UPDATE for 7-stage orchestration
├── app/
│   ├── pipeline_runner.py                  # UPDATE execute_v2_pipeline()
│   └── routes.py                           # ADD /api/pipeline/cards endpoint
├── tests/
│   ├── test_stage4_concept_generation.py   # NEW - Story 3
│   ├── test_stage5_competitive_intel.py    # NEW - Story 3
│   ├── test_stage6_opportunity_packaging.py # NEW - Story 3
│   └── test_pipeline_v2_full_e2e.py        # NEW - Story 3 (comprehensive)
└── .env                                    # Verify PERPLEXITY_API_KEY, PIPELINE_VERSION
```

**Lifecycle Strategy to Execution Approach Mapping** (from handoff doc):
- **PIONEER** (EMERGING trends): First-mover advantage, high risk, requires market education
  - Execution: Innovation-led, 12-18 month horizon, higher investment
- **VALIDATE** (ACCELERATING trends): Proven demand, fast-follower strategy, adapt proven models
  - Execution: Fast-follower, 6-12 month horizon, moderate investment
- **DEFEND** (PEAKING trends): Maintain relevance, category stakes, incremental innovation
  - Execution: Category defense, 3-6 month horizon, lower investment

**Narrative Framework Structure** (from handoff doc lines 544-556):
1. **Customer Problem**: What frustrates them? (from consumer insight)
   - Example: "Bread buyers face 47 SKU choices causing decision fatigue"
2. **Brand Solution**: How does concept solve it? (from innovation mechanism)
   - Example: "Le Guide St-Méthode curates into 3 simple categories via QR code on shelf"
3. **Emotional Payoff**: How will they feel? (from emotional needs)
   - Example: "Feel confident and carefree when choosing, like rediscovering childhood simplicity"
4. **Proof Points**: Why will it work? (analogies + evidence)
   - Example: "Wine curation increased trial by 38%, Trader Joe's curated model drives loyalty"

**CPG Feasibility Assessment Components**:
1. **Capabilities Required**: Specific capabilities brand must have or build
   - Example: "QR system integration, shelf redesign, content creation"
2. **Estimated Investment**: Budget range based on concept scope
   - Pilot (3 stores): $40K-$60K
   - Rollout (50 stores): $200K-$300K
   - Full scale (500 stores): $2M-$3M
3. **Go-to-Market**: Distribution channel strategy
   - Retail in-aisle, DTC digital, Foodservice B2B
4. **Success Metrics**: Measurable KPIs
   - Trial Rate: % customers who engage with tool
   - New SKU Trial: % who try non-default product
   - Repeat Purchase: % who return within 2 weeks

**Competitive Search Query Strategy** (3 queries per concept):
1. **Direct Query**: Same concept in same category
   - Purpose: Find direct competitors doing exactly this
   - Example: "curated bread selection tool bakery in-store"
   - Expected: Often empty (innovation opportunity) OR direct threats
2. **Analogous Query**: Same mechanism in different category
   - Purpose: Find transferable threats from adjacent categories
   - Example: "product curation recommendation system wine grocery"
   - Expected: Analogous competitors (assess transferability to CPG)
3. **Competitive Query**: Brand's competitors + innovation type
   - Purpose: Check if direct competitors are already innovating in this space
   - Example: "Whole Foods bakery innovation 2024 customer experience"
   - Expected: Competitive intelligence on rivals' innovation activity

**Honesty Constraints (CRITICAL)**:
- ❌ **NEVER say**: "Zero competition", "No competitors exist", "First mover in category"
- ✅ **ALWAYS say**: "No evidence found in top 50 search results", "Search has limitations", "Absence of evidence ≠ evidence of absence"
- ✅ **If competitors found**: Acknowledge and propose differentiation angle
- ✅ **If no direct found**: Note analogous threats with transferability assessment

**No-Hallucination Boundary (Maintained Across All Stages)**:
- ✅ **What we know** (facts from source documents):
  - WGSN trend names, lifecycle stages, evidence from report
  - Brand context from Perplexity search (Stage 0)
  - Competitive search results from Perplexity (Stage 5)
- ✅ **What we infer** (reasoned synthesis):
  - Convergence patterns from trend enumeration
  - Consumer insights from trend + brand mapping
  - Directional concepts from insight + technique + lifecycle
  - Analogous proof points (wine curation → bread curation)
- ❌ **What we DON'T claim** (outside LLM capability):
  - Exact market size (TAM, SAM, SOM)
  - Market share statistics
  - Financial projections or guaranteed ROI
  - "Zero competition" or "no competitors"
  - Definitive success predictions

**Opportunity Card Success Criteria**:
1. **Retail-ready**: Innovation team can present to stakeholders without further editing
2. **Decision-ready**: Contains enough information to make go/no-go decision
3. **Transparent**: No-Hallucination Disclosure clearly defines boundaries
4. **Traceable**: Full derivation chain from trends to final card
5. **Defensible**: Competitive intelligence provides honest landscape assessment

**Context from Stories 1-2**:
- **Story 1 outputs**:
  - Stage 0: Enriched brand context (category challenges, positioning, competitors, innovation history)
  - Stage 1: Trend objects with L1-L4 abstraction, lifecycle stages, emotional drivers
  - Feature flag, cache system, Perplexity API client
- **Story 2 outputs**:
  - Stage 2: Consumer insights from trend convergence (functional + emotional + social needs)
  - Stage 3: Matched techniques (SIT/TRIZ/Doblin with defensibility assessment)
  - Technique library data files, convergence patterns database

### Testing

**Test File Locations**:
- `/backend/tests/test_stage4_concept_generation.py` - Stage 4 unit tests
- `/backend/tests/test_stage5_competitive_intel.py` - Stage 5 unit tests
- `/backend/tests/test_stage6_opportunity_packaging.py` - Stage 6 unit tests
- `/backend/tests/test_pipeline_v2_full_e2e.py` - Comprehensive integration tests

**Testing Framework**: pytest with fixtures

**Testing Patterns**:
1. **Unit Tests for Stage 4**:
   - Mock Stage 2 consumer insights
   - Mock Stage 3 matched techniques
   - Mock Stage 0 brand context
   - Test concept formulation logic
   - Test narrative framework generation
   - Test CPG feasibility assessment
   - Test no-hallucination boundary inclusion
   - Mock OpenRouter LLM calls

2. **Unit Tests for Stage 5**:
   - Mock Stage 4 directional concepts
   - Test search query generation (3 queries per concept)
   - Test result triangulation (direct vs analogous vs no evidence)
   - Test honesty constraints enforcement
   - Test competitive landscape assessment
   - Mock Perplexity API responses

3. **Unit Tests for Stage 6**:
   - Mock Stage 4 concepts + Stage 5 competitive intel
   - Test markdown template rendering
   - Test traceability chain inclusion
   - Test No-Hallucination Disclosure section presence
   - Verify card is valid markdown format

4. **End-to-End Integration Tests**:
   - Use real WGSN PDF: `/data/document/WGSN - FC27-Emotions - Report.pdf`
   - Use test brand: `Boulangerie St-Méthode` (from CLAUDE.md)
   - Run full 7-stage pipeline: Stage 0 → Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → Stage 6
   - Verify 3-5 opportunity cards generated
   - Validate JSON schemas at each stage handoff
   - Verify full traceability in opportunity cards
   - Verify performance: Total execution < 3 minutes

**Fixtures** (add to `/backend/tests/conftest.py`):
```python
@pytest.fixture
def sample_matched_techniques_from_stage3():
    """Matched techniques from Stage 3"""
    return [{
        "insight_id": "uuid-insight-1",
        "matched_techniques": {
            "sit": {
                "primary_technique": "Task Unification",
                "application": "Assign simplification task to shelf/packaging",
                "cpg_example_analogy": "Good Eggs curated selection"
            },
            "doblin": {
                "types_activated": [
                    {"type": "Product Performance", "category": "Offering"},
                    {"type": "Service", "category": "Experience"},
                    {"type": "Brand", "category": "Experience"}
                ],
                "defensibility_score": "MEDIUM"
            }
        }
    }]

@pytest.fixture
def sample_directional_concepts_from_stage4():
    """Directional concepts from Stage 4"""
    return [{
        "concept_id": "uuid-concept-1",
        "concept_name": "Le Guide St-Méthode",
        "concept_tagline": "Rediscover bread joy without choice overwhelm",
        "core_insight": "Bread buyers overwhelmed by 47 SKUs want purchasing to feel like rediscovering childhood simplicity",
        "innovation_mechanism": {
            "primary_technique": "SIT: Task Unification",
            "how_it_works": "Assign simplification task to shelf/packaging via QR"
        },
        "narrative_framework": {
            "customer_problem": "47 bread SKUs creates decision fatigue",
            "brand_solution": "Le Guide curates into 3 simple categories",
            "emotional_payoff": "Feel carefree and confident",
            "proof_points": ["Wine curation increased trial 38%"]
        },
        "cpg_feasibility": {
            "capabilities_required": ["QR system", "Shelf redesign"],
            "estimated_investment": "$40K-$60K for 3-store pilot"
        }
    }]

@pytest.fixture
def mock_perplexity_competitive_results():
    """Mock Perplexity search results for competitive intel"""
    return {
        "direct": {"results": []},  # No direct competitors found
        "analogous": {
            "results": [{
                "title": "Winc AI Wine Curation",
                "url": "https://winc.com",
                "snippet": "AI-powered wine recommendation system"
            }]
        },
        "competitive": {"results": []}  # No competitive activity found
    }

@pytest.fixture
def sample_wgsn_report_pdf():
    """Real WGSN PDF for end-to-end test"""
    return "/data/document/WGSN - FC27-Emotions - Report.pdf"

@pytest.fixture
def sample_test_brand():
    """Test brand for end-to-end test"""
    return {
        "brand_name": "Boulangerie St-Méthode",
        "industry": "CPG - Bakery",
        "geography": "Quebec, Canada",
        "product_portfolio": "25 SKUs with healthy bread focus"
    }
```

**Performance Benchmarking Strategy**:
1. **Individual Stage Timing**:
   - Measure each stage execution time separately
   - Identify bottlenecks (LLM calls, API waits, database writes)
2. **Cumulative Timing**:
   - Measure Stages 0-3 (foundation + core innovation)
   - Measure Stages 4-6 (validation + packaging)
   - Measure total end-to-end (all 7 stages)
3. **Optimization Targets**:
   - If total > 3 minutes: Identify slowest stage
   - Consider parallel execution for Stage 5 (3 searches can run concurrently)
   - Consider caching for Stage 4 if same insight generates same concept

**Test Standards** (same as Stories 1-2):
- All tests must pass before merging to main
- Unit test coverage > 80% for new code
- Integration tests run against Railway staging environment
- Performance tests validate < 3 minute total pipeline execution
- End-to-end test with real WGSN report produces valid opportunity cards

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-11-19 | 1.0 | Story created from EPIC-001 | John (PM Agent) |

## Dev Agent Record

### Agent Model Used
<!-- Populated by Dev Agent during implementation -->

### Debug Log References
<!-- Populated by Dev Agent during implementation -->

### Completion Notes List
<!-- Populated by Dev Agent during implementation -->

### File List
<!-- Populated by Dev Agent during implementation -->

## QA Results
<!-- Populated by QA Agent after implementation -->
