# Vercel Deployment Guide for Innovation Web

## ⚠️ CRITICAL: Deployment Configuration

This document ensures correct Vercel deployment setup to prevent build failures.

## Current Working Configuration

### ✅ Correct Setup (DO NOT CHANGE)

**Vercel Dashboard Settings:**
- **Root Directory:** `(empty/blank)` ← MUST BE EMPTY
- **Framework Preset:** Next.js
- **Build Command:** (default) `next build`
- **Output Directory:** (default) `.next`
- **Install Command:** (default) `npm install`
- **Node Version:** 22.x

**Local Setup:**
- `.vercel` folder location: `/innovation-web/.vercel`
- Git repository root: `/innovation-intelligence-system/`
- Next.js app location: `/innovation-intelligence-system/innovation-web/`

### 🚨 Common Mistake That WILL BREAK Deployment

**❌ NEVER set Root Directory to `innovation-web`**

**Why?** The local `.vercel` link is created FROM the `innovation-web/` directory. If you also set Root Directory to `innovation-web`, Vercel will look for:
```
innovation-web/innovation-web/package.json  ← DOES NOT EXIST
```

This causes the error:
```
Error: No Next.js version detected. Make sure your package.json has "next"
in either "dependencies" or "devDependencies".
```

## Deployment Methods

### Method 1: CLI Deployment (Recommended for Testing)

```bash
cd /path/to/innovation-intelligence-system/innovation-web
vercel --prod --yes
```

**Expected Output:**
```
✓ Deploying philippe-beliveaus-projects/innovation-web
✓ Inspect: https://vercel.com/...
✓ Production: https://innovation-web-rho.vercel.app
```

### Method 2: GitHub Auto-Deploy (Production)

Push to the `hackaton` branch:
```bash
git add .
git commit -m "your message"
git push origin hackaton
```

Vercel will automatically:
1. Detect the push
2. Clone the repository
3. Build from `innovation-web/` directory
4. Deploy to production

### Method 3: Manual Vercel Dashboard Deploy

1. Go to: https://vercel.com/philippe-beliveaus-projects/innovation-web
2. Click "Deployments" tab
3. Find a successful deployment
4. Click "⋯" menu → "Redeploy"

## Troubleshooting

### Error: "No Next.js version detected"

**Cause:** Root Directory is set to `innovation-web` in dashboard

**Fix:**
1. Go to: https://vercel.com/philippe-beliveaus-projects/innovation-web/settings
2. Scroll to "Root Directory"
3. **Clear the field** (leave it blank)
4. Click "Save"
5. Redeploy

### Error: "Couldn't find any pages or app directory"

**Cause:** Vercel is looking at repo root instead of `innovation-web/`

**Fix:**
1. Check that `.vercel/project.json` exists in `innovation-web/` directory
2. If missing, re-link the project:
   ```bash
   cd innovation-web
   rm -rf .vercel
   vercel link --yes
   ```

### Error: "The provided path .../innovation-web/innovation-web does not exist"

**Cause:** Double-nesting issue (Root Directory + local link both set)

**Fix:** See "Error: No Next.js version detected" above

## Verification Checklist

Before deploying, verify:

- [ ] You are in `/innovation-web/` directory when running `vercel` command
- [ ] `.vercel/project.json` exists in `innovation-web/` directory
- [ ] Vercel dashboard Root Directory is **empty/blank**
- [ ] `package.json` exists and has `next` dependency
- [ ] `app/` directory exists with valid Next.js pages

## Production URLs

**Primary:** https://innovation-web-rho.vercel.app
**Aliases:**
- https://innovation-web-philippe-beliveaus-projects.vercel.app
- https://innovation-web-philbeliveau-philippe-beliveaus-projects.vercel.app

## Environment Variables

Required environment variables (set in Vercel dashboard):
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `BLOB_READ_WRITE_TOKEN`
- `OPENROUTER_API_KEY`
- `NEXT_PUBLIC_BACKEND_URL`

**Set at:** https://vercel.com/philippe-beliveaus-projects/innovation-web/settings/environment-variables

## Build Logs Access

**Via Dashboard:**
https://vercel.com/philippe-beliveaus-projects/innovation-web

**Via CLI:**
```bash
vercel logs [deployment-url]
```

## Key Lessons

### Monorepo Configuration Rules

| Scenario | Local Link Location | Root Directory | Result |
|----------|-------------------|----------------|---------|
| ✅ Correct | `/innovation-web/` | `(empty)` | Works perfectly |
| ✅ Alternative | `/repo-root/` | `innovation-web` | Also works |
| ❌ WRONG | `/innovation-web/` | `innovation-web` | FAILS - double nesting |

### Why Our Setup Works

1. **Local `.vercel` link** establishes project context from `innovation-web/`
2. **Empty Root Directory** tells Vercel to use the linked directory as-is
3. **No path concatenation** = no double nesting issue

## Contact & Support

**Project Dashboard:** https://vercel.com/philippe-beliveaus-projects/innovation-web
**Vercel Docs:** https://vercel.com/docs/projects/project-configuration

---

**Last Updated:** 2025-10-21
**Configuration Status:** ✅ Working
**Deployment Status:** ✅ Auto-deploy enabled for `hackaton` branch
