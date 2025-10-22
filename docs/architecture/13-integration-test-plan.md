# 13. Integration Test Plan

## Overview

This document defines the regression and integration testing strategy to ensure the Python pipeline continues functioning correctly after database retrofit and Railway deployment.

## Test Pyramid

```
┌─────────────────────────────────────┐
│   E2E Tests (5%)                    │  Full user journey tests
├─────────────────────────────────────┤
│   Integration Tests (25%)           │  Pipeline + Database + API
├─────────────────────────────────────┤
│   Unit Tests (70%)                  │  Individual stage validation
└─────────────────────────────────────┘
```

---

## 1. Pipeline Regression Test Suite

### 1.1 Test Data Setup

**Location:** `tests/fixtures/`

```
tests/
  fixtures/
    sample-report.pdf          # 3-page trend report for testing
    brand-profiles/
      test-company.yaml        # Minimal test brand profile
    expected-outputs/
      stage1-inspirations.json # Known-good Stage 1 output
      stage2-trends.json       # Known-good Stage 2 output
      stage3-lessons.json      # Known-good Stage 3 output
      stage4-context.json      # Known-good Stage 4 output
      stage5-opportunities.json # Known-good Stage 5 output
```

### 1.2 Stage-Level Regression Tests

**File:** `tests/test_pipeline_stages.py`

```python
import pytest
import asyncio
from pathlib import Path
from pipeline.stages.stage1 import Stage1Executor
from pipeline.stages.stage2 import Stage2Executor
from pipeline.stages.stage3 import Stage3Executor
from pipeline.stages.stage4 import Stage4Executor
from pipeline.stages.stage5 import Stage5Executor

@pytest.fixture
def test_document():
    """Load test PDF"""
    return Path("tests/fixtures/sample-report.pdf")

@pytest.fixture
def test_brand():
    """Load test brand profile"""
    return "test-company"

@pytest.fixture
async def db_service():
    """Mock database service for isolated testing"""
    from tests.mocks.mock_db_service import MockDatabaseService
    service = MockDatabaseService()
    await service.connect()
    yield service
    await service.disconnect()

class TestStage1Regression:
    """Validate Stage 1: Inspiration Extraction"""

    @pytest.mark.asyncio
    async def test_stage1_output_structure(self, test_document, db_service):
        """Ensure Stage 1 produces valid JSON structure"""
        executor = Stage1Executor(db_service)
        result = await executor.execute(
            document_path=test_document,
            run_id="test-run-001"
        )

        # Validate structure matches expected schema
        assert "inspirations" in result
        assert len(result["inspirations"]) == 2
        assert all("title" in insp for insp in result["inspirations"])
        assert all("content" in insp for insp in result["inspirations"])
        assert all("key_elements" in insp for insp in result["inspirations"])

    @pytest.mark.asyncio
    async def test_stage1_database_write(self, test_document, db_service):
        """Ensure Stage 1 writes to database correctly"""
        executor = Stage1Executor(db_service)
        result = await executor.execute(
            document_path=test_document,
            run_id="test-run-002"
        )

        # Verify database write
        stored = await db_service.get_inspiration_report("test-run-002")
        assert stored is not None
        assert stored["inspiration1_title"] == result["inspirations"][0]["title"]

    @pytest.mark.asyncio
    async def test_stage1_backward_compatibility(self, test_document):
        """Ensure Stage 1 still works WITHOUT database (file-based fallback)"""
        executor = Stage1Executor(db_service=None)  # No database
        result = await executor.execute(
            document_path=test_document,
            run_id="test-run-003",
            output_mode="file"  # Force file-based output
        )

        # Verify file was created
        output_file = Path(f"data/test-outputs/test-run-003/stage1/inspirations.json")
        assert output_file.exists()

class TestStage2Regression:
    """Validate Stage 2: Trend Amplification"""

    @pytest.mark.asyncio
    async def test_stage2_receives_stage1_output(self, db_service):
        """Ensure Stage 2 can read Stage 1 database output"""
        # Setup: Write Stage 1 output to database
        await db_service.create_inspiration_report(
            run_id="test-run-004",
            inspiration1_title="Test Inspiration 1",
            inspiration1_content="Content 1",
            inspiration1_elements=["Element A", "Element B"],
            inspiration2_title="Test Inspiration 2",
            inspiration2_content="Content 2",
            inspiration2_elements=["Element C", "Element D"]
        )

        # Execute Stage 2
        executor = Stage2Executor(db_service)
        result = await executor.execute(run_id="test-run-004")

        # Validate Stage 2 used Stage 1 data
        assert result is not None
        assert "trends" in result

    @pytest.mark.asyncio
    async def test_stage2_output_structure(self, db_service):
        """Validate Stage 2 output matches expected schema"""
        # (Similar structure to test_stage1_output_structure)
        pass

class TestStage3Regression:
    """Validate Stage 3: Universal Lessons"""
    # Similar tests for Stage 3
    pass

class TestStage4Regression:
    """Validate Stage 4: Brand Contextualization"""

    @pytest.mark.asyncio
    async def test_stage4_loads_brand_profile(self, db_service):
        """Ensure Stage 4 loads YAML brand profile correctly"""
        executor = Stage4Executor(db_service)
        result = await executor.execute(
            run_id="test-run-005",
            brand_id="test-company"
        )

        # Verify brand context was incorporated
        assert "brand_specific_opportunities" in result
        assert result["brand_name"] == "Test Company"

class TestStage5Regression:
    """Validate Stage 5: Opportunity Generation"""

    @pytest.mark.asyncio
    async def test_stage5_generates_5_cards(self, db_service):
        """Ensure Stage 5 generates exactly 5 opportunity cards"""
        executor = Stage5Executor(db_service)
        result = await executor.execute(run_id="test-run-006")

        assert len(result["opportunities"]) == 5
        assert all("title" in opp for opp in result["opportunities"])
        assert all("tagline" in opp for opp in result["opportunities"])

    @pytest.mark.asyncio
    async def test_stage5_database_write(self, db_service):
        """Ensure Stage 5 writes opportunity cards to database"""
        executor = Stage5Executor(db_service)
        await executor.execute(run_id="test-run-007", user_id="test-user-123")

        # Verify cards were written
        cards = await db_service.get_opportunity_cards("test-run-007")
        assert len(cards) == 5
        assert cards[0]["number"] == 1
        assert cards[4]["number"] == 5
```

