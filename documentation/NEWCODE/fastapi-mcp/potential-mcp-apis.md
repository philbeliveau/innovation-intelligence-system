# Potential APIs for MCP Transformation

This document analyzes which APIs in the Innovation Intelligence System could benefit from being exposed as MCP tools.

---

## Current MCP Tools (Backend - Railway)

**Already Implemented:**

1. ✅ **`health_check`** - Check backend health status
2. ✅ **`run_pipeline`** - Start a new pipeline execution
3. ✅ **`get_status`** - Get pipeline status by run_id

**Location:** `backend/app/routes.py`
**Deployment:** Railway (https://innovation-backend-production.up.railway.app/mcp)

---

## Candidate APIs for MCP Transformation

### Category 1: Backend Development & Testing Tools (HIGH VALUE)

These would be extremely useful during backend development in Claude Code.

#### 1. **Brand Profile Operations** 🌟 HIGH PRIORITY

**Current Implementation:** Helper functions in `backend/app/routes.py`

**Potential MCP Tools:**

```python
# List all available brand profiles
@router.get("/brands", operation_id="list_brands")
async def list_brands():
    """List all available brand profiles"""
    # Return: ["lactalis-canada", "mccormick-usa", "decathlon", "columbia-sportswear"]

# Get brand profile details
@router.get("/brands/{brand_id}", operation_id="get_brand_profile")
async def get_brand_profile(brand_id: str):
    """Get detailed brand profile by ID"""
    # Return: Full YAML data (company_name, portfolio, positioning, etc.)

# Validate brand profile YAML
@router.post("/brands/validate", operation_id="validate_brand_profile")
async def validate_brand_profile(profile_yaml: str):
    """Validate brand profile YAML structure"""
    # Return: {valid: bool, errors: [...], warnings: [...]}
```

**Use Case:**
- Claude can list available brands when user asks "which brands are configured?"
- Claude can inspect brand profiles to understand pipeline context
- Claude can validate new brand profiles before deployment

---

#### 2. **Pipeline Debug & Introspection** 🌟 HIGH PRIORITY

**Potential MCP Tools:**

```python
# Get detailed stage output
@router.get("/debug/runs/{run_id}/stage/{stage_num}", operation_id="get_stage_output")
async def get_stage_output(run_id: str, stage_num: int):
    """Get raw output from specific pipeline stage"""
    # Return: Stage JSON output, prompts used, LLM response

# List all pipeline runs
@router.get("/debug/runs", operation_id="list_all_runs")
async def list_all_runs(limit: int = 20):
    """List all pipeline runs with status"""
    # Return: [{run_id, status, created_at, brand_id, current_stage}, ...]

# Get pipeline logs
@router.get("/debug/runs/{run_id}/logs", operation_id="get_run_logs")
async def get_run_logs(run_id: str):
    """Get execution logs for debugging"""
    # Return: Full execution log with timestamps

# Clean up test runs
@router.delete("/debug/runs/{run_id}", operation_id="delete_test_run")
async def delete_test_run(run_id: str):
    """Delete test run and cleanup temp files"""
    # Return: {deleted: true, files_removed: [...]}
```

**Use Case:**
- Debug why Stage 3 failed for run-123456
- Compare outputs between different runs
- Clean up test runs after development

---

#### 3. **Configuration & Environment** 🔧 MEDIUM PRIORITY

**Potential MCP Tools:**

```python
# Get environment status
@router.get("/config/env-check", operation_id="check_environment")
async def check_environment():
    """Check which environment variables are configured"""
    # Return: {
    #   configured: ["OPENROUTER_API_KEY", "LLM_MODEL"],
    #   missing: ["WEBHOOK_SECRET"],
    #   warnings: ["VERCEL_BLOB_READ_WRITE_TOKEN is empty"]
    # }

# Get active configuration
@router.get("/config/settings", operation_id="get_settings")
async def get_settings():
    """Get current pipeline configuration (non-sensitive)"""
    # Return: {llm_model: "...", base_url: "...", timeout: 120}

# Test LLM connection
@router.post("/config/test-llm", operation_id="test_llm_connection")
async def test_llm_connection():
    """Test connection to OpenRouter/LLM"""
    # Return: {success: true, latency_ms: 245, model: "..."}
```

**Use Case:**
- Quickly check if API keys are configured correctly
- Test LLM connectivity before running expensive pipelines
- Understand current configuration during debugging

---

### Category 2: Frontend Development Tools (MEDIUM VALUE)

These would help when building/testing the Next.js frontend.

#### 4. **Database Introspection** 🔧 MEDIUM PRIORITY

**Current:** Prisma database via frontend API routes

**Potential MCP Tools:**

```python
# List recent uploads
@router.get("/data/uploads", operation_id="list_uploads")
async def list_uploads(limit: int = 10):
    """List recent document uploads"""
    # Return: [{upload_id, filename, user_id, created_at, status}, ...]

# Get opportunity cards for run
@router.get("/data/runs/{run_id}/cards", operation_id="get_opportunity_cards")
async def get_opportunity_cards(run_id: str):
    """Get all opportunity cards for a pipeline run"""
    # Return: [{card_id, title, description, starred, created_at}, ...]

# Search opportunity cards
@router.post("/data/cards/search", operation_id="search_opportunity_cards")
async def search_cards(query: str, user_id: str = None):
    """Search opportunity cards by content"""
    # Return: Matching cards with relevance scores
```

**Use Case:**
- Claude can inspect database state while debugging frontend
- Test if opportunity cards were created correctly
- Search for specific cards during testing

---

#### 5. **Frontend API Testing** 🔧 LOW-MEDIUM PRIORITY

**Current:** Next.js API routes in `innovation-web/app/api/`

**Potential MCP Tools:**

```python
# Simulate webhook
@router.post("/test/webhook-simulate", operation_id="simulate_webhook")
async def simulate_webhook(run_id: str, stage: int, status: str):
    """Simulate pipeline webhook for testing frontend"""
    # Send actual webhook to frontend
    # Return: {sent: true, response_code: 200}

# Test file upload flow
@router.post("/test/upload-simulate", operation_id="simulate_upload")
async def simulate_upload(filename: str, size_mb: float):
    """Simulate Vercel Blob upload for testing"""
    # Return mock blob URL without actual upload
    # Return: {blob_url: "https://...", upload_id: "..."}
```

**Use Case:**
- Test frontend webhook handling without running full pipeline
- Test upload flow without uploading actual files

---

### Category 3: Analytics & Monitoring (LOW-MEDIUM VALUE)

#### 6. **Pipeline Analytics** 📊 LOW-MEDIUM PRIORITY

**Potential MCP Tools:**

```python
# Get pipeline statistics
@router.get("/analytics/stats", operation_id="get_pipeline_stats")
async def get_stats(days: int = 7):
    """Get pipeline execution statistics"""
    # Return: {
    #   total_runs: 45,
    #   success_rate: 0.89,
    #   avg_duration_sec: 342,
    #   most_common_failures: [{"stage": 3, "count": 3}]
    # }

# Get stage performance
@router.get("/analytics/stage-performance", operation_id="get_stage_performance")
async def get_stage_performance():
    """Analyze which stages take longest"""
    # Return: [{stage: 1, avg_duration: 45}, {stage: 2, avg_duration: 120}, ...]

# Get error patterns
@router.get("/analytics/errors", operation_id="get_error_patterns")
async def get_error_patterns(days: int = 7):
    """Analyze common error patterns"""
    # Return: [{error_type: "LLM timeout", count: 5, last_seen: "..."}, ...]
```

**Use Case:**
- Claude can analyze pipeline performance trends
- Identify bottleneck stages
- Report common error patterns

---

## Recommendation Priority

### 🌟 Implement Immediately (High Impact, Low Effort)

1. **Brand Profile Operations** (`list_brands`, `get_brand_profile`)
   - **Why:** Essential for understanding pipeline context
   - **Effort:** 30 minutes (just expose existing helper functions)
   - **Impact:** Claude can answer "which brands exist?" and inspect configurations

2. **Pipeline Debug Tools** (`get_stage_output`, `list_all_runs`)
   - **Why:** Critical for debugging pipeline issues
   - **Effort:** 1 hour (read from `/tmp/runs/` directory)
   - **Impact:** Claude can debug "why did Stage 3 fail?" questions

3. **Environment Check** (`check_environment`)
   - **Why:** Quick validation of deployment configuration
   - **Effort:** 15 minutes (check env vars)
   - **Impact:** Prevents wasted time debugging missing API keys

### 🔧 Implement Soon (Medium Impact)

4. **Get Run Logs** (`get_run_logs`)
   - **Effort:** 1 hour
   - **Impact:** Better debugging with full execution logs

5. **Database Introspection** (`list_uploads`, `get_opportunity_cards`)
   - **Effort:** 2 hours (integrate with Prisma)
   - **Impact:** Claude can verify database state during development

### 📊 Consider Later (Lower Priority)

6. **Analytics Tools** (`get_pipeline_stats`, `get_stage_performance`)
   - **Effort:** 3-4 hours
   - **Impact:** Useful for optimization, not critical for development

7. **Test Simulation Tools** (`simulate_webhook`, `simulate_upload`)
   - **Effort:** 2-3 hours
   - **Impact:** Nice-to-have for testing

---

## Implementation Example: Brand Profile Operations

Here's how to add the brand profile MCP tools:

**File: `backend/app/routes.py`**

```python
from pathlib import Path

# Add after existing routes

@router.get("/brands", operation_id="list_brands")
async def list_brands():
    """List all available brand profiles for pipeline execution"""
    brand_dir = Path(__file__).parent.parent / "data" / "brand-profiles"

    if not brand_dir.exists():
        return {"brands": []}

    brands = []
    for yaml_file in brand_dir.glob("*.yaml"):
        brand_id = yaml_file.stem
        brands.append(brand_id)

    return {
        "brands": sorted(brands),
        "count": len(brands)
    }


@router.get("/brands/{brand_id}", operation_id="get_brand_profile")
async def get_brand_profile_endpoint(brand_id: str):
    """Get detailed brand profile configuration by ID"""
    # Reuse existing load_brand_profile() helper
    brand_profile = load_brand_profile(brand_id)

    return {
        "brand_id": brand_id,
        "profile": brand_profile
    }
```

**Then update FastAPI MCP configuration:**

```python
# In backend/app/main.py
mcp = FastApiMCP(
    app,
    name="Innovation Intelligence MCP",
    description="MCP server for CPG innovation pipeline",
    include_operations=[
        "health_check",
        "run_pipeline",
        "get_status",
        "list_brands",           # NEW
        "get_brand_profile",     # NEW
    ]
)
mcp.mount_http()
```

**Deploy:**
```bash
railway up
```

**Result:** Claude Code can now call:
- `mcp__innovation-backend__list_brands`
- `mcp__innovation-backend__get_brand_profile`

---

## Benefits Summary

### With Brand Profile Tools:
```
User: "Which brands can I test with?"
Claude: [calls list_brands tool]
"You can test with: lactalis-canada, mccormick-usa, decathlon, columbia-sportswear"

User: "What's Decathlon's positioning?"
Claude: [calls get_brand_profile tool with brand_id="decathlon"]
"Decathlon's positioning focuses on accessible outdoor/sports equipment..."
```

### With Debug Tools:
```
User: "Why did run-123456 fail?"
Claude: [calls get_status tool]
[calls get_stage_output tool with run_id and stage_num=3]
"Stage 3 (General Translation) failed because the LLM response was malformed JSON.
Here's the actual output: {...}"
```

### With Environment Check:
```
User: "Is everything configured correctly?"
Claude: [calls check_environment tool]
"Warning: VERCEL_BLOB_READ_WRITE_TOKEN is missing. PDF downloads will fail."
```

---

## Security Considerations

### Safe to Expose (Read-Only):
- ✅ `list_brands` - Just lists filenames
- ✅ `get_brand_profile` - Reads YAML files
- ✅ `get_status` - Reads status.json
- ✅ `get_stage_output` - Reads existing outputs
- ✅ `list_all_runs` - Lists directories
- ✅ `check_environment` - Checks env vars (no values exposed)

### Requires Authentication:
- ⚠️ `delete_test_run` - Destructive operation
- ⚠️ `simulate_webhook` - Could spam frontend
- ⚠️ `get_settings` - May expose sensitive config

### Should NOT Expose:
- ❌ Database write operations
- ❌ User data access without auth
- ❌ API key values
- ❌ Admin operations (delete all, reset database, etc.)

---

## Next Steps

1. **Implement Top 3 Priority Tools** (Brand profile + Debug + Environment)
   - Estimated time: 2-3 hours
   - Deploy to Railway
   - Test in Claude Code

2. **Document Usage Patterns**
   - Add examples to setup-guide.md
   - Create troubleshooting recipes

3. **Monitor Usage**
   - Track which tools are most useful
   - Gather feedback for future improvements

4. **Consider Authentication**
   - If exposing write operations
   - Use FastAPI MCP's AuthConfig

---

## Conclusion

**Quick Wins (Implement Now):**
- Brand profile operations (30 min)
- Environment check (15 min)
- List all runs (30 min)

**Total Effort:** ~1.5 hours
**Impact:** Significantly better development experience with Claude Code

**Long-term Vision:**
- Full pipeline introspection
- Analytics and performance monitoring
- Test simulation tools
- Database query capabilities

The key is to start with **read-only, safe operations** that provide immediate value for development and debugging.
