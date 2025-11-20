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
# STAGE 3: Innovation Technique Matching
# ============================================================

class TechniqueTransferability(BaseModel):
    """Transferability mapping from L1 to L4."""
    L1_domain: str = Field(description="Domain-specific application")
    L4_universal: str = Field(description="Universal principle")


class InnovationTechnique(BaseModel):
    """Primary or secondary innovation technique."""
    framework: str = Field(description="SIT, TRIZ, or Doblin")
    technique: str = Field(description="Technique name")
    rationale: str = Field(description="Why this technique applies")
    defensibility_score: Optional[float] = Field(ge=0.0, le=1.0, default=None)


class MatchedTechnique(BaseModel):
    """Technique match for a consumer insight."""
    insight_id: str = Field(description="Reference to ConsumerInsight.insight_id")
    primary_technique: InnovationTechnique
    secondary_technique: Optional[InnovationTechnique] = None
    doblin_type: str = Field(description="Doblin innovation type for strategic classification")
    transferability: TechniqueTransferability


class Stage3Output(BaseModel):
    """Output from Stage 3: Technique Matching."""
    matched_techniques: List[MatchedTechnique]
    sit_matches: int = Field(description="Number of SIT matches")
    triz_matches: int = Field(description="Number of TRIZ matches (conditional)")


# ============================================================
# STAGE 4: Directional Concept Generation
# ============================================================

class DirectionalConcept(BaseModel):
    """Directional concept from Stage 4 (NOT detailed specs)."""
    concept_id: str
    insight_id: str = Field(description="Reference to ConsumerInsight.insight_id")
    technique_id: str = Field(description="Reference to matched technique")
    concept_name: str = Field(description="Clear, memorable name")
    concept_statement: str = Field(description="1-sentence what-is-it")
    mechanism: str = Field(description="How it works (mechanism only, not implementation)")
    why_it_works: str = Field(description="Why it addresses the insight")
    boundary_disclosure: str = Field(
        description="Explicit statement of what is NOT included (no financials, no validation)"
    )


class Stage4Output(BaseModel):
    """Output from Stage 4: Directional Concepts."""
    concepts: List[DirectionalConcept]
    total_concepts: int = Field(description="Should be 3-5 concepts")
    boundary_enforcement_applied: bool = Field(
        description="Confirms no-hallucination boundaries were enforced"
    )


# ============================================================
# STAGE 5: Competitive Intelligence
# ============================================================

class CompetitiveFinding(BaseModel):
    """Single competitive intelligence finding from Stage 5."""
    match_type: str = Field(description="Direct Match, Analogous, or Novel")
    query: str = Field(description="Search query that generated this finding")
    description: str = Field(description="Search result content")
    source_urls: List[str] = Field(description="Citation URLs from search")
    what_we_know: str = Field(description="Factual information with sources")
    what_we_infer: str = Field(description="Interpretive or comparative statements")


class CompetitiveIntelligence(BaseModel):
    """Competitive intelligence for a single concept."""
    concept_id: str = Field(description="Reference to DirectionalConcept.concept_id")
    search_queries: List[str] = Field(description="3 search queries: Direct, Analogous, Competitive")
    findings: List[CompetitiveFinding]
    novelty_assessment: str = Field(description="Overall novelty assessment")


class Stage5Output(BaseModel):
    """Output from Stage 5: Competitive Intelligence."""
    competitive_intel: List[CompetitiveIntelligence]
    search_enabled: bool = Field(description="Whether Perplexity search was enabled")
    total_queries_executed: int


# ============================================================
# STAGE 6: Opportunity Card Packaging
# ============================================================

class OpportunityCard(BaseModel):
    """Final opportunity card in markdown format from Stage 6."""
    card_id: str
    concept_id: str = Field(description="Reference to DirectionalConcept.concept_id")
    markdown_content: str = Field(description="Full markdown-formatted opportunity card")
    card_sections: Dict[str, str] = Field(
        description="Parsed sections: concept_name, consumer_insight, mechanism, why_now, why_brand, competitive_landscape, boundary_disclosure"
    )


class Stage6Output(BaseModel):
    """Output from Stage 6: Opportunity Cards."""
    opportunity_cards: List[OpportunityCard]
    total_cards: int
    markdown_format_validated: bool = Field(description="Confirms markdown structure is valid")


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
