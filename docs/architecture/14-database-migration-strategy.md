# 14. Database Migration Strategy: File-Based → PostgreSQL

## Overview

This document defines the migration path from the existing file-based pipeline output system (`data/test-outputs/`) to the new PostgreSQL database architecture.

## Current State vs Target State

### Current: File-Based System

```
data/
  test-outputs/
    {run_id}/
      stage1/
        inspirations.json          # 2 inspiration objects
      stage2/
        trends.json                # Extracted trends
      stage3/
        lessons.json               # Universal lessons
      stage4/
        context.json               # Brand-specific context
      stage5/
        opportunity-1.md           # 5 separate markdown files
        opportunity-2.md
        opportunity-3.md
        opportunity-4.md
        opportunity-5.md
```

### Target: PostgreSQL Database

```sql
-- 5 Tables (see Architecture Section 3.5.3)
User
Run
OpportunityCard (5 records per run)
InspirationReport (1 record per run)
StageOutput (5 records per run, one per stage)
```

---

## Migration Strategy: Hybrid Approach

**Philosophy:** Dual-write during transition, gradual deprecation of file-based system.

### Phase 1: Database Introduction (Week 1)

**Action:** Add database writes ALONGSIDE existing file writes

```python
# Stage 1 Executor (Modified)
class Stage1Executor:
    def __init__(self, db_service=None):
        self.db_service = db_service  # Optional during transition

    async def execute(self, document_path, run_id):
        # ... existing LLM processing ...

        result = {
            "inspirations": [
                {"title": "...", "content": "...", "key_elements": [...]},
                {"title": "...", "content": "...", "key_elements": [...]}
            ]
        }

        # 1. EXISTING: Write to file (KEEP for backward compatibility)
        output_dir = Path(f"data/test-outputs/{run_id}/stage1")
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "inspirations.json", "w") as f:
            json.dump(result, f, indent=2)

        # 2. NEW: Write to database (if available)
        if self.db_service:
            await self.db_service.create_inspiration_report(
                run_id=run_id,
                inspiration1_title=result["inspirations"][0]["title"],
                inspiration1_content=result["inspirations"][0]["content"],
                inspiration1_elements=result["inspirations"][0]["key_elements"],
                inspiration2_title=result["inspirations"][1]["title"],
                inspiration2_content=result["inspirations"][1]["content"],
                inspiration2_elements=result["inspirations"][1]["key_elements"]
            )

        return result
```

**Benefits:**
- ✅ Zero breaking changes (file-based still works)
- ✅ Database can be tested in parallel
- ✅ Rollback = disable database writes, keep file writes

### Phase 2: Database-First Reads (Week 2)

**Action:** Read from database first, fallback to files if not found

```python
# Stage 2 Executor (Modified)
class Stage2Executor:
    async def execute(self, run_id):
        stage1_output = None

        # Try database first
        if self.db_service:
            inspiration_report = await self.db_service.get_inspiration_report(run_id)
            if inspiration_report:
                stage1_output = {
                    "inspirations": [
                        {
                            "title": inspiration_report["inspiration1_title"],
                            "content": inspiration_report["inspiration1_content"],
                            "key_elements": inspiration_report["inspiration1_elements"]
                        },
                        {
                            "title": inspiration_report["inspiration2_title"],
                            "content": inspiration_report["inspiration2_content"],
                            "key_elements": inspiration_report["inspiration2_elements"]
                        }
                    ]
                }

        # Fallback to file if database read failed
        if not stage1_output:
            file_path = Path(f"data/test-outputs/{run_id}/stage1/inspirations.json")
            if file_path.exists():
                with open(file_path) as f:
                    stage1_output = json.load(f)

        if not stage1_output:
            raise FileNotFoundError(f"No Stage 1 output found for run {run_id}")

        # ... continue with Stage 2 processing ...
```

### Phase 3: File Deprecation (Week 3+)

**Action:** Remove file writes, database-only mode

```python
# Stage 1 Executor (Final)
class Stage1Executor:
    def __init__(self, db_service):
        self.db_service = db_service  # REQUIRED, no longer optional

    async def execute(self, document_path, run_id):
        # ... LLM processing ...

        # Database-only write
        await self.db_service.create_inspiration_report(...)

        return result
```

---

## Backfill Script: Migrate Existing Files to Database

**File:** `scripts/migrate_files_to_database.py`

