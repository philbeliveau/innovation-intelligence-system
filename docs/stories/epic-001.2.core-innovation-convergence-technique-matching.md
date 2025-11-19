# Story EPIC-001.2: Core Innovation - Convergence Synthesis + Technique Matching (Stages 2-3)

## Status

Draft

## Story

**As an** Innovation Intelligence System,
**I want** to discover multi-trend convergence patterns and match them to validated innovation frameworks (SIT/TRIZ/Doblin),
**so that** CPG innovation teams receive brand-specific consumer insights grounded in systematic innovation techniques.

## Acceptance Criteria

### Functional Requirements

1. **Stage 2 (Consumer Insight Synthesis)**:
   - Enumerates all possible trend pairs via C(n,2) combinations (where n = trend count from Stage 1)
   - Discovers convergence patterns based on: complementary emotions, shared drivers, lifecycle alignment
   - Generates brand-specific consumer insights combining 2+ trends
   - Maps insights to brand challenges (from Stage 0 enriched context)
   - Outputs functional + emotional + social consumer needs
   - Applies lifecycle strategy (PIONEER/VALIDATE/DEFEND) based on trend stages

2. **Stage 3 (Technique Library Matching)**:
   - Matches consumer insights to SIT techniques (5 techniques: Subtraction, Task Unification, Multiplication, Attribute Dependency, Division)
   - Conditionally matches to TRIZ techniques (10 CPG-relevant principles from 40 total)
   - Maps to Doblin innovation types (10 types across Configuration/Offering/Experience)
   - Assesses defensibility (LOW: 1-2 types, MEDIUM: 3 types, HIGH: 4+ types)
   - Includes CPG-specific examples for each matched technique

3. **Convergence Pattern Discovery**:
   - Discovers non-obvious multi-trend connections (convergence discovery rate > 50%)
   - Full traceability from source trends to converged insights
   - Transparent derivation metadata (enumeration method, brand mapping, synthesis method)

4. **Technique Library Data**:
   - SIT: 5 techniques with CPG examples loaded from data files
   - TRIZ: 10 CPG-relevant principles with examples (from 40 total)
   - Doblin: 10 innovation types categorized by Configuration/Offering/Experience

### Integration Requirements

5. **Stage 2 consumes Stage 1 outputs**:
   - Reads trend objects with L1-L4 abstraction levels from Stage 1
   - Reads enriched brand context from Stage 0
   - Validates input JSON schema before processing

6. **Stage 3 consumes Stage 2 outputs**:
   - Reads consumer insights from Stage 2
   - Validates brand relevance mapping
   - Outputs matched techniques ready for Stage 4 concept generation

7. **Database schema updates are additive**:
   - New tables: `convergence_patterns`, `technique_libraries`, `consumer_insights`
   - No breaking changes to existing tables
   - Migration is reversible

### Quality Requirements

8. **Convergence validation**:
   - All C(n,2) trend pairs evaluated (no missed combinations)
   - Convergence patterns include shared emotional drivers or lifecycle alignment
   - Brand relevance includes positioning fit (HIGH/MEDIUM/LOW)

9. **Technique matching validation**:
   - SIT techniques include specific CPG application description
   - Doblin types activate 3+ types for MEDIUM defensibility
   - TRIZ only applied to technical insights (skip for purely emotional/positioning insights)

10. **Testing coverage**:
    - Unit tests for Stage 2 and Stage 3 pass
    - Integration test: Stage 1 output → Stage 2 → Stage 3 → Valid technique-matched insights
    - Convergence discovery rate > 50% (verified with sample WGSN report)

11. **Performance meets targets**:
    - Stage 2 execution: < 60 seconds (for 6 trends = 15 combinations)
    - Stage 3 execution: < 30 seconds (technique library matching)
    - Total Stages 0-3: < 2.5 minutes

## Tasks / Subtasks

### Task 1: Technique Library Data Files (AC: 4)
- [ ] Create `/backend/pipeline/data/sit_techniques.yaml`
  - [ ] Define 5 SIT techniques (Subtraction, Task Unification, Multiplication, Attribute Dependency, Division)
  - [ ] Add CPG examples for each technique (e.g., Task Unification: Good Eggs curated selection)
  - [ ] Include application guidance per technique
