"""API Route Handlers

Implementation for pipeline execution and status endpoints.
"""
import os
import json
import logging
import time
from pathlib import Path
from threading import Thread
from typing import Dict, Any

import requests
import yaml
from fastapi import APIRouter, HTTPException
from app.models import (
    RunPipelineRequest,
    RunPipelineResponse,
    PipelineStatus,
    HealthResponse
)
from app.pipeline_runner import execute_pipeline_background

logger = logging.getLogger(__name__)

router = APIRouter()


def generate_run_id() -> str:
    """Generate unique run ID in format run-{timestamp}-{random}"""
    import random
    timestamp = int(time.time())
    random_suffix = random.randint(1000, 9999)
    return f"run-{timestamp}-{random_suffix}"


def validate_blob_url(url: str) -> bool:
    """Validate blob URL is from Vercel Blob storage."""
    return url.startswith("https://") and "blob.vercel-storage.com" in url


def download_pdf_from_blob(blob_url: str, run_id: str) -> str:
    """Download PDF from Vercel Blob and save to /tmp.

    Args:
        blob_url: Vercel Blob URL
        run_id: Run identifier

    Returns:
        Path to downloaded PDF

    Raises:
        HTTPException: If download fails or file invalid
    """
    pdf_path = f"/tmp/{run_id}.pdf"

    try:
        logger.info(f"Downloading PDF from {blob_url}")
        response = requests.get(blob_url, timeout=30)
        response.raise_for_status()

        # Validate file size (max 25MB)
        content_length = len(response.content)
        if content_length > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="PDF file size exceeds 25MB limit"
            )

        # Save to temp file
        with open(pdf_path, "wb") as f:
            f.write(response.content)

        logger.info(f"PDF downloaded successfully: {pdf_path} ({content_length} bytes)")
        return pdf_path

    except requests.RequestException as e:
        logger.error(f"Failed to download PDF from blob: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to download PDF from Vercel Blob: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error saving PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF download: {str(e)}"
        )


