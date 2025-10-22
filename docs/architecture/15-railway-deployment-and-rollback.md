# 15. Railway Deployment Environment & Rollback Strategy

## Overview

This document addresses two critical brownfield concerns:
1. **Railway deployment environment differences** from local development
2. **Rollback strategy with feature flags** to revert to file-based pipeline if database fails

---

## Part 1: Railway Deployment Environment Configuration

### 1.1 Environment Differences: Local vs Railway

| Aspect | Local Development | Railway Production |
|--------|-------------------|---------------------|
| **File System** | Absolute paths `/Users/...` | Relative paths `/app/...` |
| **Database** | Local PostgreSQL or Railway proxy | Railway PostgreSQL (internal network) |
| **Brand Profiles** | `data/brand-profiles/*.yaml` | Same path (included in Docker image) |
| **Temp Files** | `/tmp/` | `/tmp/` (container temp directory) |
| **Logs** | Console + local files | Std

out → Railway logs |
| **Python Version** | User's system Python | Docker: Python 3.11 |
| **Environment Variables** | `.env` file | Railway dashboard |

### 1.2 Dockerfile for Railway Deployment

**File:** `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ /app/backend/
COPY pipeline/ /app/pipeline/
COPY data/ /app/data/

# Copy brand profiles (CRITICAL - needed for pipeline)
COPY data/brand-profiles/ /app/data/brand-profiles/

# Set Python path
ENV PYTHONPATH=/app

# Create temp directory for pipeline outputs
RUN mkdir -p /app/data/test-outputs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Start FastAPI server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.3 Environment Variables Configuration

**Railway Dashboard → Environment Variables:**

```bash
# Database (Railway PostgreSQL)
DATABASE_URL=postgresql://user:pass@railway.internal:5432/railway

# OpenRouter API
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Feature Flags (see Section 2)
ENABLE_DATABASE_WRITES=true
ENABLE_FILE_FALLBACK=true

# Logging
LOG_LEVEL=INFO
RAILWAY_ENVIRONMENT=production

# Prisma (for migrations)
DATABASE_URL_NON_POOLING=postgresql://user:pass@railway.internal:5432/railway
```

### 1.4 Path Resolution Strategy

**File:** `pipeline/utils/path_resolver.py`

```python
import os
from pathlib import Path

class PathResolver:
    """
    Resolve file paths for local vs Railway environments.
    """

    def __init__(self):
        self.is_railway = os.getenv("RAILWAY_ENVIRONMENT") == "production"
        self.base_dir = Path("/app") if self.is_railway else Path.cwd()

    def get_brand_profile_path(self, brand_id: str) -> Path:
        """Get path to brand YAML file."""
        return self.base_dir / "data" / "brand-profiles" / f"{brand_id}.yaml"

    def get_output_dir(self, run_id: str, stage: int) -> Path:
        """Get output directory for stage results."""
        output_dir = self.base_dir / "data" / "test-outputs" / run_id / f"stage{stage}"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def get_temp_dir(self) -> Path:
        """Get temporary directory for downloads."""
        return Path("/tmp")

# Global instance
path_resolver = PathResolver()
```

**Usage in Pipeline:**

```python
# Instead of hardcoded paths:
# ❌ profile_path = Path("data/brand-profiles/lactalis-canada.yaml")

# Use path resolver:
# ✅ profile_path = path_resolver.get_brand_profile_path("lactalis-canada")
```

### 1.5 Railway-Specific Testing

**File:** `tests/railway/test_railway_environment.sh`

```bash
#!/bin/bash
# Railway environment validation script

set -e

echo "🧪 Testing Railway Environment..."

# Test 1: Brand profiles accessible
echo "  ✓ Testing brand profile access..."
python -c "
import yaml
from pathlib import Path
profile = Path('/app/data/brand-profiles/lactalis-canada.yaml')
assert profile.exists(), 'Brand profile not found'
data = yaml.safe_load(profile.read_text())
assert data['brand_name'] == 'Lactalis', 'Invalid brand data'
print('    ✅ Brand profiles accessible')
"

# Test 2: Database connection
echo "  ✓ Testing database connection..."
python -c "
import asyncpg
import asyncio
import os

async def test():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    result = await conn.fetchval('SELECT 1')
    await conn.close()
    assert result == 1

asyncio.run(test())
print('    ✅ Database connection successful')
"

# Test 3: Temp directory writable
echo "  ✓ Testing temp directory..."
python -c "
from pathlib import Path
temp = Path('/tmp/railway-test.txt')
temp.write_text('test')
assert temp.exists()
temp.unlink()
print('    ✅ Temp directory writable')
"

