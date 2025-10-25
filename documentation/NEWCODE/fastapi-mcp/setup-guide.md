# FastAPI MCP Setup Guide - Complete Implementation

## Overview

This guide documents the complete process of integrating **FastAPI MCP** into the Innovation Intelligence System backend, enabling Claude Code to directly call backend APIs as MCP tools.

**Goal**: Expose FastAPI endpoints (`/health`, `/run`, `/status/{run_id}`) as MCP tools that Claude Code can discover and call automatically.

**Result**: 3 MCP tools available in Claude Code:
- `mcp__innovation-backend__health_check`
- `mcp__innovation-backend__run_pipeline`
- `mcp__innovation-backend__get_status`

---

## Prerequisites

- FastAPI backend already running
- Railway deployment configured
- Claude Code CLI installed
- Python 3.11+

---

## Step 1: Install FastAPI MCP Package

Add `fastapi-mcp` to your backend dependencies:

```bash
# From backend directory
pip install fastapi-mcp==0.4.0

# Add to requirements.txt
echo "fastapi-mcp==0.4.0" >> requirements.txt
```

**Why 0.4.0?** This version supports the latest HTTP transport method which is required for Claude Code compatibility.

---

## Step 2: Add Operation IDs to FastAPI Routes

FastAPI MCP uses the `operation_id` parameter from route decorators as MCP tool names. Without explicit operation IDs, FastAPI generates cryptic auto-generated names.

**File: `backend/app/routes.py`**

```python
from fastapi import APIRouter

router = APIRouter()

# ✅ GOOD: Explicit operation_id = clear MCP tool name
@router.get("/health", response_model=HealthResponse, operation_id="health_check")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

# ✅ GOOD: Explicit operation_id
@router.post("/run", response_model=RunPipelineResponse, operation_id="run_pipeline")
async def run_pipeline(request: RunPipelineRequest):
    """Start a new pipeline run"""
    # Implementation here
    pass

# ✅ GOOD: Explicit operation_id
@router.get("/status/{run_id}", response_model=PipelineStatus, operation_id="get_status")
async def get_status(run_id: str):
    """Get pipeline status by run_id"""
    # Implementation here
    pass
```

**❌ BAD: No operation_id (auto-generated names)**
```python
# This creates a tool named something like: "read_status_status__run_id__get"
@router.get("/status/{run_id}")
async def get_status(run_id: str):
    pass
```

---

## Step 3: Configure FastAPI MCP in Main Application

**File: `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from app.routes import router

app = FastAPI(
    title="Innovation Intelligence API",
    description="Backend API for CPG Innovation Intelligence Pipeline",
    version="1.0.0"
)

# Register routes FIRST (before FastAPI MCP)
app.include_router(router)

# ============================================
# FastAPI MCP Configuration
# ============================================

# Create MCP server instance
mcp = FastApiMCP(
    app,
    name="Innovation Intelligence MCP",
    description="MCP server for CPG innovation pipeline - exposes pipeline execution and status endpoints",
    # IMPORTANT: Only expose specific endpoints by operation_id
    include_operations=["health_check", "run_pipeline", "get_status"]
)

# Mount using HTTP transport (recommended for Claude Code)
# HTTP transport implements the latest MCP Streamable HTTP specification
mcp.mount_http()

# ============================================
# Root endpoint (optional - for verification)
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Innovation Intelligence API",
        "version": "1.0.0",
        "docs": "/docs",
        "mcp": "/mcp",
        "transport": "http"  # Indicates HTTP transport is enabled
    }
```

**Key Configuration Options:**

1. **`include_operations`**: Whitelist specific endpoints by operation_id
   - Alternative: Use `exclude_operations` to blacklist endpoints
   - Alternative: Use `include_tags` or `exclude_tags` for tag-based filtering

2. **`mount_http()` vs `mount()`**:
   - `mount_http()` → HTTP transport (recommended for Claude Code)
   - `mount_sse()` → Server-Sent Events transport (backwards compatibility)
   - `mount()` → Sets up both HTTP and SSE (not recommended)

3. **Security**: Only expose safe, read-only operations or operations that require authentication

---

## Step 4: Deploy Backend to Railway

The backend must be deployed for Claude Code to access the MCP endpoint.

**From project root directory:**

```bash
# Check Railway status
railway status

# Deploy from project root (Railway expects 'backend' folder relative to root)
railway up

# Monitor deployment
railway logs
```

