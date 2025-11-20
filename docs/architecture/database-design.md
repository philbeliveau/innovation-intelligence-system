# Database Design Guide

## Overview

This guide defines the database schema, indexing strategy, and operational patterns for the experiments tracking database. Extracted from Story 11.4 to separate requirements from technical specifications.

**Target Story:** 11.4 - Experiment Tracking Database
**Purpose:** Store all pipeline experimentation runs for analysis and improvement tracking

---

## Database Schema

### Experiments Table (PostgreSQL)

```sql
CREATE TABLE experiments (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Run Identification
    run_id VARCHAR(255) UNIQUE NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),

    -- Input Data
    report_text TEXT,  -- Full PDF text (may be large)
    report_name VARCHAR(500),  -- Original filename

    -- Brand Profile (JSONB for flexibility)
    brand_profile JSONB NOT NULL,

    -- Pipeline Outputs (JSONB for all 7 stages)
    stage_outputs JSONB NOT NULL,

    -- User Assessment
    experiment_notes TEXT,
    quality_tag VARCHAR(20) CHECK (quality_tag IN ('good', 'needs_work', 'failed')),

    -- Metadata
    pipeline_version VARCHAR(50),
    execution_time_seconds INTEGER,
    token_usage JSONB,  -- Per-stage token tracking
    cost_usd DECIMAL(10, 4),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_experiments_updated_at
BEFORE UPDATE ON experiments
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

## JSONB Structure Specifications

### brand_profile Column

```json
{
  "brand_name": "Lactalis Canada",
  "industry": "Dairy & Food Products",
  "country": "Canada",
  "product_portfolio": [
    "Milk (2%, whole, skim)",
    "Cheese (cheddar, mozzarella, brie)",
    "Yogurt (Greek, regular, probiotic)"
  ],
  "positioning": "Premium quality dairy products for Canadian families",
  "enrichment": {
    "recent_news": ["optional"],
    "competitive_landscape": "optional",
    "confidence_score": 0.85
  }
}
```

### stage_outputs Column

```json
{
  "stage_0": {
    "brand_context": { },
    "execution_time_ms": 1234,
    "tokens": {"input": 500, "output": 300}
  },
  "stage_1": {
    "trends": [ ],
    "execution_time_ms": 8932,
    "tokens": {"input": 8234, "output": 1567}
  },
  "stage_2": {
    "insights": [ ],
    "execution_time_ms": 5421,
    "tokens": {"input": 6123, "output": 1234}
  },
  "stage_3": {
    "matched_techniques": [ ],
    "execution_time_ms": 3892,
    "tokens": {"input": 4567, "output": 987}
  },
  "stage_4": {
    "concepts": [ ],
    "execution_time_ms": 6234,
    "tokens": {"input": 7891, "output": 1876}
  },
  "stage_5": {
    "competitive_intel": [ ],
    "execution_time_ms": 4123,
    "tokens": {"input": 3456, "output": 654}
  },
  "stage_6": {
    "opportunity_cards_markdown": "...",
    "execution_time_ms": 2345,
    "tokens": {"input": 5678, "output": 1234}
  }
}
```

### token_usage Column

```json
{
  "total_input_tokens": 50123,
  "total_output_tokens": 28945,
  "by_stage": {
    "stage_0": {"input": 500, "output": 300},
    "stage_1": {"input": 8234, "output": 1567},
    "stage_2": {"input": 6123, "output": 1234},
    "stage_3": {"input": 4567, "output": 987},
    "stage_4": {"input": 7891, "output": 1876},
    "stage_5": {"input": 3456, "output": 654},
    "stage_6": {"input": 5678, "output": 1234}
  },
  "model_used": "anthropic/claude-3-opus-20240229",
  "estimated_cost_usd": 0.82
}
```

---

## Index Strategy

### Performance Indexes

```sql
-- 1. Timestamp index (for date range queries)
CREATE INDEX idx_experiments_timestamp
ON experiments(timestamp DESC);

-- 2. Quality tag index (for filtering by quality)
CREATE INDEX idx_experiments_quality_tag
ON experiments(quality_tag);

-- 3. Run ID index (for unique lookups - already UNIQUE constraint provides this)
-- No additional index needed

-- 4. Brand name index (JSONB field access)
CREATE INDEX idx_experiments_brand_name
ON experiments((brand_profile->>'brand_name'));

-- 5. Industry index (JSONB field access)
CREATE INDEX idx_experiments_industry
ON experiments((brand_profile->>'industry'));

-- 6. Pipeline version index (for version comparison)
CREATE INDEX idx_experiments_pipeline_version
ON experiments(pipeline_version);