# Test 4: Environment variables
echo "  ✓ Testing environment variables..."
python -c "
import os
required = ['DATABASE_URL', 'OPENROUTER_API_KEY', 'RAILWAY_ENVIRONMENT']
for var in required:
    assert os.getenv(var), f'Missing {var}'
print('    ✅ All required environment variables set')
"

echo "✅ Railway environment validation complete!"
```

**Run during Railway deployment:**

```bash
# In Railway build command
npm run build && ./tests/railway/test_railway_environment.sh
```

---

## Part 2: Rollback Strategy with Feature Flags

### 2.1 Feature Flag Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Feature Flag System                    │
│                                                          │
│  ENABLE_DATABASE_WRITES   = true/false                  │
│  ENABLE_FILE_FALLBACK     = true/false                  │
│                                                          │
│  Modes:                                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │ 1. Database-Only (Production Target)           │    │
│  │    ENABLE_DATABASE_WRITES=true                 │    │
│  │    ENABLE_FILE_FALLBACK=false                  │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ 2. Dual-Write (Transition Phase)               │    │
│  │    ENABLE_DATABASE_WRITES=true                 │    │
│  │    ENABLE_FILE_FALLBACK=true                   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ 3. File-Only (Rollback/Emergency)              │    │
│  │    ENABLE_DATABASE_WRITES=false                │    │
│  │    ENABLE_FILE_FALLBACK=true                   │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Feature Flag Implementation

**File:** `pipeline/utils/feature_flags.py`

```python
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class FeatureFlags:
    """
    Centralized feature flag management for rollback control.
    """

    def __init__(self):
        self.database_writes_enabled = self._parse_bool("ENABLE_DATABASE_WRITES", default=True)
        self.file_fallback_enabled = self._parse_bool("ENABLE_FILE_FALLBACK", default=True)

    def _parse_bool(self, env_var: str, default: bool) -> bool:
        """Parse boolean from environment variable."""
        value = os.getenv(env_var)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def should_write_to_database(self) -> bool:
        """Check if pipeline should write to database."""
        return self.database_writes_enabled

    def should_write_to_files(self) -> bool:
        """Check if pipeline should write to files."""
        return self.file_fallback_enabled

    def get_mode(self) -> str:
        """Get current operational mode."""
        if self.database_writes_enabled and not self.file_fallback_enabled:
            return "DATABASE_ONLY"
        elif self.database_writes_enabled and self.file_fallback_enabled:
            return "DUAL_WRITE"
        elif not self.database_writes_enabled and self.file_fallback_enabled:
            return "FILE_ONLY"
        else:
            logger.warning("Invalid feature flag configuration: Both writes disabled")
            return "INVALID"

    def log_configuration(self):
        """Log current feature flag configuration."""
        logger.info(f"Feature Flags Configuration:")
        logger.info(f"  Mode: {self.get_mode()}")
        logger.info(f"  Database Writes: {self.database_writes_enabled}")
        logger.info(f"  File Fallback: {self.file_fallback_enabled}")

# Global instance
feature_flags = FeatureFlags()
```

### 2.3 Modified Pipeline Orchestrator with Feature Flags

```python
# pipeline/orchestrator.py (UPDATED)

from pipeline.utils.feature_flags import feature_flags

class PipelineOrchestrator:
    def __init__(self, db_service: Optional[DatabaseService] = None):
        self.db_service = db_service
        feature_flags.log_configuration()  # Log mode on startup

    async def execute_full_pipeline(
        self,
        document_path: str,
        brand_id: str,
        run_id: str,
        user_id: Optional[str] = None
    ) -> Dict:
        try:
            # Stage 1 execution
            stage1_result = await stage1.execute(...)

            # FEATURE FLAG CHECK: Database write
            if feature_flags.should_write_to_database() and self.db_service:
                await self.db_service.save_inspiration_report(...)
                logger.info(f"[{run_id}] Wrote Stage 1 to database")

            # FEATURE FLAG CHECK: File write
            if feature_flags.should_write_to_files():
                output_dir = path_resolver.get_output_dir(run_id, 1)
                with open(output_dir / "inspirations.json", "w") as f:
                    json.dump(stage1_result, f, indent=2)
                logger.info(f"[{run_id}] Wrote Stage 1 to file")

            # ... continue with other stages ...

        except Exception as e:
            logger.error(f"[{run_id}] Pipeline failed: {str(e)}")

            # Mark run as FAILED (only if database writes enabled)
            if feature_flags.should_write_to_database() and self.db_service:
                await self.db_service.fail_run(run_id, str(e))

            return {"status": "FAILED", "error_message": str(e)}
