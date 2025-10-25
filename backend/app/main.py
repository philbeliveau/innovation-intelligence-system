"""FastAPI Application Entry Point

Minimal FastAPI backend for Innovation Intelligence System.
Handles pipeline execution requests from frontend.
"""
import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from app.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Innovation Intelligence API",
    description="Backend API for CPG Innovation Intelligence Pipeline",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup - fail fast if critical env vars missing"""
    logger.info("=" * 60)
    logger.info("Innovation Intelligence API - Starting Up")
    logger.info("=" * 60)

    # Required environment variables
    required_vars = [
        "OPENROUTER_API_KEY",
        "OPENROUTER_BASE_URL",
        "LLM_MODEL"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"CRITICAL: Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Application cannot start. Check Railway dashboard Variables tab.")
        logger.error("Exiting...")
        sys.exit(1)

    # Log configuration (with redacted secrets)
    logger.info("Configuration validated:")
    logger.info(f"  OPENROUTER_API_KEY: [REDACTED]")
    logger.info(f"  OPENROUTER_BASE_URL: {os.getenv('OPENROUTER_BASE_URL')}")
    logger.info(f"  LLM_MODEL: {os.getenv('LLM_MODEL')}")

    # Optional variables
    if os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN"):
        logger.info(f"  VERCEL_BLOB_READ_WRITE_TOKEN: [REDACTED]")
    else:
        logger.warning("  VERCEL_BLOB_READ_WRITE_TOKEN: Not set (PDF downloads will fail)")

    logger.info("Startup complete - API ready to accept requests")
    logger.info("=" * 60)


# CORS middleware - allow Vercel frontend to call Railway backend
# NOTE: Wildcard patterns like "https://*.vercel.app" are NOT supported by CORS spec
# Railway deployment will need environment variable ALLOWED_ORIGINS for dynamic origins
allowed_origins = [
    "http://localhost:3000",  # Local dev
    "https://innovation-web.vercel.app"  # Production frontend
]

# Add environment-based origins (for Vercel preview deployments)
env_origins = os.getenv("ALLOWED_ORIGINS", "")
if env_origins:
    allowed_origins.extend([origin.strip() for origin in env_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)

# FastAPI MCP - Expose endpoints as MCP tools for Claude
mcp = FastApiMCP(
    app,
    name="Innovation Intelligence MCP",
    description="MCP server for CPG innovation pipeline - exposes pipeline execution and status endpoints",
    # Only expose specific endpoints (by operation_id)
    include_operations=["health_check", "run_pipeline", "get_status"]
)

# Mount MCP server - using HTTP transport (recommended for Claude Code)
# HTTP transport implements the latest MCP Streamable HTTP specification
mcp.mount_http()


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Innovation Intelligence API",
        "version": "1.0.0",
        "docs": "/docs",
        "mcp": "/mcp",
        "transport": "http"  # HTTP transport enabled
    }
