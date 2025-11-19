# Story EPIC-001.1: Foundation - Brand Enrichment + Trend Decomposition (Stages 0-1)

## Status

Draft

## Story

**As an** Innovation Intelligence System,
**I want** to enrich minimal brand inputs with search-based context and decompose trend reports across 4 abstraction levels (L1-L4),
**so that** downstream stages can discover multi-trend convergences and generate brand-specific innovation opportunities.

## Acceptance Criteria

### Functional Requirements

1. **Stage 0 (Brand Profile Enrichment)**:
   - Accepts minimal brand input (4 required fields: brand_name, industry, geography, product_portfolio)
   - Enriches context via Perplexity API with 4 dimensions: category, positioning, competitors, innovation_history
   - Outputs confidence scores (0-1) per enrichment dimension
   - Cites sources for every enrichment claim
   - Flags conflicting information without hallucinating resolution

2. **Stage 1 (Multi-Trend Decomposition)**:
   - Extracts 3-6 distinct trends from WGSN report PDF
   - Decomposes each trend across L1-L4 abstraction levels (Domain → Industry → Cross-Domain → Universal)
   - Maps lifecycle stage (EMERGING/ACCELERATING/PEAKING) from WGSN report
   - Extracts emotional drivers (current_negative + aspirational_positive)
   - Outputs brand-agnostic reusable trend objects

3. **Stage Caching System**:
   - Stage 0 cache: Per brand with quarterly refresh (cache hit rate > 90%)
   - Stage 1 cache: Per report, brand-agnostic (cache hit rate > 95%)
   - Cache invalidation logic for manual refresh

4. **Feature Flag Implementation**:
   - Environment variable `PIPELINE_VERSION` (values: `v1_5stage`, `v2_7stage`)
   - Default: `v1_5stage` for safe rollback
   - Routes pipeline execution to appropriate stage executor

### Integration Requirements

5. **Existing REST API remains unchanged**:
   - `POST /api/pipeline/run` accepts same payload: `{blob_url, brand_id}`
   - `GET /api/pipeline/status/{run_id}` returns progress with updated stage names

6. **Database schema changes are additive**:
   - New tables: `brand_enrichment`, `trend_objects_v2`, `stage_cache`
   - No breaking changes to existing `pipeline_run` or `pipeline_stage` tables
   - Migration is reversible

7. **Webhook notifications updated**:
   - Stage count updates from 5 → 7 stages
   - Payload structure unchanged (frontend compatible)

### Quality Requirements

8. **Stage 0 validation**:
   - All 4 enrichment dimensions attempted (even if low confidence)
   - Confidence scores reflect source quality
   - Sources cited for every claim

9. **Stage 1 validation**:
   - L1-L4 levels ascend from concrete to universal (not redundant)
   - Lifecycle stage explicitly stated or clearly implied from report
   - No hallucinated statistics or competitive claims

10. **Testing coverage**:
    - Unit tests for Stage 0 and Stage 1 pass
    - Integration test: Brand input → Stage 0 → Stage 1 → Valid JSON output
    - Cache hit rate tests verify > 90% (Stage 0) and > 95% (Stage 1)

11. **Performance meets targets**:
    - Stage 0 execution: < 30 seconds (with Perplexity API)
    - Stage 1 execution: < 45 seconds (with LLM extraction)
    - Feature flag toggle: < 1 second overhead

## Tasks / Subtasks

### Task 1: Feature Flag Infrastructure (AC: 4, 5)
- [ ] Add `PIPELINE_VERSION` environment variable to Railway configuration
- [ ] Update `/backend/app/pipeline_runner.py` to route based on flag
  - [ ] Create `execute_v1_pipeline()` function (existing 5-stage)
  - [ ] Create `execute_v2_pipeline()` function (new 7-stage)
  - [ ] Default to `v1_5stage` if env var not set
- [ ] Add integration test for feature flag toggle
- [ ] Document feature flag usage in deployment guide