- [ ] Create `/backend/pipeline/data/triz_principles_cpg.yaml`
  - [ ] Select 10 most CPG-relevant TRIZ principles from 40 total
  - [ ] Examples: Principle 1 (Segmentation), Principle 10 (Prior Action), Principle 15 (Dynamics)
  - [ ] Add CPG-specific examples for each principle
  - [ ] Include applicability criteria (when to use each principle)
- [ ] Create `/backend/pipeline/data/doblin_types.yaml`
  - [ ] Define 10 Doblin innovation types across 3 categories:
    - Configuration: Profit Model, Network, Structure, Process
    - Offering: Product Performance, Product System
    - Experience: Service, Channel, Brand, Customer Engagement
  - [ ] Add CPG examples per type
  - [ ] Include defensibility guidance (3+ types = MEDIUM, 4+ types = HIGH)
- [ ] Create data loader in `/backend/pipeline/technique_library.py`
  - [ ] Load YAML files on startup
  - [ ] Cache technique libraries in memory
  - [ ] Provide query methods by framework (SIT/TRIZ/Doblin)

### Task 2: Stage 2 - Consumer Insight Synthesis (AC: 1, 3, 8)
- [ ] Replace `/backend/pipeline/stages/stage2_trend_extraction.py` with `stage2_insight_synthesis.py`
  - [ ] Implement `InsightSynthesisStage` class
  - [ ] Define input schema (trends from Stage 1 + brand context from Stage 0)
  - [ ] Define output schema (consumer insights per handoff doc lines 250-283)
- [ ] Implement convergence enumeration logic
  - [ ] Generate all C(n,2) trend pair combinations
  - [ ] Identify convergence type: complementary_emotions | shared_drivers | lifecycle_aligned
  - [ ] Extract shared emotional drivers from trend pairs
  - [ ] Skip pairs with no emotional/lifecycle overlap
- [ ] Create `/backend/pipeline/prompts/stage2_prompt.py`
  - [ ] Prompt for convergence pattern discovery (enumeration-based, not graph-based)
  - [ ] Prompt for brand relevance mapping (category challenge, positioning fit, permission to play)
  - [ ] Prompt for lifecycle strategy determination (PIONEER/VALIDATE/DEFEND)
  - [ ] Prompt for consumer needs synthesis (functional + emotional + social)
- [ ] Implement brand mapping logic
  - [ ] Match convergence to brand's category challenges (from Stage 0)
  - [ ] Assess positioning fit (HIGH/MEDIUM/LOW)
  - [ ] Determine abstraction level relevance (L1=tactical, L3=mechanism, L4=strategic)
- [ ] Add derivation transparency metadata
  - [ ] Record convergence source: "enumeration"
  - [ ] Record brand mapping source: "semantic_matching"
  - [ ] Record insight generation method: "LLM synthesis"
- [ ] Create unit tests in `/backend/tests/test_stage2_insight_synthesis.py`
  - [ ] Test C(n,2) enumeration (6 trends = 15 combinations)
  - [ ] Test convergence type identification
  - [ ] Test brand relevance scoring
  - [ ] Mock OpenRouter LLM calls

### Task 3: Stage 3 - Technique Library Matching (AC: 2, 9)
- [ ] Create `/backend/pipeline/stages/stage3_technique_matching.py`
  - [ ] Implement `TechniqueMatchingStage` class
  - [ ] Define input schema (consumer insights from Stage 2)
  - [ ] Define output schema (matched techniques per handoff doc lines 320-350)
- [ ] Create `/backend/pipeline/prompts/stage3_prompt.py`
  - [ ] Prompt for SIT technique selection (which of 5 techniques applies)
  - [ ] Prompt for TRIZ applicability check (technical vs emotional insight)
  - [ ] Prompt for Doblin type mapping (aim for 3+ types)
  - [ ] Prompt for defensibility assessment
