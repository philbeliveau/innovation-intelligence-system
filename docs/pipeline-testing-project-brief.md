# Project Brief: Innovation Intelligence Pipeline Testing System

**Version:** 1.0
**Date:** 2025-10-03
**Author:** Product Management
**Status:** Ready for PRD Development

---

## Executive Summary

Build and validate an automated **Innovation Intelligence Pipeline** that transforms market signals (case studies, trend reports, spotted innovations) into 5-10 brand-specific, actionable innovation opportunities. The pipeline will be tested across 4 different CPG/retail brands (Lactalis Canada, McCormick USA, Columbia, Decathlon) with 5 diverse input sources to validate the core business hypothesis: can we systematically convert raw innovation signals into high-value, contextually relevant opportunities that innovation teams will pay for?

**Expected Output:** 100-200 opportunity cards across 20 test scenarios to validate pipeline quality, speed, relevance, and differentiation.

---

## Problem Statement

### Current State
The Innovation Intelligence System business concept proposes delivering "freshly baked" innovation opportunities to CPG companies. However, the core value proposition remains **unvalidated**:

- **Unclear problem definition:** Is the real constraint volume (not enough ideas), quality (too many bad ideas), speed (too slow), translation (can't contextualize), or conviction (can't get buy-in)?
- **Unproven transformation capability:** No evidence that we can systematically convert generic market signals into brand-specific actionable opportunities
- **Unknown output quality:** Will 5-10 ideas per brand be genuinely valuable, or will quality degrade after the first 2-3?
- **Uncertain differentiation:** Will the same input (e.g., "Savannah Bananas") generate meaningfully different opportunities for dairy vs. spices vs. outdoor gear?

### Impact
Without a validated pipeline, the business cannot:
- Prove value proposition to potential customers
- Determine defensible moat vs. competitors or internal solutions
- Establish pricing based on actual output quality
- Identify what data sources and processing are truly necessary

### Why Now
The business is in early validation phase. Building this testing pipeline enables rapid hypothesis validation before significant infrastructure investment.

---

## Proposed Solution

### Core Concept
Build a **5-stage automated pipeline** that processes innovation inputs through systematic analysis to generate brand-specific opportunity cards:

1. **Stage 1: Input Processing** - Content review, inspiration identification, research
2. **Stage 2: Signal Amplification** - Social media pulse, trend extraction
3. **Stage 3: General Translation** - Universal lessons and principles (brand-agnostic)
4. **Stage 4: Brand Contextualization** - Deep brand research, customization
5. **Stage 5: Opportunity Generation** - 5-10 actionable opportunities + follow-up prompts

### Key Differentiators
- **Systematic & Repeatable:** Not ad-hoc analysis, but a testable, documented process
- **Multi-stage Validation:** Each stage has clear inputs/outputs for quality control
- **Brand Contextualization:** Generic insights transformed into brand-specific actions
- **Quantifiable Testing:** 20 test runs (5 inputs × 4 brands) enable statistical validation

### Why This Will Succeed
- Leverages existing BMAD agent orchestration framework
- Uses proven innovation methodologies (TRIZ, SIT, biomimicry) from research documentation
- Applies SPECTRE validation framework for quality assurance
- Creates measurable outputs for business case validation

---

## Target Users

### Primary User Segment: Internal Product Team
**Profile:**
- Product manager, innovation strategist, business analyst validating Innovation Intelligence System concept
- Needs to prove/disprove core business hypothesis before customer acquisition
- Currently operating with assumptions, needs empirical evidence

**Current Workflow:**
- Manual prompting through ChatGPT/Claude with inconsistent results
- Re-typing similar prompts for different brands/inputs
- No systematic way to compare outputs or measure quality

**Needs:**
- Automated, repeatable pipeline execution
- Structured output format (opportunity cards)
- Ability to compare results across brands and input types
- Clear quality metrics and validation criteria

**Goals:**
- Validate that transformation from signal → opportunity actually works
- Determine if output quality justifies proposed pricing ($149-$1,500/month)
- Identify pipeline bottlenecks and failure modes
- Build evidence for investor/customer conversations

