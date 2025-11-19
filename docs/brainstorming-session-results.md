# Brainstorming Session Results

**Session Date:** November 14, 2025
**Facilitator:** Business Analyst (Mary)
**Participant:** Philippe Beliveau

---

## Executive Summary

**Topic:** Optimal approach to design the extraction pipeline framework - objectives-first vs input/output-first, or anything else

**Session Goals:** Broad exploration of framework design approaches for the Innovation Intelligence System, focusing on extracting value from Mintel/WGSN trend reports for CPG innovation teams

**Techniques Used:** First Principles Thinking (45 minutes)

**Total Ideas Generated:** 15+ key insights and framework components

### Key Themes Identified:
- SIT (Systematic Inventive Thinking) provides superior framework to TRIZ for CPG/emotional innovation
- Two-input extraction model: WGSN trend reports + brand profiles
- Five-stage pipeline architecture for systematic value extraction
- LLM-based reasoning with strict no-hallucination boundaries
- Structural mechanisms = SIT techniques + application context

---

## Technique Sessions

### First Principles Thinking - 45 minutes

**Description:** Breaking down the pipeline design to fundamental requirements by questioning what the system MUST accomplish and working upward from irreducible components.

#### Ideas Generated:

1. **The Core Transformation**: Pipeline extracts "Trend → Mechanism → Narrative" engine that shows CPG teams the hidden value in their $50K Mintel reports

2. **SIT Framework Superiority**: Replace TRIZ with SIT (Systematic Inventive Thinking) because:
   - 5 simple techniques vs 40 TRIZ principles
   - Applicable to products, services, business models (not just technical problems)
   - Perfect mapping to CPG marketing/positioning innovations

3. **Two-Input Extraction Model**:
   - Input 1: WGSN/Mintel trend reports (general emotional trends)
   - Input 2: Brand profile (4 required fields: name, industry, geography, product portfolio)

4. **Five-Stage Pipeline Architecture**:
   - Stage 1: Trend Decomposition (reusable trend objects)
   - Stage 2: Consumer Insight Synthesis (industry-specific wants)
   - Stage 3: SIT Technique Matching (pattern matching)
   - Stage 4: Initiative Generation (directional concept)
   - Stage 5: Packaging (opportunity card)

5. **No-Hallucination Boundaries**:
   - Never fabricate market statistics (TAM, share, growth rates)
   - Never invent competitive landscape details
   - Never generate financial projections or business plans
   - Stop at directional concept + product idea

6. **Structural Mechanism Definition**: SIT Technique + Application Context
   - Example: "Task Unification: Assign decision-support to existing customer touchpoints"
   - Transferable, domain-agnostic, storable in latent space database

7. **LLM-Based Reasoning**: All extraction via LLM prompting (NO heuristics, NO templates)

8. **Minimum Viable Brand Profile**: 4 required fields only
   - Company name
   - Industry
   - Geography
   - Product portfolio description

#### Insights Discovered:

- **Mintel's Process Reveals the Gap**: Diana Smith's video showed Mintel spends "the brunt of time" manually data mining for insights. This is exactly what the pipeline automates.

- **TRIZ Doesn't Map to Emotional/Positioning Problems**: Technical contradiction resolution (Strength vs Weight) doesn't apply to "Health vs Joy" positioning challenges in CPG.

- **SIT Techniques Map Perfectly to Boulangerie Example**:
  - "Redécouvre le plaisir du pain" = Attribute Dependency (correlate health with pleasure)
  - "Le Guide St-Méthode" = Task Unification (assign simplification to shelf/packaging)
  - "QR Transparency Platform" = Task Unification (assign proof to packaging)

- **The Extraction is More Complex Than Expected**: WGSN says "Witherwill = longing to be free from responsibility" (general). Pipeline must infer "overwhelmed by bread choices" (specific). This is heavy LLM reasoning, not simple extraction.

- **Brand Context from Perplexity + Manual Fields**: Perplexity searches provide category context (SKU proliferation, market trends). Manual fields provide brand-specific data (product count, positioning).

- **Competitive Gap Analysis is Out of Scope**: We cannot reliably say "NO brand does X" without real-time competitive intelligence we don't have. Remove this from pipeline.

#### Notable Connections:

- **Combinatorial Creativity Paper → SIT Mechanisms**: The "structural mechanisms" concept from combinatorial creativity maps to SIT techniques as decomposable, recombinable innovation building blocks

- **Amabile's Componential Theory → No-Hallucination Boundary**: Domain-relevant skills (understanding brand constraints) are critical inputs. LLM shouldn't fabricate market expertise.