- [ ] Implement SIT matching logic
  - [ ] Load SIT techniques from data file
  - [ ] Identify primary SIT technique per insight
  - [ ] Generate specific CPG application description
  - [ ] Include analogous CPG example from library
  - [ ] Allow secondary techniques if applicable
- [ ] Implement TRIZ matching logic (conditional)
  - [ ] Check if insight is technical (product performance/packaging/supply chain)
  - [ ] If technical: Match to relevant TRIZ principles
  - [ ] If purely emotional/positioning: Skip TRIZ with rationale
- [ ] Implement Doblin type mapping
  - [ ] Identify which of 10 types are activated by concept
  - [ ] Categorize by Configuration/Offering/Experience
  - [ ] Calculate defensibility score (LOW: 1-2, MEDIUM: 3, HIGH: 4+)
  - [ ] Generate defensibility rationale
- [ ] Add CPG actionability assessment
  - [ ] Capability fit: Can brand implement? (HIGH/MEDIUM/LOW)
  - [ ] Permission fit: Does brand positioning allow? (HIGH/MEDIUM/LOW)
  - [ ] Resource fit: Within innovation budget? (HIGH/MEDIUM/LOW + cost estimate)
- [ ] Create unit tests in `/backend/tests/test_stage3_technique_matching.py`
  - [ ] Test SIT technique selection
  - [ ] Test TRIZ conditional application
  - [ ] Test Doblin defensibility scoring
  - [ ] Mock technique library data

### Task 4: Database Schema Updates (AC: 7)
- [ ] Create Prisma migration for new tables
  - [ ] `convergence_patterns` table:
    - `id` (UUID), `trend_a_id` (UUID), `trend_b_id` (UUID)
    - `convergence_type` (VARCHAR), `shared_emotions` (JSONB)
    - `brand_relevance` (JSONB), `lifecycle_strategy` (JSONB)
  - [ ] `consumer_insights` table:
    - `id` (UUID), `insight_statement` (TEXT), `convergence_pattern_id` (UUID)
    - `functional_need` (TEXT), `emotional_need` (TEXT), `social_need` (TEXT)
    - `brand_relevance` (JSONB), `derivation_transparency` (JSONB)
  - [ ] `technique_libraries` table:
    - `id` (UUID), `framework` (VARCHAR: SIT/TRIZ/DOBLIN)
    - `technique_name` (VARCHAR), `description` (TEXT), `cpg_examples` (JSONB)
  - [ ] `matched_techniques` table:
    - `id` (UUID), `insight_id` (UUID)
    - `sit_techniques` (JSONB), `triz_principles` (JSONB), `doblin_types` (JSONB)
    - `defensibility_score` (VARCHAR), `cpg_actionability` (JSONB)
- [ ] Update `/backend/app/models.py` with new models
- [ ] Seed technique libraries table with data from YAML files
- [ ] Run migration in development environment
- [ ] Verify migration is reversible (test rollback)

### Task 5: Integration Testing (AC: 10, 11)
- [ ] Create end-to-end test in `/backend/tests/test_pipeline_v2_core_innovation.py`
  - [ ] Test: Stage 1 trends → Stage 2 → Consumer insights with convergences
  - [ ] Test: Stage 2 insights → Stage 3 → Matched techniques (SIT/TRIZ/Doblin)
  - [ ] Test: Full pipeline Stages 0-3 with real WGSN report
  - [ ] Verify convergence discovery rate > 50% (non-obvious connections found)
- [ ] Convergence pattern validation tests
  - [ ] Verify all C(n,2) combinations evaluated
  - [ ] Verify convergence types correctly identified
  - [ ] Verify brand relevance scoring works
- [ ] Technique matching validation tests
  - [ ] Verify SIT techniques include CPG examples
  - [ ] Verify TRIZ only applied to technical insights
  - [ ] Verify Doblin defensibility calculation (3+ types = MEDIUM)
- [ ] Performance benchmarking
  - [ ] Measure Stage 2 execution time (target: < 60 seconds for 15 combinations)
  - [ ] Measure Stage 3 execution time (target: < 30 seconds)
  - [ ] Verify total Stages 0-3 execution < 2.5 minutes