### Task 2: Stage 0 - Brand Profile Enrichment (AC: 1, 8)
- [ ] Create `/backend/pipeline/stages/stage0_brand_enrichment.py`
  - [ ] Implement `BrandEnrichmentStage` class with `execute()` method
  - [ ] Define input schema (4 required fields per handoff doc lines 66-71)
  - [ ] Define output schema (enriched_context per handoff doc lines 87-119)
- [ ] Create `/backend/pipeline/prompts/stage0_prompt.py`
  - [ ] System prompt for search query generation
  - [ ] Prompt for confidence scoring
  - [ ] Prompt for conflict detection
- [ ] Integrate Perplexity API
  - [ ] Add `PERPLEXITY_API_KEY` to environment variables
  - [ ] Create Perplexity client in `/backend/app/api_clients.py`
  - [ ] Implement 4 search queries (category, positioning, competitors, innovation)
  - [ ] Add exponential backoff for rate limits
- [ ] Create unit tests in `/backend/tests/test_stage0_brand_enrichment.py`
  - [ ] Test minimal brand input processing
  - [ ] Test confidence scoring logic
  - [ ] Test source citation
  - [ ] Mock Perplexity API responses

### Task 3: Stage 1 - Multi-Trend Decomposition (AC: 2, 9)
- [ ] Refactor `/backend/pipeline/stages/stage1_input_processing.py` → `stage1_trend_decomposition.py`
  - [ ] Update class name to `TrendDecompositionStage`
  - [ ] Keep PDF text extraction logic (from existing Stage 1)
  - [ ] Add L1-L4 abstraction extraction
  - [ ] Add lifecycle stage mapping (EMERGING/ACCELERATING/PEAKING)
  - [ ] Add emotional driver extraction (current_negative + aspirational_positive)
- [ ] Create `/backend/pipeline/prompts/stage1_prompt.py`
  - [ ] Jinja2 template for L1-L4 abstraction ladder (per handoff doc lines 165-173)
  - [ ] Prompt for lifecycle stage identification
  - [ ] Prompt for emotional driver extraction
- [ ] Update output schema to match handoff doc lines 169-191
- [ ] Create unit tests in `/backend/tests/test_stage1_trend_decomposition.py`
  - [ ] Test trend extraction (3-6 trends)
  - [ ] Test L1-L4 differentiation validation
  - [ ] Test lifecycle stage mapping
  - [ ] Mock OpenRouter LLM calls

### Task 4: Stage Caching System (AC: 3)
- [ ] Create `/backend/pipeline/stage_cache.py`
  - [ ] Implement `StageCache` class with Redis backend
  - [ ] Add cache key generation (brand hash for Stage 0, report hash for Stage 1)
  - [ ] Add cache expiration logic (quarterly for Stage 0, permanent for Stage 1)
  - [ ] Add manual cache invalidation endpoint
- [ ] Update Stage 0 to use cache
  - [ ] Check cache before Perplexity API call
  - [ ] Store enriched brand context in cache after success
- [ ] Update Stage 1 to use cache
  - [ ] Check cache before LLM extraction
  - [ ] Store trend objects in cache after success
- [ ] Add cache hit rate monitoring
  - [ ] Emit cache hit/miss metrics to logging
  - [ ] Add `/api/pipeline/cache/stats` endpoint for monitoring
- [ ] Create cache tests in `/backend/tests/test_stage_cache.py`

### Task 5: Database Schema Updates (AC: 6)
- [ ] Create Prisma migration for new tables
  - [ ] `brand_enrichment` table (stores Stage 0 outputs)
  - [ ] `trend_objects_v2` table (stores Stage 1 outputs with L1-L4)
  - [ ] `stage_cache` table (stores cache metadata)
- [ ] Update `/backend/app/models.py` with new models
- [ ] Run migration in development environment
- [ ] Verify migration is reversible (test rollback)
- [ ] Update database schema documentation