### 1.3 End-to-End Pipeline Test

**File:** `tests/test_pipeline_e2e.py`

```python
import pytest
import asyncio
from pathlib import Path
from pipeline.orchestrator import PipelineOrchestrator

@pytest.mark.asyncio
async def test_full_pipeline_with_database():
    """
    CRITICAL TEST: Full pipeline execution from PDF → 5 Opportunity Cards
    This validates the entire integration works end-to-end.
    """
    orchestrator = PipelineOrchestrator()

    result = await orchestrator.execute_full_pipeline(
        document_path="tests/fixtures/sample-report.pdf",
        brand_id="test-company",
        run_id="test-run-e2e-001",
        user_id="test-user-123"
    )

    # Validate all stages completed
    assert result["status"] == "COMPLETED"
    assert result["current_stage"] == 5

    # Validate database contains all outputs
    from backend.services.database_service import DatabaseService
    db = DatabaseService()
    await db.connect()

    # Check InspirationReport exists
    inspiration = await db.get_inspiration_report("test-run-e2e-001")
    assert inspiration is not None

    # Check 5 OpportunityCards exist
    cards = await db.get_opportunity_cards("test-run-e2e-001")
    assert len(cards) == 5

    # Check StageOutputs exist for all 5 stages
    outputs = await db.get_stage_outputs("test-run-e2e-001")
    assert len(outputs) == 5
    assert set(output["stage_number"] for output in outputs) == {1, 2, 3, 4, 5}

    await db.disconnect()

@pytest.mark.asyncio
async def test_pipeline_error_handling():
    """Validate pipeline handles errors gracefully"""
    orchestrator = PipelineOrchestrator()

    # Test with invalid document
    result = await orchestrator.execute_full_pipeline(
        document_path="nonexistent.pdf",
        brand_id="test-company",
        run_id="test-run-error-001",
        user_id="test-user-123"
    )

    assert result["status"] == "FAILED"
    assert result["error_message"] is not None
```