def load_brand_profile(brand_id: str) -> Dict[str, Any]:
    """Load brand profile from YAML file.

    Args:
        brand_id: Brand identifier (e.g., 'lactalis-canada')

    Returns:
        Brand profile data

    Raises:
        HTTPException: If brand not found or YAML malformed
    """
    # Look in both backend/data and /data (for local dev vs Railway)
    possible_paths = [
        Path(__file__).parent.parent / "data" / "brand-profiles" / f"{brand_id}.yaml",
        Path("/app/data/brand-profiles") / f"{brand_id}.yaml"
    ]

    yaml_path = None
    for path in possible_paths:
        if path.exists():
            yaml_path = path
            break

    if not yaml_path:
        logger.error(f"Brand profile not found: {brand_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Brand '{brand_id}' not found"
        )

    try:
        with open(yaml_path, "r") as f:
            brand_profile = yaml.safe_load(f)

        # Validate required fields
        required_fields = ["company_name", "portfolio", "positioning"]
        missing_fields = [field for field in required_fields if field not in brand_profile]

        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Brand profile missing required fields: {', '.join(missing_fields)}"
            )

        logger.info(f"Loaded brand profile for {brand_id}")
        return brand_profile

    except yaml.YAMLError as e:
        logger.error(f"Malformed YAML for brand {brand_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Malformed brand profile YAML: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error loading brand profile {brand_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading brand profile: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, operation_id="health_check")
async def health_check():
    """Health check endpoint for Railway monitoring

    Returns 'ok' if all required environment variables are present AND
    frontend webhook URL is reachable, 'degraded' otherwise.
    """
    required_vars = [
        "OPENROUTER_API_KEY",
        "OPENROUTER_BASE_URL",
        "LLM_MODEL",
        "VERCEL_BLOB_READ_WRITE_TOKEN"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    # Test frontend connectivity
    frontend_url = os.getenv("FRONTEND_WEBHOOK_URL", "https://innovation-web-rho.vercel.app")
    frontend_reachable = False

    try:
        # Try to ping frontend health endpoint with 5s timeout
        response = requests.get(f"{frontend_url}/api/health", timeout=5)
        frontend_reachable = response.ok
        if not frontend_reachable:
            logger.warning(f"Frontend health check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.warning(f"Frontend not reachable at {frontend_url}: {e}")

    # Status is degraded if env vars missing OR frontend unreachable
    status = "degraded" if (missing_vars or not frontend_reachable) else "ok"

    details = {}
    if missing_vars:
        details["missing_env_vars"] = missing_vars
    if not frontend_reachable:
        details["frontend_status"] = "unreachable"
        details["frontend_url"] = frontend_url

    return HealthResponse(status=status, version="1.0.0", details=details if details else None)


@router.post("/run", response_model=RunPipelineResponse, operation_id="run_pipeline")
async def run_pipeline(request: RunPipelineRequest):
    """
    Start pipeline execution

    Accepts blob URL and brand ID, downloads PDF, and executes
    5-stage pipeline in background.

    If run_id is provided by frontend, use it (prevents race condition).
    Otherwise, generate one here (backward compatibility).
    """
    from app.prisma_client import PrismaAPIClient

    # Validate blob URL
    if not validate_blob_url(request.blob_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid blob URL. Must be HTTPS URL from blob.vercel-storage.com"
        )

    # Use frontend-provided run_id or generate new one
    run_id = request.run_id or generate_run_id()
    logger.info(f"Pipeline run_id: {run_id} {'(frontend-provided)' if request.run_id else '(backend-generated)'}")

    # Download PDF
    pdf_path = download_pdf_from_blob(request.blob_url, run_id)

    # Load brand profile
    brand_profile = load_brand_profile(request.brand_id)

    # Extract document name from blob URL
    try:
        document_name = request.blob_url.split('/')[-1].split('-', 1)[-1] if '/' in request.blob_url else "document.pdf"
    except:
        document_name = "document.pdf"

    # If run_id was backend-generated (not from frontend), initialize PipelineRun record
    if not request.run_id:
        logger.info(f"[{run_id}] Backend-generated run_id - initializing PipelineRun in database")
        prisma_client = PrismaAPIClient()
        brand_name = brand_profile.get("company_name", request.brand_id)

        # Initialize PipelineRun record via API
        init_success = prisma_client.initialize_pipeline_run(
            run_id=run_id,
            blob_url=request.blob_url,
            brand_name=brand_name,
            document_name=document_name
        )

        if not init_success:
            logger.warning(f"[{run_id}] Failed to initialize PipelineRun - continuing anyway")

    # Start background execution
    thread = Thread(
        target=execute_pipeline_background,
        args=(run_id, pdf_path, brand_profile),
        daemon=True
    )
    thread.start()

    logger.info(f"Started pipeline execution for run {run_id}")

    return RunPipelineResponse(run_id=run_id, status="running")


@router.get("/status/{run_id}", response_model=PipelineStatus, operation_id="get_status")
async def get_status(run_id: str):
    """
    Get pipeline execution status

    Returns current status including stage progress and outputs.
    Queries Prisma database for real-time status.
    """
    from app.prisma_client import PrismaAPIClient

    try:
        prisma_client = PrismaAPIClient()

        # Query database for pipeline run status
        run_data = prisma_client.get_run_status(run_id)

        if not run_data:
            raise HTTPException(
                status_code=404,
                detail=f"Run '{run_id}' not found"
            )

        # Transform database format to PipelineStatus model
        # run_data has: {status, stageOutputs: [{stageNumber, status, output}]}
        stages_dict = {}
        current_stage = 0

        for stage_output in run_data.get("stageOutputs", []):
            stage_num = stage_output["stageNumber"]
            stage_status = stage_output["status"]

            # Map database status to API status
            if stage_status == "COMPLETED":
                status_str = "complete"
                current_stage = max(current_stage, stage_num)
            elif stage_status == "PROCESSING":
                status_str = "running"
                current_stage = max(current_stage, stage_num)
            elif stage_status == "FAILED":
                status_str = "failed"
            else:  # PENDING
                status_str = "pending"

            stages_dict[str(stage_num)] = {
                "status": status_str,
                "output": json.loads(stage_output["output"]) if stage_output.get("output") else None
            }

        # Determine overall status
        run_status = run_data.get("status", "PENDING")
        if run_status == "COMPLETED":
            overall_status = "complete"
        elif run_status == "FAILED":
            overall_status = "failed"
        else:
            overall_status = "running"

        return PipelineStatus(
            run_id=run_id,
            status=overall_status,
            current_stage=current_stage,
            stages=stages_dict
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading status for run {run_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading status: {str(e)}"
        )


# ============================================
# MCP Development & Debug Tools
# ============================================

@router.get("/brands", operation_id="list_brands")
async def list_brands():
    """List all available brand profiles for pipeline execution

    Returns list of brand IDs that can be used with run_pipeline.
    """
    # Look in both backend/data and /data (for local dev vs Railway)
    possible_paths = [
        Path(__file__).parent.parent / "data" / "brand-profiles",
        Path("/app/data/brand-profiles")
    ]

    brand_dir = None
    for path in possible_paths:
        if path.exists():
            brand_dir = path
            break

    if not brand_dir:
        return {"brands": [], "count": 0}

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
    """Get detailed brand profile configuration by ID

    Returns the full brand profile YAML data including company_name,
    portfolio, positioning, and other configuration.
    """
    # Reuse existing load_brand_profile() helper
    brand_profile = load_brand_profile(brand_id)

    return {
        "brand_id": brand_id,
        "profile": brand_profile
    }


@router.get("/config/env-check", operation_id="check_environment")
async def check_environment():
    """Check which environment variables are configured

    Verifies presence of required environment variables without
    exposing their values. Useful for deployment validation.
    """
    required_vars = [
        "OPENROUTER_API_KEY",
        "OPENROUTER_BASE_URL",
        "LLM_MODEL",
        "VERCEL_BLOB_READ_WRITE_TOKEN"
    ]

    optional_vars = [
        "WEBHOOK_SECRET",
        "FRONTEND_WEBHOOK_URL"
    ]

    configured = []
    missing = []
    warnings = []

    # Check required vars
    for var in required_vars:
        value = os.getenv(var)
        if value:
            configured.append(var)
        else:
            missing.append(var)

    # Check optional vars
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            configured.append(var)
        else:
            warnings.append(f"{var} not set (optional)")

    return {
        "configured": configured,
        "missing": missing,
        "warnings": warnings,
        "status": "ok" if not missing else "incomplete"
    }


@router.get("/debug/runs", operation_id="list_all_runs")
async def list_all_runs(limit: int = 20):
    """List all pipeline runs with status

    Returns recent pipeline executions for debugging and monitoring.
    Useful for checking pipeline history and finding run IDs.
    """
    runs_dir = Path("/tmp/runs")

    if not runs_dir.exists():
        return {"runs": [], "count": 0}

    runs = []

    # Get all run directories
    for run_dir in runs_dir.iterdir():
        if not run_dir.is_dir():
            continue

        run_id = run_dir.name
        status_file = run_dir / "status.json"

        if status_file.exists():
            try:
                with open(status_file, "r") as f:
                    status_data = json.load(f)

                runs.append({
                    "run_id": run_id,
                    "status": status_data.get("status", "unknown"),
                    "current_stage": status_data.get("current_stage", 0),
                    "brand_id": status_data.get("brand_id", "unknown"),
                    "created_at": status_data.get("created_at", None)
                })
            except Exception as e:
                logger.warning(f"Could not read status for {run_id}: {e}")
                runs.append({
                    "run_id": run_id,
                    "status": "error_reading_status",
                    "error": str(e)
                })

    # Sort by creation time (newest first)
    runs.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # Limit results
    runs = runs[:limit]

    return {
        "runs": runs,
        "count": len(runs),
        "limit": limit
    }


@router.get("/debug/runs/{run_id}/stage/{stage_num}", operation_id="get_stage_output")
async def get_stage_output(run_id: str, stage_num: int):
    """Get raw output from specific pipeline stage

    Returns the complete output JSON from a specific stage,
    useful for debugging stage failures and inspecting intermediate results.
    """
    if stage_num < 1 or stage_num > 5:
        raise HTTPException(
            status_code=400,
            detail="Stage number must be between 1 and 5"
        )

    run_dir = Path("/tmp/runs") / run_id

    if not run_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found"
        )

    # Look for stage output file
    stage_file = run_dir / f"stage{stage_num}_output.json"

    if not stage_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Stage {stage_num} output not found for run '{run_id}'. Stage may not have completed yet."
        )

    try:
        with open(stage_file, "r") as f:
            stage_data = json.load(f)

        return {
            "run_id": run_id,
            "stage": stage_num,
            "output": stage_data
        }

    except json.JSONDecodeError as e:
        logger.error(f"Corrupted stage output for {run_id}/stage{stage_num}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Stage {stage_num} output file corrupted"
        )
    except Exception as e:
        logger.error(f"Error reading stage output {run_id}/stage{stage_num}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading stage output: {str(e)}"
        )
