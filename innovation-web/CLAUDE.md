# Claude AI Agent Instructions - Innovation Web Deployment

## 🤖 Instructions for AI Agents

When working with Vercel deployments for this Next.js project, **YOU MUST** follow these rules to prevent deployment failures.

## Critical Deployment Rules

### Rule 1: NEVER Modify Root Directory Setting
**⚠️ CRITICAL:** The Vercel dashboard Root Directory setting MUST remain **empty/blank**.

**Why:** This project uses a monorepo structure where:
- Repository root: `/innovation-intelligence-system/`
- Next.js app: `/innovation-intelligence-system/innovation-web/`
- Vercel link: Created from `/innovation-web/` directory

Setting Root Directory to `innovation-web` creates double nesting: `innovation-web/innovation-web/`

### Rule 2: Always Deploy from Correct Directory
When using Vercel CLI, **ALWAYS** run from the `innovation-web/` directory:

```bash
cd /path/to/innovation-intelligence-system/innovation-web
vercel --prod --yes
```

**NEVER** run from repository root unless you change the configuration.

### Rule 3: Understand the Configuration
**Current Working Setup:**
- `.vercel` folder location: `/innovation-web/.vercel`
- Vercel Root Directory: `(empty)`
- Result: Vercel builds from `innovation-web/` automatically

**This configuration is CORRECT. Do not change it.**

## Deployment Commands for AI Agents

### To Deploy via CLI:
```bash
cd innovation-web
vercel --prod --yes
```

### To Trigger GitHub Auto-Deploy:
```bash
git add .
git commit -m "feat: your description"
git push origin hackaton
```

### To Monitor Deployment Status:
Use Vercel MCP tools:
```
mcp__vercel-innovation-web__list_deployments
mcp__vercel-innovation-web__get_deployment(idOrUrl)
mcp__vercel-innovation-web__get_deployment_build_logs(idOrUrl)
```

## Error Detection & Resolution

### If You Encounter: "No Next.js version detected"

**Diagnosis Steps:**
1. Check build logs for path errors
2. Look for `innovation-web/innovation-web` in error messages
3. Verify Root Directory setting in dashboard

**Resolution:**
```
ERROR CAUSE: Root Directory is set to "innovation-web"
FIX: Clear Root Directory in Vercel dashboard (leave blank)
URL: https://vercel.com/philippe-beliveaus-projects/innovation-web/settings
```

### If You Encounter: "Couldn't find pages or app directory"

**Diagnosis:**
Vercel is looking at wrong directory (likely repo root)

**Resolution:**
1. Verify `.vercel/project.json` exists in `innovation-web/`
2. If missing, re-link:
   ```bash
   cd innovation-web
   rm -rf .vercel
   vercel link --yes
   ```
3. Ensure Root Directory in dashboard is **empty**

## Configuration Verification Protocol

Before any deployment, verify:

```bash
# 1. Check current directory
pwd  # Should end with /innovation-web

# 2. Verify package.json exists
ls -la package.json  # Should exist

# 3. Verify app directory exists
ls -la app/  # Should exist with page.tsx files

# 4. Verify .vercel link exists
ls -la .vercel/project.json  # Should exist

# 5. Confirm you're on correct branch
git branch --show-current  # Should show 'hackaton' or 'main'
```

## What NOT to Do

❌ **NEVER** set Root Directory to `innovation-web` in dashboard
❌ **NEVER** run `vercel` from repository root without changing config
❌ **NEVER** modify `.vercel/project.json` manually
❌ **NEVER** add `.vercel/` to Git (it's already gitignored)
❌ **NEVER** assume monorepo setup works like single-project setup

## What TO Do

✅ **ALWAYS** keep Root Directory empty in dashboard
✅ **ALWAYS** run `vercel` from `innovation-web/` directory
✅ **ALWAYS** check build logs if deployment fails
✅ **ALWAYS** verify configuration before making changes
✅ **ALWAYS** test with `vercel --prod --yes` before pushing to Git

## Quick Reference

**Production URL:** https://innovation-web-rho.vercel.app
**Dashboard:** https://vercel.com/philippe-beliveaus-projects/innovation-web
**Settings:** https://vercel.com/philippe-beliveaus-projects/innovation-web/settings

**Working Directory:** `/innovation-web/`
**Root Directory Setting:** `(empty)`
**Auto-Deploy Branch:** `hackaton`

## Historical Context

**Problem Solved:** 2025-10-21
- Previous deployments were failing with "No Next.js version detected"
- Root cause: Double nesting (`innovation-web/innovation-web/`)
- Solution: Cleared Root Directory setting in dashboard
- Result: Deployments now succeed consistently

**Configuration History:**
1. ❌ Root Directory = `innovation-web` → FAILED (double nesting)
2. ✅ Root Directory = `(empty)` → WORKS (correct path resolution)

## Testing Protocol

When making deployment changes:

1. **Test locally first:**
   ```bash
   cd innovation-web
   npm run build  # Should succeed
   ```

2. **Test CLI deployment:**
   ```bash
   vercel --prod --yes
   ```

3. **Verify build logs:**
   Check for errors using MCP tools or dashboard

4. **Only then push to Git:**
   ```bash
   git push origin hackaton
   ```

## Environment Variables

Required for production (already set):
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `BLOB_READ_WRITE_TOKEN`
- `OPENROUTER_API_KEY`
- `NEXT_PUBLIC_BACKEND_URL`

**Never modify these without user confirmation.**

---

**For AI Agents:** This file contains critical deployment instructions. Follow them exactly to prevent deployment failures. If you encounter an error not covered here, investigate thoroughly before suggesting configuration changes.

**Last Updated:** 2025-10-21
**Status:** ✅ Configuration verified and working
