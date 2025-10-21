"""API Route Handlers

Minimal implementation for MVP - placeholder endpoints.
Full implementation in Story 5.4.
"""
from fastapi import APIRouter, HTTPException
from app.models import (
    RunPipelineRequest,
    RunPipelineResponse,
    PipelineStatus,
    HealthResponse
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Railway monitoring"""
    return HealthResponse(status="ok", version="1.0.0")


@router.post("/run", response_model=RunPipelineResponse, status_code=501)
async def run_pipeline(request: RunPipelineRequest):
    """
    Start pipeline execution (PLACEHOLDER - Story 5.4)

    Currently returns 501 Not Implemented.
    Full implementation will:
    1. Download PDF from Vercel Blob
    2. Load brand profile from /backend/data/brand-profiles/
    3. Execute 5-stage pipeline
    4. Write outputs to /backend/tmp/runs/{run_id}/
    """
    raise HTTPException(
        status_code=501,
        detail="Pipeline execution not yet implemented. See Story 5.4."
    )


@router.get("/status/{run_id}", response_model=PipelineStatus, status_code=501)
async def get_status(run_id: str):
    """
    Get pipeline execution status (PLACEHOLDER - Story 5.4)

    Currently returns 501 Not Implemented.
    Full implementation will read status from /backend/tmp/runs/{run_id}/status.json
    """
    raise HTTPException(
        status_code=501,
        detail="Status polling not yet implemented. See Story 5.4."
    )