-- 7. Composite index for common query patterns
CREATE INDEX idx_experiments_quality_timestamp
ON experiments(quality_tag, timestamp DESC);
```

### Index Usage Examples

```sql
-- Fast: Uses idx_experiments_timestamp
SELECT * FROM experiments
WHERE timestamp > '2025-11-01'
ORDER BY timestamp DESC
LIMIT 20;

-- Fast: Uses idx_experiments_quality_tag
SELECT * FROM experiments
WHERE quality_tag = 'good';

-- Fast: Uses idx_experiments_brand_name (JSONB index)
SELECT * FROM experiments
WHERE brand_profile->>'brand_name' = 'Lactalis Canada';

-- Fast: Uses composite index
SELECT * FROM experiments
WHERE quality_tag = 'good'
  AND timestamp > '2025-11-01'
ORDER BY timestamp DESC;
```

---

## Prisma Schema

### Schema Definition

**File:** `/backend/prisma/schema.prisma`

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-py"
  recursive_type_depth = 5
}

model Experiment {
  id                    String   @id @default(uuid())
  runId                 String   @unique @map("run_id")
  timestamp             DateTime @default(now())

  reportText            String?  @map("report_text")
  reportName            String?  @map("report_name")

  brandProfile          Json     @map("brand_profile")
  stageOutputs          Json     @map("stage_outputs")

  experimentNotes       String?  @map("experiment_notes")
  qualityTag            String?  @map("quality_tag")

  pipelineVersion       String?  @map("pipeline_version")
  executionTimeSeconds  Int?     @map("execution_time_seconds")
  tokenUsage            Json?    @map("token_usage")
  costUsd               Decimal? @map("cost_usd") @db.Decimal(10, 4)

  createdAt             DateTime @default(now()) @map("created_at")
  updatedAt             DateTime @updatedAt @map("updated_at")

  @@index([timestamp(sort: Desc)])
  @@index([qualityTag])
  @@index([pipelineVersion])
  @@map("experiments")
}
```

### Migration Command

```bash
# Create migration
npx prisma migrate dev --name add_experiments_table

# Apply to production
npx prisma migrate deploy
```

---

## Database Operations

### Save Experiment (PrismaAPIClient Extension)

```python
from prisma import Prisma
from datetime import datetime
import json

class ExperimentsManager:
    def __init__(self, prisma_client: Prisma):
        self.db = prisma_client

    async def save_experiment(
        self,
        run_id: str,
        report_text: str,
        report_name: str,
        brand_profile: dict,
        stage_outputs: dict,
        quality_tag: str = None,
        notes: str = None,
        execution_time: int = None,
        token_usage: dict = None,
        cost_usd: float = None,
        pipeline_version: str = "1.0"
    ):
        """
        Save complete pipeline experiment to database

        Args:
            run_id: Unique run identifier
            report_text: Full PDF text
            report_name: Original filename
            brand_profile: Brand context dict
            stage_outputs: All 7 stage outputs
            quality_tag: "good" | "needs_work" | "failed" | None
            notes: User notes
            execution_time: Total seconds
            token_usage: Token tracking dict
            cost_usd: Estimated cost
            pipeline_version: Pipeline version

        Returns:
            Created experiment record
        """

        experiment = await self.db.experiment.create({
            "data": {
                "runId": run_id,
                "reportText": report_text,
                "reportName": report_name,
                "brandProfile": brand_profile,
                "stageOutputs": stage_outputs,
                "qualityTag": quality_tag,
                "experimentNotes": notes,
                "executionTimeSeconds": execution_time,
                "tokenUsage": token_usage,
                "costUsd": cost_usd,
                "pipelineVersion": pipeline_version
            }
        })

        return experiment
```

### Retrieve Experiments

```python
async def get_experiments(
    self,
    quality_tag: str = None,
    brand_name: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = 20,
    offset: int = 0,
    order_by: str = "timestamp_desc"
):
    """
    Query experiments with flexible filters

    Args:
        quality_tag: Filter by quality ("good", "needs_work", "failed")
        brand_name: Filter by brand name
        start_date: Filter by timestamp >= start_date
        end_date: Filter by timestamp <= end_date
        limit: Max results to return
        offset: Skip N results (for pagination)
        order_by: Sort order ("timestamp_desc", "timestamp_asc", "cost_desc")

    Returns:
        List of experiment records
    """

    # Build where clause
    where = {}

    if quality_tag:
        where["qualityTag"] = quality_tag

    if start_date or end_date:
        where["timestamp"] = {}
        if start_date:
            where["timestamp"]["gte"] = start_date
        if end_date:
            where["timestamp"]["lte"] = end_date

    # Note: brand_name filtering requires raw SQL for JSONB
    # Use Prisma raw query for JSONB filters

    experiments = await self.db.experiment.find_many(
        where=where,
        take=limit,
        skip=offset,
        order={"timestamp": "desc" if "desc" in order_by else "asc"}
    )

    # Post-filter by brand name (if needed)
    if brand_name:
        experiments = [
            exp for exp in experiments
            if exp.brandProfile.get("brand_name") == brand_name
        ]

    return experiments

async def get_experiment_by_run_id(self, run_id: str):
    """Get single experiment by run_id"""
    return await self.db.experiment.find_unique(
        where={"runId": run_id}
    )

async def count_experiments(self, quality_tag: str = None):
    """Count total experiments with optional quality filter"""
    where = {"qualityTag": quality_tag} if quality_tag else {}
    return await self.db.experiment.count(where=where)
```