---

## 2. Database Integration Tests

### 2.1 asyncpg Service Tests

**File:** `backend/tests/test_database_service.py`

```python
import pytest
import asyncio
from backend.services.database_service import DatabaseService

@pytest.fixture
async def db():
    """Database service fixture"""
    service = DatabaseService()
    await service.connect()
    yield service
    await service.disconnect()

class TestDatabaseService:
    """Validate asyncpg database service"""

    @pytest.mark.asyncio
    async def test_connection_pool(self, db):
        """Ensure connection pool initializes correctly"""
        assert db.pool is not None
        assert db.pool._holders  # Pool has connections

    @pytest.mark.asyncio
    async def test_create_run(self, db):
        """Test run creation"""
        run_id = await db.create_run(
            run_id="test-run-db-001",
            user_id="test-user-123",
            company_id="lactalis-canada",
            company_name="Lactalis",
            document_name="test.pdf",
            document_url="https://example.com/test.pdf"
        )

        assert run_id == "test-run-db-001"

        # Verify run was created
        run = await db.get_run("test-run-db-001")
        assert run["company_id"] == "lactalis-canada"

    @pytest.mark.asyncio
    async def test_update_run_status(self, db):
        """Test run status updates"""
        await db.create_run(
            run_id="test-run-db-002",
            user_id="test-user-123",
            company_id="test-company",
            company_name="Test Company",
            document_name="test.pdf",
            document_url="https://example.com/test.pdf"
        )

        # Update to RUNNING
        await db.update_run_status("test-run-db-002", "RUNNING", current_stage=1)
        run = await db.get_run("test-run-db-002")
        assert run["status"] == "RUNNING"
        assert run["current_stage"] == 1

        # Update to COMPLETED
        await db.update_run_status("test-run-db-002", "COMPLETED", current_stage=5)
        run = await db.get_run("test-run-db-002")
        assert run["status"] == "COMPLETED"
        assert run["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_retry_logic(self, db):
        """Ensure retry logic works for transient failures"""
        # Simulate connection drop
        await db.pool.close()

        # This should trigger retry and reconnect
        run = await db.get_run("nonexistent-run")
        assert run is None  # Graceful handling of not found
```

---

## 3. API Integration Tests

### 3.1 Next.js API Route Tests

**File:** `tests/api/test_api_routes.test.ts`

```typescript
import { describe, it, expect, beforeAll, afterAll } from '@jest/globals'
import { createMocks } from 'node-mocks-http'

describe('/api/run endpoint', () => {
  it('should create run and trigger pipeline', async () => {
    const { req, res } = createMocks({
      method: 'POST',
      body: {
        blob_url: 'https://example.com/test.pdf',
        brand_id: 'lactalis-canada'
      }
    })

    // Mock Clerk auth
    jest.mock('@clerk/nextjs/server', () => ({
      auth: () => ({ userId: 'test-user-123' })
    }))

    const handler = await import('@/app/api/run/route')
    await handler.POST(req)

    expect(res._getStatusCode()).toBe(200)
    const json = JSON.parse(res._getData())
    expect(json.run_id).toBeDefined()
    expect(json.status).toBe('PENDING')
  })
})

describe('/api/status/[runId] endpoint', () => {
  it('should return run status from database', async () => {
    // Setup: Create test run in database
    const prisma = new PrismaClient()
    await prisma.run.create({
      data: {
        id: 'test-run-api-001',
        userId: 'test-user-123',
        companyId: 'lactalis-canada',
        companyName: 'Lactalis',
        documentName: 'test.pdf',
        documentUrl: 'https://example.com/test.pdf',
        status: 'RUNNING',
        currentStage: 2
      }
    })

    // Test: Fetch status
    const { req, res } = createMocks({
      method: 'GET',
      query: { runId: 'test-run-api-001' }
    })

    const handler = await import('@/app/api/status/[runId]/route')
    await handler.GET(req, { params: { runId: 'test-run-api-001' } })

    expect(res._getStatusCode()).toBe(200)
    const json = JSON.parse(res._getData())
    expect(json.status).toBe('RUNNING')
    expect(json.current_stage).toBe(2)
  })
})
```