- **Mintel's Data Mining → Pipeline Stage 2-3**: Their manual process of "looking for gold in demographics" is exactly what Stages 2-3 automate: synthesizing general trends into specific consumer insights

- **WGSN Emotions Report Structure → Stage 1 Output**: The report's emotional driver breakdown (dysregulated/stressed/bored → included/serene/inspired) provides template for structured trend objects

---

## Idea Categorization

### Immediate Opportunities
*Ideas ready to implement now*

1. **Five-Stage Pipeline Architecture**
   - Description: Structure extraction pipeline with clear stage boundaries: (1) Trend Decomposition, (2) Consumer Insight Synthesis, (3) SIT Technique Matching, (4) Initiative Generation, (5) Packaging
   - Why immediate: Well-defined, leverages existing LLM capabilities, aligns with project constraints
   - Resources needed: LLM prompts for each stage, JSON schemas for inter-stage data

2. **SIT Framework Integration**
   - Description: Replace TRIZ with SIT (5 techniques: Subtraction, Task Unification, Multiplication, Attribute Dependency, Division) for CPG innovation
   - Why immediate: Psychology research already documented, clear mapping to Boulangerie examples, simpler than TRIZ
   - Resources needed: SIT technique library with CPG examples, pattern matching prompts

3. **Minimum Viable Brand Profile (4 Fields)**
   - Description: Start with simplest required inputs: company name, industry, geography, product portfolio
   - Why immediate: Reduces friction, testable with existing brand profiles (Decathlon, Lactalis), expandable later
   - Resources needed: Brand profile schema, Perplexity integration for enrichment

### Future Innovations
*Ideas requiring development/research*

1. **Latent Space Ideation Engine**
   - Description: Populate database with SIT mechanisms from extraction pipeline to enable novel idea generation through combinatorial recombination
   - Development needed: Database schema for structural mechanisms, recombination algorithms, novelty scoring

2. **Multi-Brand Cross-Pollination**
   - Description: Extract mechanisms from one industry (bread) and apply to another (sporting goods, dairy) using latent space patterns
   - Development needed: Industry-agnostic abstraction layer, transfer learning validation
   
3. **Lifecycle-Aware Strategic Positioning**
   - Description: Integrate lifecycle stage (EMERGING/ACCELERATING/PEAKING) into initiative recommendations (PIONEER vs VALIDATE vs DEFEND)
   - Development needed: Strategic framework integration, timing-based scoring
   - Timeline estimate: 2-3 months (Wants-Needs-Engine-v2.md already has logic)

### Moonshots
*Ambitious, transformative concepts*

1. **Automated Competitive Intelligence Layer**
   - Description: Real-time competitive gap analysis via web scraping, news monitoring, product launch databases to validate "NO brand does X" claims
   - Transformative potential: Eliminates major gap in current pipeline (competitive landscape), provides defensibility scores
   - Challenges to overcome: Data access, hallucination risk, real-time infrastructure

2. **Multi-Report Synthesis Engine**
   - Description: Process multiple WGSN/Mintel reports simultaneously to identify trend convergence and compound opportunities
   - Transformative potential: "Strategic Joy + Witherwill = X" insights that single-report analysis misses
   - Challenges to overcome: Cross-report reasoning complexity, computational cost, insight validation

### Insights & Learnings
*Key realizations from the session*

- **Framework selection is critical**: Forcing TRIZ onto CPG emotional problems was a dead-end. SIT's simplicity and business model applicability is the breakthrough.

- **Constraints enable creativity**: The "no hallucination" boundary forced clearer thinking about what the pipeline CAN vs CANNOT do. Stopping at directional concepts (not business plans) is the right scope.

- **Two inputs are necessary**: WGSN alone can't generate brand-specific insights. Brand profile provides grounding in reality. This two-input model is fundamental.

- **Stage separation enables reuse**: Trend Decomposition (Stage 1) runs once per report and serves ALL brands. This architectural decision has major efficiency implications.

- **LLM reasoning is the engine**: Rejecting heuristics/templates in favor of pure LLM prompting aligns with the project's AI-native approach. The challenge is prompt engineering, not rules engineering.

---

## Action Planning

### Top 3 Priority Ideas

#### #1 Priority: Define Stage-by-Stage LLM Prompts

- **Rationale**: The five-stage architecture is agreed upon. Next bottleneck is designing the LLM prompts that perform each transformation (trend → insight → SIT → initiative).

- **Next steps**:
  1. Draft Stage 1 prompt (WGSN PDF → structured trend JSON)
  2. Draft Stage 2 prompt (trend + brand profile → consumer insight)
  3. Test with actual WGSN Emotions Report + Boulangerie profile
  4. Iterate based on output quality

