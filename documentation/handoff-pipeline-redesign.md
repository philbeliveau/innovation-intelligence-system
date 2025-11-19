# Pipeline Redesign Handoff - Innovation Intelligence System

## Task Overview
Redesign the existing 5-stage pipeline in `/backend/pipeline/` to implement the new 7-stage architecture specified in `/documentation/docs-pipeline-strategy/google-docs/simplified.md`.

## Context
The current pipeline transforms WGSN trend reports into opportunity cards but lacks:
- Multi-trend convergence capabilities
- Systematic innovation framework (SIT/TRIZ/Doblin)
- Lifecycle-aware strategic positioning
- Transparent stage-by-stage validation

The new architecture solves these issues with a more sophisticated 7-stage approach.

## Current State Assessment

### Existing Pipeline Location
- **Directory**: `/backend/pipeline/`
- **Key Files**:
  - `stage1_input_processing.py`
  - `stage2_trend_extraction.py`
  - `stage3_industry_translation.py`
  - `stage4_brand_application.py`
  - `stage5_opportunity_generation.py`
  - `executor.py` (orchestrator)

### Current Pipeline Flow
```
PDF → Extract Trends → Translate to Industry → Apply to Brand → Generate Opportunities
```

## Target State Architecture

### New 7-Stage Pipeline (from simplified.md)
```
Stage 0: Brand Profile Enrichment (via Perplexity search)
Stage 1: Multi-Trend Decomposition (L1-L4 abstraction levels)
Stage 2: Consumer Insight Synthesis (convergence patterns)
Stage 3: Technique Library Matching (SIT + TRIZ + Doblin)
Stage 4: Directional Concept Generation
Stage 5: Competitive Intelligence Integration
Stage 6: Opportunity Card Packaging
```

## Implementation Requirements

### 1. Preserve Existing Infrastructure
- **Keep**: Database models, API endpoints, webhook system, Vercel Blob integration
- **Modify**: Stage implementations and prompts
- **Add**: New stages (Stage 0, Stage 3, Stage 5)

### 2. Stage-Specific Changes

#### Stage 0 (NEW): Brand Profile Enrichment
**Reference**: simplified.md lines 85-142

```python
# NEW FILE: backend/pipeline/stage0_brand_enrichment.py
class BrandEnrichmentStage:
    """
    Transform minimal brand input (4 fields) into enriched context via search-based intelligence
    Per simplified.md Stage 0 specification (lines 85-142)
    """

    def input_schema(self):
        # From simplified.md lines 88-94
        return {
            "brand_name": "string (required)",
            "industry": "string (required) - e.g., 'CPG - Bakery', 'CPG - Dairy'",
            "geography": "string (required) - e.g., 'North America', 'France'",
            "product_portfolio": "string (required) - 2-3 sentence description"
        }

    def processing_logic(self):
        # From simplified.md lines 95-102
        """
        1. Search Enrichment via Perplexity/web search:
           - Category context (SKU count, price positioning, distribution channels)
           - Brand positioning (messaging themes, emotional territory)
           - Competitive set (3-5 direct, 2-3 analogous brands)
           - Innovation history (recent launches, innovation pattern)
        2. Confidence Scoring: 0-1 per enrichment dimension
        3. Conflict Resolution: Flag contradictions, don't hallucinate
        """

    def output_schema(self):
        # From simplified.md lines 103-131
        return {
            "brand_name": "string",
            "enriched_context": {
                "category": {
                    "sku_count_estimate": "string - e.g., '200-300 SKUs'",
                    "price_positioning": "value | mid-tier | premium",
                    "distribution_channels": ["retail", "DTC", "foodservice"],
                    "category_challenges": ["SKU proliferation", "margin pressure"]
                },
                "positioning": {
                    "messaging_themes": ["keyword1", "keyword2", "keyword3"],
                    "emotional_territory": "functional | aspirational | rebellious | nostalgic",
                    "current_narrative": "1-2 sentence summary"
                },
                "competitors": {
                    "direct": ["Brand A", "Brand B", "Brand C"],
                    "analogous": ["Brand X (different category, similar positioning)"]
                },
                "innovation_history": {
                    "recent_launches": ["Launch 1 (2024)", "Launch 2 (2023)"],
                    "innovation_pattern": "incremental | transformational"
                }
            },
            "confidence_scores": {
                "category_context": 0.85,
                "positioning": 0.72,
                "competitors": 0.68,
                "innovation_history": 0.45
            },
            "sources": [{"url": "...", "title": "...", "retrieval_date": "2025-11-15"}],
            "enrichment_timestamp": "2025-11-15T08:00:00Z"
        }

    def validation_criteria(self):
        # From simplified.md lines 137-141
        """
        ✓ All 4 enrichment dimensions attempted (even if low confidence)
        ✓ Confidence scores reflect source quality
        ✓ Conflicting information flagged, not resolved via hallucination
        ✓ Sources cited for every enrichment claim
        """
```

