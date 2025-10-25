# Testing the New MCP Tools

## Overview

We've added 5 new MCP tools to the Innovation Intelligence System backend. This guide shows how to test and use each tool.

---

## Available MCP Tools (Total: 8)

### Core Pipeline Operations (Original 3)
1. ✅ `health_check` - Check backend health
2. ✅ `run_pipeline` - Start pipeline execution
3. ✅ `get_status` - Get pipeline status

### Brand Profile Operations (NEW)
4. 🆕 `list_brands` - List all available brand profiles
5. 🆕 `get_brand_profile` - Get detailed brand configuration

### Environment & Configuration (NEW)
6. 🆕 `check_environment` - Verify environment variables

### Debug & Introspection (NEW)
7. 🆕 `list_all_runs` - List all pipeline executions
8. 🆕 `get_stage_output` - Get stage-level output for debugging

---

## How to Verify Tools Are Available

### 1. Check Claude Code MCP Status

```bash
claude mcp list
```

**Expected output:**
```
innovation-backend: https://innovation-backend-production.up.railway.app/mcp (HTTP) - ✓ Connected
  Tools: 8 tools
```

### 2. View All Available Tools

In Claude Code, you can ask:
```
Show me all available MCP tools
```

Or check via CLI:
```bash
claude mcp show innovation-backend
```

---

## Testing Each Tool

## Important: About `run_pipeline` Testing

**⚠️ Blob URL Validation:**

The `run_pipeline` tool **requires real Vercel Blob URLs** that match the pattern:
- ✅ Valid: `https://blob.vercel-storage.com/your-file-abc123.pdf`
- ❌ Invalid: `https://public-blob-store.vercel-storage.com/...`
- ❌ Invalid: `https://example.com/test.pdf`
- ❌ Invalid: Local file paths

**To test `run_pipeline`, you must:**
1. Upload a PDF through the frontend: `https://innovation-web-rho.vercel.app/upload`
2. Copy the blob URL from the response
3. Use that real blob URL with the MCP tool

**Why this validation exists:**
- Security: Prevents arbitrary file downloads
- Cost control: Vercel Blob storage is the authorized source
- Reliability: Ensures proper file access permissions

---

### Tool 1: `list_brands`

**Purpose:** Discover which brand profiles are configured

**Test in Claude Code:**
```
Can you list all available brands?
```

**Expected response from Claude:**
```
[Calls mcp__innovation-backend__list_brands]

Available brands:
- columbia-sportswear
- decathlon
- lactalis-canada
- mccormick-usa

Total: 4 brands
```

**Direct API test:**
```bash
curl https://innovation-backend-production.up.railway.app/brands
```

---

### Tool 2: `get_brand_profile`

**Purpose:** Inspect detailed brand configuration

**Test in Claude Code:**
```
What's the brand profile for decathlon?
```

**Expected response from Claude:**
```
[Calls mcp__innovation-backend__get_brand_profile with brand_id="decathlon"]

Decathlon brand profile:
- Company: Decathlon
- Portfolio: Accessible outdoor and sports equipment
- Positioning: Democratizing sports through affordable innovation
- Target audience: Active families, amateur athletes, outdoor enthusiasts
- Innovation areas: Sustainable materials, user-centric design, modular systems
```

**Direct API test:**
```bash
curl https://innovation-backend-production.up.railway.app/brands/decathlon
```

---

### Tool 3: `check_environment`

**Purpose:** Validate deployment configuration

**Test in Claude Code:**
```
Is the backend configured correctly?
```

**Expected response from Claude:**
```
[Calls mcp__innovation-backend__check_environment]

Backend configuration status: ✓ OK

Configured:
- OPENROUTER_API_KEY ✓
- OPENROUTER_BASE_URL ✓
- LLM_MODEL ✓
- VERCEL_BLOB_READ_WRITE_TOKEN ✓
- WEBHOOK_SECRET ✓
- FRONTEND_WEBHOOK_URL ✓

No missing required variables.
```

**If something is missing:**
```
Backend configuration status: ⚠ INCOMPLETE

Configured:
- OPENROUTER_API_KEY ✓
- LLM_MODEL ✓

Missing (required):
- OPENROUTER_BASE_URL ❌
- VERCEL_BLOB_READ_WRITE_TOKEN ❌

Warnings:
- WEBHOOK_SECRET not set (optional)
```

**Direct API test:**
```bash
curl https://innovation-backend-production.up.railway.app/config/env-check
```

---

### Tool 4: `list_all_runs`

**Purpose:** View pipeline execution history

**Test in Claude Code:**
```
Show me the recent pipeline runs
```

**Expected response from Claude:**
```
[Calls mcp__innovation-backend__list_all_runs]

Recent pipeline runs:

1. run-1730000001-1234
   Status: completed
   Brand: lactalis-canada
   Current Stage: 5/5
   Created: 2025-10-25T19:00:00Z

2. run-1730000002-5678
   Status: failed
   Brand: mccormick-usa
   Current Stage: 3/5
   Created: 2025-10-25T18:45:00Z

3. run-1730000003-9012
   Status: running
   Brand: decathlon
   Current Stage: 2/5
   Created: 2025-10-25T18:30:00Z
```

**Test with limit:**
```
Show me the last 5 pipeline runs
```

**Direct API test:**
```bash
curl https://innovation-backend-production.up.railway.app/debug/runs?limit=5
```

---

### Tool 5: `get_stage_output`

**Purpose:** Debug pipeline failures by inspecting stage-level output

**Test in Claude Code:**
```
Why did run-1730000002-5678 fail at stage 3?
```

