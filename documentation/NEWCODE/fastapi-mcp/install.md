  📋 FastAPI MCP Implementation Plan

⏺ Step 1: Install FastAPI MCP in Backend

  cd backend
  uv add fastapi-mcp
  # or pip install fastapi-mcp

  Step 2: Integrate into backend/app/main.py

  # backend/app/main.py
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  from fastapi_mcp import FastApiMCP  # NEW
  from app.routes import router

  app = FastAPI(
      title="Innovation Intelligence API",
      description="Backend API for CPG Innovation Intelligence Pipeline",
      version="1.0.0"
  )

  # ... existing CORS and startup code ...

  # Register routes
  app.include_router(router)

  # NEW: Add FastAPI MCP
  mcp = FastApiMCP(
      app,
      name="Innovation Intelligence MCP",
      description="MCP server for CPG innovation pipeline",
      # Only expose specific endpoints
      include_operations=["run_pipeline", "get_status", "health_check"]
  )

  # Mount MCP server at /mcp
  mcp.mount_http()

  Step 3: Add operation_id to routes (for clean MCP tool names)

  # backend/app/routes.py
  @router.get("/health", response_model=HealthResponse, operation_id="health_check")
  async def health_check():
      """Health check endpoint"""
      ...

  @router.post("/run", response_model=RunPipelineResponse, operation_id="run_pipeline")
  async def run_pipeline(request: RunPipelineRequest):
      """Start pipeline execution"""
      ...

  @router.get("/status/{run_id}", response_model=PipelineStatus, operation_id="get_status")
  async def get_status(run_id: str):
      """Get pipeline status"""
      ...

  Step 4: Configure Claude Code to Use MCP

  Create .claude/mcp_config.json:
  {
    "mcpServers": {
      "innovation-backend": {
        "url": "http://localhost:8000/mcp"
      }
    }
  }

  🎬 Demonstration: Building Frontend with FastAPI MCP

  Workflow:

  STEP 1: Start backend with MCP
  $ cd backend
  $ uvicorn app.main:app --reload
  > MCP server available at http://localhost:8000/mcp

  STEP 2: In Claude Code
  Me: "List available MCP tools from innovation backend"
  Claude: Shows 3 tools:
    - health_check
    - run_pipeline
    - get_status

  STEP 3: Build component with live testing
  Me: "Build ExtractionAnimation component and test it by starting a real pipeline"

  Claude:
  1. Generates ExtractionAnimation.tsx
  2. Uses MCP tool "run_pipeline" with test blob URL
  3. Gets run_id: "run-789"
  4. Uses MCP tool "get_status" to monitor
  5. Updates component to handle real status responses
  6. Tests all 4 states with actual pipeline data

  STEP 4: Debug issues in real-time
  Me: "The component shows 'error' but backend says 'running'"

  Claude (via MCP):
  1. Calls get_status(run_id)
  2. Inspects actual response
  3. Identifies: Frontend expects "processing" but backend returns "running"
  4. Updates component state mapping
  5. Re-tests via MCP
  6. Confirms fix works

  💡 Key Benefits for This Project

  | Without FastAPI MCP                         | With FastAPI MCP                    |
  |---------------------------------------------|-------------------------------------|
  | Manual curl testing                         | Claude calls API directly           |
  | Guess request/response formats              | Auto-extracted from Pydantic models |
  | Switch between Claude & terminal            | Everything in Claude                |
  | Mock data for testing                       | Real pipeline execution             |
  | Frontend-backend mismatches discovered late | Caught immediately via MCP          |
  | Manual status polling                       | Claude polls automatically          |

  🎯 Recommendation

  YES - Integrate FastAPI MCP immediately!

  Why:
  1. 5 minutes to add (3 lines of code)
  2. Saves hours debugging frontend-backend integration
  3. Perfect for demo (matches Newcode video #1: "FastAPI MCP Debugging")
  4. Live testing of components with real pipeline data
  5. Autonomous agent can test backend without your intervention

  Next Steps:

  1. Install FastAPI MCP in backend (5 min)
  2. Test MCP connection from Claude Code (2 min)
  3. Start building frontend with live backend testing (autonomous)

  Would you like me to:
  1. Add FastAPI MCP to the backend right now?
  2. Generate the MCP config for Claude Code?
  3. Start building the first frontend component with live MCP testing?