#### Stage 1 (REFACTOR): Multi-Trend Decomposition
**Reference**: simplified.md lines 143-212

```python
# MODIFY: backend/pipeline/stage1_input_processing.py
class TrendDecompositionStage:
    """
    Extract all trends from WGSN report, decomposed across 4 abstraction levels (L1-L4)
    Per simplified.md Stage 1 specification (lines 143-212)
    """

    def input_schema(self):
        # From simplified.md lines 150-161
        return {
            "report_source": "WGSN Future Consumer 2027 Emotions Report",
            "report_text": "string (full PDF text extracted)",
            "report_metadata": {
                "publication_date": "2025-XX-XX",
                "forecast_horizon": "2027",
                "report_type": "Emotions"
            }
        }

    def processing_logic(self):
        # From simplified.md lines 165-173
        """
        1. Trend Identification: Extract 3-6 major trends per report
        2. Abstraction Ladder for each trend:
           - L1 (Domain-Specific): CPG-actionable application
           - L2 (Industry-Specific): Category-level pattern
           - L3 (Cross-Domain): Transferable mechanism
           - L4 (Universal Principle): Fundamental dynamic
        3. Lifecycle Mapping: EMERGING/ACCELERATING/PEAKING from WGSN
        4. Emotional Driver Extraction: current_negative + aspirational_positive
        """

    def output_schema(self):
        # From simplified.md lines 176-202
        return [{
            "trend_id": "uuid",
            "trend_name": "Strategic Joy",
            "lifecycle_stage": "EMERGING | ACCELERATING | PEAKING",
            "lifecycle_rationale": "WGSN states 'will emerge in 2026-2027'",
            "emotional_drivers": {
                "current_negative_emotions": ["dysregulated", "stressed", "bored"],
                "aspirational_positive_emotions": ["included", "serene", "inspired"]
            },
            "consumer_behaviors": [
                "Seeking products that make healthy habits feel effortless",
                "Gravitating toward brands with playful, joy-first messaging"
            ],
            "abstraction_levels": {
                "L1_domain_specific": "CPG products that gamify healthy eating",
                "L2_industry_specific": "Food/beverage brands using playfulness",
                "L3_cross_domain": "Pleasure activism: reframe obligation as choice",
                "L4_universal_principle": "Joy as strategic business tool"
            },
            "trend_description": "2-3 sentence summary from WGSN report",
            "wgsn_source_section": "Section title from report",
            "extraction_confidence": 0.95
        }]

    def validation_criteria(self):
        # From simplified.md lines 206-210
        """
        ✓ All distinct trends extracted (3-6 per report)
        ✓ L1-L4 ascend from concrete to universal (not redundant)
        ✓ Lifecycle stage explicitly stated or clearly implied
        ✓ Emotional drivers include both negative + positive
        ✓ No hallucinated statistics or competitive claims
        """
```

#### Stage 2 (MAJOR REFACTOR): Consumer Insight Synthesis
**Reference**: simplified.md lines 214-426 (Using Option A: JSON-Based Convergence)