---

## Export Functionality

### JSON Export

```python
import json
from pathlib import Path

class ExperimentExporter:
    def __init__(self, experiments_manager):
        self.manager = experiments_manager

    async def export_to_json(
        self,
        output_path: str,
        quality_tag: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ):
        """
        Export experiments to JSON file

        Args:
            output_path: Path to output JSON file
            quality_tag: Optional quality filter
            start_date: Optional date range start
            end_date: Optional date range end

        Returns:
            Path to exported file
        """

        experiments = await self.manager.get_experiments(
            quality_tag=quality_tag,
            start_date=start_date,
            end_date=end_date,
            limit=1000  # Large limit for bulk export
        )

        # Convert to dict
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_experiments": len(experiments),
            "filters": {
                "quality_tag": quality_tag,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "experiments": [
                {
                    "run_id": exp.runId,
                    "timestamp": exp.timestamp.isoformat(),
                    "brand_profile": exp.brandProfile,
                    "stage_outputs": exp.stageOutputs,
                    "quality_tag": exp.qualityTag,
                    "notes": exp.experimentNotes,
                    "execution_time_seconds": exp.executionTimeSeconds,
                    "token_usage": exp.tokenUsage,
                    "cost_usd": float(exp.costUsd) if exp.costUsd else None
                }
                for exp in experiments
            ]
        }

        # Write to file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        return output_path
```

### CSV Export

```python
import csv
import json

async def export_to_csv(
    self,
    output_path: str,
    quality_tag: str = None,
    start_date: datetime = None,
    end_date: datetime = None
):
    """
    Export experiments to CSV (flattened structure)

    Note: JSONB fields (brand_profile, stage_outputs) converted to JSON strings
    """

    experiments = await self.manager.get_experiments(
        quality_tag=quality_tag,
        start_date=start_date,
        end_date=end_date,
        limit=1000
    )

    # Define CSV columns
    fieldnames = [
        'run_id',
        'timestamp',
        'brand_name',
        'industry',
        'country',
        'quality_tag',
        'execution_time_seconds',
        'total_tokens',
        'cost_usd',
        'pipeline_version',
        'notes',
        'stage_outputs_json'
    ]

    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for exp in experiments:
            total_tokens = (
                exp.tokenUsage.get('total_input_tokens', 0) +
                exp.tokenUsage.get('total_output_tokens', 0)
                if exp.tokenUsage else 0
            )

            writer.writerow({
                'run_id': exp.runId,
                'timestamp': exp.timestamp.isoformat(),
                'brand_name': exp.brandProfile.get('brand_name', ''),
                'industry': exp.brandProfile.get('industry', ''),
                'country': exp.brandProfile.get('country', ''),
                'quality_tag': exp.qualityTag or '',
                'execution_time_seconds': exp.executionTimeSeconds or 0,
                'total_tokens': total_tokens,
                'cost_usd': float(exp.costUsd) if exp.costUsd else 0,
                'pipeline_version': exp.pipelineVersion or '1.0',
                'notes': exp.experimentNotes or '',
                'stage_outputs_json': json.dumps(exp.stageOutputs)
            })

    return output_path
```

---

## Data Retention Policy

### Configuration

