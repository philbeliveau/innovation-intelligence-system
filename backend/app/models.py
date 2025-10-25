"""Pydantic Models for Request/Response Schemas"""
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class RunPipelineRequest(BaseModel):
    """Request model for POST /run endpoint"""
    blob_url: str = Field(..., description="Vercel Blob URL of uploaded PDF")
    brand_id: str = Field(..., description="Brand identifier (e.g., 'lactalis-canada')")
    run_id: Optional[str] = Field(None, description="Pre-generated run ID from frontend (prevents race condition)")


class RunPipelineResponse(BaseModel):
    """Response model for POST /run endpoint"""
    run_id: str
    status: Literal["running"]


class StageInfo(BaseModel):
    """Information about a single pipeline stage"""
    status: Literal["pending", "running", "complete", "failed"]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    output: Optional[Dict[str, Any]] = None


class PipelineStatus(BaseModel):
    """Pipeline execution status - matches 6-api-design.md schema"""
    run_id: str
    status: Literal["running", "complete", "failed"]
    current_stage: int
    stages: Dict[str, StageInfo]  # Object keyed by stage number ("1", "2", etc.)
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: Literal["ok", "degraded"]
    version: str = "1.0.0"