**Important:**
- Deploy from **project root** (`innovation-intelligence-system/`), NOT from `backend/` subdirectory
- Railway is configured with "Root Directory: backend" in the dashboard
- This means Railway looks for `backend/` folder relative to where you deploy from

**Verify deployment:**
```bash
# Check root endpoint shows HTTP transport
curl https://innovation-backend-production.up.railway.app/

# Expected output:
# {
#   "name": "Innovation Intelligence API",
#   "version": "1.0.0",
#   "docs": "/docs",
#   "mcp": "/mcp",
#   "transport": "http"
# }
```

---

## Step 5: Add MCP Server to Claude Code

Claude Code uses a different configuration system than Claude Desktop.

**Using Claude Code CLI:**

```bash
# Navigate to project directory
cd /Users/your-username/path/to/innovation-intelligence-system

# Add MCP server with HTTP transport
claude mcp add --transport http innovation-backend https://innovation-backend-production.up.railway.app/mcp

# Verify configuration
claude mcp list

# Expected output:
# innovation-backend: https://innovation-backend-production.up.railway.app/mcp (HTTP) - ✓ Connected
```

**Configuration is stored in:**
- Global: `~/.claude.json`
- Project-specific: `.claude/.mcp.json` (if using project scope)

**Alternative: Manual JSON configuration:**

Create or edit `.mcp.json` in your project:

```json
{
  "mcpServers": {
    "innovation-backend": {
      "type": "http",
      "url": "https://innovation-backend-production.up.railway.app/mcp"
    }
  }
}
```

---

## Step 6: Verify MCP Tools Are Available

**Check MCP server status:**

```bash
claude mcp list
```

**Expected output:**
```
innovation-backend: https://innovation-backend-production.up.railway.app/mcp (HTTP) - ✓ Connected
  Tools: 3 tools
```

**In Claude Code conversation, the tools appear as:**
```
mcp__innovation-backend__health_check
mcp__innovation-backend__run_pipeline
mcp__innovation-backend__get_status
```

---

## Step 7: Test MCP Tools

**Test health_check tool:**
```xml
<invoke name="mcp__innovation-backend__health_check">
</invoke>
```

**Test run_pipeline tool:**
```xml
<invoke name="mcp__innovation-backend__run_pipeline">
  <parameter name="blob_url">https://blob.vercel-storage.com/test.pdf</parameter>
  <parameter name="brand_id">test-brand</parameter>
  <parameter name="run_id">test-run-123</parameter>
</invoke>
```

**Test get_status tool:**
```xml
<invoke name="mcp__innovation-backend__get_status">
  <parameter name="run_id">test-run-123</parameter>
</invoke>
```

---

## Troubleshooting

### Issue 1: "Failed to connect" in Claude Code

**Symptoms:**
```
innovation-backend: https://.../.../mcp (HTTP) - ✗ Failed to connect
```

**Possible causes:**
1. Railway hasn't finished deploying
2. Backend is using SSE transport instead of HTTP transport
3. CORS issues

**Solution:**
```bash
# 1. Check if backend is running
curl https://innovation-backend-production.up.railway.app/health

# 2. Verify HTTP transport is enabled
curl https://innovation-backend-production.up.railway.app/
# Should show: "transport": "http"

# 3. Remove and re-add MCP server
claude mcp remove innovation-backend
claude mcp add --transport http innovation-backend https://innovation-backend-production.up.railway.app/mcp

# 4. Check Railway logs
railway logs
```

### Issue 2: Tools not appearing

**Symptoms:** MCP shows "Connected" but no tools listed

**Possible causes:**
1. `include_operations` doesn't match actual operation_id values
2. Routes registered after `mcp.mount_http()` call

**Solution:**
```python
# Check OpenAPI schema to see actual operation IDs
curl https://innovation-backend-production.up.railway.app/openapi.json | jq '.paths'

# Ensure routes are registered BEFORE mcp.mount_http()
app.include_router(router)  # ✅ Must be BEFORE mcp creation
mcp = FastApiMCP(app, include_operations=[...])
mcp.mount_http()
```

### Issue 3: Wrong transport method (SSE instead of HTTP)

**Symptoms:**
```bash
curl -I https://.../mcp
# Shows: content-type: text/event-stream
```

**Solution:**
```python
# Change in backend/app/main.py
mcp.mount()  # ❌ Sets up SSE transport

# To:
mcp.mount_http()  # ✅ Uses HTTP transport
```

Then redeploy:
```bash
railway up
```

### Issue 4: Railway not auto-deploying

**Symptoms:** Code changes pushed but Railway doesn't rebuild

