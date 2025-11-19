# Pipeline Redesign to 7-Stage Architecture - Brownfield Enhancement

## Epic Goal

Transform the existing 5-stage pipeline into a sophisticated 7-stage system that enables multi-trend convergence discovery, systematic innovation framework integration (SIT/TRIZ/Doblin), and lifecycle-aware strategic positioning to deliver higher-quality, defensible CPG innovation opportunities.

## Epic Description

### Existing System Context

- **Current functionality**: 5-stage pipeline transforms WGSN trend reports into opportunity cards
- **Technology stack**: Python, FastAPI, Prisma (PostgreSQL), OpenRouter (LLM), Vercel Blob (PDF), Railway deployment
- **Integration points**: REST API `/api/pipeline/run`, webhooks to frontend, database models in `app/models.py`
- **Current pipeline flow**:
  - Stage 1: Input Processing (PDF text extraction)
  - Stage 2: Signal Amplification (trend extraction)
  - Stage 3: General Translation (industry translation)
  - Stage 4: Brand Contextualization (brand application)
  - Stage 5: Opportunity Generation (opportunity cards)

### Enhancement Details

**What's being added/changed:**

Transform 5-stage pipeline → 7-stage pipeline with:

1. **NEW Stage 0: Brand Profile Enrichment** - Perplexity search-based brand context enrichment
2. **REFACTOR Stage 1: Multi-Trend Decomposition** - L1-L4 abstraction levels for cross-domain transfer
3. **MAJOR REFACTOR Stage 2: Consumer Insight Synthesis** - Trend convergence pattern discovery via JSON enumeration
4. **NEW Stage 3: Technique Library Matching** - SIT (5) + TRIZ (10) + Doblin (10) pattern validation
5. **REFACTOR Stage 4: Directional Concept Generation** - Lifecycle-aware concept formulation
6. **NEW Stage 5: Competitive Intelligence Integration** - Search-based competitive validation with honesty constraints
7. **UPDATE Stage 6: Opportunity Card Packaging** - Updated card format with transparency layers

**How it integrates:**

- Preserves existing REST API endpoints, webhook system, and database infrastructure
- Modifies stage implementations and prompts
- Adds new database tables for technique libraries and convergence patterns
- Introduces Perplexity API dependency for Stages 0 and 5
- Maintains backward compatibility with frontend expectations

**Success criteria:**

- All 7 stages execute successfully end-to-end
- JSON schemas validated at each stage handoff
- Full traceability from trend → insight → convergence → technique → concept → card
- L1-L4 abstraction levels clearly differentiated
- Convergence patterns discover non-obvious multi-trend connections
- No hallucinated statistics or competitive claims
- Caching reduces redundant API calls by 70%
- End-to-end pipeline completes in < 3 minutes

## Stories

### Story 1: Foundation - Brand Enrichment + Trend Decomposition (Stages 0-1)

**Description:** Implement Stage 0 (Brand Profile Enrichment) with Perplexity API integration and refactor Stage 1 (Input Processing → Multi-Trend Decomposition) to extract L1-L4 abstraction levels from WGSN reports.

**Key deliverables:**
- New file: `backend/pipeline/stages/stage0_brand_enrichment.py`
- Refactored: `backend/pipeline/stages/stage1_input_processing.py` → `stage1_trend_decomposition.py`
- Perplexity API integration for search-based enrichment
- L1-L4 abstraction prompt templates
- Stage caching system for Stage 0 (brand) and Stage 1 (report)
- Database schema updates for enriched brand context
- Unit tests for Stage 0 and Stage 1

**Acceptance criteria:**
- Stage 0 enriches minimal brand input (4 fields) into full context with confidence scores
- Stage 1 extracts 3-6 trends with L1-L4 abstraction levels per trend
- Stage 1 output is brand-agnostic and reusable across brands
- Stage 0 cache hit rate > 90% after initial runs
- Stage 1 cache hit rate > 95% after initial runs

### Story 2: Core Innovation - Convergence Synthesis + Technique Matching (Stages 2-3)

**Description:** Major refactor of Stage 2 (Signal Amplification → Consumer Insight Synthesis) to discover trend convergence patterns via JSON enumeration, and implement Stage 3 (Technique Library Matching) to validate insights against SIT/TRIZ/Doblin frameworks.

**Key deliverables:**
- Refactored: `backend/pipeline/stages/stage2_signal_amplification.py` → `stage2_insight_synthesis.py`
- New file: `backend/pipeline/stages/stage3_technique_matching.py`
- Convergence enumeration logic (C(n,2) trend pairs)
- Technique library data files (SIT: 5, TRIZ: 10, Doblin: 10 with CPG examples)
- Database schema for convergence_patterns and technique_libraries tables
- Brand-specific insight synthesis with lifecycle strategy mapping
- Multi-framework validation logic
- Unit tests for Stage 2 and Stage 3