- [ ] Regression testing
  - [ ] Verify Stage 1 outputs are consumed correctly
  - [ ] Verify Stage 0 brand context is used in brand mapping
  - [ ] Verify webhook notifications work for Stages 2-3

## Dev Notes

### Existing System Integration

**Technology Stack**: Python 3.11+, FastAPI, Prisma (PostgreSQL), OpenRouter (LLM API)

**Integration Points**:
- **Stage 2 (MAJOR REFACTOR)**: Completely replaces `stage2_trend_extraction.py` with convergence-based synthesis
- **Stage 3 (NEW)**: New stage for systematic technique matching
- **Database**: New tables for convergence patterns and technique libraries
- **Dependency**: Story 1 must be completed first (requires Stage 0 brand context + Stage 1 L1-L4 trends)

**Existing Patterns to Follow**:

1. **Stage Class Structure** (same as Story 1):
```python
class InsightSynthesisStage:
    async def execute(self, input_data: dict, run_id: str) -> dict:
        # 1. Load trends from Stage 1 output
        # 2. Load brand context from Stage 0 output
        # 3. Enumerate C(n,2) trend combinations
        # 4. Call LLM for convergence discovery
        # 5. Map to brand challenges
        # 6. Generate consumer insights
        # 7. Store to database
        return consumer_insights
```

2. **Prompt Engineering for Convergence** (per handoff doc lines 273-352):
```python
# In stage2_prompt.py
CONVERGENCE_ENUMERATION_PROMPT = """
You are analyzing {n} trends for brand {brand_name}.

STEP 1: Enumerate all {combination_count} possible trend pairs.

For each pair:
- Check for shared emotional drivers (current_negative OR aspirational_positive overlap)
- Check for complementary lifecycle stages (EMERGING + ACCELERATING = validated opportunity)
- If overlap found, classify convergence type: complementary_emotions | shared_drivers | lifecycle_aligned

STEP 2: Map convergences to brand challenges:
- Brand's category challenge: {category_challenge}
- Does convergence address this challenge? (YES/MAYBE/NO)
- Brand positioning: {positioning}
- Does brand have permission to play? (HIGH/MEDIUM/LOW)
- What abstraction level is most relevant? (L1=tactical, L3=mechanism, L4=strategic)

STEP 3: Generate consumer insights from converged patterns:
- Combine primary trend + secondary trend
- Apply lifecycle strategy (dominant stage determines posture)
- Generate functional + emotional + social needs

Output JSON schema: {schema}
"""
```

3. **Technique Library Structure** (YAML format):
```yaml
# sit_techniques.yaml
techniques:
  - id: task_unification
    name: Task Unification
    description: Assign a new task to an existing resource
    cpg_examples:
      - brand: Good Eggs
        application: Packaging doubles as recipe card
      - brand: Oatly
        application: Carton becomes marketing channel
    when_to_use: When insight requires adding value without cost
```

**Source Tree Updates** (from Story 1):
```
/backend/
├── pipeline/
│   ├── data/                              # NEW - Story 2
│   │   ├── sit_techniques.yaml           # 5 SIT techniques
│   │   ├── triz_principles_cpg.yaml      # 10 CPG-relevant TRIZ principles
│   │   └── doblin_types.yaml             # 10 Doblin innovation types
│   ├── stages/
│   │   ├── stage0_brand_enrichment.py    # From Story 1
│   │   ├── stage1_trend_decomposition.py # From Story 1
│   │   ├── stage2_insight_synthesis.py   # REPLACE stage2_trend_extraction.py
│   │   └── stage3_technique_matching.py  # NEW - Story 2
│   ├── prompts/
│   │   ├── stage2_prompt.py              # REPLACE existing
│   │   └── stage3_prompt.py              # NEW - Story 2
│   ├── technique_library.py              # NEW - Story 2 (data loader)
│   └── stage_cache.py                    # From Story 1
├── tests/
│   ├── test_stage2_insight_synthesis.py  # NEW - Story 2
│   ├── test_stage3_technique_matching.py # NEW - Story 2
│   └── test_pipeline_v2_core_innovation.py # NEW - Story 2 integration test
└── prisma/schema.prisma                  # Add 4 new tables
```