```python
# REPLACE: backend/pipeline/stage2_trend_extraction.py
class InsightSynthesisStage:
    """
    Navigate enumerated convergence patterns to discover brand-specific insights
    Per simplified.md Stage 2 Option A specification (lines 217-426)
    """

    def processing_logic(self):
        # From simplified.md lines 273-352
        """
        Step 1: Enumerate All Possible Trend Pairs
        - Transparent, non-graph-based enumeration
        - Check for shared emotional drivers
        - Check for complementary lifecycle stages
        - Generate all C(n,2) convergences where n = trend count

        Step 2: Map Convergences to Brand Challenges
        - Does convergence address brand's category challenge? (YES/MAYBE/NO)
        - Does brand have permission to play? (positioning overlap)
        - What abstraction level is most relevant? (L1=tactical, L3=mechanism, L4=strategic)

        Step 3: Generate Consumer Insights from Converged Patterns
        - Combine primary + secondary trend
        - Apply lifecycle strategy
        - Generate functional + emotional + social needs
        """

    def input_schema(self):
        # From simplified.md lines 362-376
        return {
            "trends_array": [...],  # From Stage 1
            "brand_context": {...},  # From Stage 0
            "convergence_patterns": [{
                "trend_a_id": "uuid_1",
                "trend_b_id": "uuid_2",
                "convergence_type": "complementary_emotions | shared_drivers | lifecycle_aligned",
                "shared_emotions": ["overwhelmed", "carefree"],
                "reasoning": "..."
            }]
        }

    def output_schema(self):
        # From simplified.md lines 380-415
        return [{
            "insight_id": "uuid",
            "insight_statement": "Bread buyers overwhelmed by choice want purchasing to feel like rediscovering childhood simplicity",
            "convergence_pattern": {
                "primary_trend": "Witherwill (ACCELERATING)",
                "secondary_trend": "Strategic Joy (EMERGING)",
                "convergence_type": "complementary_emotions",
                "shared_emotional_drivers": ["overwhelmed", "carefree"],
                "lifecycle_combination": "ACCELERATING + EMERGING = validated opportunity"
            },
            "brand_relevance": {
                "category_challenge_addressed": "Bread category has 47 SKUs causing decision fatigue",
                "positioning_fit": "HIGH | MEDIUM | LOW",
                "permission_to_play": "HIGH - Brand owns 'authentic, simple' territory",
                "abstraction_level_applied": "L3: Simplification as self-care + Pleasure activism"
            },
            "lifecycle_strategy": {
                "dominant_stage": "ACCELERATING",
                "strategic_posture": "VALIDATE",
                "rationale": "Witherwill is ACCELERATING = proven demand signal",
                "execution_timeline": "6 months"
            },
            "consumer_needs": {
                "functional_need": "Reduce bread choice from 47 to 3 categories",
                "emotional_need": "Feel confident and carefree when choosing",
                "social_need": "Be perceived as discerning not indecisive"
            },
            "derivation_transparency": {
                "convergence_source": "enumeration",
                "brand_mapping_source": "semantic_matching",
                "insight_generation_method": "LLM synthesis"
            }
        }]
```

#### Stage 3 (NEW): Technique Library Matching
**Reference**: simplified.md lines 463-534

```python
# NEW FILE: backend/pipeline/stage3_technique_matching.py
class TechniqueMatchingStage:
    """
    Validate insights against 55 innovation patterns (SIT: 5, TRIZ: 40, Doblin: 10)
    Per simplified.md Stage 3 specification (lines 463-534)
    """

    def processing_logic(self):
        # From simplified.md lines 477-490
        """
        1. SIT Matching: Identify which of 5 techniques address insight
           - Subtraction: Remove component, force adaptation
           - Task Unification: Assign new task to existing resource
           - Multiplication: Copy component but change it
           - Attribute Dependency: Correlate independent attributes
           - Division: Divide and reorganize

        2. TRIZ Matching (Conditional): Only for technical insights
           - If product performance/packaging/supply chain → Match TRIZ
           - If purely emotional/positioning → Skip TRIZ

        3. Doblin Type Mapping: Identify which of 10 types
           - Aim for 3+ types across Configuration/Offering/Experience
           - 4+ types = 2x better financial performance

        4. Defensibility Assessment:
           - 1-2 types = LOW, 3 types = MEDIUM, 4+ types = HIGH
        """

    def output_schema(self):
        # From simplified.md lines 491-519
        return [{
            "insight_id": "from_stage_2",
            "matched_techniques": {
                "sit": {
                    "primary_technique": "Task Unification",
                    "application": "Assign simplification task to packaging/shelf",
                    "cpg_example_analogy": "Like Good Eggs curated selection",
                    "secondary_techniques": ["Division: Divide 47 SKUs into 3 categories"]
                },
                "triz": {
                    "applicable": False,
                    "rationale": "Insight is positioning/emotional, not technical"
                },
                "doblin": {
                    "types_activated": [
                        {"type": "5. Product Performance", "category": "Offering", "how": "Curated SKU selection"},
                        {"type": "7. Service", "category": "Experience", "how": "Shelf guidance system"},
                        {"type": "9. Brand", "category": "Experience", "how": "Position as simplifying expert"}
                    ],
                    "defensibility_score": "MEDIUM",
                    "defensibility_rationale": "3 types across Offering + Experience"
                }
            },
            "technique_justification": "Task Unification fits because insight requires adding value without cost",
            "cpg_actionability": {
                "capability_fit": "HIGH - Brand can implement without new manufacturing",
                "permission_fit": "HIGH - Brand positioned as traditional expert",
                "resource_fit": "MEDIUM - Requires ~$50K within innovation budget"
            }
        }]
```

