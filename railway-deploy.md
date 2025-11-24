# Railway Deployment Fix Documentation

## Problem Summary

Railway deployment was failing with multiple cascading issues that took several iterations to diagnose and fix.

---

## Error Timeline & Fixes

### ❌ Error 1: "failed to read dockerfile: open /backend/Dockerfile: no such file or directory"

**Symptom:**
```
Build Failed: bc.Build: failed to solve: failed to read dockerfile:
open /backend/Dockerfile: no such file or directory
```

**Initial Railway Configuration:**
- Root Directory: `backend`
- Dockerfile Path: `/backend/Dockerfile` (absolute path)
- Builder: Dockerfile

**Root Cause:**
When Railway's root directory is set to `backend`, it changes context to that subdirectory. Setting Dockerfile Path to `/backend/Dockerfile` (absolute path) causes Railway to look for the file at an invalid absolute path instead of relative to the root directory.

**Attempted Fix #1 (FAILED):**
Created `backend/railway.json` to explicitly configure the Dockerfile builder:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "dockerfile",
    "dockerfilePath": "Dockerfile"
  }
}
```

**Why it failed:** `railway.json` location was wrong. When root directory is set to `backend`, Railway expects `railway.json` at project root, not inside `backend/`.

**Attempted Fix #2 (FAILED):**
Moved `railway.json` to project root.

**Why it failed:** This created more confusion. The `railway.json` was conflicting with Railway dashboard settings.

**Actual Fix:**
1. **Deleted `railway.json` entirely** (commit `1c2c87d`)
2. **Changed Railway dashboard settings:**
   - Root Directory: `.` (project root, NOT `backend`)
   - Dockerfile Path: `backend/Dockerfile` (relative path from project root)
   - Builder: Dockerfile

**Key Insight:** The successful deployment at commit `724660b` had NO `railway.json` and relied solely on Railway dashboard settings.

---

### ❌ Error 2: Silent Build Failure (34 seconds, no logs)

**Symptom:**
After fixing Error 1, Railway would start the build but fail silently after 34 seconds with absolutely no build logs.

**Initial Hypothesis (WRONG):**
Thought it was a build timeout or missing `.dockerignore` causing the build to hang.

**Root Cause:**
`requirements.txt` was missing from the `backend/` directory. The Dockerfile had:
```dockerfile
COPY requirements.txt .
```

But there was no `backend/requirements.txt` file. The file existed only at project root (`./requirements.txt`), which was the WRONG file (missing FastAPI, uvicorn, psycopg2-binary, and other critical dependencies).

**Fix:**
Restored correct `requirements.txt` from successful deployment (commit `724660b`) to `backend/requirements.txt` with all dependencies:
```
fastapi==0.115.0
uvicorn==0.32.0
langchain==0.1.20
psycopg2-binary>=2.9.0
httpx>=0.27.0
# ... etc
```

**However:** This file was ALREADY present in the git commit. The issue wasn't actually the file being missing from git, but rather the Docker build context problem (see Error 3).

---

### ❌ Error 3: "uvicorn: not found" on Container Start

**Symptom:**
Docker build succeeded, but container failed to start:
```
Starting Container
/bin/sh: 1: uvicorn: not found
/bin/sh: 1: uvicorn: not found
/bin/sh: 1: uvicorn: not found
```

**Railway Configuration at this point:**
- Root Directory: `.` (project root)
- Dockerfile Path: `backend/Dockerfile`

**Root Cause:**
When Railway's root directory is `.` (project root) and Dockerfile path is `backend/Dockerfile`, the **Docker build context is the project root**, not the `backend/` directory.

The original Dockerfile did:
```dockerfile
WORKDIR /app
COPY requirements.txt .     # Copies from project root
COPY . .                     # Copies ENTIRE project including backend/
CMD uvicorn app.main:app
```

This resulted in:
- Application code at `/app/backend/app/` (wrong path)
- `uvicorn app.main:app` looking for `/app/app/` (doesn't exist)
- Python can't find the `app` module → "uvicorn: not found"

**Fix (commit `d95bb89`):**
Updated `backend/Dockerfile` to use correct paths relative to project root build context:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .    # ← Changed from "requirements.txt"
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (includes templates/ directory)
COPY backend/ .                     # ← Changed from "COPY . ."

# Expose port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**Key Changes:**
- Line 7: `COPY backend/requirements.txt .` (path from project root)
- Line 11: `COPY backend/ .` (copy only backend dir contents to /app)

This puts the app code at `/app/app/main.py`, so `uvicorn app.main:app` works correctly.

---

## ✅ Final Working Configuration

### Railway Dashboard Settings
- **Root Directory:** `.` (project root)
- **Dockerfile Path:** `backend/Dockerfile`
- **Builder:** Dockerfile
- **Branch:** `gradio-pipeline-deployment`

### Dockerfile (`backend/Dockerfile`)
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (includes templates/ directory)
COPY backend/ .

# Expose port
EXPOSE 8000

# Run FastAPI with uvicorn
# Railway sets $PORT dynamically, default to 8000 for local development
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### File Structure Required
```
/ (project root)
├── backend/
│   ├── Dockerfile              ← Railway builds this
│   ├── requirements.txt        ← MUST exist with all dependencies
│   ├── app/
│   │   ├── main.py            ← FastAPI app
│   │   ├── routes.py
│   │   └── ...
│   ├── pipeline/
│   └── ...
└── (other project files)
```

### Critical Files
**`backend/requirements.txt` (must include):**
```txt
fastapi==0.115.0
uvicorn==0.32.0
langchain==0.1.20
langchain-openai==0.0.8
langchain-community==0.0.38
langchain-core==0.1.52
openai>=1.0.0
pypdf>=3.17.0
pyyaml>=6.0
jinja2>=3.1.3
python-dotenv>=1.0.0
pydantic>=2.5.0
httpx>=0.27.0
requests>=2.31.0
psycopg2-binary>=2.9.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
fastapi-mcp==0.4.0
```

---

## Key Learnings

### 1. Railway Root Directory Behavior
- **Root Directory = `backend`**: Railway changes context to `backend/`, expects relative paths
- **Root Directory = `.`**: Railway stays at project root, Dockerfile paths must include `backend/`

### 2. railway.json Location
- When root directory is set to a subdirectory, `railway.json` should be at **project root**, not in the subdirectory
- **Best practice:** Don't use `railway.json` at all - use Railway dashboard settings only

### 3. Docker Build Context
- Build context is determined by Railway's Root Directory setting
- All `COPY` commands in Dockerfile are relative to the build context
- **Mismatch between root directory and COPY paths = build failures**

### 4. Silent Build Failures
- If Docker build starts but produces no logs, it's usually:
  - Missing file in `COPY` command
  - Build context mismatch
  - Cached error state (clear build cache in Railway)

### 5. Container Start vs Build Success
- Docker build can succeed but container fails to start
- Check that application code is at expected path: `/app/app/` for `uvicorn app.main:app`
- Use `COPY backend/ .` not `COPY . .` when building from project root

---

## Commit History

1. **b0135b7** - `fix: restore railway.json for explicit Dockerfile configuration`
   - ❌ Attempted to fix with railway.json (wrong approach)

2. **1c2c87d** - `fix: remove railway.json to use Railway dashboard configuration only`
   - ✅ Removed railway.json, changed Railway dashboard to Root Directory = `.`

3. **d95bb89** - `fix: update Dockerfile paths for project root build context`
   - ✅ Updated Dockerfile COPY paths to work with project root context
   - **DEPLOYMENT SUCCESSFUL** ✅

---

## Troubleshooting Guide

### If you see "failed to read dockerfile"
1. Check Railway Root Directory setting
2. Ensure Dockerfile Path is **relative** to Root Directory (not absolute path)
3. Verify Dockerfile exists at that path in your git branch

### If build starts but produces no logs
1. Check that `requirements.txt` exists at the path specified in Dockerfile
2. Clear Railway build cache (Settings → Build Cache → Clear)
3. Verify all files in `COPY` commands exist in the git commit

### If you see "command not found" on container start
1. Check that `COPY` commands are copying files to correct locations
2. Verify build context matches Dockerfile paths
3. Test locally: `docker build -t test -f backend/Dockerfile .` (from project root)

---

## Testing Locally

To test the exact Railway configuration locally:

```bash
# From project root
docker build -t innovation-backend -f backend/Dockerfile .

# Run container
docker run -p 8000:8000 -e PORT=8000 innovation-backend

# Test health endpoint
curl http://localhost:8000/health
```

Expected output:
```json
{"status": "ok", "version": "1.0.0"}
```

---

## Final Status

✅ **DEPLOYMENT SUCCESSFUL**

- Branch: `gradio-pipeline-deployment`
- Commit: `d95bb89`
- Railway URL: `https://innovation-backend-production.up.railway.app`
- Health Check: `/health` endpoint responding
- Pipeline: All 7 stages (Stage 0-6) deployed and operational
