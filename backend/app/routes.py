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


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Railway monitoring

    Returns 'ok' if all required environment variables are present,
    'degraded' if any are missing.
    """
    required_vars = [
        "OPENROUTER_API_KEY",
        "OPENROUTER_BASE_URL",
        "LLM_MODEL",
        "VERCEL_BLOB_READ_WRITE_TOKEN"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    status = "degraded" if missing_vars else "ok"

    return HealthResponse(status=status, version="1.0.0")


@router.post("/run", response_model=RunPipelineResponse)
async def run_pipeline(request: RunPipelineRequest):
    """
    Start pipeline execution

    Accepts blob URL and brand ID, downloads PDF, and executes
    5-stage pipeline in background.
    """
    # Validate blob URL
    if not validate_blob_url(request.blob_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid blob URL. Must be HTTPS URL from blob.vercel-storage.com"
        )

    # Generate run ID
    run_id = generate_run_id()

    # Download PDF
    pdf_path = download_pdf_from_blob(request.blob_url, run_id)

    # Load brand profile
    brand_profile = load_brand_profile(request.brand_id)

    # Start background execution
    thread = Thread(
        target=execute_pipeline_background,
        args=(run_id, pdf_path, brand_profile),
        daemon=True
    )
    thread.start()

    logger.info(f"Started pipeline execution for run {run_id}")

    return RunPipelineResponse(run_id=run_id, status="running")


@router.get("/status/{run_id}", response_model=PipelineStatus)
async def get_status(run_id: str):
    """
    Get pipeline execution status

    Returns current status including stage progress and outputs.
    """
    status_file = Path("/tmp/runs") / run_id / "status.json"

    if not status_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found"
        )

    try:
        with open(status_file, "r") as f:
            status_data = json.load(f)

        return PipelineStatus(**status_data)

    except json.JSONDecodeError as e:
        logger.error(f"Corrupted status file for run {run_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Status file corrupted"
        )
    except Exception as e:
        logger.error(f"Error reading status for run {run_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading status: {str(e)}"
        )
