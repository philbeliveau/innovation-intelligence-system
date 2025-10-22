# Prisma Database Setup Guide

## Overview

This guide documents the PostgreSQL + Prisma ORM setup for the Innovation Intelligence System web application.

**Database:** Railway PostgreSQL 15
**ORM:** Prisma 6.18.0
**Deployment:** Vercel with automatic Prisma Client generation

---

## Quick Start

### 1. Install Dependencies

```bash
cd innovation-web
npm install
```

### 2. Configure Environment Variables

Create `.env.local` with your Railway database connection:

```env
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

**Get your DATABASE_URL from:**
- Railway PostgreSQL service → Connect → Connection URL (Public)
- Always use the **public** connection URL (not internal)
- Always include `?sslmode=require` for security

### 3. Run Initial Migration

```bash
# Create all database tables
npx prisma migrate dev

# Generate Prisma Client types
npx prisma generate
```

### 4. Seed Database (Optional)

```bash
# Populate with test data
npm run prisma:seed
```

### 5. Verify Setup

```bash
# Open Prisma Studio to view data
npx prisma studio

# Test health check endpoint
npm run dev
# Visit: http://localhost:3000/api/health/database
```

---

## Database Schema

### Models

**5 Core Models:**

1. **User** - Clerk authentication integration
   - `clerkId` (unique) - Maps to Clerk user ID
   - `email`, `name`
   - Relations: `pipelineRuns[]`

2. **PipelineRun** - Core run metadata
   - `userId`, `documentName`, `companyName`
   - `status` (PROCESSING, COMPLETED, FAILED, CANCELLED)
   - `pipelineVersion`, `duration`, `completedAt`
   - Relations: `user`, `opportunityCards[]`, `inspirationReport`, `stageOutputs[]`

3. **OpportunityCard** - Generated innovation opportunities
   - `runId`, `number` (1-5)
   - `title`, `content` (markdown)
   - `isStarred` (favorite functionality)
   - Relations: `run`

4. **InspirationReport** - Full pipeline output
   - `runId` (unique, 1:1 with run)
   - `selectedTrack`, `nonSelectedTrack`
   - `stage1Output` through `stage5Output` (markdown)
   - Relations: `run`

5. **StageOutput** - Individual stage results
   - `runId`, `stageNumber` (1-5)
   - `stageName`, `status`, `output`
   - `completedAt`
   - Relations: `run`

### Cascade Delete Behavior

**All relations use `ON DELETE CASCADE`:**
- Deleting a User → Deletes all their PipelineRuns
- Deleting a PipelineRun → Deletes OpportunityCards, InspirationReport, StageOutputs

### Indexes

**Performance optimizations:**
- `User.clerkId` (unique index)
- `PipelineRun.[userId, createdAt]` (compound index for user run history)
- `PipelineRun.status` (index for filtering)
- `OpportunityCard.[runId, number]` (compound unique index)
- `OpportunityCard.isStarred` (index for favorites)
- `StageOutput.[runId, stageNumber]` (compound unique index)

---

## Common Commands

### Development

```bash
# Start dev server (auto-loads .env.local)
npm run dev

# Open Prisma Studio (database GUI)
npx prisma studio

# View migration status
npx prisma migrate status

# Create new migration
npx prisma migrate dev --name your_migration_name

# Generate Prisma Client (after schema changes)
npx prisma generate
```

### Production Deployment

```bash
# Apply migrations to production database
npx prisma migrate deploy

# Build with Prisma Client generation
npm run build
```

### Database Management

```bash
# Reset database (WARNING: Deletes all data!)
npx prisma migrate reset

# Pull current database schema into Prisma schema
npx prisma db pull

# Push schema changes without creating migration
npx prisma db push
```

---

## Vercel Deployment

### Environment Variables

Add to Vercel project settings:

**Production:**
```
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

**Preview (optional separate database):**
```
DATABASE_URL=postgresql://user:password@host:port/database_preview?sslmode=require
```

### Build Configuration

Already configured in `package.json`:

```json
{
  "scripts": {
    "build": "prisma generate && next build",
    "postinstall": "prisma generate"
  }
}
```

**What this does:**
1. `postinstall` runs after `npm install` (generates Prisma Client)
2. `build` generates Prisma Client before Next.js build

### Deployment Checklist

- [ ] DATABASE_URL added to Vercel environment variables
- [ ] Railway database accessible from external connections
- [ ] SSL mode required in connection string
- [ ] Migrations applied: `npx prisma migrate deploy`
- [ ] Health check endpoint returns 200: `/api/health/database`

---

## Troubleshooting

### "Can't reach database server"

**Problem:** Prisma can't connect to Railway database

**Solutions:**
1. Verify DATABASE_URL is correct (check Railway dashboard)
2. Use **public** connection URL (not `railway.internal`)
3. Include `?sslmode=require` in connection string
4. Test connection: `npx prisma migrate status`

### "No Prisma Client"

**Problem:** TypeScript can't find `@prisma/client`

**Solutions:**
1. Run `npx prisma generate`
2. Restart TypeScript server in VS Code
3. Check `node_modules/@prisma/client` exists

### "Migration already applied"

**Problem:** Migration file exists but database is out of sync

**Solutions:**
1. View status: `npx prisma migrate status`
2. Resolve: `npx prisma migrate resolve --applied <migration-name>`
3. Or reset (WARNING: deletes data): `npx prisma migrate reset`

### Vercel Build Failing

**Problem:** "Error: @prisma/client did not initialize yet"

**Solutions:**
1. Verify `postinstall` script in package.json
2. Check DATABASE_URL set in Vercel environment variables
3. View build logs for Prisma errors
4. Try: Delete Vercel deployment cache and redeploy

---

## Security Best Practices

✅ **SSL Required:** All connection strings use `?sslmode=require`
✅ **No Credentials in Code:** DATABASE_URL only in environment variables
✅ **Git Ignored:** `.env*` files never committed
✅ **Client-Side Safe:** DATABASE_URL only used in API routes/server components
✅ **Connection Pooling:** Prisma singleton pattern prevents connection leaks

---

## Backup & Rollback

### Create Backup

```bash
# Export database schema
npx prisma db pull

# Backup all data (requires psql)
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d-%H%M%S).sql
```

### Restore from Backup

```bash
# Restore data
psql $DATABASE_URL < backup-YYYYMMDD-HHMMSS.sql
```

### Emergency Rollback

See: `docs/architecture/14-database-migration-strategy.md` for detailed rollback procedures

---

## Next Steps

After completing this setup:

1. **Update API Routes:** Replace mock data in stories 7.1-7.3 with real Prisma queries
2. **Test Integration:** Run QA validation on stories 7.1-7.3
3. **Deploy to Vercel:** Apply migrations to production database
4. **Monitor Performance:** Check Railway database metrics

---

**Last Updated:** 2025-10-22
**Story:** 7.0 - Prisma Database Foundation Setup
**Status:** ✅ Setup Complete