**Expected workflow:**
```
[Claude calls get_status first to confirm the run exists]
[Then calls get_stage_output with run_id and stage_num=3]

Stage 3 (General Translation) failed because:

Output analysis:
- LLM returned malformed JSON
- Missing closing brace in response
- Error occurred at line 342

Raw output excerpt:
{
  "mechanisms": [
    {"name": "Experience Theater", "description": "..."}
    // Missing closing brace here
  ]
```

**Test specific stage:**
```
What did stage 1 extract from run-1730000001-1234?
```

**Direct API test:**
```bash
# Get stage 3 output
curl https://innovation-backend-production.up.railway.app/debug/runs/run-1730000002-5678/stage/3

# Get stage 1 output
curl https://innovation-backend-production.up.railway.app/debug/runs/run-1730000001-1234/stage/1
```

---

## Example Conversation Flows

### Scenario 1: Starting a New Pipeline Run

```
User: "I want to test the pipeline with a CPG brand"

Claude: [Calls list_brands]
"You can test with these brands:
- lactalis-canada (dairy)
- mccormick-usa (spices/seasonings)
- decathlon (sports equipment)
- columbia-sportswear (outdoor apparel)

Which brand would you like to use?"

User: "Let's use lactalis-canada"

Claude: [Calls get_brand_profile to understand context]
"Great choice. Lactalis Canada focuses on dairy innovation...
Do you have a PDF URL ready?"

User: "Yes, https://blob.vercel-storage.com/test-abc123.pdf"

Claude: [Calls run_pipeline with blob_url and brand_id="lactalis-canada"]
"Pipeline started! Run ID: run-1730000004-3456
I'll monitor the progress..."
```

---

### Scenario 2: Debugging a Failed Run

```
User: "Why did my pipeline fail?"

Claude: [Calls list_all_runs to find recent failures]
"I see a failed run: run-1730000002-5678 (mccormick-usa)
It failed at Stage 3. Let me investigate..."

[Calls get_stage_output with stage_num=3]

"The issue is in Stage 3 (General Translation):
- The LLM returned incomplete JSON
- Stage 2 output contained 12 mechanisms
- But Stage 3 only processed 8 before the JSON error

The raw LLM response shows a missing closing bracket.

Would you like me to:
1. Check if Stage 2 output was valid?
2. Suggest a fix for the prompt?
3. Rerun the pipeline with the same inputs?"
```

---

### Scenario 3: Environment Validation

```
User: "The pipeline keeps failing immediately"

Claude: [Calls check_environment]
"Found the issue - your environment is misconfigured:

Missing required variables:
- OPENROUTER_API_KEY ❌

The backend can't call the LLM without this API key.
Check your Railway dashboard → Settings → Variables"
```

---

## Common Testing Patterns

### Pattern 1: Brand Discovery Before Running Pipeline
```
1. list_brands → Get available options
2. get_brand_profile → Understand brand context
3. run_pipeline → Execute with chosen brand
4. get_status → Monitor progress
```

### Pattern 2: Debugging Failed Pipeline
```
1. list_all_runs → Find failed run_id
2. get_status → Confirm which stage failed
3. get_stage_output → Inspect raw output
4. get_stage_output (previous stage) → Verify inputs were valid
```

### Pattern 3: Deployment Validation
```
1. health_check → Backend is up
2. check_environment → All config present
3. list_brands → Data files accessible
4. get_brand_profile → YAML parsing works
```

---

## Error Scenarios to Test

### Test 1: Invalid Brand ID
```
Ask Claude: "Get the profile for fake-brand"

Expected: HTTPException 404
Message: "Brand 'fake-brand' not found"
```

### Test 2: Non-Existent Run ID
```
Ask Claude: "Check status of run-9999999"

Expected: HTTPException 404
Message: "Run 'run-9999999' not found"
```

### Test 3: Invalid Stage Number
```
Ask Claude: "Get stage 10 output for run-123"

Expected: HTTPException 400
Message: "Stage number must be between 1 and 5"
```

### Test 4: Stage Not Yet Complete
```
Ask Claude: "Get stage 5 output for run-123"
(where run-123 is only at stage 2)

Expected: HTTPException 404
Message: "Stage 5 output not found for run 'run-123'. Stage may not have completed yet."
```

---

## Troubleshooting

### Issue: Tools Not Appearing

**Check 1: Verify Railway deployment**
```bash
curl https://innovation-backend-production.up.railway.app/
# Should show: "transport": "http"
```

**Check 2: Reconnect MCP server**
```bash
claude mcp remove innovation-backend
claude mcp add --transport http innovation-backend https://innovation-backend-production.up.railway.app/mcp
```

**Check 3: Verify tool count**
```bash
claude mcp list
# Should show: "Tools: 8 tools"
```

---

### Issue: Tool Returns Unexpected Results

**Check 4: Test API directly**
```bash
# Test each endpoint
curl https://innovation-backend-production.up.railway.app/brands
curl https://innovation-backend-production.up.railway.app/config/env-check
curl https://innovation-backend-production.up.railway.app/debug/runs
```

**Check 5: Check Railway logs**
```bash
railway logs
```

---

## Summary

**New Capabilities:**
- ✅ Brand discovery and inspection
- ✅ Environment validation
- ✅ Pipeline history browsing
- ✅ Stage-level debugging
- ✅ Configuration verification

**Use Cases Enabled:**
1. **Faster debugging** - Inspect stage outputs without SSH/Railway dashboard
2. **Better testing** - Discover brands and configurations quickly
3. **Deployment validation** - Check env vars before running pipelines
4. **Pipeline monitoring** - See all runs and their status
5. **Development flow** - Claude can guide users through pipeline setup

**Next Steps:**
1. Test each tool with real data
2. Document common debugging workflows
3. Consider adding more tools (run logs, delete test runs, etc.)
