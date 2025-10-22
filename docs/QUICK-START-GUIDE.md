# Quick Start Guide - Innovation Intelligence System

## 🚀 Ready to Build? Follow This Order

### Step 1: Read the Summary (2 minutes)

📄 **Read:** `docs/PO-VALIDATION-RESOLUTION-SUMMARY.md`

**What you'll learn:**
- All 6 critical blockers have been resolved
- New architecture sections created (13-15)
- Updated implementation roadmap with Hour -2 to 0 prep work

---

### Step 2: Review Critical Architecture Sections (30 minutes)

**🔴 MUST READ BEFORE CODING:**

1. **Section 13: Integration Test Plan** (`docs/architecture/13-integration-test-plan.md`)
   - Understand regression testing requirements
   - See how to validate pipeline still works after modifications
   - Learn CI/CD integration strategy

2. **Section 14: Database Migration Strategy** (`docs/architecture/14-database-migration-strategy.md`)
   - Understand dual-write approach (database + file fallback)
   - Learn 3-phase migration timeline
   - See backfill script for existing data

3. **Section 15: Railway Deployment & Rollback** (`docs/architecture/15-railway-deployment-and-rollback.md`)
   - Understand feature flag system
   - Learn rollback procedures (3 scenarios)
   - See Railway environment configuration

---

### Step 3: Pre-Implementation Setup (2-3 hours)

Follow **Section 9: Implementation Roadmap** exactly:

#### Hour -2: Railway PostgreSQL Deployment

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and create project
railway login
railway init
railway link

# 3. Add PostgreSQL database
railway add --database postgres

# 4. Get DATABASE_URL
railway variables
# Copy DATABASE_URL value

# 5. Set local environment
echo "DATABASE_URL=<railway-url>?pgbouncer=true&connection_limit=1" >> .env
echo "DATABASE_URL_NON_POOLING=<railway-url>" >> .env

# 6. Test connection
psql $DATABASE_URL -c "SELECT 1"
```

**✅ Validation:** Should see `(1 row)`

---

#### Hour -1: Prisma Schema Deployment

```bash
# 1. Install Prisma
npm install -D prisma @prisma/client

# 2. Generate Prisma Client
npx prisma generate

# 3. Deploy migrations
npx prisma migrate deploy

# 4. Verify schema
npx prisma studio
# Check tables: User, Run, OpportunityCard, InspirationReport, StageOutput

# 5. Add remaining env vars
cat >> .env << 'EOF'
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
ENABLE_DATABASE_WRITES=true
ENABLE_FILE_FALLBACK=true
EOF
```

**✅ Validation:** Prisma Studio shows all 5 tables

---

#### Hour 0: Integration Test Baseline

```bash
# 1. Run existing pipeline to create baseline
python scripts/run_pipeline.py \
  --input-file tests/fixtures/sample-report.pdf \
  --brand lactalis-canada \
  --run-id baseline-test-001

# 2. Save baseline outputs
mkdir -p tests/fixtures/expected-outputs/
cp -r data/test-outputs/baseline-test-001/ tests/fixtures/expected-outputs/

# 3. Install pytest
pip install pytest pytest-asyncio

# 4. Run first regression test
pytest tests/test_pipeline_stages.py::TestStage1Regression -v
```

**✅ Validation:** At least 1 test passes

---

### Step 4: Start Development (Hours 1-10)

Now follow **Section 9: Implementation Roadmap** starting from **Hour 1**.

**Key milestones:**
- Hour 1-2: Next.js project + Clerk auth
- Hour 2-3: Homepage UI with file upload
- Hour 3-4: Intermediary card page
- Hour 4-5: API routes (upload, analyze, run)
- Hour 5-6: Pipeline modifications (inject DatabaseService)
- Hour 6-8: Pipeline viewer UI (real-time progress)
- Hour 8-9: Results page (opportunity cards)
- Hour 9-10: Polish + deployment

---

## 🔥 Critical Reminders

### Feature Flags Configuration

**During Development/Staging:**
```bash
ENABLE_DATABASE_WRITES=true   # Write to database
ENABLE_FILE_FALLBACK=true     # ALSO write to files (safety net)
```

**Production (after 1 week of stable operation):**
```bash
ENABLE_DATABASE_WRITES=true   # Write to database
ENABLE_FILE_FALLBACK=false    # Files disabled (database-only)
```

**Emergency Rollback:**
```bash
ENABLE_DATABASE_WRITES=false  # Disable database
ENABLE_FILE_FALLBACK=true     # Fall back to files
```

---

### Rollback Scenarios

| Symptom | Rollback Command | Timeline |
|---------|------------------|----------|
| Database timeout | `ENABLE_DATABASE_WRITES=false` | 5 min |
| Schema mismatch | `ENABLE_DATABASE_WRITES=false` | 15 min |
| Slow queries | Enable `ENABLE_FILE_FALLBACK=true` | 1 hour |

See **Section 15, Part 2.4** for detailed rollback procedures.

---

### Testing Checkpoints

**After Hour 6 (Pipeline Modifications):**
```bash
# Run regression tests
pytest tests/test_pipeline_stages.py -v