**Possible causes:**
1. Pushing to wrong branch (Railway watches `main` by default)
2. Railway service not linked to GitHub

**Solution:**
```bash
# Check Railway project settings in dashboard
# Or manually trigger deployment:
railway up
```

---

## Architecture: How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│ Claude Code Session                                             │
│                                                                 │
│  1. Claude discovers MCP tools via /mcp endpoint                │
│  2. Claude calls: mcp__innovation-backend__health_check         │
│                                                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP Request
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Railway (https://innovation-backend-production.up.railway.app)   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ FastAPI Application                                       │  │
│  │                                                           │  │
│  │  /mcp ────────────► FastApiMCP (HTTP Transport)          │  │
│  │                     │                                     │  │
│  │                     ├─► health_check (operation_id)      │  │
│  │                     ├─► run_pipeline (operation_id)      │  │
│  │                     └─► get_status (operation_id)        │  │
│  │                                                           │  │
│  │  /health ──────────► health_check()                      │  │
│  │  /run ─────────────► run_pipeline()                      │  │
│  │  /status/{id} ─────► get_status()                        │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Flow:**
1. Claude Code connects to `/mcp` endpoint (HTTP transport)
2. FastAPI MCP responds with available tools (3 tools based on `include_operations`)
3. When Claude invokes a tool, FastAPI MCP maps it to the corresponding endpoint
4. FastAPI MCP calls the endpoint internally (ASGI transport, no HTTP overhead)
5. Response is returned to Claude Code as MCP tool result

---

## Benefits of FastAPI MCP Integration

### 1. **Real-time Testing During Development**
Claude can test the full pipeline execution and see errors immediately:
```
✅ See which stage failed
✅ See actual error messages
✅ See intermediate results
✅ Debug pipeline issues in real-time
```

### 2. **Automatic API Discovery**
No need to manually write API documentation for Claude:
```python
# FastAPI generates OpenAPI schema automatically
# FastAPI MCP converts it to MCP tools automatically
# Claude discovers tools automatically
```

### 3. **Type Safety**
FastAPI's Pydantic models ensure type-safe tool parameters:
```python
class RunPipelineRequest(BaseModel):
    blob_url: str  # Must be string
    brand_id: str
    run_id: str

# Claude gets parameter types and validation automatically
```

### 4. **Unified Testing**
Same endpoints used by:
- Frontend (Next.js)
- Claude Code (MCP tools)
- Direct API calls (curl/Postman)

No separate test infrastructure needed.

---

## Security Considerations

### 1. **Only Expose Safe Operations**

```python
# ✅ SAFE: Read-only operations
include_operations=["health_check", "get_status"]

# ⚠️ CAUTION: Write operations (ensure authentication)
include_operations=["run_pipeline", "delete_pipeline"]

# ❌ DANGEROUS: Admin operations
include_operations=["delete_all_data", "reset_database"]
```

### 2. **Add Authentication (if needed)**

```python
from fastapi import Depends
from fastapi_mcp import FastApiMCP, AuthConfig

mcp = FastApiMCP(
    app,
    auth_config=AuthConfig(
        issuer="https://auth.example.com/",
        authorize_url="https://auth.example.com/authorize",
        client_id="your-client-id",
        client_secret="your-client-secret",
        dependencies=[Depends(verify_token)],
    ),
)
```

### 3. **Rate Limiting**

Consider adding rate limiting to prevent abuse:
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/run", operation_id="run_pipeline")
@limiter.limit("5/minute")
async def run_pipeline(request: RunPipelineRequest):
    pass
```

---

## References

- **FastAPI MCP Docs**: https://github.com/tadata-org/fastapi_mcp
- **MCP Specification**: https://modelcontextprotocol.io/
- **Claude Code MCP**: https://docs.claude.com/en/docs/claude-code/mcp
- **Railway Deployment**: https://docs.railway.app/

---

## Summary

1. ✅ Install `fastapi-mcp==0.4.0`
2. ✅ Add explicit `operation_id` to all routes
3. ✅ Configure `FastApiMCP` with `include_operations`
4. ✅ Use `mcp.mount_http()` for Claude Code compatibility
5. ✅ Deploy to Railway using `railway up` from project root
6. ✅ Add MCP server to Claude Code: `claude mcp add --transport http ...`
7. ✅ Verify tools appear: `claude mcp list`
8. ✅ Test tools in Claude Code conversation

**Result**: Claude Code can now directly call your backend APIs, test pipelines in real-time, and see detailed error messages during development.
