# Story Manager Handoff: Pipeline Redesign to 7-Stage Architecture

## Handoff Summary

**Epic**: Pipeline Redesign to 7-Stage Architecture - Brownfield Enhancement
**Epic ID**: EPIC-001
**Epic Document**: `/docs/epics/pipeline-redesign-7-stage.md`
**Validation Report**: `/docs/epics/pipeline-redesign-7-stage-validation.md`
**Source Requirements**: `/documentation/handoff-pipeline-redesign.md`

---

## Request to Story Manager

Please develop **3 detailed user stories** for this brownfield epic. Key considerations:

### System Context

**This is an enhancement to an existing system running:**
- **Technology stack**: Python 3.11+, FastAPI, Prisma (PostgreSQL), OpenRouter (LLM API), Vercel Blob (PDF storage), Railway (deployment)
- **Current pipeline**: 5 stages (Input Processing → Signal Amplification → General Translation → Brand Contextualization → Opportunity Generation)
- **Backend location**: `/backend/pipeline/stages/`, `/backend/app/`
- **API integration**: REST endpoints (`/api/pipeline/run`, `/api/pipeline/status`), webhook notifications to frontend
- **Database**: PostgreSQL managed by Prisma ORM, models in `/backend/app/models.py`

### Integration Points

**Key integration points to preserve:**

1. **REST API Contract**:
   - Endpoint: `POST /api/pipeline/run` with `{blob_url, brand_id}` input
   - Endpoint: `GET /api/pipeline/status/{run_id}` for progress tracking
   - **Must maintain**: Same request/response structure for frontend compatibility

2. **Webhook System**:
   - Webhook notifications sent to frontend after each stage completion
   - **Must update**: Stage names and stage count (5 → 7) but maintain webhook payload structure

3. **Database Models**:
   - Existing: `PipelineRun`, `PipelineStage`, `TrendObject`, `OpportunityCard`
   - **Must add**: New tables for `BrandEnrichment`, `ConvergencePattern`, `TechniqueLibrary`, `CompetitiveIntelligence`
   - **Constraint**: All changes must be additive (no breaking schema changes)

4. **Perplexity API**:
   - **New dependency**: Required for Stage 0 (brand enrichment) and Stage 5 (competitive search)
   - **Configuration**: API key via environment variable `PERPLEXITY_API_KEY`

### Existing Patterns to Follow

**Code patterns established in current pipeline:**

1. **Stage Structure**:
   - Each stage in `/backend/pipeline/stages/stageN_name.py`
   - Each stage has corresponding prompt in `/backend/pipeline/prompts/stageN_prompt.py`
   - Stage class structure:
     ```python
     class StageNameStage:
         async def execute(self, input_data: dict, run_id: str) -> dict:
             # Stage logic
             return output_data
     ```

2. **Prompt Management**:
   - System prompts in dedicated `prompts/` directory
   - Use Jinja2 templates for dynamic prompt construction
   - Validation schemas defined alongside prompts

3. **Error Handling**:
   - Custom exceptions in `/backend/app/pipeline_errors.py`
   - Structured error responses with stage context
   - Automatic retry logic for transient failures

4. **Testing**:
   - Unit tests in `/backend/tests/test_pipeline_runner.py`
   - Integration tests using pytest fixtures
   - Mock OpenRouter API calls in tests

### Critical Compatibility Requirements

**Each story must include verification that:**

1. **Existing REST API endpoints continue to work unchanged**
   - Test: Frontend can still call `/api/pipeline/run` with same payload
   - Test: `/api/pipeline/status` returns expected progress structure

2. **Database migrations are backward compatible**
   - All schema changes are additive only (no column drops, no table drops)
   - Existing `PipelineRun` records can coexist with new 7-stage runs
   - Migration rollback is safe and tested

3. **Webhook notifications maintain expected structure**
   - Stage count updates from 5 → 7 but payload structure unchanged
   - Frontend can parse new stage names without breaking

4. **Frontend integration remains intact**
   - Opportunity cards output format compatible with frontend expectations
   - Progress tracking UI can display 7 stages without code changes (graceful degradation)

5. **Performance meets target**
   - End-to-end execution time < 3 minutes (vs current < 2 minutes)
   - Stage 0 and Stage 1 caching reduces redundant API calls by 70%

### Story Sequencing Strategy

**Stories MUST be implemented in sequence** (Story 1 → Story 2 → Story 3):

**Story 1** builds foundation:
- Stage 0 (brand enrichment) provides context for Stage 2
- Stage 1 (trend decomposition with L1-L4) provides structured trends for Stage 2
- Caching infrastructure required before expensive stages (2-6)

**Story 2** builds on Story 1:
- Stage 2 (convergence synthesis) requires Stage 1's L1-L4 abstraction levels
- Stage 3 (technique matching) requires Stage 2's consumer insights

**Story 3** completes the pipeline:
- Stage 4 (concept generation) requires Stage 3's validated techniques
- Stage 5 (competitive intel) requires Stage 4's directional concepts
- Stage 6 (opportunity packaging) requires all previous stage outputs

### Acceptance Criteria Reminders

**Every story acceptance criteria must include:**

1. **Functional verification**:
   - Stage executes successfully with sample input
   - Output matches defined JSON schema
   - Integration with next stage succeeds

2. **Backward compatibility verification**:
   - Existing API endpoints still work
   - Database migrations are reversible
   - Frontend can consume new outputs

