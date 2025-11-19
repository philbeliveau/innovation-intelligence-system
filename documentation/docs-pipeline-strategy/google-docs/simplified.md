Innovation Intelligence System: Reference Architecture Table of Contents 
Stage 0: Brand Profile Enrichment
Stage 1: Multi-Trend Decomposition
Stage 2: Consumer Insight Synthesis via Trend Reasoning
Integration with Stage 3
Stage 3: Technique Library Matching (SIT + TRIZ + Doblin)
Integration with Stage 4
Stage 4: Directional Concept Generation
Integration with Stage 5
Stage 6: Opportunity Card Packaging

Technical Specification for 7-Stage Hybrid Pipeline 
Version: 1.0 
Date: November 15, 2025 
Status: Design Complete - Implementation Pending 
Purpose: Concise reference guide for stage-by-stage implementation with integration specifications 
System Overview 
Description 
Hybrid extraction-synthesis pipeline that transforms WGSN trend reports + brand context into retail-ready CPG innovation opportunities through systematic multi-trend convergence, multi-framework validation, and lifecycle-aware strategic positioning. 
Architectural Approach 
Stages 0-1: Template-driven extraction (reliable, consistent structure) 
Stage 2: Graph-based synthesis (discover non-obvious convergence) 
Stage 3: Pattern validation (SIT/TRIZ/Doblin multi-framework) 
Stages 4-6: Lifecycle-aware ideation with competitive intelligence 