```python
#!/usr/bin/env python3
"""
Migrate existing file-based pipeline outputs to PostgreSQL database.

Usage:
    python scripts/migrate_files_to_database.py --run-id <run_id>
    python scripts/migrate_files_to_database.py --all  # Migrate all runs in data/test-outputs/
"""

import asyncio
import json
import yaml
from pathlib import Path
from typing import List, Dict
import asyncpg
import argparse

class FileToDBMigrator:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None

    async def connect(self):
        """Initialize database connection pool"""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )

    async def disconnect(self):
        """Close connection pool"""
        await self.pool.close()

    async def migrate_run(self, run_id: str, user_id: str = "migration-user"):
        """
        Migrate a single run from files to database.

        Args:
            run_id: The run ID (e.g., "test-run-001")
            user_id: User ID to assign ownership (default: migration-user)
        """
        run_dir = Path(f"data/test-outputs/{run_id}")

        if not run_dir.exists():
            print(f"❌ Run directory not found: {run_dir}")
            return False

        print(f"📂 Migrating run: {run_id}")

        try:
            # 1. Create Run record
            await self._create_run_record(run_id, user_id, run_dir)

            # 2. Migrate Stage 1 (InspirationReport)
            await self._migrate_stage1(run_id)

            # 3. Migrate Stage 5 (OpportunityCards)
            await self._migrate_stage5(run_id, user_id)

            # 4. Migrate all stage outputs (StageOutput)
            await self._migrate_stage_outputs(run_id)

            print(f"✅ Successfully migrated run: {run_id}")
            return True

        except Exception as e:
            print(f"❌ Migration failed for {run_id}: {e}")
            return False

    async def _create_run_record(self, run_id: str, user_id: str, run_dir: Path):
        """Create Run record in database"""
        # Try to infer metadata from directory structure
        company_id = "unknown"  # Default
        document_name = "migrated-document.pdf"

        # Check if brand profile can be inferred from context files
        stage4_file = run_dir / "stage4" / "context.json"
        if stage4_file.exists():
            with open(stage4_file) as f:
                stage4_data = json.load(f)
                if "brand_id" in stage4_data:
                    company_id = stage4_data["brand_id"]

        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO "Run" (
                    id, "userId", "companyId", "companyName", "documentName",
                    "documentUrl", status, "currentStage", "createdAt",
                    "updatedAt", "completedAt"
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW(), NOW())
                ON CONFLICT (id) DO NOTHING
            """, run_id, user_id, company_id, company_id.replace("-", " ").title(),
                 document_name, f"https://migrated/{run_id}", "COMPLETED", 5)

        print(f"  ✅ Created Run record")

    async def _migrate_stage1(self, run_id: str):
        """Migrate Stage 1 inspirations.json → InspirationReport table"""
        stage1_file = Path(f"data/test-outputs/{run_id}/stage1/inspirations.json")

        if not stage1_file.exists():
            print(f"  ⚠️  Stage 1 file not found, skipping")
            return

        with open(stage1_file) as f:
            data = json.load(f)

        inspirations = data.get("inspirations", [])
        if len(inspirations) < 2:
            print(f"  ⚠️  Stage 1 has <2 inspirations, skipping")
            return

        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO "InspirationReport" (
                    id, "runId", "inspiration1Title", "inspiration1Content",
                    "inspiration1Elements", "inspiration2Title", "inspiration2Content",
                    "inspiration2Elements", "createdAt", "updatedAt"
                ) VALUES (
                    gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, NOW(), NOW()
                )
                ON CONFLICT ("runId") DO NOTHING
            """, run_id,
                 inspirations[0]["title"],
                 inspirations[0]["content"],
                 inspirations[0]["key_elements"],
                 inspirations[1]["title"],
                 inspirations[1]["content"],
                 inspirations[1]["key_elements"])

        print(f"  ✅ Migrated Stage 1 (InspirationReport)")

    async def _migrate_stage5(self, run_id: str, user_id: str):
        """Migrate Stage 5 opportunity-{1-5}.md → OpportunityCard table"""
        stage5_dir = Path(f"data/test-outputs/{run_id}/stage5")

        if not stage5_dir.exists():
            print(f"  ⚠️  Stage 5 directory not found, skipping")
            return

        # Check for JSON version first (structured data)
        opportunities_json = stage5_dir / "opportunities.json"
        if opportunities_json.exists():
            with open(opportunities_json) as f:
                data = json.load(f)
                opportunities = data.get("opportunities", [])
        else:
            # Parse from markdown files
            opportunities = []
            for i in range(1, 6):
                md_file = stage5_dir / f"opportunity-{i}.md"
                if md_file.exists():
                    content = md_file.read_text()
                    # Parse markdown (simplified)
                    opp = self._parse_opportunity_markdown(content, i)
                    opportunities.append(opp)

        if len(opportunities) == 0:
            print(f"  ⚠️  No Stage 5 opportunities found, skipping")
            return

        async with self.pool.acquire() as conn:
            for opp in opportunities:
                await conn.execute("""
                    INSERT INTO "OpportunityCard" (
                        id, "runId", "userId", number, title, tagline,
                        problem, solution, "why_now", "target_segment",
                        "quick_win", starred, "createdAt", "updatedAt"
                    ) VALUES (
                        gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, $9,
                        $10, false, NOW(), NOW()
                    )
                    ON CONFLICT DO NOTHING
                """, run_id, user_id, opp["number"], opp["title"], opp["tagline"],
                     opp["problem"], opp["solution"], opp["why_now"],
                     opp["target_segment"], opp["quick_win"])

        print(f"  ✅ Migrated Stage 5 ({len(opportunities)} OpportunityCards)")

    def _parse_opportunity_markdown(self, content: str, number: int) -> Dict:
        """Parse opportunity markdown file into structured data"""
        # Simplified parser (assumes markdown format from Stage 5)
        lines = content.split("\n")

        opp = {
            "number": number,
            "title": "Untitled",
            "tagline": "",
            "problem": "",
            "solution": "",
            "why_now": "",
            "target_segment": "",
            "quick_win": ""
        }

        # Extract title from first # heading
        for line in lines:
            if line.startswith("# "):
                opp["title"] = line[2:].strip()
                break

        # Extract sections (simplified)
        current_section = None
        for line in lines:
            if line.startswith("## "):
                section = line[3:].lower().strip()
                if "tagline" in section:
                    current_section = "tagline"
                elif "problem" in section:
                    current_section = "problem"
                elif "solution" in section:
                    current_section = "solution"
                elif "why now" in section:
                    current_section = "why_now"
                elif "target" in section:
                    current_section = "target_segment"
                elif "quick win" in section:
                    current_section = "quick_win"
            elif current_section and line.strip():
                opp[current_section] += line.strip() + " "

        return opp

    async def _migrate_stage_outputs(self, run_id: str):
        """Migrate all stage JSON files → StageOutput table"""
        run_dir = Path(f"data/test-outputs/{run_id}")

        for stage_num in range(1, 6):
            stage_dir = run_dir / f"stage{stage_num}"
            if not stage_dir.exists():
                continue

            # Find primary JSON file for this stage
            json_files = list(stage_dir.glob("*.json"))
            if not json_files:
                continue

            primary_file = json_files[0]  # Take first JSON file
            with open(primary_file) as f:
                json_data = json.load(f)

            # Check if markdown file exists
            markdown_output = ""
            md_files = list(stage_dir.glob("*.md"))
            if md_files:
                markdown_output = md_files[0].read_text()

            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO "StageOutput" (
                        id, "runId", "stageNumber", "markdownOutput",
                        "jsonOutput", "createdAt"
                    ) VALUES (
                        gen_random_uuid(), $1, $2, $3, $4, NOW()
                    )
                    ON CONFLICT DO NOTHING
                """, run_id, stage_num, markdown_output, json.dumps(json_data))

        print(f"  ✅ Migrated StageOutputs")

    async def migrate_all_runs(self, user_id: str = "migration-user"):
        """Migrate all runs in data/test-outputs/"""
        test_outputs_dir = Path("data/test-outputs")

        if not test_outputs_dir.exists():
            print("❌ data/test-outputs/ directory not found")
            return

        run_dirs = [d for d in test_outputs_dir.iterdir() if d.is_dir()]
        print(f"📊 Found {len(run_dirs)} runs to migrate\n")

        success_count = 0
        for run_dir in run_dirs:
            run_id = run_dir.name
            if await self.migrate_run(run_id, user_id):
                success_count += 1
            print()  # Blank line between runs

        print(f"✅ Migration complete: {success_count}/{len(run_dirs)} runs migrated")

async def main():
    parser = argparse.ArgumentParser(description="Migrate file-based pipeline outputs to PostgreSQL")
    parser.add_argument("--run-id", help="Specific run ID to migrate")
    parser.add_argument("--all", action="store_true", help="Migrate all runs")
    parser.add_argument("--user-id", default="migration-user", help="User ID to assign ownership")
    parser.add_argument("--database-url", help="PostgreSQL connection string (default: from env)")

    args = parser.parse_args()

    database_url = args.database_url or os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set (use --database-url or env var)")
        return

    migrator = FileToDBMigrator(database_url)
    await migrator.connect()

    try:
        if args.all:
            await migrator.migrate_all_runs(args.user_id)
        elif args.run_id:
            await migrator.migrate_run(args.run_id, args.user_id)
        else:
            print("❌ Specify --run-id or --all")
    finally:
        await migrator.disconnect()

if __name__ == "__main__":
    import os
    asyncio.run(main())
```