**Acceptance criteria:**
- Stage 2 enumerates all possible trend pairs and discovers convergences
- Stage 2 generates brand-specific consumer insights combining 2+ trends
- Stage 2 outputs include functional + emotional + social needs
- Stage 3 matches insights to appropriate SIT/TRIZ/Doblin techniques
- Stage 3 includes defensibility assessment (LOW/MEDIUM/HIGH)
- Convergence patterns are fully traceable back to source trends

### Story 3: Validation & Packaging - Concept Generation + Competitive Intel + Cards (Stages 4-6)

**Description:** Refactor Stage 4 (Brand Contextualization → Directional Concept Generation) to use validated techniques, implement Stage 5 (Competitive Intelligence Integration) with search-based validation, and update Stage 6 (Opportunity Generation → Opportunity Card Packaging) with new card format including transparency layers.

**Key deliverables:**
- Refactored: `backend/pipeline/stages/stage4_brand_contextualization.py` → `stage4_concept_generation.py`
- New file: `backend/pipeline/stages/stage5_competitive_intel.py`
- Updated: `backend/pipeline/stages/stage5_opportunity_generation.py` → `stage6_opportunity_packaging.py`
- Perplexity API integration for competitive search
- Narrative framework for concept generation
- 3-query competitive validation (direct, analogous, competitive)
- Updated opportunity card markdown template with no-hallucination disclosure
- Integration tests for end-to-end pipeline
- Performance optimization for < 3 minute total execution

**Acceptance criteria:**
- Stage 4 generates directional concepts combining insight + technique + lifecycle strategy
- Stage 4 outputs include narrative framework (Problem/Solution/Payoff/Proof)
- Stage 5 executes 3 search queries per concept for competitive validation
- Stage 5 includes honesty constraints ("no evidence found" vs "zero competition")
- Stage 6 produces retail-ready opportunity cards in markdown format
- All cards include no-hallucination disclosure section
- End-to-end test passes: WGSN PDF → 7 stages → 3-5 opportunity cards
- Full traceability from trend extraction to final card

## Compatibility Requirements

- [x] Existing REST API endpoints remain unchanged (`/api/pipeline/run`, `/api/pipeline/status`)
- [x] Database schema changes are additive only (new tables, no breaking changes to existing models)
- [x] Webhook notification system continues to work with updated stage names
- [x] Frontend expectations maintained (stage progress updates, final output format)
- [x] Performance impact is acceptable (< 3 minutes vs current < 2 minutes)
- [x] Existing pipeline runs can complete during deployment (graceful degradation)

## Risk Mitigation

**Primary Risk:** Breaking existing frontend integration during multi-stage refactor

**Mitigation:**
- Maintain existing API contract while upgrading backend implementation
- Add feature flag for 7-stage vs 5-stage pipeline selection during transition
- Deploy stages incrementally with rollback capability
- Comprehensive integration tests before each deployment

**Rollback Plan:**
- Feature flag allows instant switch back to 5-stage pipeline
- Database migrations are additive (no data loss on rollback)
- Git tag before each story deployment for quick revert
- Railway allows instant rollback to previous deployment via dashboard

**Additional Risks:**

1. **Perplexity API dependency**: Rate limits or service outages
   - **Mitigation**: Implement exponential backoff, fallback to graceful degradation (skip Stage 0/5 enrichment)

2. **Performance degradation**: 7 stages may exceed 3-minute target
   - **Mitigation**: Parallel execution for brand-specific stages (2-6), aggressive caching for Stages 0-1

3. **Prompt quality**: New stages may produce low-quality outputs initially
   - **Mitigation**: Experimentation framework for A/B testing prompts, comprehensive validation criteria per stage

## Definition of Done

- [x] All 3 stories completed with acceptance criteria met
- [x] Existing functionality verified through regression testing
- [x] Integration points working correctly (API, webhooks, database)
- [x] Documentation updated (API docs, stage specifications, deployment guide)
- [x] No regression in existing features (frontend still receives progress updates)
- [x] End-to-end test passes with real WGSN report
- [x] Performance meets < 3 minute target
- [x] Deployed to Railway staging environment and validated
- [x] Production deployment successful with zero downtime

## Epic Metadata

- **Epic ID**: EPIC-001
- **Target Timeline**: 3 weeks (1 week per story)
- **Priority**: HIGH
- **Dependencies**: Perplexity API access, WGSN FC27 Emotions Report PDF
- **Stakeholders**: Innovation intelligence team, CPG clients
- **Success Metrics**:
  - Opportunity card quality score > 8/10 (based on stakeholder review)
  - Convergence discovery rate > 50% (non-obvious connections found)
  - Competitive validation accuracy > 90% (no false "zero competition" claims)
  - End-to-end execution time < 3 minutes

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-11-19 | 1.0 | Epic created from handoff document | John (PM Agent) |