### Task 6: Integration Testing (AC: 10, 11)
- [ ] Create end-to-end test in `/backend/tests/test_pipeline_v2_foundation.py`
  - [ ] Test: Minimal brand input → Stage 0 → Enriched context
  - [ ] Test: WGSN PDF → Stage 1 → 3-6 trend objects with L1-L4
  - [ ] Test: Stage 0 + Stage 1 → Valid JSON handoff
  - [ ] Test: Feature flag toggle between v1 and v2 pipelines
- [ ] Performance benchmarking
  - [ ] Measure Stage 0 execution time (target: < 30 seconds)
  - [ ] Measure Stage 1 execution time (target: < 45 seconds)
  - [ ] Verify cache hit rates (Stage 0 > 90%, Stage 1 > 95% after warmup)
- [ ] Regression testing
  - [ ] Verify existing `/api/pipeline/run` endpoint still works
  - [ ] Verify existing 5-stage pipeline (v1) still executes
  - [ ] Verify webhook notifications work with updated stage names

## Dev Notes

### Existing System Integration

**Technology Stack**:
- Python 3.11+, FastAPI, Prisma (PostgreSQL), OpenRouter (LLM API), Vercel Blob (PDF storage)
- Current pipeline: 5 stages in `/backend/pipeline/stages/`
- API endpoints: `/backend/app/routes.py`
- Database models: `/backend/app/models.py`
- Pipeline orchestrator: `/backend/app/pipeline_runner.py`

**Integration Points**:
- **Stage 0 (NEW)**: Runs BEFORE existing pipeline, enriches brand context
- **Stage 1 (REFACTOR)**: Replaces `stage1_input_processing.py` with L1-L4 abstraction
- **Feature Flag**: Allows safe rollback to 5-stage pipeline if issues arise
- **Database**: All schema changes are additive (no breaking changes)
- **Webhooks**: Update stage names but maintain payload structure

**Existing Patterns to Follow**:

1. **Stage Class Structure** (from current stages):
```python
class StageName:
    async def execute(self, input_data: dict, run_id: str) -> dict:
        # 1. Validate input against schema
        # 2. Call LLM/API with prompt template
        # 3. Parse and validate output
        # 4. Store to database if needed
        # 5. Return structured output
        return output_data
```

2. **Prompt Management** (from existing prompts):
- Use Jinja2 templates in `/backend/pipeline/prompts/`
- Include system prompt + user prompt structure
- Define JSON schema for LLM output validation

3. **Error Handling** (from existing stages):
- Custom exceptions in `/backend/app/pipeline_errors.py`
- Structured error responses with stage context
- Automatic retry logic for transient failures (3 retries with exponential backoff)

4. **Database Operations** (from existing models):
- Use Prisma ORM for all database operations
- Store intermediate stage outputs for debugging
- Link outputs to `pipeline_run.id` for traceability

**Source Tree Context**:
```
/backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── routes.py                  # API endpoints (preserve /api/pipeline/run)
│   ├── models.py                  # Prisma models (add new models here)
│   ├── pipeline_runner.py         # Orchestrator (add feature flag logic here)
│   ├── pipeline_errors.py         # Custom exceptions
│   └── api_clients.py             # External API clients (add Perplexity here)
├── pipeline/
│   ├── stages/
│   │   ├── stage0_brand_enrichment.py      # NEW - Story 1
│   │   ├── stage1_trend_decomposition.py   # REFACTOR - Story 1
│   │   ├── stage2_trend_extraction.py      # REFACTOR - Story 2
│   │   ├── stage3_industry_translation.py  # Will be replaced by stage2/3 in Story 2
│   │   ├── stage4_brand_application.py     # REFACTOR - Story 3
│   │   └── stage5_opportunity_generation.py # Will become stage6 in Story 3
│   ├── prompts/
│   │   ├── stage0_prompt.py               # NEW - Story 1
│   │   ├── stage1_prompt.py               # UPDATE - Story 1
│   │   └── ...
│   ├── stage_cache.py                     # NEW - Story 1
│   └── executor.py                        # UPDATE for 7-stage flow
├── prisma/
│   └── schema.prisma                      # Add new models here
├── tests/
│   ├── test_stage0_brand_enrichment.py   # NEW - Story 1
│   ├── test_stage1_trend_decomposition.py # NEW - Story 1
│   ├── test_stage_cache.py               # NEW - Story 1
│   └── test_pipeline_v2_foundation.py    # NEW - Story 1 integration test
└── .env                                   # Add PERPLEXITY_API_KEY, PIPELINE_VERSION
```