```

### 2.4 Rollback Procedures

#### Scenario 1: Database Connection Failures

**Symptoms:**
- Pipeline runs fail with "connection timeout" errors
- Railway logs show `asyncpg.exceptions.ConnectionDoesNotExistError`

**Rollback Steps:**

```bash
# 1. Disable database writes immediately (Railway dashboard)
ENABLE_DATABASE_WRITES=false
ENABLE_FILE_FALLBACK=true

# 2. Verify rollback
railway logs --tail 100 | grep "Feature Flags Configuration"
# Expected: "Mode: FILE_ONLY"

# 3. Test pipeline execution
curl -X POST https://your-railway-app.up.railway.app/run \
  -H "Content-Type: application/json" \
  -d '{"run_id":"test","blob_url":"...","company_id":"lactalis-canada","user_id":"test"}'

# 4. Monitor logs
railway logs --tail 100
# Should see: "Wrote Stage 1 to file" (NO database writes)

# 5. Investigate database issue
railway logs --service postgres
```

#### Scenario 2: Database Schema Mismatch

**Symptoms:**
- Pipeline fails with `column "clerkId" does not exist` or similar PostgreSQL errors

**Rollback Steps:**

```bash
# 1. Immediate rollback to file-only mode
ENABLE_DATABASE_WRITES=false
ENABLE_FILE_FALLBACK=true

# 2. Fix Prisma schema
# Edit prisma/schema.prisma

# 3. Deploy migration
npx prisma migrate deploy

# 4. Re-enable database writes
ENABLE_DATABASE_WRITES=true

# 5. Test with single pipeline run
```

#### Scenario 3: Slow Database Performance

**Symptoms:**
- Pipeline execution time doubles
- Railway database CPU at 100%

**Rollback Steps:**

```bash
# Option A: Dual-write mode (database + files)
ENABLE_DATABASE_WRITES=true
ENABLE_FILE_FALLBACK=true
# Allows time to optimize database while keeping file-based backups

# Option B: Full rollback to file-only
ENABLE_DATABASE_WRITES=false
ENABLE_FILE_FALLBACK=true

# Investigate performance
railway logs --service postgres
# Check connection pool size, slow queries
```

### 2.5 Rollback Testing Procedure

**File:** `tests/rollback/test_rollback_scenarios.py`

```python
import pytest
import os
from pipeline.orchestrator import PipelineOrchestrator
from pipeline.utils.feature_flags import FeatureFlags

class TestRollbackScenarios:
    """Test rollback scenarios with feature flags."""

    @pytest.mark.asyncio
    async def test_file_only_mode(self, monkeypatch):
        """Simulate rollback to file-only mode."""
        # Set feature flags
        monkeypatch.setenv("ENABLE_DATABASE_WRITES", "false")
        monkeypatch.setenv("ENABLE_FILE_FALLBACK", "true")

        flags = FeatureFlags()
        assert flags.get_mode() == "FILE_ONLY"

        # Run pipeline
        orchestrator = PipelineOrchestrator(db_service=None)
        result = await orchestrator.execute_full_pipeline(
            document_path="tests/fixtures/sample-report.pdf",
            brand_id="lactalis-canada",
            run_id="rollback-test-001"
        )

        # Verify file was created (no database writes)
        from pathlib import Path
        output_file = Path("data/test-outputs/rollback-test-001/stage1/inspirations.json")
        assert output_file.exists()

        assert result["status"] == "COMPLETED"

    @pytest.mark.asyncio
    async def test_database_failure_fallback(self, monkeypatch):
        """Test automatic fallback when database write fails."""
        monkeypatch.setenv("ENABLE_DATABASE_WRITES", "true")
        monkeypatch.setenv("ENABLE_FILE_FALLBACK", "true")

        # Mock database service that fails
        class FailingDatabaseService:
            async def save_inspiration_report(self, *args, **kwargs):
                raise Exception("Database connection failed")

        orchestrator = PipelineOrchestrator(db_service=FailingDatabaseService())
        result = await orchestrator.execute_full_pipeline(
            document_path="tests/fixtures/sample-report.pdf",
            brand_id="lactalis-canada",
            run_id="rollback-test-002"
        )

        # Should still succeed with file fallback
        from pathlib import Path
        output_file = Path("data/test-outputs/rollback-test-002/stage1/inspirations.json")
        assert output_file.exists()