---

## 4. Railway Environment Tests

### 4.1 Environment Validation Script

**File:** `tests/railway/test_environment.py`

```python
import os
import pytest
from pathlib import Path

class TestRailwayEnvironment:
    """Validate Railway deployment environment"""

    def test_required_env_vars(self):
        """Ensure all required environment variables are set"""
        required = [
            "DATABASE_URL",
            "OPENROUTER_API_KEY",
            "RAILWAY_ENVIRONMENT"
        ]

        for var in required:
            assert os.getenv(var), f"Missing required env var: {var}"

    def test_file_paths_accessible(self):
        """Ensure critical file paths are accessible"""
        # Brand profiles must be readable
        profiles_dir = Path("data/brand-profiles")
        assert profiles_dir.exists(), "Brand profiles directory missing"

        # Test YAML loading
        test_profile = profiles_dir / "lactalis-canada.yaml"
        assert test_profile.exists(), "Test brand profile missing"

        import yaml
        with open(test_profile) as f:
            data = yaml.safe_load(f)
        assert data["brand_name"] == "Lactalis"

    def test_temp_directory_writable(self):
        """Ensure temp directory is writable"""
        temp_file = Path("/tmp/railway-test.txt")
        temp_file.write_text("test")
        assert temp_file.exists()
        temp_file.unlink()

    def test_database_connection(self):
        """Validate database connection works"""
        import asyncpg
        import asyncio

        async def test_conn():
            conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            return result

        result = asyncio.run(test_conn())
        assert result == 1
```

---

## 5. Test Execution Strategy

### 5.1 Local Development Testing

```bash
# Run all unit tests (fast)
pytest tests/test_pipeline_stages.py -v

# Run integration tests (medium)
pytest tests/test_database_service.py -v
pytest tests/api/ -v

# Run E2E tests (slow, ~2 minutes)
pytest tests/test_pipeline_e2e.py -v

# Run all tests with coverage
pytest --cov=pipeline --cov=backend tests/
```

### 5.2 Pre-Deployment Testing (Railway)

```bash
# Test Railway environment before full deployment
railway run pytest tests/railway/test_environment.py

# Run E2E test against Railway staging database
DATABASE_URL=$RAILWAY_DATABASE_URL pytest tests/test_pipeline_e2e.py
```

### 5.3 CI/CD Integration (GitHub Actions)

**File:** `.github/workflows/test.yml`

```yaml
name: Integration Tests

on:
  push:
    branches: [main, hackaton]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Python dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install Node dependencies
        run: npm install

      - name: Run Prisma migrations
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres
        run: npx prisma migrate deploy

      - name: Run Python tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: pytest tests/ -v --cov=pipeline --cov=backend

      - name: Run TypeScript tests
        run: npm test
```

---

## 6. Acceptance Criteria

### Before Merging to Main

- ✅ All unit tests pass (100% of stage tests)
- ✅ All integration tests pass (database service + API routes)
- ✅ At least 1 E2E test passes (full pipeline execution)
- ✅ Railway environment tests pass
- ✅ Code coverage ≥70% for pipeline stages

### Before Production Deployment

- ✅ All tests pass on Railway staging environment
- ✅ Manual smoke test: Upload PDF → Verify 5 cards generated
- ✅ Database migration deployed successfully
- ✅ Rollback procedure tested and documented

---

## Next Steps

After implementing this test plan:

1. Run baseline tests against CURRENT pipeline (pre-database retrofit)
2. Capture known-good outputs in `tests/fixtures/expected-outputs/`
3. Implement database integration
4. Re-run tests to validate regression
5. Add new tests for database-specific features

**Estimated Implementation Time:** 4-6 hours (before starting Hour 1 of implementation roadmap)