Theoretical Foundation 
Combinatorial Creativity: Boden (2004), Gu et al. (2024) — novelty through multi-level recombination [ 2] 1][ Graph-Augmented Reasoning: KG-RAR, GIVE framework — structured knowledge reduces hallucination [ 4] 3][ Systematic Innovation: SIT (5 techniques), TRIZ (40 principles), Doblin (10 types) [ 6][^7] 5][ 
Data Flow Architecture
┌─────────────────────────────────────────────────────────────┐ │ INPUTS │ 
├─────────────────────────────────────────────────────────────┤ │ • WGSN Trend Report (PDF) │ 
│ • Brand Profile (4 fields: name, industry, geo, portfolio) │ 
└─────────────────────────────────────────────────────────────┘ ↓ 
┌─────────────────────────────────────────────────────────────┐ │ STAGE 0: Brand Profile Enrichment │ 
│ Output: enriched_brand_context.json │ 
└─────────────────────────────────────────────────────────────┘ ↓ 
┌─────────────────────────────────────────────────────────────┐ │ STAGE 1: Multi-Trend Decomposition │ 
│ Output: trend_objects_array.json (reusable across brands) │ 
└─────────────────────────────────────────────────────────────┘ ↓  
┌─────────────────────────────────────────────────────────────┐ │ STAGE 2: Consumer Insight Synthesis  │ 
│ Input: trend_graph.json + enriched_brand_context.json │ 
│ Output: consumer_insights_array.json │ 
└─────────────────────────────────────────────────────────────┘ ↓ 
┌─────────────────────────────────────────────────────────────┐ │ STAGE 3: Technique Library Matching │ 
│ Input: consumer_insights_array.json + libraries (SIT/TRIZ/ │ 
│ Doblin) │ 
│ Output: validated_techniques.json │ 
└─────────────────────────────────────────────────────────────┘ ↓ 
┌─────────────────────────────────────────────────────────────┐ │ STAGE 4: Directional Concept Generation │ 
│ Input: validated_techniques.json + enriched_brand_context │ 
│ Output: directional_concepts.json │ 
└─────────────────────────────────────────────────────────────┘ ↓ 
┌─────────────────────────────────────────────────────────────┐ │ STAGE 5: Competitive Intelligence Integration │ 
│ Input: directional_concepts.json │ 
│ Output: competitive_validation.json │ 
└─────────────────────────────────────────────────────────────┘ ↓ 
┌─────────────────────────────────────────────────────────────┐ │ STAGE 6: Opportunity Card Packaging │ 
│ Input: All previous stage outputs │ 
│ Output: opportunity_cards.md (retail-ready) │ 
└─────────────────────────────────────────────────────────────┘ ↓ 
┌─────────────────────────────────────────────────────────────┐ │ OUTPUTS │ 
├─────────────────────────────────────────────────────────────┤ │ • 3-5 Opportunity Cards per (report × brand) combination │ 
│ • Markdown format, 30-second pitch ready │ 
│ • Includes: insight, mechanism, strategy, roadmap, metrics │ 
└─────────────────────────────────────────────────────────────┘ 
Stage Integration Architecture 
Execution Dependencies 
Stage 0: RUNS ONCE PER BRAND 
Enriched context is cached for reuse across multiple reports 
Re-run only if brand profile changes or quarterly refresh needed 
Integration: Output feeds into Stage 2 (brand context) and Stage 4 (concept generation) 
Stage 1: RUNS ONCE PER REPORT 
Trend extraction is report-specific but brand-agnostic 
Output is reusable across all brands analyzing the same report 
Cost optimization: Extract once, synthesize many times 
Integration: Output feeds into Graph Builder (pre-Stage 2) and Stage 2 directly 
Stages 2-6: RUN PER (REPORT × BRAND) COMBINATION 
Each brand gets custom insights from same trend extraction 
Stage 2 synthesizes brand-specific insights from shared trends 
Stages 3-6 build on brand-specific insights sequentially 
Critical Integration Rule: All stages output valid JSON with explicit schemas. No free-text handoffs. This enables: 
Debugging: Inspect intermediate outputs at any stage 
Validation: Test each stage independently 
Modularity: Swap Stage 2 implementation without breaking Stage 3 
Traceability: Track which trend → insight → technique → concept 
Stage 0: Brand Profile Enrichment 
Objective 
Transform minimal brand input (4 fields) into enriched context via search-based intelligence to enable brand-specific synthesis in downstream stages. 
Input Schema 
{ 
"brand_name": "string (required)", 
"industry": "string (required) - e.g., 'CPG - Bakery', 'CPG - Dairy'", 
"geography": "string (required) - e.g., 'North America', 'France'", 
"product_portfolio": "string (required) - 2-3 sentence description" 
} 
Processing Logic 
1. Search Enrichment: Use Perplexity/web search to gather: 
Category context (SKU count estimate, price positioning, distribution channels) 
Brand positioning (messaging themes from website/social, emotional territory) 
Competitive set (3-5 direct competitors, 2-3 analogous brands) 
Innovation history (recent launches, innovation pattern) 
2. Confidence Scoring: Assign 0-1 confidence score per enrichment dimension based on source quality 
3. Conflict Resolution: If search returns contradictory info, flag for manual review (don't hallucinate a resolution)
Output Schema 
{"brand_name": "string", 
"enriched_context": { 
"category": { 
"sku_count_estimate": "string - e.g., '200-300 SKUs'", 
"price_positioning": "value | mid-tier | premium", 
"distribution_channels": ["retail", "DTC", "foodservice"], 
"category_challenges": ["SKU proliferation", "margin pressure"] 
},"positioning": { 
"messaging_themes": ["keyword1", "keyword2", "keyword3"], 
"emotional_territory": "functional | aspirational | rebellious | nostalgic", "current_narrative": "1-2 sentence summary" 
},"competitors": { 
"direct": ["Brand A", "Brand B", "Brand C"], 
"analogous": ["Brand X (different category, similar positioning)"] },"innovation_history": { 
"recent_launches": ["Launch 1 (2024)", "Launch 2 (2023)"], 

} 
}, 
"innovation_pattern": "incremental | transformational" 

"confidence_scores": { 
"category_context": 0.85, 
"positioning": 0.72, 
"competitors": 0.68, 
"innovation_history": 0.45 
},"sources": [ 
{"url": "...", "title": "...", "retrieval_date": "2025-11-15"} ],"enrichment_timestamp": "2025-11-15T08:00:00Z" 
} 
Integration with Downstream Stages 
→ Stage 2: enriched_context.category and enriched_context.positioning inform brand-specific insight synthesis → Stage 4: enriched_context.positioning.emotional_territory determines brand permission for concepts → Stage 6: Full enriched context included in opportunity card for transparency 
Key Sources 
Perplexity AI multi-source search [^8] 
CPG market intelligence (category context) [^9] 
Brand positioning frameworks [^10] 
Validation Criteria 
✓ All 4 enrichment dimensions attempted (even if confidence is low) 
✓ Confidence scores reflect source quality (official site > news > social media) 
✓ Conflicting information flagged, not resolved via hallucination 
✓ Sources cited for every enrichment claim 

Stage 1: Multi-Trend Decomposition

## Objective

Extract all trends from WGSN report, decomposed across 4 abstraction levels (L1-L4) to enable combinatorial creativity and cross-domain transfer.

## Input Schema

```json
{
  "report_source": "WGSN Future Consumer 2027 Emotions Report",
  "report_text": "string (full PDF text extracted)",
  "report_metadata": {
    "publication_date": "2025-XX-XX",
    "forecast_horizon": "2027",
    "report_type": "Emotions"
  }
}
```

## Processing Logic

1. **Trend Identification**: Extract every distinct emotional trend mentioned (typically 3-6 major trends per report)
2. **Abstraction Ladder**: For each trend, extract 4 levels:
   - **L1 (Domain-Specific)**: CPG-actionable application (e.g., "Protein bars with gamified packaging")
   - **L2 (Industry-Specific)**: Category-level pattern (e.g., "Food brands using play to reframe health")
   - **L3 (Cross-Domain)**: Transferable mechanism (e.g., "Pleasure activism: reframe obligation as choice")
   - **L4 (Universal Principle)**: Fundamental dynamic (e.g., "Joy as strategic business tool")
3. **Lifecycle Mapping**: Extract WGSN's lifecycle stage (EMERGING/ACCELERATING/PEAKING) from report language
4. **Emotional Driver Extraction**: Capture both current negative emotions (what consumers feel now) and aspirational positive emotions (what they want to feel)

## Output Schema

```json
[
  {
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
      "L1_domain_specific": "CPG products that gamify healthy eating (e.g., streaks, challenges, rewards)",
      "L2_industry_specific": "Food/beverage brands using playfulness to drive trial and habit formation",
      "L3_cross_domain": "Pleasure activism: reframing obligation (eat healthy) as choice (enjoy health)",
      "L4_universal_principle": "Joy as strategic business tool (not just outcome, but method)"
    },
    "trend_description": "2-3 sentence summary from WGSN report",
    "wgsn_source_section": "Section title from report (e.g., 'Strategic Joy p. 12-15')",
    "extraction_confidence": 0.95
  }
]
```

## Validation Criteria

✓ All distinct trends extracted (3-6 per report)  
✓ L1-L4 ascend from concrete to universal (not redundant levels)  
✓ Lifecycle stage explicitly stated or clearly implied by WGSN  
✓ Emotional drivers include both current negative + aspirational positive  
✓ No hallucinated statistics or competitive claims

***

Stage 2: Consumer Insight Synthesis via Trend Reasoning

## Option A: Structured JSON-Based Convergence (Recommended for Phase 1)

### Architecture Philosophy

**Abandon the graph infrastructure for small-scale processing.** Instead of building a 20-node graph and navigating it with LLM traversal logic, use **transparent combinatorial enumeration** with structured JSON. The LLM's job is **semantic reasoning**, not graph navigation.

### Implementation

```json
{
  "trends_array": [
    {
      "trend_id": "uuid_1",
      "trend_name": "Strategic Joy",
      "lifecycle_stage": "EMERGING",
      "emotional_drivers": {
        "current_negative": ["dysregulated", "stressed"],
        "aspirational_positive": ["serene", "inspired"]
      },
      "abstraction_levels": {
        "L1": "CPG products that gamify healthy eating",
        "L2": "Food/beverage brands using playfulness to drive trial",
        "L3": "Pleasure activism: reframe obligation as choice",
        "L4": "Joy as strategic business tool"
      }
    },
    {
      "trend_id": "uuid_2",
      "trend_name": "Witherwill",
      "lifecycle_stage": "ACCELERATING",
      "emotional_drivers": {
        "current_negative": ["overwhelmed", "fatigued"],
        "aspirational_positive": ["carefree", "grounded"]
      },
      "abstraction_levels": {
        "L1": "Minimalist bread packaging, curated SKU sets",
        "L2": "Food brands reducing choice architecture",
        "L3": "Simplification as self-care: fewer options, lower burden",
        "L4": "Restraint as luxury"
      }
    }
  ],
  "brand_context": {
    "brand_name": "Boulangerie St-Méthode",
    "category_challenges": [
      "Bread category has 47 SKUs at average supermarket, causing decision fatigue",
      "Consumers view artisan bread as premium but intimidating"
    ],
    "current_positioning": "Traditional craft, nostalgia-driven",
    "emotional_territory_brand_owns": ["carefree", "authentic", "simple"]
  }
}
```

### Processing Logic

**Step 1: Enumerate All Possible Trend Pairs**

```python
# Transparent, non-graph-based enumeration
convergences = []

for i, trend_a in enumerate(trends):
    for trend_b in trends[i+1:]:
        # Check for shared emotional drivers
        shared_current = (
            set(trend_a["emotional_drivers"]["current_negative"]) & 
            set(trend_b["emotional_drivers"]["current_negative"])
        )
        shared_aspirational = (
            set(trend_a["emotional_drivers"]["aspirational_positive"]) & 
            set(trend_b["emotional_drivers"]["aspirational_positive"])
        )
        
        # Check for complementary lifecycle stages
        lifecycle_fit = assess_lifecycle_compatibility(
            trend_a["lifecycle_stage"], 
            trend_b["lifecycle_stage"]
        )
        
        if shared_current or shared_aspirational or lifecycle_fit:
            convergences.append({
                "trend_a_id": trend_a["trend_id"],
                "trend_b_id": trend_b["trend_id"],
                "convergence_type": classify_convergence(
                    shared_current, shared_aspirational, lifecycle_fit
                ),
                "shared_emotions": list(shared_current | shared_aspirational),
                "reasoning": f"Trends share emotions: {shared_current | shared_aspirational}"
            })
```

**Step 2: Map Convergences to Brand Challenges**

For each convergence, the LLM assesses:

- **Does this convergence address the brand's category challenge?** (Decisively: YES/MAYBE/NO)
- **Does the brand have permission to play?** (Does brand positioning overlap with trend emotional territory?)
- **What abstraction level is most relevant?** (L1=tactical execution, L3=mechanism transfer, L4=strategic principle)

This mapping is **not a graph traversal**—it's **semantic matching** between convergence patterns and brand context.

**Step 3: Generate Consumer Insights from Converged Patterns**

```json
{
  "insight_id": "uuid",
  "insight_statement": "Bread buyers overwhelmed by choice want purchasing to feel like rediscovering childhood simplicity and control",
  "convergence_pattern": {
    "primary_trend": "Witherwill (ACCELERATING)",
    "secondary_trend": "Strategic Joy (EMERGING)",
    "convergence_type": "complementary_emotions",
    "shared_emotional_drivers": ["overwhelmed", "carefree"],
    "lifecycle_combination": "ACCELERATING + EMERGING = validated opportunity + emerging hedgehog"
  },
  "brand_relevance": {
    "category_challenge_addressed": "Bread category has 47 SKUs causing decision fatigue",
    "positioning_fit": "HIGH - Brand already positioned in nostalgia/simplicity",
    "permission_to_play": "HIGH - Brand owns 'authentic, simple' emotional territory",
    "abstraction_level_applied": "L3: Simplification as self-care + Pleasure activism = Curated simplicity as joy-enabler"
  },
  "lifecycle_strategy": {
    "dominant_stage": "ACCELERATING (Witherwill primary)",
    "strategic_posture": "VALIDATE",
    "rationale": "Witherwill is ACCELERATING = proven demand signal. Fast-follower approach reduces education cost",
    "execution_timeline": "6 months"
  },
  "consumer_needs": {
    "functional_need": "Reduce bread choice from 47 SKUs to 3 curated categories (sourdough, everyday, specialty)",
    "emotional_need": "Feel confident and carefree when choosing, not paralyzed or guilty",
    "social_need": "Be perceived as discerning (knows what's good) not indecisive"
  },
  "derivation_transparency": {
    "convergence_source": "Trend enumeration (Step 1)",
    "brand_mapping_source": "Semantic matching (Step 2)",
    "insight_generation_method": "LLM synthesis from converged pattern + brand context (Step 3)"
  }
}
```

### Objective (Option A)

Navigate **enumerated convergence patterns** (not graph nodes) to discover brand-specific consumer insights through **multi-trend mapping**. This approach is intellectually honest about scale: instead of pretending 3-6 trends justify graph infrastructure, it uses **transparent combinatorial enumeration** paired with **semantic reasoning**.

### Input Schema

```json
{
  "trends_array": [...],
  "brand_context": {...},
  "convergence_patterns": [
    {
      "trend_a_id": "uuid_1",
      "trend_b_id": "uuid_2",
      "convergence_type": "complementary_emotions | shared_drivers | lifecycle_aligned",
      "shared_emotions": ["overwhelmed", "carefree"],
      "reasoning": "..."
    }
  ]
}
```

### Output Schema

```json
[
  {
    "insight_id": "uuid",
    "insight_statement": "...",
    "convergence_pattern": {
      "primary_trend": "uuid",
      "secondary_trend": "uuid",
      "convergence_type": "...",
      "shared_emotional_drivers": [...],
      "lifecycle_combination": "..."
    },
    "brand_relevance": {
      "category_challenge_addressed": "...",
      "positioning_fit": "HIGH | MEDIUM | LOW",
      "permission_to_play": "HIGH | MEDIUM | LOW",
      "abstraction_level_applied": "L1 | L2 | L3 | L4"
    },
    "lifecycle_strategy": {
      "dominant_stage": "EMERGING | ACCELERATING | PEAKING",
      "strategic_posture": "PIONEER | VALIDATE | DEFEND",
      "rationale": "...",
      "execution_timeline": "..."
    },
    "consumer_needs": {
      "functional_need": "...",
      "emotional_need": "...",
      "social_need": "..."
    },
    "derivation_transparency": {
      "convergence_source": "enumeration",
      "brand_mapping_source": "semantic_matching",
      "insight_generation_method": "LLM synthesis"
    }
  }
]
```

### Validation Criteria (Option A)

✓ Every insight combines 2+ trends (enumeration produced the convergence)  
✓ Insight is brand-specific (positioning fit and permission to play honestly assessed)  
✓ Lifecycle strategy justified (timing rationale provided)  
✓ Convergence enumeration was exhaustive (all $$\binom{n}{2}$$ pairs evaluated where n = trend count)  
✓ Functional + Emotional + Social needs specified  
✓ Derivation fully transparent (enumeration → semantic matching → synthesis)

***

## Recommendation for Phase 1

**Choose Option A (Structured JSON-Based Convergence).**

**Why**: You stated "at this stage, we aren't going to generate this large graph, later yes." Option A is **honest about your current constraints**—3-6 trends per report don't justify graph infrastructure. It delivers working insights faster, is easier to debug, and produces output that feeds directly into Stage 3.

**When to Transition to Option B**: After processing 5+ WGSN reports and accumulating 15-30 trends in your library. At that point, the graph becomes valuable for discovering convergence patterns that enumeration alone would miss.

***

Integration with Stage 3

**Both options produce identical output structure**, so Stage 3 integration is unchanged. Stage 3 receives:
- `insight_statement`: The converged opportunity
- `consumer_needs` (functional, emotional, social): Requirements for technique matching
- `lifecycle_strategy.strategic_posture`: Influences SIT/TRIZ/Doblin selection
- `brand_relevance`: Permission to play and positioning fit

***

## Key Sources

Combinatorial Creativity Theory: L1-L4 abstraction levels  
WGSN Future Consumer Methodology  
Graph-Augmented Reasoning: Phase 2+ only  
Jobs-to-be-Done Framework

Sources

Combinatorial Creativity Theory: L1-L4 abstraction levels
WGSN Future Consumer Methodology
Graph-Augmented Reasoning: Phase 2+ only
Jobs-to-be-Done Framework

Stage 3: Technique Library Matching (SIT + TRIZ + Doblin) 
Objective 
Validate consumer insights against 55 innovation patterns (SIT: 5, TRIZ: 40, Doblin: 10) to ensure insights have actionable mechanisms and defensible innovation types. 
Input Schema 
{ 
"consumer_insights": [...], // From Stage 2 
"technique_libraries": { 
"sit": [...], // 5 techniques with CPG examples 
"triz": [...], // Top 10 TRIZ principles for CPG 

} 
} 
"doblin": [...] // 10 innovation types 

Processing Logic 
1. SIT Matching: Identify which of 5 techniques address insight's core dynamic Subtraction: Remove component, force adaptation 
Task Unification: Assign new task to existing resource 
Multiplication: Copy component but change it 
Attribute Dependency: Correlate previously independent attributes 
Division: Divide and reorganize 
2. TRIZ Matching (Conditional): Only apply to technical insights 
If insight requires product performance, packaging, or supply chain innovation → Match TRIZ If insight is purely emotional/positioning → Skip TRIZ (wrong tool) 
3. Doblin Type Mapping: Identify which of 10 types innovation would activate Aim for 3+ types across Configuration/Offering/Experience categories 
Research shows 4+ types = 2x better financial performance [^7] 
4. Defensibility Assessment: 
1-2 Doblin types = LOW defensibility (easy to copy) 
3 types = MEDIUM defensibility
4+ types across categories = HIGH defensibility 
Output Schema 
[ 
{"insight_id": "from_stage_2", 
"matched_techniques": { 
"sit": { 
"primary_technique": "Task Unification", 
"application": "Assign simplification task to packaging/shelf (e.g., QR code with curated selection guide)", "cpg_example_analogy": "Like 'Good Eggs' curated selection vs Whole Foods overwhelming choice", "secondary_techniques": ["Division: Divide 47 SKUs into 3 categories"] 
},"triz": { 
"applicable": false, 
"rationale": "Insight is positioning/emotional, not technical contradiction. TRIZ not applicable." },"doblin": { 
"types_activated": [ 
{"type": "5. Product Performance", 
"category": "Offering", 
"how": "Curated SKU selection (fewer, better choices)" 
}, 
{"type": "7. Service", 
"category": "Experience", 
"how": "Shelf guidance system or QR code decision tool" 
}, 
{ 
"type": "9. Brand", 
"category": "Experience", 
"how": "Position as 'simplifying expert' vs competitor noise" } 
],"defensibility_score": "MEDIUM", 
"defensibility_rationale": "3 types activated across Offering + Experience. Adding Configuration type (e.g., Profit Model } 
},"technique_justification": "Task Unification fits because insight requires adding value (simplification) without adding cost "cpg_actionability": { 
"capability_fit": "HIGH - Brand can implement QR codes or shelf signage without new manufacturing capabilities", "permission_fit": "HIGH - Brand positioned as 'traditional expert' has credibility to curate", 
"resource_fit": "MEDIUM - Requires ~$50K for QR system + shelf redesign, within typical innovation budget" } 
} 
] 
Integration with Stage 4 
Critical Handoff: Validated techniques inform concept generation. 
What Stage 4 Needs: 
matched_techniques.sit.primary_technique + application: Concrete mechanism for concept matched_techniques.doblin.types_activated: Ensure concept activates multiple types cpg_actionability: Determines feasibility constraints for concept 
Key Sources 
SIT Framework [ 6] 5][ 
TRIZ 40 Principles [ 15] 14][ 
Doblin 10 Types [ 16] 7][
Validation Criteria 
✓ SIT technique directly addresses insight's functional/emotional need 
✓ TRIZ only applied to technical problems (not forced onto positioning) 
✓ Doblin includes 3+ types (preferably across categories) 
✓ CPG examples provided show analogous applications 
✓ Actionability assessed honestly (capability/permission/resources) 
Stage 4: Directional Concept Generation 
Objective 
Generate brand-specific directional concepts (NOT full product specs) that combine consumer insight + innovation technique + lifecycle strategy + compelling narrative. 
Input Schema 
{"validated_techniques": [...], // From Stage 3 
"enriched_brand_context": {...}, // From Stage 0 
"consumer_insights": [...] // From Stage 2 (for context) 
} 
Processing Logic 
1. Concept Formulation: Combine: 
Consumer insight (what problem/opportunity) 
Innovation mechanism (how to address it via SIT/TRIZ/Doblin) 
Lifecycle strategy (when/how to execute based on trend stage) 
Brand permission (why this brand can credibly do this) 
2. Narrative Framework: Every concept must answer: 
Customer Problem: What frustrates them today? 
Brand Solution: How does this concept solve it? 
Emotional Payoff: How will they feel? 
Proof Points: Why will it work? 
3. No-Hallucination Boundary: Explicitly state: 
What we know (trend report facts + brand context) 
What we infer (directional concepts based on patterns) 
What we don't claim (market size, competitive gaps, financial ROI) 
Output Schema
[ 
{"concept_id": "uuid", 
"concept_name": "Le Guide St-Méthode", 
"concept_tagline": "Rediscover bread joy without choice overwhelm", 
"core_insight": "Bread buyers (overwhelmed by 47 SKUs) want purchasing to feel like rediscovering childhood simplicity, not h "innovation_mechanism": { 
"primary_technique": "SIT: Task Unification", 
"how_it_works": "Assign simplification task to shelf/packaging: QR code on shelf provides curated selection guide that divi },"directional_concept_description": { 
"what": "In-aisle curated selection tool (QR code + shelf signage) that simplifies bread buying", 
"who": "Overwhelmed shoppers (typically families, time-pressed consumers) facing 47+ bread SKUs", 
"why_now": "Witherwill trend is ACCELERATING per WGSN. Proven demand for simplification (see meal kits, curated wine). Fast "why_this_brand": "Boulangerie positioned as 'traditional craft expert' has credibility to curate. Nostalgia territory alig 
},"lifecycle_strategy": { 
"trend_stage": "ACCELERATING", 
"strategic_posture": "VALIDATE", 
"execution_approach": "Fast-follower: Adapt proven curation models (Winc, Good Eggs) to bread category", "timeline": "6 months (pilot in 3 stores, measure trial/repeat, scale if validated)" 
},"narrative_framework": { 
"customer_problem": "47 bread SKUs creates decision fatigue. Shoppers spend 3+ minutes choosing bread, leave feeling overwh "brand_solution": "Le Guide St-Méthode curates 47 SKUs into 3 simple categories with expert recommendations. QR code provid "emotional_payoff": "Shoppers feel carefree (not overwhelmed) and confident (not paralyzed). Rediscover joy of trying new b "proof_points": [ 
"Wine curation (Winc) increased trial by 38%", 
"Meal kits (Blue Apron) reduced decision fatigue by simplifying recipes", 
"Trader Joe's curated SKU model drives highest revenue/sq ft in grocery" ] 
},"cpg_feasibility": { 
"capabilities_required": ["QR code system", "Shelf redesign", "Content creation (recipes/pairings)"], "estimated_investment": "$40K - $60K (QR system + shelf signage for 3-store pilot)", "go_to_market": "Retail (in-aisle activation at existing stores)", 
"success_metrics": { 
"trial_rate": "Target: 15% of shoppers scan QR in-aisle", 
"new_sku_trial": "Target: 25% of scanners try non-default bread", 
"repeat_purchase": "Target: 40% of new-SKU triers return within 2 weeks" } 
},"no_hallucination_boundary": { 
"what_we_know": "WGSN identifies Witherwill (simplification) as ACCELERATING trend. Brand positioned as traditional expert. "what_we_infer": "Directional concept (Le Guide) based on convergence of Witherwill + Strategic Joy + brand context. Analog 

] 
"what_we_dont_claim": "We do NOT claim: exact market size for curated bread, zero competitive offerings, guaranteed financi } 
} 

Integration with Stage 5 
Critical Handoff: Concepts feed into competitive intelligence search. 
What Stage 5 Needs: 
concept_name + concept_tagline: Search query construction 
innovation_mechanism.primary_technique: Identify analogous competitors using same mechanism directional_concept_description.what: Direct competitor search 
Key Sources 
Narrative structures for innovation adoption [^17] 
CPG innovation process [^18] 
No-hallucination boundary constraints [^19] 
Validation Criteria 
✓ Concept name is memorable (3-5 words, not generic) 
✓ Concept combines insight + technique + lifecycle strategy 
✓ Narrative answers: Problem / Solution / Payoff / Proof 
✓ Feasibility is CPG-realistic ($50K budget, 6-12 month timeline) 
✓ No-hallucination boundary clearly states what's known vs. inferred 
Stage 5: Competitive Intelligence Integration
Objective 
Conduct honest, search-based competitive validation to flag if similar concepts already exist, using transparency about limitations to maintain credibility. 
Input Schema 
{"directional_concepts": [...] // From Stage 4 
} 
Processing Logic 
1. Multi-Query Search: For each concept, run 3 searches: 
Direct: Same concept, same category (e.g., "curated bread selection tool bakery") 
Analogous: Same mechanism, different category (e.g., "product curation system wine") 
Competitive: Brand's competitors + innovation type (e.g., "Whole Foods bakery innovation 2024") 
2. Result Triangulation: Aggregate findings across 3 queries to identify: 
Direct competitors (exact concept match) 
Analogous competitors (mechanism transferable to brand's category) 
No evidence (absence of results ≠ absence of competition) 
3. Honesty Constraints: NEVER claim "zero competition" 
Say: "No evidence found in top 50 search results" 
Don't say: "No brand does this" 
Acknowledge: "Search-based validation has blind spots (emerging startups, private initiatives, unreported pilots)" 
4. Differentiation Angle: If competitors found, propose differentiation strategy 
Output Schema
[ 
{"concept_id": "from_stage_4", 
"competitive_validation": { 
"search_queries_executed": [ 
"curated bread selection tool bakery", 
"product curation system wine grocery", 
"Whole Foods bakery innovation 2024" 
], 
"direct_competitors_found": [], 
"analogous_competitors_found": [ 
{"competitor": "Winc", 
"category": "Wine e-commerce", 
"mechanism": "AI-driven curation based on taste preferences", 
"source": "https://winc.com", 
"transferability": "HIGH - Curation algorithm could adapt to bread preferences (flavor profile, use case, dietary needs "threat_level": "MEDIUM - If Winc or similar player enters CPG curation space" 
}, 
{"competitor": "Good Eggs", 
"category": "Curated grocery delivery", 
"mechanism": "Expert curation of SKUs to reduce choice overwhelm", 
"source": "https://goodeggs.com", 
"transferability": "HIGH - In-store version of Good Eggs' curated model", 
"threat_level": "LOW - Good Eggs is DTC, not in-store activation" } 
],"no_evidence_caveat": "Top 50 search results found no direct in-store bread curation tools. This does NOT confirm zero comp "competitive_assessment": { 
"landscape": "OPEN", 
"landscape_rationale": "No direct competitors in bread category using in-store curation. Analogous models exist (wine, gr "first_mover_opportunity": "MEDIUM-HIGH", 
"opportunity_rationale": "6-12 month window before analogous players transfer mechanism. Risk: Major retailer (Whole Food 
"differentiation_angle": "If competitors emerge: Differentiate via (1) Brand's traditional expert credibility, (2) Recipe } 
} 

] 
} 

Integration with Stage 6 
Critical Handoff: Competitive intelligence feeds into opportunity card. 
What Stage 6 Needs: 
competitive_assessment.landscape: Informs opportunity framing (first-mover vs. fast-follower vs. differentiation) analogous_competitors_found: Provides proof points ("wine curation works, bread is next") 
no_evidence_caveat: Transparency builds trust in final opportunity card 
Key Sources 
Competitive intelligence methodology [^20] 
Search-based validation limitations [^8] 
Validation Criteria 
✓ 3 queries executed per concept (direct, analogous, competitive) 
✓ Direct competitors flagged with similarity score 
✓ Analogous competitors flagged with transferability assessment 
✓ No-evidence caveat included (honesty about limitations) 
✓ All claims sourced with URLs 
Stage 6: Opportunity Card Packaging 
Objective 
Package directional concepts into retail-ready opportunity cards with: concept summary, strategic rationale, execution roadmap, success metrics, next steps. 
Input Schema 
{"directional_concepts": [...], // From Stage 4 
"competitive_validation": [...], // From Stage 5 
"consumer_insights": [...], // From Stage 2 
"validated_techniques": [...], // From Stage 3 
"enriched_brand_context": {...} // From Stage 0 } 
Processing Logic 
1. 30-Second Pitch Structure: Organize content for rapid comprehension: Headline: Concept name + tagline 
Problem: Consumer insight (1 sentence) 
Solution: Innovation mechanism (2 sentences) 
Strategy: Lifecycle-aware execution (timing + posture) 
2. Decision-Ready Artifact: Include everything executives need to approve: Strategic fit (trend convergence + brand permission) 
Competitive landscape (honest assessment) 
Execution roadmap (3-phase: validate, build, launch) 
Investment required (budget estimate + timeline) 
Success metrics (trial, repeat, velocity) 
3. Transparency Layer: No-hallucination disclosure in every card
Output Schema (Markdown Format) 
## Opportunity Card: Le Guide St-Méthode<a></a> 
**Tagline:** Rediscover bread joy without choice overwhelm 
### Strategic Fit<a></a> 
- **Consumer Insight:** Bread buyers (overwhelmed by 47 SKUs) want purchasing to feel like rediscovering childhood simplicity, no - **Trend Convergence:** Witherwill (ACCELERATING) + Strategic Joy (EMERGING) → Simplification meets joyful rediscovery - **Lifecycle Stage:** ACCELERATING 
- **Strategic Posture:** VALIDATE (fast-follower, proven demand) 
### Concept Overview<a></a> 
Le Guide St-Méthode is an in-aisle curated selection tool that simplifies bread buying through QR code + shelf signage. The syste This concept applies **SIT Task Unification** (assign simplification task to existing shelf real estate) and activates **3 Doblin 
### Innovation Mechanism<a></a> 
- **Primary Technique:** SIT Task Unification — Assign simplification task to packaging/shelf 
- **How It Works:** QR code + shelf signage curate 47 SKUs into 3 categories, provide recipes/pairings - **Defensibility:** MEDIUM (3 Doblin types across Offering + Experience) 
### Why Now?<a></a> 
Witherwill trend is ACCELERATING per WGSN (2027 forecast). Proven demand for simplification across categories (meal kits, curated 
### Why This Brand?<a></a> 
Boulangerie positioned as "traditional craft expert" has credibility to curate—consumers trust expertise. Nostalgia territory ali 
### Competitive Landscape<a></a> 
- **Direct Competitors:** None found (top 50 search results) 
- **Analogous Threats:** Winc (wine curation), Good Eggs (curated grocery) — transferability HIGH, but not yet in bread - **Differentiation Angle:** If competitors emerge: (1) Traditional expert credibility, (2) Recipe/pairing content, (3) Nostalgia 
### Execution Roadmap<a></a> 
- **Phase 1 (Months 1-3):** Pilot in 3 stores. Build QR system + shelf signage. Create 20 recipes/pairings. Measure trial rate (t - **Phase 2 (Months 4-6):** Refine based on pilot feedback. Measure new-SKU trial (target: 25% try non-default bread). Measure re - **Phase 3 (Months 7-12):** If pilot validates, scale to 30 stores. Expand content library (50+ recipes). Integrate with loyalty 
### Investment Required<a></a> 
- **Estimated Budget:** $40K - $60K for 3-store pilot (QR system, shelf redesign, content creation) - **Team:** Digital product manager, content creator, retail operations 
- **Timeline:** 6 months (pilot + validation), 12 months (scale) 
### Success Metrics<a></a> 
- **Trial Rate:** 15% of shoppers scan QR in-aisle (pilot phase) 
- **New SKU Trial:** 25% of scanners try non-default bread 
- **Repeat Purchase:** 40% of new-SKU triers return within 2 weeks 
- **Retail Velocity:** 10% increase in units/store/week (scale phase) 
### Next Steps<a></a> 
1. **Approve pilot budget** ($50K) and assign digital PM 
2. **Select 3 pilot stores** (mix of high/medium traffic) 
3. **Build QR system + content** (2 months) 
4. **Launch pilot** (Month 3), measure for 3 months 
5. **Go/no-go decision** (Month 6 based on trial/repeat metrics) 
### No-Hallucination Disclosure<a></a> 
This opportunity card is based on: 
**What we know:** WGSN identifies Witherwill (simplification) as ACCELERATING trend. Brand positioned as traditional expert. Cate **What we infer:** Directional concept (Le Guide) based on convergence of Witherwill + Strategic Joy + brand context. Analogous m **What we DON'T claim:** Exact market size for curated bread, zero competitive offerings, guaranteed financial ROI. These require 
--- 
Integration with External Systems 
Outputs feed into: 
Innovation pipeline management: Opportunity cards become pipeline entries for quarterly review 
Executive decision-making: 30-second pitch enables rapid prioritization 
Retail buyer conversations: Cards provide structured pitch for shelf space negotiation
Key Sources 
CPG innovation pipeline frameworks [^18] 
Decision artifact design [^21] 
Validation Criteria 
✓ 30-second pitch test (can explain concept in 30 seconds) 
✓ All decision inputs included (insight, strategy, roadmap, budget, metrics) 
✓ Competitive landscape honestly assessed 
✓ No-hallucination disclosure present 
✓ Next steps actionable (not vague "explore further") 
Critical Integration Points 
Stage 0 ↔ Stage 2 
Output: enriched_brand_context.json 
Consumed by: Stage 2 graph reasoning (brand node in graph) 
Why critical: Brand-specific insights require brand context. Without enrichment, Stage 2 generates generic insights. 
Stage 1 ↔ Stage 2 
Output: trend_objects_array.json 
Transformation: Graph Builder converts trends to nodes/edges 
Consumed by: Stage 2 (trend graph) 
Why critical: Graph structure enables multi-hop reasoning. Without graph, LLM can't discover convergence patterns. 
Stage 2 ↔ Stage 3 
Output: consumer_insights_array.json 
Consumed by: Stage 3 (technique matching) 
Why critical: Insights provide requirements for technique selection. Functional/Emotional/Social needs guide SIT/TRIZ/Doblin matching. 
Stage 3 ↔ Stage 4 
Output: validated_techniques.json 
Consumed by: Stage 4 (concept generation) 
Why critical: Techniques provide actionable mechanisms. Without validated techniques, concepts lack implementation specificity. 
Stage 4 ↔ Stage 5 
Output: directional_concepts.json 
Consumed by: Stage 5 (competitive search) 
Why critical: Concepts trigger search queries. Without concepts, no competitive validation possible. 
All Stages ↔ Stage 6 
Output: All previous stage outputs 
Consumed by: Stage 6 (packaging) 
Why critical: Opportunity cards require full context for completeness. Missing any stage = incomplete card. Validation Framework
Stage-Level Validation 
Each stage has explicit validation criteria (see individual stage sections). Validation must occur before proceeding to next stage. Validation Process: 
1. Output Schema Check: Does output match expected JSON schema? 
2. Content Quality Check: Does output meet validation criteria? 
3. Integration Test: Does output successfully feed into next stage? 
End-to-End Validation 
After Stage 6, validate complete pipeline: 
Traceability: Can you trace opportunity card back to source trends? 
Coherence: Do all stages tell consistent story? 
Actionability: Can CPG team act on opportunity card? 
Feedback Loop 
Short-term (Weekly): Inspect Stage 1-2 outputs, refine prompts 
Medium-term (Monthly): Measure Stage 3-4 quality (how many concepts pass feasibility check?) Long-term (Quarterly): Track which opportunity cards get greenlit by CPG teams 
Reference Sources by Stage 
Stage 0: Brand Profile Enrichment 
[^8] Perplexity AI multi-source search capabilities 
[^9] CPG market intelligence and category analysis 
[^10] Brand positioning frameworks 
Stage 1: Multi-Trend Decomposition 
[^1] Boden, M.A. (2004). The Creative Mind: Myths and Mechanisms 
[^2] Gu et al. (2024). LLMs Can Realize Combinatorial Creativity 
[^11] WGSN Future Consumer Methodology 
Stage 2: Consumer Insight Synthesis 
[^3] KG-RAR: Graph-Augmented Reasoning framework 
[^4] GIVE: Structured Reasoning with Knowledge Graphs 
[^12] Jobs-to-be-Done Framework (Christensen et al.) 
[^13] Product Lifecycle Management research 
Stage 3: Technique Library Matching 
[^5] Goldenberg & Mazursky: SIT Framework 
[^6] Systematic Inventive Thinking research 
[^7] Doblin: Ten Types of Innovation 
[^14] Altshuller: TRIZ Theory 
[^15] 40 Inventive Principles for process improvement 
[^16] Doblin innovation defensibility research
Stage 4: Directional Concept Generation 
[^17] Narrative structures for innovation adoption 
[^18] CPG innovation process frameworks 
[^19] LLM hallucination constraints research 
Stage 5: Competitive Intelligence 
[^20] Competitive intelligence methodology 
[^8] Search-based validation (Perplexity) 
Stage 6: Opportunity Card Packaging 
[^18] CPG innovation pipeline frameworks 
[^21] Decision artifact design principles 
Implementation Readiness 
Ready to Build 
✅ Stage 0: Prompt template complete 
✅ Stage 1: Prompt template + output schema complete 
✅ Graph Builder: Logic defined, ready to code 
✅ Stage 2: Prompt template + graph reasoning logic complete ✅ Stage 3: Technique libraries populated, matching logic defined ✅ Stage 4: Prompt template + narrative framework complete 
✅ Stage 5: Search methodology + honesty constraints defined ✅ Stage 6: Markdown template complete 
Requires Testing 
⚠️ All stages: Prompts written but untested with real WGSN data ⚠️ Stage 1: L1-L4 abstraction quality unknown until tested 
⚠️ Stage 2: Graph reasoning effectiveness unknown until tested ⚠️ Stage 3: Technique matching accuracy unknown until tested ⚠️ End-to-end: Complete pipeline untested 
Next Steps 
1. Test Stage 1 with WGSN Emotions Report → Extract trends, validate L1-L4 2. Build Graph Builder from Stage 1 output → Validate graph structure 3. Test Stage 2 with graph + brand context → Validate convergence discovery 4. Populate libraries (SIT/TRIZ/Doblin) → Test Stage 3 matching 5. Run end-to-end with 3 brands → Generate opportunity cards, validate quality
Document Version: 1.0 
Last Updated: November 15, 2025 
Status: Design Complete - Ready for Implementation 
Recommended Use: Reference guide for building each stage sequentially ⁂ 
