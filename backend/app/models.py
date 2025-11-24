"""Pydantic Models for Request/Response Schemas"""
from typing import Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field


class RunPipelineRequest(BaseModel):
    """Request model for POST /run endpoint"""
    blob_url: str = Field(..., description="Vercel Blob URL of uploaded PDF")
    brand_id: str = Field(..., description="Brand identifier (e.g., 'lactalis-canada')")
    run_id: Optional[str] = Field(None, description="Pre-generated run ID from frontend (prevents race condition)")


class RunPipelineLocalRequest(BaseModel):
    """Request model for POST /run/local endpoint (for HuggingFace Spaces and local dev)"""
    pdf_text: str = Field(..., description="Raw PDF text content")
    brand_profile: Dict[str, Any] = Field(..., description="Brand profile configuration object")
    run_id: Optional[str] = Field(None, description="Pre-generated run ID from frontend")
    custom_prompts: Optional[Dict[str, str]] = Field(None, description="Optional custom prompt templates (stage_0 through stage_6)")


class RunPipelineResponse(BaseModel):
    """Response model for POST /run endpoint"""
    run_id: str
    status: Literal["running"]


class StageInfo(BaseModel):
    """Information about a single pipeline stage"""
    status: Literal["pending", "running", "complete", "failed"]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    output: Optional[Union[Dict[str, Any], str]] = None  # Accept both dict and markdown string


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
    details: Optional[Dict[str, Any]] = Field(None, description="Additional health check details (missing env vars, connectivity issues)")


class SaveExperimentRequest(BaseModel):
    """Request model for POST /experiments/save endpoint"""
    run_id: str = Field(..., description="Unique run identifier")
    timestamp: str = Field(..., description="ISO 8601 timestamp of experiment")
    report_text: str = Field(..., description="Original PDF report text")
    brand_profile: Dict[str, Any] = Field(..., description="Brand profile configuration")
    stage_outputs: Dict[str, Any] = Field(..., description="All stage outputs from pipeline")
    quality_tag: Literal["good", "needs work", "failed"] = Field(..., description="Quality assessment tag")
    notes: Optional[str] = Field(None, description="User notes about the experiment")


class SaveExperimentResponse(BaseModel):
    """Response model for POST /experiments/save endpoint"""
    success: bool
    message: str
    experiment_id: Optional[str] = None


class RenameExperimentRequest(BaseModel):
    """Request model for PUT /experiments/{id}/rename endpoint"""
    new_name: str = Field(..., description="New name for the experiment", min_length=1, max_length=200)


class RenameExperimentResponse(BaseModel):
    """Response model for PUT /experiments/{id}/rename endpoint"""
    success: bool
    message: str
    experiment_id: str


class DeleteExperimentResponse(BaseModel):
    """Response model for DELETE /experiments/{id} endpoint"""
    success: bool
    message: str
    experiment_id: str