3. **Testing verification**:
   - Unit tests pass for new/modified stages
   - Integration tests pass end-to-end
   - Performance meets targets (< 3 minutes total)

4. **Documentation verification**:
   - Stage specification documented
   - API docs updated if endpoints changed
   - Database schema documented

### Epic Goal (Reminder)

The epic should maintain system integrity while delivering **multi-trend convergence discovery, systematic innovation framework integration (SIT/TRIZ/Doblin), and lifecycle-aware strategic positioning** to produce higher-quality, defensible CPG innovation opportunities.

---

## Reference Documents

**Primary specification**:
- `/documentation/docs-pipeline-strategy/google-docs/simplified.md` - Detailed 7-stage architecture specification (830 lines)

**Supporting context**:
- `/documentation/handoff-pipeline-redesign.md` - Implementation handoff with technical details
- `/docs/epics/pipeline-redesign-7-stage.md` - Epic document with 3 stories breakdown
- `/docs/epics/pipeline-redesign-7-stage-validation.md` - Validation report with scope assessment

**Current implementation**:
- `/backend/pipeline/stages/` - Existing 5-stage implementation
- `/backend/pipeline/prompts/` - Current prompt templates
- `/backend/app/models.py` - Database models
- `/backend/app/routes.py` - API endpoints
- `/backend/app/pipeline_runner.py` - Pipeline orchestrator

---

## Story Templates

Please use the **brownfield story template** (`.bmad-core/templates/story-tmpl.yaml`) for each story with the following sections populated:

### Required Sections Per Story

1. **Status**: Draft (initially)

2. **Story**: Standard user story format
   - **As a** {Innovation intelligence system}
   - **I want** {specific stage enhancement}
   - **So that** {value delivered}

3. **Acceptance Criteria**: Copy from epic, expand with technical details

4. **Tasks / Subtasks**: Break down into implementation steps with AC references

5. **Dev Notes**: Include:
   - **Existing patterns**: Reference current stage implementations to follow
   - **Integration points**: Specific files/models that need updates
   - **Technical constraints**: JSON schemas, API contracts, performance targets
   - **Previous story context**: What was built in prior stories (for Stories 2-3)

6. **Testing Standards**: Include:
   - Test file location: `/backend/tests/test_stageN_name.py`
   - Testing framework: pytest with fixtures
   - Integration test requirements: End-to-end pipeline test

---

## Feature Flag Requirement

**CRITICAL**: Story 1 MUST include implementation of feature flag system to toggle between 5-stage (legacy) and 7-stage (new) pipelines.

**Implementation details**:
- Environment variable: `PIPELINE_VERSION` (values: `v1_5stage`, `v2_7stage`)
- Default: `v1_5stage` (safe rollback)
- Location: `/backend/app/pipeline_runner.py`
- Behavior: Route pipeline execution to appropriate stage executor based on flag

This feature flag is **non-negotiable** for risk mitigation and rollback capability.

---

## Success Metrics

Each story should contribute to these epic-level success metrics:

1. **Quality**: Opportunity card quality score > 8/10 (stakeholder review)
2. **Discovery**: Convergence discovery rate > 50% (non-obvious connections)
3. **Accuracy**: Competitive validation accuracy > 90% (no false claims)
4. **Performance**: End-to-end execution time < 3 minutes
5. **Reliability**: Stage cache hit rate > 90% (Stage 0), > 95% (Stage 1)

---

## Timeline Expectation

**Target**: 3 weeks total
- **Week 1**: Story 1 (Foundation - Stages 0-1)
- **Week 2**: Story 2 (Core Innovation - Stages 2-3)
- **Week 3**: Story 3 (Validation & Packaging - Stages 4-6)

**Note**: Per validation report, each story is estimated at 1 week (not typical 1-session brownfield story). This is acceptable given the complexity, but monitor for scope creep.

---

## Stakeholder Decision Required

**Before proceeding**, confirm with stakeholder:

- [ ] **Proceed with 3-story brownfield epic** (current approach, faster but higher risk)
- [ ] **Escalate to full brownfield PRD process** (recommended by validation report, slower but lower risk)

If stakeholder selects "Escalate to PRD", use `*create-brownfield-prd` command instead of creating stories.

---

## Story Manager Next Steps

1. **Review reference documents**:
   - Read `/documentation/docs-pipeline-strategy/google-docs/simplified.md` for technical specifications
   - Read `/documentation/handoff-pipeline-redesign.md` for implementation guidance

2. **Create 3 detailed stories** using brownfield story template:
   - Story 1: Foundation - Brand Enrichment + Trend Decomposition (Stages 0-1)
   - Story 2: Core Innovation - Convergence Synthesis + Technique Matching (Stages 2-3)
   - Story 3: Validation & Packaging - Concept Generation + Competitive Intel + Cards (Stages 4-6)

3. **Ensure each story includes**:
   - Existing system integration awareness
   - Backward compatibility requirements
   - Feature flag implementation (Story 1)
   - Testing strategy covering existing functionality
   - Clear handoff to next story (Stories 1-2)

4. **Save stories to**: `/docs/stories/epic-001.{story-number}.{story-title}.md`

---

**Handoff Date**: 2025-11-19
**Prepared by**: John (PM Agent)
**Epic Status**: Ready for story breakdown
**Blocker**: Stakeholder decision required (3-story epic vs full PRD)