```python
# Environment variable
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "365"))  # Default 1 year

# Retention script
async def cleanup_old_experiments(
    prisma_client: Prisma,
    retention_days: int = 365,
    archive_before_delete: bool = True
):
    """
    Delete experiments older than retention period

    Args:
        prisma_client: Prisma database client
        retention_days: Keep experiments for N days
        archive_before_delete: Export to JSON before deletion
    """

    cutoff_date = datetime.now() - timedelta(days=retention_days)

    # Find old experiments
    old_experiments = await prisma_client.experiment.find_many(
        where={"timestamp": {"lt": cutoff_date}}
    )

    if not old_experiments:
        print(f"No experiments older than {retention_days} days found.")
        return

    print(f"Found {len(old_experiments)} experiments to delete.")

    # Archive if requested
    if archive_before_delete:
        archive_path = f"/backend/archives/experiments_{datetime.now().strftime('%Y%m%d')}.json"
        exporter = ExperimentExporter(ExperimentsManager(prisma_client))
        await exporter.export_to_json(
            archive_path,
            end_date=cutoff_date
        )
        print(f"Archived to {archive_path}")

    # Delete
    deleted = await prisma_client.experiment.delete_many(
        where={"timestamp": {"lt": cutoff_date}}
    )

    print(f"Deleted {deleted} old experiments.")
```

---

## Backup Strategy

### Railway PostgreSQL Backups (Automatic)

Railway provides daily snapshots:
- **Frequency:** Daily
- **Retention:** 7 days (free tier), 30 days (paid)
- **Access:** Railway dashboard → Database → Backups

### Manual Backup to Vercel Blob

```python
from vercel_blob import put

async def backup_to_vercel_blob(prisma_client: Prisma):
    """
    Manual backup of experiments table to Vercel Blob Storage
    """

    # Export to JSON
    exporter = ExperimentExporter(ExperimentsManager(prisma_client))
    temp_path = f"/tmp/experiments_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    await exporter.export_to_json(temp_path)

    # Upload to Vercel Blob
    with open(temp_path, 'rb') as f:
        blob_url = put(
            f"backups/experiments_{datetime.now().strftime('%Y%m%d')}.json",
            f.read(),
            token=os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")
        )

    print(f"Backup uploaded to: {blob_url}")
    return blob_url
```

### Restore from Backup

```python
async def restore_from_backup(prisma_client: Prisma, backup_file_path: str):
    """
    Restore experiments from JSON backup file
    """

    with open(backup_file_path, 'r') as f:
        backup_data = json.load(f)

    experiments = backup_data.get("experiments", [])

    print(f"Restoring {len(experiments)} experiments...")

    manager = ExperimentsManager(prisma_client)

    for exp_data in experiments:
        try:
            await manager.save_experiment(
                run_id=exp_data["run_id"],
                report_text=exp_data.get("report_text", ""),
                report_name=exp_data.get("report_name", ""),
                brand_profile=exp_data["brand_profile"],
                stage_outputs=exp_data["stage_outputs"],
                quality_tag=exp_data.get("quality_tag"),
                notes=exp_data.get("notes"),
                execution_time=exp_data.get("execution_time_seconds"),
                token_usage=exp_data.get("token_usage"),
                cost_usd=exp_data.get("cost_usd")
            )
        except Exception as e:
            print(f"Error restoring {exp_data['run_id']}: {e}")

    print("Restore complete.")
```

---

## Configuration Summary

```python
# /backend/experimentation/config.py

class DatabaseConfig:
    """Database configuration for experiments"""

    # Connection
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///experiments.db")

    # Retention
    RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "365"))
    AUTO_CLEANUP_ENABLED = os.getenv("AUTO_CLEANUP_ENABLED", "false").lower() == "true"

    # Backup
    BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
    BACKUP_FREQUENCY = os.getenv("BACKUP_FREQUENCY", "daily")  # daily | weekly
    BACKUP_LOCATION = os.getenv("BACKUP_LOCATION", "vercel_blob")  # vercel_blob | railway

    # Performance
    QUERY_TIMEOUT_SECONDS = int(os.getenv("QUERY_TIMEOUT_SECONDS", "30"))
    MAX_RESULTS_PER_QUERY = int(os.getenv("MAX_RESULTS_PER_QUERY", "1000"))
```

---

## Testing Checklist

- [ ] Schema creates successfully on first run
- [ ] Save operation stores all fields correctly
- [ ] JSONB fields queryable with nested access
- [ ] Indexes improve query performance (verify with EXPLAIN)
- [ ] Retrieve operations filter correctly by quality tag
- [ ] Retrieve operations filter correctly by date range
- [ ] Retrieve operations filter correctly by brand name (JSONB)
- [ ] Pagination works correctly (limit + offset)
- [ ] JSON export produces valid file
- [ ] CSV export flattens JSONB correctly
- [ ] Cleanup script archives before deletion
- [ ] Backup to Vercel Blob succeeds
- [ ] Restore from backup recreates experiments

---

## References

- **Story 11.4:** `/docs/stories/11.4.experiment-database.md`
- **Prisma Client:** `/backend/app/prisma_client.py`
- **Prisma Schema:** `/backend/prisma/schema.prisma`
- **PRD Section:** "Single Table Schema" (lines 268-279)
