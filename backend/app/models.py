"""Pydantic Models for Request/Response Schemas"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class RunPipelineRequest(BaseModel):
    """Request model for POST /run endpoint"""
    blob_url: str = Field(..., description="Vercel Blob URL of uploaded PDF")
    brand: str = Field(..., description="Brand identifier (e.g., 'lactalis-canada')")
    run_id: str = Field(..., description="Unique run identifier (UUID)")


class RunPipelineResponse(BaseModel):
    """Response model for POST /run endpoint"""
    status: Literal["started", "error"]
    run_id: str
    message: Optional[str] = None


class PipelineStatus(BaseModel):
    """Pipeline execution status"""
    run_id: str
    status: Literal["running", "completed", "error"]
    current_stage: Optional[int] = Field(None, description="Current stage (1-5)")
    progress: Optional[float] = Field(None, description="Progress percentage (0-100)")
    error_message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: Literal["ok", "degraded"]
    version: str = "1.0.0"