**Perplexity API Integration**:
- **API Documentation**: [Perplexity API Docs](https://docs.perplexity.ai/)
- **Authentication**: API key in `Authorization: Bearer <key>` header
- **Rate Limits**: 20 requests/minute (implement exponential backoff)
- **Endpoint**: `POST https://api.perplexity.ai/chat/completions`
- **Request Format**:
```python
{
    "model": "sonar-pro",
    "messages": [
        {"role": "system", "content": "You are a brand research assistant."},
        {"role": "user", "content": "Search for [brand] category context..."}
    ],
    "return_citations": True
}
```

**L1-L4 Abstraction Levels** (from handoff doc):
- **L1 (Domain-Specific)**: CPG-actionable application (e.g., "gamified healthy eating products")
- **L2 (Industry-Specific)**: Category-level pattern (e.g., "food/beverage using playfulness")
- **L3 (Cross-Domain)**: Transferable mechanism (e.g., "pleasure activism: reframe obligation as choice")
- **L4 (Universal Principle)**: Fundamental dynamic (e.g., "joy as strategic business tool")

**No-Hallucination Boundaries**:
- ✅ Extract facts from WGSN report (trend names, lifecycle stages, evidence)
- ✅ Synthesize consumer insights from trend convergence
- ✅ Search for brand context via Perplexity API
- ❌ Invent market statistics (TAM, growth rates, market share)
- ❌ Claim "zero competition" (say "no evidence found in search results")
- ❌ Generate financial projections or ROI predictions

**Context from Previous Stories**: N/A (this is Story 1)

### Testing

**Test File Locations**:
- `/backend/tests/test_stage0_brand_enrichment.py` - Stage 0 unit tests
- `/backend/tests/test_stage1_trend_decomposition.py` - Stage 1 unit tests
- `/backend/tests/test_stage_cache.py` - Cache system unit tests
- `/backend/tests/test_pipeline_v2_foundation.py` - Integration tests

**Testing Framework**: pytest with fixtures

**Testing Patterns**:
1. **Unit Tests** (per stage):
   - Mock external API calls (Perplexity, OpenRouter)
   - Test input schema validation
   - Test output schema validation
   - Test error handling and retries

2. **Integration Tests**:
   - Use real WGSN PDF: `/data/document/WGSN - FC27-Emotions - Report.pdf`
   - Use test brand profile: `Boulangerie St-Méthode` (from CLAUDE.md)
   - Verify JSON handoff between Stage 0 → Stage 1
   - Verify cache hit rate after warmup

3. **Fixtures** (create in `/backend/tests/conftest.py`):
```python
@pytest.fixture
def sample_brand_input():
    return {
        "brand_name": "Boulangerie St-Méthode",
        "industry": "CPG - Bakery",
        "geography": "Quebec, Canada",
        "product_portfolio": "25 SKUs with healthy bread focus"
    }

@pytest.fixture
def mock_perplexity_response():
    # Mock enrichment response
    pass

@pytest.fixture
def sample_wgsn_pdf_text():
    # Extract from test PDF
    pass
```

**Test Standards**:
- All tests must pass before merging to main
- Unit test coverage > 80% for new code
- Integration tests run against Railway staging environment
- Performance tests validate < 3 minute total pipeline execution

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