**Convergence Enumeration Logic** (from handoff doc lines 273-352):

**Example with 6 trends**:
- C(6,2) = 15 possible trend pair combinations
- For each pair, check:
  1. **Shared emotional drivers**: Do trends share negative emotions (e.g., both address "overwhelmed")?
  2. **Complementary emotions**: Do trends offer complementary solutions (e.g., "overwhelmed" + "carefree")?
  3. **Lifecycle alignment**: Are lifecycle stages compatible (ACCELERATING + EMERGING = validated + emerging opportunity)?

**Convergence Types**:
- `complementary_emotions`: Trend A addresses Problem X, Trend B offers Solution Y to X
- `shared_drivers`: Both trends driven by same consumer frustration
- `lifecycle_aligned`: Lifecycle stages create strategic timing opportunity (e.g., ACCELERATING validates EMERGING)

**Brand Mapping Logic**:
1. **Category Challenge Match**: Does convergence address brand's specific challenge from Stage 0?
   - Example: St-Méthode has "47 SKUs causing decision fatigue" → Convergence about simplification = HIGH relevance
2. **Positioning Fit**: Does brand's emotional territory overlap with convergence?
   - Example: St-Méthode owns "authentic, simple" → Witherwill (simplification) = HIGH fit
3. **Abstraction Level Selection**:
   - L1: Tactical product features (quick wins)
   - L3: Transferable mechanisms (innovation opportunities)
   - L4: Strategic positioning shifts (brand evolution)

**Lifecycle Strategy Mapping** (from handoff doc):
- **EMERGING + EMERGING**: PIONEER (first-mover, high risk)
- **ACCELERATING + EMERGING**: VALIDATE (proven demand + new opportunity)
- **ACCELERATING + ACCELERATING**: VALIDATE (strong demand signal)
- **PEAKING + ACCELERATING**: DEFEND (maintain relevance)
- **PEAKING + PEAKING**: DEFEND (category stakes)

**SIT Technique Selection Criteria**:
1. **Subtraction**: Insight requires removing component to force adaptation
   - Example: Remove 44 SKUs to simplify choice
2. **Task Unification**: Insight requires adding new task to existing resource
   - Example: Packaging becomes decision-support tool
3. **Multiplication**: Insight requires copying component but changing it
   - Example: Multiple product lines with slight variations
4. **Attribute Dependency**: Insight requires correlating independent attributes
   - Example: SKU availability depends on consumer confidence level
5. **Division**: Insight requires dividing and reorganizing
   - Example: Divide 47 SKUs into 3 curated categories

**TRIZ Applicability Logic**:
- **Apply TRIZ if insight is technical**:
  - Product performance (shelf life, texture, nutrition)
  - Packaging innovation (materials, formats, sustainability)
  - Supply chain optimization (distribution, freshness)
- **Skip TRIZ if insight is purely emotional/positioning**:
  - Brand messaging shifts
  - Emotional territory changes
  - Customer engagement strategies

**Doblin Defensibility Formula** (from handoff doc):
- 1-2 types activated = LOW defensibility (easily copied)
- 3 types activated = MEDIUM defensibility (2x better financial performance)
- 4+ types activated = HIGH defensibility (3-4x better financial performance)
- **Goal**: Aim for 3+ types across Configuration/Offering/Experience categories

**No-Hallucination Boundaries** (maintained from Story 1):
- ✅ Discover convergence patterns from enumerated trend pairs
- ✅ Match insights to validated innovation frameworks (SIT/TRIZ/Doblin)
- ✅ Generate brand-specific consumer needs
- ❌ Invent convergences not supported by shared emotional drivers
- ❌ Claim techniques guarantee success or specific ROI
- ❌ Fabricate CPG examples not in technique library data

**Context from Story 1**:
- **Stage 0 outputs**: Enriched brand context with category challenges, positioning, competitors
- **Stage 1 outputs**: Trend objects with L1-L4 abstraction levels, emotional drivers, lifecycle stages
- **Feature flag**: `PIPELINE_VERSION=v2_7stage` enables new pipeline
- **Cache system**: Stage 0 and Stage 1 are cached, Stage 2-3 run fresh per brand

