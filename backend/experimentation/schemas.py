"""Pydantic Schemas for 7-Stage Pipeline Outputs

Defines the data models for each stage output to ensure type safety
and validation across the pipeline.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================
# STAGE 0: Brand Enrichment
# ============================================================

class BrandEnrichment(BaseModel):
    """Brand enrichment data from Stage 0."""
    brand_name: str
    industry: str
    country: str
    product_portfolio: List[str]
    positioning: Optional[str] = None
    recent_news: Optional[List[str]] = None
    competitive_landscape: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0, default=1.0)


class Stage0Output(BaseModel):
    """Output from Stage 0: Brand Enrichment."""
    brand_context: BrandEnrichment
    enrichment_method: str = Field(description="'basic' or 'perplexity_enriched'")


# ============================================================
# STAGE 1: Trend Decomposition with L1-L4 Abstraction
# ============================================================

class AbstractionLadder(BaseModel):
    """Multi-level abstraction from L1 (domain-specific) to L4 (universal)."""
    L1_domain_specific: str = Field(description="CPG/industry-specific application")
    L2_category: str = Field(description="Category-level pattern")
    L3_cross_category: str = Field(description="Transferable mechanism")
    L4_universal: str = Field(description="Fundamental dynamic")


class EmotionalDrivers(BaseModel):
    """Emotional drivers for a trend."""
    current_negative: List[str] = Field(description="What consumers feel now (negative)")
    aspirational_positive: List[str] = Field(description="What consumers want to feel (positive)")


class TrendTimeline(BaseModel):
    """Timeline for trend lifecycle."""
    emergence_year: Optional[int] = None
    peak_year: Optional[int] = None


class Trend(BaseModel):
    """Structured trend object from Stage 1."""
    trend_id: str
    name: str
    lifecycle_stage: str = Field(description="EMERGING, ACCELERATING, PEAKING, or DECLINING")
    timeline: Optional[TrendTimeline] = None
    evidence: List[str] = Field(description="Market signals, stats, examples")
    weak_signals: List[str] = Field(description="Early indicators")
    emotional_drivers: EmotionalDrivers
    abstraction_ladder: AbstractionLadder


class Stage1Output(BaseModel):
    """Output from Stage 1: Trend Decomposition."""
    trends: List[Trend]
    total_trends_extracted: int


# ============================================================
# STAGE 2: Consumer Insights Synthesis
# ============================================================

class ConsumerInsight(BaseModel):
    """Brand-specific consumer insight from Stage 2."""
    insight_id: str
    source_trends: List[str] = Field(description="Trend IDs that generated this insight")
    consumer_statement: str = Field(description="First-person consumer need statement")
    functional_need: str = Field(description="Practical problem to solve")
    emotional_need: str = Field(description="Feeling to achieve")
    social_need: str = Field(description="Identity/belonging to signal")
    brand_relevance_score: float = Field(ge=0.0, le=1.0, description="Brand permission to play")


class Stage2Output(BaseModel):
    """Output from Stage 2: Consumer Insights."""
    insights: List[ConsumerInsight]
    convergence_count: int = Field(description="Number of multi-trend convergences analyzed")


# ============================================================
# PIPELINE RUN STATE
# ============================================================

class PipelineStageState(BaseModel):
    """State of a single pipeline stage."""
    stage_number: int
    stage_name: str
    status: str = Field(description="PENDING, PROCESSING, COMPLETE, or FAILED")
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PipelineRunState(BaseModel):
    """Complete pipeline run state."""
    run_id: str
    status: str = Field(description="RUNNING, COMPLETED, or FAILED")
    current_stage: int = Field(description="Current stage being processed (1-7)")
    stages: Dict[str, PipelineStageState]
    created_at: str
    completed_at: Optional[str] = None
    total_duration_ms: Optional[int] = None