### Secondary User Segment: Future PM/Development Team
**Profile:**
- Product manager or developer who will build production Innovation Intelligence System
- Needs clear requirements for productionizing the validated pipeline

**Needs:**
- Complete documentation of pipeline stages and prompting strategies
- Test results showing what works/doesn't work
- User stories for building production version
- Understanding of required data sources and integrations

---

## Goals & Success Metrics

### Business Objectives
- **Hypothesis Validation:** Determine if automated pipeline can generate genuinely valuable brand-specific opportunities (binary: proceed or pivot)
- **Quality Baseline:** Establish minimum quality threshold for "actionable opportunity" that would justify customer payment
- **Differentiation Proof:** Demonstrate that same input generates meaningfully different outputs across brands (validates customization value)
- **Speed Benchmark:** Measure pipeline execution time to determine if "daily opportunities" tier is feasible

### User Success Metrics
- **Completion Rate:** Successfully execute all 20 test scenarios (5 inputs × 4 brands) without pipeline failures
- **Output Consistency:** Generate 5-10 opportunities per test run with consistent format/structure
- **Time to Results:** Complete single test run (1 input + 1 brand) in <30 minutes of active work
- **Repeatability:** Re-run same test scenario and get comparable quality outputs

### Key Performance Indicators (KPIs)

| KPI | Definition | Target |
|-----|------------|--------|
| **Pipeline Success Rate** | % of test runs that complete all 5 stages without errors | 95%+ |
| **Opportunity Quality Score** | Avg. rating (1-5) across novelty, actionability, relevance, specificity | 3.5+ |
| **Brand Differentiation Index** | % of opportunities that are unique per brand for same input | 70%+ |
| **Execution Speed** | Average time to complete 1 test run (all 5 stages) | <30 min |
| **Output Volume Consistency** | % of test runs generating 5-10 opportunities (not more/less) | 90%+ |

---

## MVP Scope

### Core Features (Must Have)

1. **Brand Context Profile System**
   - Create structured profiles for 4 test brands (Lactalis, McCormick, Columbia, Decathlon)
   - Include: positioning, portfolio, target customers, recent innovations, strategic priorities
   - Format: Reusable data files that pipeline can ingest

2. **Input Processing Module (Stages 1-3)**
   - Ingest 5 different input types (case study PDFs, trend reports, spotted innovations)
   - Execute prompting strategy for content review, research, social pulse, trend extraction
   - Output: Brand-agnostic universal insights and lessons
   - Must handle PDF content extraction and structured summarization

3. **Brand Contextualization Module (Stage 4)**
   - Load brand context profile
   - Execute prompting strategy for brand research and insight customization
   - Output: Brand-specific strategic insights ready for opportunity generation

4. **Opportunity Generation Module (Stage 5)**
   - Generate 5-10 distinct, actionable opportunities per test run
   - Create visual opportunity cards with descriptions
   - Generate follow-up prompts for further development
   - Output: Structured opportunity card format (markdown or similar)

5. **Testing Framework**
   - Ability to execute single test run (1 input + 1 brand)
   - Ability to batch execute multiple test runs
   - Output storage and organization (20 test scenarios)
   - Basic logging to track execution flow and errors

6. **Quality Validation System**
   - Manual review checklist for opportunity quality assessment
   - Scoring rubric for: novelty, actionability, relevance, specificity
   - Comparison framework for evaluating differentiation across brands

### Out of Scope for MVP
- Automated quality scoring (manual review acceptable for 100-200 opportunities)
- Real-time data source integration (APIs, web scraping)
- User interface or dashboard (command-line execution acceptable)
- Multi-user support or collaboration features
- Production-grade error handling and monitoring
- Automated visual generation (placeholder images or manual selection acceptable)
- Integration with actual client systems or CRMs