```

### 2.6 Monitoring & Alerting

**Railway Healthcheck Endpoint:**

**File:** `backend/app/routers/health.py`

```python
from fastapi import APIRouter
from backend.app.services.database_service import DatabaseService
from pipeline.utils.feature_flags import feature_flags
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """
    Health check endpoint for Railway.

    Returns system status including feature flags and database connectivity.
    """
    status = {
        "status": "healthy",
        "mode": feature_flags.get_mode(),
        "database_writes": feature_flags.should_write_to_database(),
        "file_fallback": feature_flags.should_write_to_files(),
        "database_connection": "unknown"
    }

    # Test database connection if enabled
    if feature_flags.should_write_to_database():
        try:
            db = DatabaseService()
            pool = await db.get_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            status["database_connection"] = "healthy"
            await db.close_pool()
        except Exception as e:
            status["database_connection"] = "failed"
            status["database_error"] = str(e)
            logger.error(f"Database health check failed: {e}")
            # Don't fail entire health check - file fallback can still work

    return status
```

**Railway Monitoring Dashboard:**

```bash
# Check health endpoint
curl https://your-app.up.railway.app/health

# Expected response (healthy):
{
  "status": "healthy",
  "mode": "DUAL_WRITE",
  "database_writes": true,
  "file_fallback": true,
  "database_connection": "healthy"
}

# Rollback response (FILE_ONLY mode):
{
  "status": "healthy",
  "mode": "FILE_ONLY",
  "database_writes": false,
  "file_fallback": true,
  "database_connection": "skipped"
}
```

---

## Part 3: Deployment Checklist

### Pre-Deployment

- [ ] Run Railway environment tests locally: `./tests/railway/test_railway_environment.sh`
- [ ] Verify Dockerfile builds: `docker build -t innovation-pipeline backend/`
- [ ] Test Docker image locally: `docker run -p 8000:8000 innovation-pipeline`
- [ ] Verify brand profiles copied: `docker exec <container> ls /app/data/brand-profiles/`

### During Deployment

- [ ] Deploy to Railway staging first
- [ ] Set feature flags to DUAL_WRITE mode: `ENABLE_DATABASE_WRITES=true ENABLE_FILE_FALLBACK=true`
- [ ] Run migration: `npx prisma migrate deploy`
- [ ] Test health endpoint: `curl https://staging.railway.app/health`
- [ ] Run single pipeline test
- [ ] Monitor logs for 30 minutes

### Post-Deployment

- [ ] Gradually reduce file writes (optional): `ENABLE_FILE_FALLBACK=false` after 1 week of stable operation
- [ ] Monitor database performance metrics
- [ ] Set up Railway alerts for database connection failures
- [ ] Document rollback decision matrix for on-call team

---

## Part 4: Rollback Decision Matrix

| Issue | Severity | Rollback Action | Timeline |
|-------|----------|-----------------|----------|
| Database connection timeout | 🔴 Critical | `ENABLE_DATABASE_WRITES=false` | Immediate (5 min) |
| Slow database queries | 🟡 Medium | Enable `ENABLE_FILE_FALLBACK=true`, investigate | 1 hour |
| Schema mismatch error | 🔴 Critical | `ENABLE_DATABASE_WRITES=false`, fix migration | Immediate (15 min) |
| Prisma OOM error | 🟡 Medium | Restart service, monitor | 30 min |
| File system full | 🟡 Medium | Disable `ENABLE_FILE_FALLBACK=false` | 1 hour |
| Database at 90% CPU | 🟡 Medium | Dual-write mode, optimize queries | 2 hours |

---

## Summary

### Deployment Environment

✅ **Dockerfile** ensures consistent Python 3.11 environment
✅ **PathResolver** handles local vs Railway path differences
✅ **Environment validation** script catches deployment errors early
✅ **Brand profiles** copied into Docker image

### Rollback Strategy

✅ **3 operational modes:** Database-only, Dual-write, File-only
✅ **Feature flags** enable instant rollback without code deployment
✅ **Health endpoint** monitors system status
✅ **Automated testing** for rollback scenarios

### Risk Mitigation

- ✅ Zero breaking changes during transition (dual-write mode)
- ✅ Instant rollback capability (toggle environment variable)
- ✅ File-based fallback preserves pipeline functionality
- ✅ Monitoring and alerts for proactive issue detection

**Next Steps:** Implement feature flags in `pipeline/orchestrator.py` and test rollback scenarios before Railway deployment.