### Testing

**Test File Locations**:
- `/backend/tests/test_stage2_insight_synthesis.py` - Stage 2 unit tests
- `/backend/tests/test_stage3_technique_matching.py` - Stage 3 unit tests
- `/backend/tests/test_pipeline_v2_core_innovation.py` - Integration tests

**Testing Framework**: pytest with fixtures

**Testing Patterns**:
1. **Unit Tests for Stage 2**:
   - Mock Stage 1 trend objects (6 trends with L1-L4)
   - Mock Stage 0 brand context
   - Test C(n,2) enumeration logic (6 trends = 15 combinations)
   - Test convergence type identification
   - Test brand relevance scoring
   - Mock OpenRouter LLM calls

2. **Unit Tests for Stage 3**:
   - Mock Stage 2 consumer insights
   - Mock technique library data (SIT/TRIZ/Doblin)
   - Test SIT technique selection
   - Test TRIZ conditional application (technical vs emotional)
   - Test Doblin defensibility calculation
   - Verify CPG examples are included in output

3. **Integration Tests**:
   - Use real WGSN PDF from Story 1 test
   - Run full pipeline: Stage 0 → Stage 1 → Stage 2 → Stage 3
   - Verify convergence discovery rate > 50%
   - Verify technique matching for all insights
   - Verify JSON schema validation at each stage handoff

**Fixtures** (add to `/backend/tests/conftest.py`):
```python
@pytest.fixture
def sample_trends_from_stage1():
    """6 sample trends with L1-L4 abstraction"""
    return [
        {
            "trend_id": "uuid-1",
            "trend_name": "Strategic Joy",
            "lifecycle_stage": "EMERGING",
            "emotional_drivers": {
                "current_negative_emotions": ["stressed", "bored"],
                "aspirational_positive_emotions": ["inspired", "carefree"]
            },
            "abstraction_levels": {
                "L1_domain_specific": "Gamified healthy eating",
                "L2_industry_specific": "Food using playfulness",
                "L3_cross_domain": "Pleasure activism",
                "L4_universal_principle": "Joy as strategy"
            }
        },
        # ... 5 more trends
    ]

@pytest.fixture
def sample_brand_context_from_stage0():
    """Enriched brand context from Stage 0"""
    return {
        "brand_name": "Boulangerie St-Méthode",
        "enriched_context": {
            "category": {
                "category_challenges": ["47 SKUs causing decision fatigue"]
            },
            "positioning": {
                "messaging_themes": ["authentic", "simple", "traditional"],
                "emotional_territory": "nostalgic"
            }
        }
    }

@pytest.fixture
def sample_consumer_insights_from_stage2():
    """Consumer insights from Stage 2"""
    return [{
        "insight_id": "uuid-insight-1",
        "insight_statement": "Bread buyers overwhelmed by choice want purchasing to feel like rediscovering childhood simplicity",
        "convergence_pattern": {
            "primary_trend": "Witherwill (ACCELERATING)",
            "secondary_trend": "Strategic Joy (EMERGING)",
            "convergence_type": "complementary_emotions"
        },
        "consumer_needs": {
            "functional_need": "Reduce bread choice from 47 to 3 categories",
            "emotional_need": "Feel confident and carefree when choosing",
            "social_need": "Be perceived as discerning not indecisive"
        }
    }]

@pytest.fixture
def mock_technique_libraries():
    """Mock SIT/TRIZ/Doblin data"""
    return {
        "sit": [
            {
                "id": "task_unification",
                "name": "Task Unification",
                "description": "Assign new task to existing resource",
                "cpg_examples": [{"brand": "Good Eggs", "application": "Curated selection"}]
            }
        ],
        "doblin": [
            {"type": "Product Performance", "category": "Offering"},
            {"type": "Service", "category": "Experience"},
            {"type": "Brand", "category": "Experience"}
        ]
    }
```

**Test Standards** (same as Story 1):
- All tests must pass before merging to main
- Unit test coverage > 80% for new code
- Integration tests run against Railway staging environment
- Performance tests validate < 2.5 minutes for Stages 0-3

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