#### Stage 4 (REFACTOR): Directional Concept Generation
**Reference**: simplified.md lines 535-605

```python
# MODIFY: backend/pipeline/stage4_brand_application.py
class ConceptGenerationStage:
    """
    Generate brand-specific directional concepts (NOT full product specs)
    Per simplified.md Stage 4 specification (lines 535-605)
    """

    def processing_logic(self):
        # From simplified.md lines 544-556
        """
        1. Concept Formulation: Combine
           - Consumer insight (what problem/opportunity)
           - Innovation mechanism (how via SIT/TRIZ/Doblin)
           - Lifecycle strategy (when/how based on trend stage)
           - Brand permission (why this brand can do this)

        2. Narrative Framework: Must answer
           - Customer Problem: What frustrates them?
           - Brand Solution: How does concept solve it?
           - Emotional Payoff: How will they feel?
           - Proof Points: Why will it work?

        3. No-Hallucination Boundary:
           - What we know (trend facts + brand context)
           - What we infer (directional concepts)
           - What we don't claim (market size, competitive gaps, ROI)
        """

    def output_schema(self):
        # From simplified.md lines 558-590
        return [{
            "concept_id": "uuid",
            "concept_name": "Le Guide St-Méthode",
            "concept_tagline": "Rediscover bread joy without choice overwhelm",
            "core_insight": "Bread buyers overwhelmed by 47 SKUs...",
            "innovation_mechanism": {
                "primary_technique": "SIT: Task Unification",
                "how_it_works": "Assign simplification task to shelf/packaging via QR"
            },
            "directional_concept_description": {
                "what": "In-aisle curated selection tool",
                "who": "Overwhelmed shoppers facing 47+ bread SKUs",
                "why_now": "Witherwill trend ACCELERATING per WGSN",
                "why_this_brand": "Traditional craft expert has credibility"
            },
            "lifecycle_strategy": {
                "trend_stage": "ACCELERATING",
                "strategic_posture": "VALIDATE",
                "execution_approach": "Fast-follower: Adapt proven models",
                "timeline": "6 months pilot"
            },
            "narrative_framework": {
                "customer_problem": "47 bread SKUs creates decision fatigue",
                "brand_solution": "Le Guide curates into 3 simple categories",
                "emotional_payoff": "Feel carefree and confident",
                "proof_points": ["Wine curation increased trial 38%", "Trader Joe's model"]
            },
            "cpg_feasibility": {
                "capabilities_required": ["QR system", "Shelf redesign", "Content"],
                "estimated_investment": "$40K-$60K for 3-store pilot",
                "go_to_market": "Retail in-aisle activation",
                "success_metrics": {
                    "trial_rate": "15% scan QR",
                    "new_sku_trial": "25% try non-default",
                    "repeat_purchase": "40% return in 2 weeks"
                }
            },
            "no_hallucination_boundary": {
                "what_we_know": "WGSN identifies Witherwill as ACCELERATING",
                "what_we_infer": "Directional concept based on convergence",
                "what_we_dont_claim": "Exact market size, zero competition, guaranteed ROI"
            }
        }]
```

#### Stage 5 (NEW): Competitive Intelligence Integration
**Reference**: simplified.md lines 606-671