- **Resources needed**:
  - WGSN Emotions Report (already have)
  - Brand profile examples (create for Decathlon, Lactalis, Boulangerie)
  - JSON schemas for each stage output

- **Timeline**: 1-2 weeks

#### #2 Priority: Build SIT Technique Reference Library

- **Rationale**: Stage 3 (SIT Technique Matching) requires comprehensive examples of each technique applied to CPG/service contexts. Current psychology research provides theory, need practical application patterns.

- **Next steps**:
  1. Extract all SIT examples from `sit-systematic-inventive-thinking.md`
  2. Add CPG-specific examples (Boulangerie initiatives + others)
  3. Create pattern matching guide for LLM
  4. Document transferable mechanism format

- **Resources needed**:
  - SIT research document (already have)
  - Additional CPG innovation case studies
  - Combinatorial creativity framework integration

- **Timeline**: 1 week

#### #3 Priority: Validate No-Hallucination Boundaries with Test Outputs

- **Rationale**: Critical to prove the pipeline doesn't fabricate statistics. Need to test edge cases where LLM might be tempted to invent data.

- **Next steps**:
  1. Run extraction with incomplete brand profiles (only 2 of 4 fields)
  2. Check for fabricated TAM, market share, growth rate claims
  3. Test with ambiguous trends (how does LLM handle uncertainty?)
  4. Document failure modes and add guardrails

- **Resources needed**:
  - Test suite of edge case inputs
  - Output validation criteria
  - Red team prompting to find hallucination vulnerabilities

- **Timeline**: 1 week (parallel with #1 and #2)

---

## Reflection & Follow-up

### What Worked Well

- **Starting with objectives-first approach**: Clarified that the pipeline's goal is "show CPG teams the hidden value in their reports" - this anchored all subsequent decisions

- **Challenging assumptions with research**: Reading SIT paper revealed TRIZ was wrong framework. Challenging the approach led to breakthrough.

- **Using real example (Boulangerie)**: Grounding discussion in actual output (opportunity card) made abstract concepts concrete

- **Setting hard boundaries**: "No hallucination" constraint forced clearer thinking about scope and feasibility

- **Iterative questioning**: Each Q&A refined understanding - from vague "structural mechanisms" to precise "SIT technique + context"

### Areas for Further Exploration

- **Stage 1 Output Format**: What's the optimal JSON schema for structured trends? How much detail to extract vs leave for Stage 2?

- **Brand Profile Enrichment**: Beyond 4 required fields, what optional fields unlock higher-quality initiatives? (Distribution channels? Current positioning?)

- **Multi-Trend Synthesis**: How to handle reports with 3-6 trends? Generate initiatives for each separately or find convergence opportunities?

- **Validation Metrics**: How to score initiative quality? Novelty, feasibility, brand-fit - what's the rubric?

- **Perplexity Integration**: Exactly what queries to run for brand context enrichment? How to avoid hallucinated competitive claims?

### Recommended Follow-up Techniques

- **Time Shifting**: "How would you design this pipeline in 1995 (pre-LLM)? In 2030 (AGI)?" - might reveal architectural insights

- **Assumption Reversal**: "What if we started with initiatives and worked backward to trends?" - could expose gaps in current flow

- **SCAMPER**: Apply to each pipeline stage - Substitute/Combine/Adapt/Modify/Put to other use/Eliminate/Reverse

### Questions That Emerged

- How do we handle trends that don't cleanly map to any SIT technique? Force-fit or acknowledge gap?

- What if brand profile lacks industry context? (e.g., "Tech startup" - which industry? Which category?)

- Should Stage 5 (Packaging) include scoring/prioritization, or just formatting?

- How to version-control trend objects from Stage 1 as WGSN updates forecasts?

- Can we extract lifecycle stage reliably from WGSN reports, or does that require manual input?

- What happens when Perplexity search returns conflicting information about brand/category?

### Next Session Planning

- **Suggested topics**:
  - Prompt engineering workshop for Stage 1-5
  - Building the SIT technique library with CPG examples
  - Defining the brand profile schema + enrichment logic
  - Testing pipeline with multiple brand profiles (Decathlon, Lactalis, Colombia, McCormick)

- **Recommended timeframe**: Within 1 week to maintain momentum

- **Preparation needed**:
  - Create 3-4 sample brand profiles
  - Draft initial Stage 1 prompt
  - Compile SIT CPG examples
  - Set up test environment with WGSN report

---

*Session facilitated using the BMAD-METHOD™ brainstorming framework*
