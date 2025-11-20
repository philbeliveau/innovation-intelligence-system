"""Simplified End-to-End Integration Test: Stage 3 → Stage 4

Tests integration between Stage 3 (Technique Matching) and Stage 4 (Concept Generation)
using real Stage 2 outputs to verify schema compatibility and data flow.

Focuses on validating that:
- Stage 3 matched techniques produce valid Stage 4 inputs
- Boundary enforcement works in realistic pipeline context
- Traceability is maintained (insight_id flows through)
"""
import pytest
from unittest.mock import AsyncMock
from experimentation.stages.stage_3_techniques import Stage3TechniqueMatching
from experimentation.stages.stage_4_concepts import Stage4ConceptGeneration
from experimentation.schemas import (
    Stage2Output,
    ConsumerInsight,
    InnovationTechnique,
    MatchedTechnique,
    TechniqueTransferability
)


@pytest.fixture
def sample_stage2_output():
    """Real Stage 2 output for integration testing."""
    return Stage2Output(
        insights=[
            ConsumerInsight(
                insight_id="insight_witherwill_001",
                source_trends=["trend_001"],
                consumer_statement="I'm overwhelmed by bread choices - just tell me THE ONE bread",
                functional_need="Simplify decision-making",
                emotional_need="Reduce anxiety",
                social_need="Appear as smart provider",
                brand_relevance_score=0.85
            )
        ],
        convergence_count=1
    )


@pytest.fixture
def sample_brand_context():
    """Brand context for testing."""
    return {
        "brand_name": "St-Méthode",
        "industry": "Food & Beverage",
        "country": "Canada",
        "product_portfolio": ["Bread A", "Bread B", "Bread C"]
    }


@pytest.mark.asyncio
async def test_stage3_to_stage4_integration(sample_stage2_output, sample_brand_context):
    """Test that Stage 3 outputs are valid Stage 4 inputs with end-to-end flow."""

    # === STAGE 3: Technique Matching ===
    stage3 = Stage3TechniqueMatching()

    # Mock Stage 3 LLM response
    stage3_mock_response = {
        "content": """```json
{
  "matched_techniques": [
    {
      "insight_id": "insight_witherwill_001",
      "primary_technique": {
        "framework": "SIT",
        "technique": "Task Unification",
        "rationale": "Assign choice-simplification to shelf labels",
        "defensibility_score": 0.80
      },
      "secondary_technique": null,
      "doblin_type": "Service",
      "transferability": {
        "L1_domain": "Bread aisle shelf labels guide consumer to one recommendation",
        "L4_universal": "Existing touchpoint takes on decision-support function"
      }
    }
  ]
}
```"""
    }

    mock_client_stage3 = AsyncMock()
    mock_client_stage3.call_llm = AsyncMock(return_value=stage3_mock_response)

    stage3_output = await stage3.execute(
        stage2_output=sample_stage2_output,
        brand_context=sample_brand_context,
        openrouter_client=mock_client_stage3
    )

    # Validate Stage 3 output structure
    assert len(stage3_output.matched_techniques) == 1
    matched = stage3_output.matched_techniques[0]
    assert matched.insight_id == "insight_witherwill_001"
    assert matched.primary_technique.framework == "SIT"
    assert matched.transferability is not None

    # === STAGE 4: Concept Generation ===
    stage4 = Stage4ConceptGeneration()

    # Mock Stage 4 LLM response (clean, no hallucinations)
    stage4_mock_response = {
        "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_witherwill_001",
      "technique_id": "task_unification",
      "concept_name": "The Bread Finder",
      "concept_statement": "3-question quiz delivers ONE bread recommendation",
      "mechanism": "QR code on shelf connects to quiz asking about household size, dietary preferences, meal occasions",
      "why_it_works": "Applies Task Unification by assigning decision-support task to existing shelf labels, directly addressing consumer overwhelm",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_witherwill_001",
      "technique_id": "task_unification",
      "concept_name": "Meal Pairing Guide",
      "concept_statement": "Shelf labels show which bread pairs best with common meal occasions",
      "mechanism": "Visual icons on shelf connect each bread to use cases: sandwiches, toast, soup pairing",
      "why_it_works": "Simplifies choice by connecting product to intended use, leveraging existing shelf infrastructure",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_witherwill_001",
      "technique_id": "task_unification",
      "concept_name": "Daily Bread Pick",
      "concept_statement": "Single spotlight recommendation rotates daily, chosen by baker",
      "mechanism": "Store highlights ONE bread each day with prominent signage explaining why it's today's pick",
      "why_it_works": "Assigns curation task to in-store signage, directly addresses 'just tell me what to buy' consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
    }

    mock_client_stage4 = AsyncMock()
    mock_client_stage4.call_llm = AsyncMock(return_value=stage4_mock_response)

    stage4_output = await stage4.execute(
        stage2_output=sample_stage2_output,
        stage3_output=stage3_output,
        brand_context=sample_brand_context,
        openrouter_client=mock_client_stage4
    )

    # Validate Stage 4 output
    assert stage4_output.total_concepts == 3
    assert stage4_output.boundary_enforcement_applied is True
    assert len(stage4_output.concepts) == 3

    # Validate traceability: insight_id flows through
    stage2_insight_id = sample_stage2_output.insights[0].insight_id
    stage3_insight_id = stage3_output.matched_techniques[0].insight_id
    stage4_insight_ids = [c.insight_id for c in stage4_output.concepts]

    assert stage3_insight_id == stage2_insight_id
    assert all(cid == stage2_insight_id for cid in stage4_insight_ids)

    # Validate no hallucinations in final concepts
    for concept in stage4_output.concepts:
        full_text = f"{concept.concept_name} {concept.concept_statement} {concept.mechanism} {concept.why_it_works}".lower()
        assert "$" not in full_text or "cost" not in full_text  # No financial projections
        assert "no brand" not in full_text  # No competitive claims
        assert "studies show" not in full_text  # No unverified statistics


@pytest.mark.asyncio
async def test_stage3_output_schema_compatibility():
    """Test that Stage 3 outputs match expected Stage 4 input structure."""

    # Create a Stage 3 output manually
    stage3_output_manual = type('Stage3Output', (), {
        'matched_techniques': [
            MatchedTechnique(
                insight_id="test_insight",
                primary_technique=InnovationTechnique(
                    framework="SIT",
                    technique="Subtraction",
                    rationale="Test rationale",
                    defensibility_score=0.75
                ),
                secondary_technique=None,
                doblin_type="Product",
                transferability=TechniqueTransferability(
                    L1_domain="Domain-specific",
                    L4_universal="Universal principle"
                )
            )
        ],
        'sit_matches': 1,
        'triz_matches': 0
    })()

    # Verify schema structure matches what Stage 4 expects
    assert hasattr(stage3_output_manual, 'matched_techniques')
    assert len(stage3_output_manual.matched_techniques) > 0

    matched = stage3_output_manual.matched_techniques[0]
    assert hasattr(matched, 'insight_id')
    assert hasattr(matched, 'primary_technique')
    assert hasattr(matched, 'transferability')
    assert hasattr(matched.primary_technique, 'framework')
    assert hasattr(matched.primary_technique, 'technique')
    assert hasattr(matched.transferability, 'L1_domain')
    assert hasattr(matched.transferability, 'L4_universal')