```python
# NEW FILE: backend/pipeline/stage5_competitive_intel.py
class CompetitiveIntelligenceStage:
    """
    Search-based competitive validation with transparency about limitations
    Per simplified.md Stage 5 specification (lines 606-671)
    """

    def processing_logic(self):
        # From simplified.md lines 615-626
        """
        1. Multi-Query Search: For each concept, run 3 searches
           - Direct: Same concept, same category
           - Analogous: Same mechanism, different category
           - Competitive: Brand's competitors + innovation type

        2. Result Triangulation:
           - Direct competitors (exact match)
           - Analogous competitors (transferable mechanism)
           - No evidence (absence ≠ absence of competition)

        3. Honesty Constraints:
           - NEVER claim "zero competition"
           - Say: "No evidence found in top 50 results"
           - Acknowledge: "Search has blind spots"

        4. Differentiation Angle: If competitors found, propose strategy
        """

    def output_schema(self):
        # From simplified.md lines 627-657
        return [{
            "concept_id": "from_stage_4",
            "competitive_validation": {
                "search_queries_executed": [
                    "curated bread selection tool bakery",
                    "product curation system wine grocery",
                    "Whole Foods bakery innovation 2024"
                ],
                "direct_competitors_found": [],
                "analogous_competitors_found": [{
                    "competitor": "Winc",
                    "category": "Wine e-commerce",
                    "mechanism": "AI-driven curation",
                    "source": "https://winc.com",
                    "transferability": "HIGH - Algorithm could adapt to bread",
                    "threat_level": "MEDIUM"
                }],
                "no_evidence_caveat": "Top 50 results found no direct tools. Does NOT confirm zero",
                "competitive_assessment": {
                    "landscape": "OPEN",
                    "landscape_rationale": "No direct competitors in bread category",
                    "first_mover_opportunity": "MEDIUM-HIGH",
                    "opportunity_rationale": "6-12 month window before transfer",
                    "differentiation_angle": "Traditional expert credibility + recipes"
                }
            }
        }]
```

#### Stage 6 (MINOR UPDATE): Opportunity Card Packaging
**Reference**: simplified.md lines 672-744

```python
# UPDATE: backend/pipeline/stage5_opportunity_generation.py → stage6_opportunity_packaging.py
class OpportunityPackagingStage:
    """
    Package concepts into retail-ready opportunity cards
    Per simplified.md Stage 6 specification (lines 672-744)
    """

    def processing_logic(self):
        # From simplified.md lines 683-692
        """
        1. 30-Second Pitch Structure:
           - Headline: Concept name + tagline
           - Problem: Consumer insight (1 sentence)
           - Solution: Innovation mechanism (2 sentences)
           - Strategy: Lifecycle-aware execution

        2. Decision-Ready Artifact:
           - Strategic fit (trend convergence + brand permission)
           - Competitive landscape (honest assessment)
           - Execution roadmap (3-phase: validate, build, launch)
           - Investment required (budget + timeline)
           - Success metrics (trial, repeat, velocity)

        3. Transparency Layer: No-hallucination disclosure in every card
        """

    def output_format(self):
        # From simplified.md lines 694-730
        """
        ## Opportunity Card: [Concept Name]
        **Tagline:** [Concept tagline]

        ### Strategic Fit
        - Consumer Insight: [From Stage 2]
        - Trend Convergence: [Primary + Secondary trends]
        - Lifecycle Stage: [EMERGING/ACCELERATING/PEAKING]
        - Strategic Posture: [PIONEER/VALIDATE/DEFEND]

        ### Concept Overview
        [2-3 sentence description combining mechanism + brand fit]

        ### Innovation Mechanism
        - Primary Technique: [SIT/TRIZ/Doblin]
        - How It Works: [Specific application]
        - Defensibility: [LOW/MEDIUM/HIGH]

        ### Competitive Landscape
        - Direct Competitors: [Found/None found]
        - Analogous Threats: [List with transferability]
        - Differentiation Angle: [If needed]

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
        What we know: [Facts from reports]
        What we infer: [Directional concepts]
        What we DON'T claim: [Market size, zero competition, ROI]
        """
```

### 3. Modular Architecture Requirements

#### Stage Caching System
```python
# NEW FILE: backend/pipeline/stage_cache.py
class StageCache:
    """
    Cache expensive stages (Stage 0, 1) for reuse across brands/reports
    - Stage 0: Cache per brand (quarterly refresh)
    - Stage 1: Cache per report (brand-agnostic)
    """
```

#### Experimentation Support
```python
# NEW FILE: backend/pipeline/experiment_runner.py
class ExperimentRunner:
    """
    Run pipeline with configurable stage versions
    - Hot-swappable prompts
    - A/B testing support
    - Full intermediate output capture
    """
```

### 4. Critical Integration Points

#### JSON Schema Validation
- Every stage must output valid JSON with explicit schemas
- No free-text handoffs between stages
- Enable stage-by-stage debugging

#### Traceability Requirements
```python
# Add to each stage output
"derivation_metadata": {
    "source_stage": "stage_name",
    "source_ids": ["uuid1", "uuid2"],
    "transformation_type": "convergence|extraction|synthesis",
    "confidence_score": 0.85
}
```