**Usage:**

```bash
# Migrate specific run
python scripts/migrate_files_to_database.py --run-id test-run-001

# Migrate all existing runs
python scripts/migrate_files_to_database.py --all

# Migrate with specific user assignment
python scripts/migrate_files_to_database.py --all --user-id user_2abc123
```

---

## Rollback Procedure

### Prisma Migration Rollback Commands

```bash
# 1. View migration history
cd innovation-web
npx prisma migrate status

# 2. Rollback last migration (WARNING: Destructive!)
npx prisma migrate reset
# This will:
# - Drop all tables
# - Re-apply all migrations from scratch
# - Run seed script (if configured)

# 3. Rollback to specific migration (manual approach)
# Find migration timestamp to revert to
ls prisma/migrations/

# Connect to database and run SQL manually
psql $DATABASE_URL
# Then run migration SQL in reverse order

# 4. Safe rollback: Create new migration to undo changes
npx prisma migrate dev --name revert_init
# Edit the generated migration.sql to drop tables/columns you want to remove

# 5. Emergency rollback script (Story 7.0)
# Created at: scripts/emergency-rollback.sh
```

### Emergency Rollback Script

Create `scripts/emergency-rollback.sh`:

```bash
#!/bin/bash
# Emergency database rollback for Story 7.0
# Usage: ./scripts/emergency-rollback.sh

set -e

echo "🚨 EMERGENCY ROLLBACK - Story 7.0 Prisma Setup"
echo "This will DROP ALL DATABASE TABLES!"
read -p "Are you sure? (type 'YES' to confirm): " confirmation

if [ "$confirmation" != "YES" ]; then
    echo "❌ Rollback cancelled"
    exit 1
fi

echo "📦 Backing up current database schema..."
npx prisma db pull --force
cp prisma/schema.prisma prisma/schema.backup.prisma

echo "🗑️ Dropping all tables..."
npx prisma migrate reset --force --skip-seed

echo "✅ Database rolled back successfully"
echo "⚠️ Schema backup saved to: prisma/schema.backup.prisma"
```