### MVP Success Criteria
**The MVP is successful if:**
1. All 20 test scenarios execute successfully and generate 100-200 total opportunity cards
2. Manual quality review shows ≥70% of opportunities meet "actionable and brand-specific" threshold
3. Side-by-side comparison shows clear differentiation between brands for same input
4. Pipeline execution is fast enough to make "daily opportunities" tier plausible
5. Process documentation is sufficient for another PM to build user stories for productionization

**The MVP fails if:**
- Pipeline cannot consistently generate 5-10 ideas (gets stuck, produces 1-2, or produces generic lists)
- Opportunities are indistinguishable between brands (proves contextualization doesn't work)
- Quality degrades significantly after first 2-3 ideas per run
- Execution time makes scaled production infeasible

---

## Post-MVP Vision

### Phase 2 Features (If MVP Validates)
- **Automated Quality Scoring:** ML model or structured rubric to score opportunities without manual review
- **Expanded Brand Library:** Add 10-20 additional brands across different industries
- **Real-time Data Integration:** Live trend report APIs, social media monitoring, patent databases
- **Batch Processing UI:** Simple web interface for managing test runs and reviewing outputs
- **A/B Testing Framework:** Test different prompting strategies and compare results

### Long-term Vision (12-24 Months)
- **Production Intelligence Engine:** Fully automated system generating opportunities on daily/weekly cadence
- **Customer-facing Platform:** White-labeled delivery system for enterprise clients
- **Feedback Loop System:** Capture client reactions to opportunities to improve future generation
- **Elicitation Integration:** Connect to optional guided conversation layer for opportunity refinement

### Expansion Opportunities
- **Industry Specialization:** Vertical-specific pipelines (CPG, retail, tech, healthcare)
- **Custom Data Sources:** Client-specific data integration (proprietary research, internal data)
- **Competitive Intelligence:** Dedicated competitor monitoring and response recommendations
- **Strategic Planning:** Long-range trend synthesis for annual planning cycles

---

## Technical Considerations

### Platform Requirements
- **Execution Environment:** Claude Code CLI (local development)
- **Data Storage:** Local file system (markdown, YAML, JSON)
- **Document Processing:** PDF parsing, markdown generation
- **Performance:** Process single test run in <30 minutes (including LLM API calls)

### Technology Preferences

**Pipeline Orchestration:**
- **Framework:** BMAD Core agent orchestration system (already in repository)
- **Agent Types:** Leverage existing innovation intelligence agents (Pattern Hunter, Market Psychologist, Biomimicry Expert, etc.)
- **Task Structure:** Create BMAD tasks for each pipeline stage (5 tasks)
- **Templates:** YAML templates for brand profiles, opportunity cards, output formats

**Data Management:**
- **Input Storage:** `/data/test-inputs/` directory with PDF/markdown files
- **Brand Profiles:** `/data/brand-profiles/` directory with YAML profile files
- **Output Storage:** `/data/test-outputs/{test-id}/` directory structure
- **Results:** Structured markdown files with frontmatter metadata

**Prompting System:**
- **Prompt Templates:** Markdown files with variable substitution
- **Multi-stage Prompting:** Chain prompts across pipeline stages with context preservation
- **LLM Provider:** Claude API (Sonnet 4.5) via existing Claude Code integration

### Architecture Considerations

**Repository Structure:**
- Monorepo approach (everything in innovation-intelligence-system)
- Clear separation of: test data, brand profiles, pipeline code, test outputs, documentation

**Pipeline Execution Model:**
- Sequential stage execution (Stage 1 → 2 → 3 → 4 → 5)
- Stages 1-3 execute once per input (brand-agnostic)
- Stages 4-5 execute per brand (4× per input)
- Intermediate outputs saved between stages for debugging

**Testing Strategy:**
- Manual execution initially (command-line driven)
- Each stage independently testable
- Integration test: Full pipeline run (1 input + 1 brand)
- Batch test: All 20 scenarios in sequence

**Quality Assurance:**
- Stage output validation (schema/format checking)
- Manual quality review with scoring rubric
- Version control all outputs for comparison across iterations

---

## Constraints & Assumptions

### Constraints

**Budget:**
- No additional tooling costs (use existing Claude Code, BMAD framework, Claude API access)
- LLM API costs for 20 test runs (estimated <$50 total at current pricing)

**Timeline:**
- MVP development and testing: 2-3 weeks
- Single developer/PM (part-time availability)

**Resources:**
- Solo developer with PM support
- No design resources (basic markdown outputs acceptable)
- No DevOps/infrastructure support (local execution only)

**Technical:**
- Limited to Claude Code capabilities (no custom backend services)
- PDF parsing must work with variety of document formats
- No access to proprietary data sources (public information only for brand profiles)

### Key Assumptions

- **Input Quality:** The 5 selected inspiration sources contain sufficient substance for analysis (not all inputs will be equally rich)
- **Brand Data Availability:** Sufficient public information exists for the 4 test brands to create meaningful profiles
- **LLM Capability:** Claude Sonnet 4.5 can handle multi-stage reasoning and maintain context across pipeline stages
- **Manual Review Feasibility:** One person can meaningfully review and score 100-200 opportunity cards in reasonable time
- **Prompting Consistency:** Same prompting strategy will work across different input types and brands (may need adjustment)
- **BMAD Framework Fit:** Existing agent system can be adapted for this pipeline without major modifications

---

## Risks & Open Questions

### Key Risks

1. **Quality Degradation Risk:** Pipeline may consistently produce only 2-3 high-quality ideas, then "filler" to reach 5-10 target
   - *Impact:* Invalidates volume-based pricing tiers
   - *Mitigation:* Test with quality thresholds, accept lower volume if quality maintained

2. **Contextualization Failure Risk:** Brand-specific customization may be superficial (just swapping brand names, not meaningful adaptation)
   - *Impact:* Destroys value proposition vs. generic trend reports
   - *Mitigation:* Deep brand profile development, explicit differentiation scoring

3. **Input Dependency Risk:** Pipeline may work well with rich case studies but fail with sparse spotted innovations
   - *Impact:* Limits viable input types for production system
   - *Mitigation:* Deliberately include variety in 5 test inputs

4. **Prompt Brittleness Risk:** Small changes in prompting or input format may cause unpredictable output quality
   - *Impact:* Production system unreliable, high maintenance cost
   - *Mitigation:* Document prompt engineering decisions, version control all prompts

5. **Execution Speed Risk:** Pipeline may require 2-3 hours per test run, making daily cadence infeasible
   - *Impact:* Forces lower-frequency (weekly/monthly) delivery tiers
   - *Mitigation:* Optimize prompts, explore parallel processing where possible

### Open Questions

1. **Opportunity Format:** What level of detail makes an opportunity "actionable"? (1 paragraph? 1 page? Specific format requirements?)
2. **Visual Requirements:** What constitutes acceptable "visuals" for opportunity cards? (AI-generated images? Stock photos? Conceptual diagrams?)
3. **Follow-up Prompt Value:** Will users actually use follow-up prompts, or are opportunity cards standalone deliverable?
4. **Brand Selection Validation:** Are Lactalis/McCormick/Columbia/Decathlon representative of target market, or too diverse?
5. **Input Source Completeness:** Are 5 input sources sufficient to test pipeline robustness, or need 10-15?
6. **Quality Scoring Subjectivity:** How do we handle subjectivity in manual quality review? (Inter-rater reliability?)
7. **Production Architecture:** If MVP validates, what's the leap to production-grade system? (Re-build vs. refactor?)

### Areas Needing Further Research

- **Competitive Analysis:** What do existing innovation intelligence tools (TrendWatching, WGSN, Springwise) actually deliver? Format, frequency, depth?
- **Customer Interview Validation:** Would any of the 4 test brands actually pay for the generated opportunities? (Need real customer feedback)
- **Data Source Requirements:** What data inputs are must-haves vs. nice-to-haves for production system?
- **Prompt Engineering Best Practices:** Are there established patterns for multi-stage LLM pipelines in similar domains?
- **Automation Feasibility:** Which pipeline stages are automatable vs. require human judgment in production?

---

## Appendices

### A. Test Input Sources

1. **Case Study:** The Savannah Bananas (baseball team reimagining fan experience)
2. **Trend Report:** Mintel - The Rise of Premium Fast Food
3. **Combined Trend Reports:** Mintel 2025 Non-Alcoholic Beverage Trends (Thailand) + TrendWatching FastForward Sacred Sync
4. **Spotted Innovation:** Mars Petcare "Sexiest Cat Dad" campaign with People Magazine
5. **Spotted Innovation:** Ad-generating QR codes in garments for resale

### B. Test Brand Profiles (To Be Created)

1. **Lactalis Canada** - Dairy products (milk, cheese, yogurt)
2. **McCormick USA** - Condiments and spices
3. **Columbia Sportswear** - Outdoor gear and apparel
4. **Decathlon** - Sporting goods retail

### C. Reference Documents

- **Pipeline Flow Diagram:** `/pipeline-flow-diagram.md` (Mermaid diagram of complete system)
- **Innovation Intelligence Research:** `/documentation/research/` (24 documents, 60K+ words)
- **BMAD Framework:** `/.bmad-core/` (Agent system, tasks, templates)
- **SPECTRE Validation Framework:** `/documentation/psychology-framework/`
- **Project Instructions:** `/CLAUDE.md`

### D. Related Project Context

This testing pipeline is a validation tool for the broader **Innovation Intelligence System** business concept described in `/CLAUDE.md`. The parent project explores whether an AI-driven intelligence system could transform how organizations discover and validate breakthrough innovations. This MVP focuses specifically on validating the core transformation capability (signal → opportunity) before investing in the full intelligence architecture.

---

## Next Steps

### Immediate Actions

1. **Review & Refine Brief:** Validate assumptions, clarify open questions, confirm scope with stakeholders
2. **Create Brand Profiles:** Research and document 4 test brand profiles (Lactalis, McCormick, Columbia, Decathlon)
3. **Organize Test Inputs:** Collect and structure the 5 inspiration source documents in accessible format
4. **Initiate PRD Development:** Hand off to PM for detailed requirements and user story creation
5. **Define Quality Rubric:** Create scoring framework for evaluating opportunity quality before pipeline runs

### PM Handoff

**To the Product Manager:**

This Project Brief provides complete context for the **Innovation Intelligence Pipeline Testing System**. Your next step is to create a comprehensive **Product Requirements Document (PRD)** with:

- **Detailed functional requirements** for each pipeline stage (5 stages)
- **Data models** for brand profiles, opportunity cards, test scenarios
- **User stories and acceptance criteria** for development
- **Technical specifications** for BMAD task integration
- **Quality assurance procedures** for output validation

**Recommended approach:**
1. Use the BMAD PM agent's `*create-prd` command with this brief as input
2. Work through each section collaboratively using the elicitation workflow
3. Pay special attention to Epic sequencing (likely 3-4 epics: Setup/Foundation, Pipeline Stages 1-3, Stages 4-5, Testing & Validation)
4. Ensure user stories are sized for AI agent execution (2-4 hour completion time)

**Critical success factors for the PRD:**
- Clear acceptance criteria that enable validation of the 5 KPIs defined above
- Well-structured data models that make brand profiles reusable and extensible
- Testable requirements that prove/disprove the business hypothesis
- Documentation standards that enable future productionization

**Questions for PM:**
- Should pipeline be built as BMAD tasks/workflows, or standalone scripts that leverage BMAD agents?
- What's the preferred output format for opportunity cards (markdown with frontmatter, JSON, YAML)?
- Should test execution be fully automated (bash script), or manual step-through for learning?

---

**Document Status:** ✅ Ready for PRD Development
**Next Owner:** Product Manager (for PRD creation)
**Approval Required From:** Innovation Intelligence System stakeholders
**Estimated PRD Start Date:** Upon brief approval