### 5. Database Schema Updates
```sql
-- Add tables for new capabilities
CREATE TABLE technique_libraries (
    id UUID PRIMARY KEY,
    framework VARCHAR(20), -- 'SIT', 'TRIZ', 'DOBLIN'
    technique_name VARCHAR(100),
    description TEXT,
    cpg_examples JSONB
);

CREATE TABLE convergence_patterns (
    id UUID PRIMARY KEY,
    trend_a_id UUID,
    trend_b_id UUID,
    convergence_type VARCHAR(50),
    shared_emotions JSONB,
    brand_relevance JSONB
);
```

## Implementation Strategy

### Phase 1: Foundation (Week 1)
1. Create `stage0_brand_enrichment.py` with Perplexity integration
2. Refactor `stage1_input_processing.py` for L1-L4 abstraction
3. Create technique library data files (SIT/TRIZ/Doblin)
4. Update database schema

### Phase 2: Core Innovation (Week 2)
1. Rewrite `stage2_trend_extraction.py` → `stage2_insight_synthesis.py`
2. Implement `stage3_technique_matching.py`
3. Update `stage4_brand_application.py` to use techniques
4. Add experimentation runner

### Phase 3: Validation & Polish (Week 3)
1. Implement `stage5_competitive_intel.py`
2. Update opportunity card formatting
3. Add stage caching system
4. Build traceability visualization

### Phase 4: Testing & Tuning (Week 4)
1. Run end-to-end tests with WGSN report
2. A/B test prompt variations
3. Validate output quality
4. Performance optimization

## Success Criteria

### Functional Requirements
- [ ] All 7 stages execute successfully
- [ ] JSON schemas validated at each handoff
- [ ] Caching reduces redundant API calls by 70%
- [ ] Full traceability from trend → insight → concept → card

### Quality Requirements
- [ ] L1-L4 abstraction levels clearly differentiated
- [ ] Convergence patterns discover non-obvious connections
- [ ] SIT techniques provide actionable mechanisms
- [ ] No hallucinated statistics or claims

### Performance Requirements
- [ ] End-to-end pipeline < 3 minutes
- [ ] Stage 0 cache hit rate > 90%
- [ ] Stage 1 cache hit rate > 95%
- [ ] Parallel execution for Stages 2-6 per brand

## Testing Checklist

### Unit Tests
- [ ] Each stage processes sample input correctly
- [ ] Schema validation catches malformed data
- [ ] Cache invalidation works correctly

### Integration Tests
- [ ] WGSN PDF → 7 stages → Opportunity cards
- [ ] Multiple brands using same trend cache
- [ ] Webhook notifications at each stage

### Quality Tests
- [ ] Compare old vs new pipeline outputs
- [ ] Validate no-hallucination boundaries
- [ ] Check convergence pattern discovery rate

## Resources

### Reference Documents
- **Specification**: `/documentation/docs-pipeline-strategy/google-docs/simplified.md`
- **Current Pipeline**: `/backend/pipeline/`
- **Test Data**: `/data/document/WGSN - FC27-Emotions - Report.pdf`
- **Brand Profiles**: `/data/profiles/`

### External Dependencies
- OpenRouter API (all LLM calls)
- Perplexity API (Stage 0 enrichment)
- PostgreSQL (data persistence)
- Vercel Blob (PDF storage)

## Questions to Resolve Before Starting

1. **Perplexity API Integration**: Do we have API keys and rate limits configured?
2. **Backwards Compatibility**: Should old 5-stage pipeline remain callable?
3. **Migration Strategy**: How to handle in-progress pipeline runs during deployment?
4. **Prompt Versioning**: Where to store different prompt versions for A/B testing?
5. **Monitoring**: What metrics should we track for each stage?

## Handoff Notes

The core innovation is Stage 2's convergence discovery and Stage 3's systematic technique matching. These are the "creative" stages that will require the most tuning. Start with the JSON-based convergence approach (Option A) as specified - it's simpler and sufficient for 3-6 trends per report.

The existing webhook infrastructure should work unchanged - just update the stage names and ensure each new stage sends progress updates.

Prioritize modularity and experimentation support - the founder needs to see how input changes affect output quality, especially in Stages 2 and 4.

## Contact for Questions
[Your contact information]

---

**Ready for handoff.** This document contains everything needed to redesign the pipeline from 5 stages to 7 stages with improved innovation framework integration.