### If Migration Fails

```bash
# 1. Stop all pipeline executions
pkill -f "python.*run_pipeline"

# 2. Revert database writes in code (disable db_service)
git revert <commit-hash-of-database-integration>

# 3. Redeploy without database writes
git push railway main

# 4. Verify file-based system still works
python scripts/run_pipeline.py --input-file tests/fixtures/sample-report.pdf --brand lactalis-canada
```

### Data Preservation

```bash
# BEFORE running any migrations, backup the database
# 1. Export schema
cd innovation-web
npx prisma db pull

# 2. Backup all data (SQL dump)
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d-%H%M%S).sql

# 3. Backup existing files before migration
tar -czf data-backup-$(date +%Y%m%d).tar.gz data/test-outputs/

# Restore database from backup
psql $DATABASE_URL < backup-YYYYMMDD-HHMMSS.sql

# Restore files if needed
tar -xzf data-backup-YYYYMMDD.tar.gz
```

### Testing Rollback (Safe)

```bash
# Create dummy test migration to practice rollback
npx prisma migrate dev --name test_rollback_practice

# Edit the migration to add a test table
# prisma/migrations/XXXXXXXX_test_rollback_practice/migration.sql
# Add: CREATE TABLE "RollbackTest" ("id" TEXT PRIMARY KEY);

# Apply it
npx prisma migrate dev

# Practice rolling back
npx prisma migrate reset --force

# Verify tables dropped
npx prisma studio  # Check if RollbackTest table is gone
```

---

## Migration Timeline

| Phase | Duration | Tasks | Rollback Risk |
|-------|----------|-------|---------------|
| **Phase 1: Dual-Write** | Week 1 | Add database writes alongside file writes | LOW (files still work) |
| **Phase 2: DB-First Reads** | Week 2 | Read from DB first, fallback to files | LOW (fallback exists) |
| **Phase 3: Backfill** | Week 3 | Run migration script on existing data | MEDIUM (test in staging) |
| **Phase 4: File Deprecation** | Week 4+ | Remove file writes, DB-only mode | HIGH (no fallback) |

**Recommendation:** Stay in Phase 2 (DB-first reads with file fallback) for 1 month before Phase 4.

---

## Validation Checklist

Before declaring migration complete:

- [ ] All existing runs migrated successfully (verify count)
- [ ] Spot-check 5 random runs: Files match database records
- [ ] New pipeline runs write to database correctly
- [ ] API routes read from database correctly
- [ ] File-based fallback still works (manually disable DB to test)
- [ ] Database backups configured on Railway
- [ ] Migration script added to CI/CD for future use

---

## Next Steps

1. **Implement Phase 1** (dual-write) in pipeline stages
2. **Test migration script** on development database with 3 sample runs
3. **Run integration tests** (Section 13) to validate hybrid mode
4. **Deploy to Railway staging** and validate Phase 1
5. **Proceed to Phase 2** only after 1 week of stable Phase 1 operation