# Should pass with dual-write mode
# (both database AND file outputs)
```

**Before Deployment:**
```bash
# Full integration test
pytest tests/test_pipeline_e2e.py -v

# Railway environment test
./tests/railway/test_railway_environment.sh
```

---

## 📚 Reference Documents

### Architecture (Read in Order)

1. **Section 1:** Introduction (core philosophy)
2. **Section 3:** Tech Stack (complete technology matrix)
3. **Section 3.5:** Prisma & Database Architecture
4. **Section 7.2:** asyncpg Database Service (with integration mechanism)
5. **Section 9:** Implementation Roadmap (Hour -2 to 10)
6. **Section 13:** Integration Test Plan 🔴 **NEW**
7. **Section 14:** Database Migration Strategy 🔴 **NEW**
8. **Section 15:** Railway Deployment & Rollback 🔴 **NEW**

### Quick Access

- **PRD:** `docs/prd.md` (product requirements)
- **Architecture Index:** `docs/architecture/index.md` (all sections)
- **Validation Summary:** `docs/PO-VALIDATION-RESOLUTION-SUMMARY.md` (blocker resolution)

---

## 🛠️ Troubleshooting

### Issue: Prisma migration fails

```bash
# Check DATABASE_URL format
echo $DATABASE_URL
# Should include ?pgbouncer=true&connection_limit=1

# Use non-pooling URL for migrations
export DATABASE_URL=$DATABASE_URL_NON_POOLING
npx prisma migrate deploy
```

### Issue: Pipeline can't find brand profiles

```python
# Use PathResolver (see Section 15, Part 1.4)
from pipeline.utils.path_resolver import path_resolver

profile_path = path_resolver.get_brand_profile_path("lactalis-canada")
# Auto-handles /Users/... (local) vs /app/... (Railway)
```

### Issue: Database connection timeout

```bash
# Immediate rollback
railway variables set ENABLE_DATABASE_WRITES=false

# Check database health
curl https://your-app.railway.app/health
```

---

## ✅ Success Criteria

### Pre-Development (Hours -2 to 0)

- [ ] Railway PostgreSQL accessible (`psql` works)
- [ ] Prisma Studio shows 5 tables
- [ ] Baseline pipeline outputs captured
- [ ] At least 1 regression test passes

### Development (Hours 1-10)

- [ ] All shadcn/ui components installed
- [ ] Clerk authentication working
- [ ] File upload to Vercel Blob works
- [ ] Pipeline executes with dual-write mode
- [ ] Results page displays 5 opportunity cards

### Pre-Deployment

- [ ] All integration tests pass (70%+ coverage)
- [ ] Railway environment validated
- [ ] Rollback to FILE_ONLY mode tested
- [ ] Health endpoint returns `"status": "healthy"`

---

## 🚨 When to Stop and Ask for Help

1. **Prisma migration fails repeatedly** → Check `DATABASE_URL` format, try `DATABASE_URL_NON_POOLING`
2. **Pipeline crashes with database errors** → Enable `ENABLE_FILE_FALLBACK=true`, investigate logs
3. **Tests fail after pipeline modifications** → Compare outputs to baseline (`tests/fixtures/expected-outputs/`)
4. **Railway deployment fails** → Run `./tests/railway/test_railway_environment.sh` locally first

---

## 🎯 Final Checklist Before Coding

- [ ] Read PO Validation Resolution Summary
- [ ] Read Sections 13, 14, 15 of architecture
- [ ] Completed Hour -2 (Railway PostgreSQL deployed)
- [ ] Completed Hour -1 (Prisma schema deployed)
- [ ] Completed Hour 0 (baseline tests captured)
- [ ] Feature flags set to DUAL_WRITE mode
- [ ] `.env` file configured with all variables

**Ready?** → Start **Hour 1: Next.js Project Setup** 🚀

---

**Last Updated:** 2025-10-21
**Status:** ✅ All blockers resolved, ready for development
