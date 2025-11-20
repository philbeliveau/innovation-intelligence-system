"""Dedicated Tests for No-Hallucination Boundary Enforcement

Comprehensive testing of Stage 4 boundary enforcement against:
- Financial projections (TAM, revenue, market share, ROI)
- Unverified competitive claims
- Invented market statistics
- Business plan hallucinations

These tests use adversarial prompts designed to elicit hallucinations.
"""
import pytest
from unittest.mock import AsyncMock
from backend.experimentation.stages.stage_4_concepts import Stage4ConceptGeneration
from backend.experimentation.schemas import (
    Stage2Output,
    Stage3Output,
    ConsumerInsight,
    MatchedTechnique,
    InnovationTechnique,
    TechniqueTransferability
)


@pytest.fixture
def stage4_instance():
    """Create Stage4ConceptGeneration instance."""
    return Stage4ConceptGeneration()


@pytest.fixture
def base_inputs():
    """Base inputs for Stage 4 execution."""
    return {
        "stage2_output": Stage2Output(
            insights=[
                ConsumerInsight(
                    insight_id="insight_001",
                    source_trends=["trend_001"],
                    consumer_statement="I want X",
                    functional_need="Need X",
                    emotional_need="Feel X",
                    social_need="Signal X",
                    brand_relevance_score=0.80
                )
            ],
            convergence_count=1
        ),
        "stage3_output": Stage3Output(
            matched_techniques=[
                MatchedTechnique(
                    insight_id="insight_001",
                    primary_technique=InnovationTechnique(
                        framework="SIT",
                        technique="Task Unification",
                        rationale="Applies technique X",
                        defensibility_score=0.70
                    ),
                    secondary_technique=None,
                    doblin_type="Service",
                    transferability=TechniqueTransferability(
                        L1_domain="Domain application",
                        L4_universal="Universal principle"
                    )
                )
            ],
            sit_matches=1,
            triz_matches=0
        ),
        "brand_context": {
            "brand_name": "Test Brand",
            "industry": "Test Industry",
            "country": "USA",
            "product_portfolio": ["Product A", "Product B"]
        }
    }


class TestFinancialHallucinations:
    """Test detection of financial projections and estimates."""

    @pytest.mark.asyncio
    async def test_tam_hallucination_blocked(self, stage4_instance, base_inputs):
        """Test TAM (Total Addressable Market) mentions are blocked."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Big Market Concept",
      "concept_statement": "This addresses a TAM of $500M",
      "mechanism": "Some mechanism",
      "why_it_works": "Total addressable market is huge",
      "boundary_disclosure": "Standard disclosure"
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without financial hallucinations",
      "mechanism": "Uses existing shelf space for new choice-support function",
      "why_it_works": "Addresses consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 2",
      "concept_statement": "Another clean concept",
      "mechanism": "Applies Task Unification to simplify consumer choice",
      "why_it_works": "Leverages brand context to address specific consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="boundary violation"):
            await stage4_instance.execute(
                openrouter_client=mock_client,
                **base_inputs
            )

    @pytest.mark.asyncio
    async def test_revenue_projection_blocked(self, stage4_instance, base_inputs):
        """Test revenue projections are blocked."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Revenue Concept",
      "concept_statement": "This could generate $10M in revenue",
      "mechanism": "Revenue of $5M in year 1",
      "why_it_works": "Projected revenue is $20M by year 3",
      "boundary_disclosure": "Standard disclosure"
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without financial hallucinations",
      "mechanism": "Uses existing shelf space for new choice-support function",
      "why_it_works": "Addresses consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 2",
      "concept_statement": "Another clean concept",
      "mechanism": "Applies Task Unification to simplify consumer choice",
      "why_it_works": "Leverages brand context to address specific consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="boundary violation"):
            await stage4_instance.execute(
                openrouter_client=mock_client,
                **base_inputs
            )

    @pytest.mark.asyncio
    async def test_market_share_projection_blocked(self, stage4_instance, base_inputs):
        """Test market share projections are blocked."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Market Share Concept",
      "concept_statement": "Capture 15% market share",
      "mechanism": "Gain 20% of market share within 2 years",
      "why_it_works": "Market share opportunity is significant",
      "boundary_disclosure": "Standard disclosure"
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without financial hallucinations",
      "mechanism": "Uses existing shelf space for new choice-support function",
      "why_it_works": "Addresses consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 2",
      "concept_statement": "Another clean concept",
      "mechanism": "Applies Task Unification to simplify consumer choice",
      "why_it_works": "Leverages brand context to address specific consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="boundary violation.*market share"):
            await stage4_instance.execute(
                openrouter_client=mock_client,
                **base_inputs
            )

    @pytest.mark.asyncio
    async def test_roi_projection_blocked(self, stage4_instance, base_inputs):
        """Test ROI (Return on Investment) projections are blocked."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "High ROI Concept",
      "concept_statement": "Delivers 300% ROI",
      "mechanism": "Return on investment in 18 months",
      "why_it_works": "Strong ROI expected",
      "boundary_disclosure": "Standard disclosure"
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without financial hallucinations",
      "mechanism": "Uses existing shelf space for new choice-support function",
      "why_it_works": "Addresses consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 2",
      "concept_statement": "Another clean concept",
      "mechanism": "Applies Task Unification to simplify consumer choice",
      "why_it_works": "Leverages brand context to address specific consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="boundary violation.*ROI"):
            await stage4_instance.execute(
                openrouter_client=mock_client,
                **base_inputs
            )

    @pytest.mark.asyncio
    async def test_cost_estimate_blocked(self, stage4_instance, base_inputs):
        """Test cost estimates are blocked."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Low Cost Concept",
      "concept_statement": "Implementation cost is only $50K",
      "mechanism": "Total cost of $100K",
      "why_it_works": "Cost-effective at $75K",
      "boundary_disclosure": "Standard disclosure"
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without financial hallucinations",
      "mechanism": "Uses existing shelf space for new choice-support function",
      "why_it_works": "Addresses consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 2",
      "concept_statement": "Another clean concept",
      "mechanism": "Applies Task Unification to simplify consumer choice",
      "why_it_works": "Leverages brand context to address specific consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="boundary violation"):
            await stage4_instance.execute(
                openrouter_client=mock_client,
                **base_inputs
            )


class TestCompetitiveHallucinations:
    """Test detection of unverified competitive claims."""

    @pytest.mark.asyncio
    async def test_no_brand_does_this_blocked(self, stage4_instance, base_inputs):
        """Test 'no brand does this' claims are blocked."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Novel Concept",
      "concept_statement": "No brand has done this before",
      "mechanism": "No competitor does anything similar",
      "why_it_works": "No company has thought of this",
      "boundary_disclosure": "Standard disclosure"
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without competitive claims",
      "mechanism": "Uses existing shelf space for new choice-support function",
      "why_it_works": "Addresses consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 2",
      "concept_statement": "Another clean concept",
      "mechanism": "Applies Task Unification to simplify consumer choice",
      "why_it_works": "Leverages brand context to address specific consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="boundary violation.*no.*brand"):
            await stage4_instance.execute(
                openrouter_client=mock_client,
                **base_inputs
            )

    @pytest.mark.asyncio
    async def test_first_to_market_blocked(self, stage4_instance, base_inputs):
        """Test 'first to market' claims are blocked."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "First Mover Concept",
      "concept_statement": "We'll be first to market with this",
      "mechanism": "First-to-market advantage",
      "why_it_works": "Being first to market is key",
      "boundary_disclosure": "Standard disclosure"
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without competitive claims",
      "mechanism": "Uses existing shelf space for new choice-support function",
      "why_it_works": "Addresses consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 2",
      "concept_statement": "Another clean concept",
      "mechanism": "Applies Task Unification to simplify consumer choice",
      "why_it_works": "Leverages brand context to address specific consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="boundary violation.*first to market"):
            await stage4_instance.execute(
                openrouter_client=mock_client,
                **base_inputs
            )

    @pytest.mark.asyncio
    async def test_only_brand_that_blocked(self, stage4_instance, base_inputs):
        """Test 'only brand that' claims are blocked."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Unique Concept",
      "concept_statement": "Only brand that can do this",
      "mechanism": "We're the only company with this capability",
      "why_it_works": "Only brand with this asset",
      "boundary_disclosure": "Standard disclosure"
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without competitive claims",
      "mechanism": "Uses existing shelf space for new choice-support function",
      "why_it_works": "Addresses consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 2",
      "concept_statement": "Another clean concept",
      "mechanism": "Applies Task Unification to simplify consumer choice",
      "why_it_works": "Leverages brand context to address specific consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="boundary violation.*only.*brand"):
            await stage4_instance.execute(
                openrouter_client=mock_client,
                **base_inputs
            )


class TestStatisticalHallucinations:
    """Test detection of invented market statistics."""

    @pytest.mark.asyncio
    async def test_studies_show_blocked(self, stage4_instance, base_inputs):
        """Test 'studies show' claims are blocked."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Research-Backed Concept",
      "concept_statement": "Studies show consumers want this",
      "mechanism": "Research shows high demand",
      "why_it_works": "Studies indicate strong adoption",
      "boundary_disclosure": "Standard disclosure"
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without statistical claims",
      "mechanism": "Uses existing shelf space for new choice-support function",
      "why_it_works": "Addresses consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 2",
      "concept_statement": "Another clean concept",
      "mechanism": "Applies Task Unification to simplify consumer choice",
      "why_it_works": "Leverages brand context to address specific consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="boundary violation.*studies show"):
            await stage4_instance.execute(
                openrouter_client=mock_client,
                **base_inputs
            )

    @pytest.mark.asyncio
    async def test_percentage_of_consumers_blocked(self, stage4_instance, base_inputs):
        """Test unverified consumer percentage claims are blocked."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Popular Concept",
      "concept_statement": "75% of consumers prefer this",
      "mechanism": "85% of shoppers want this feature",
      "why_it_works": "90% of customers would adopt this",
      "boundary_disclosure": "Standard disclosure"
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without statistical claims",
      "mechanism": "Uses existing shelf space for new choice-support function",
      "why_it_works": "Addresses consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 2",
      "concept_statement": "Another clean concept",
      "mechanism": "Applies Task Unification to simplify consumer choice",
      "why_it_works": "Leverages brand context to address specific consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="boundary violation.*% of consumers"):
            await stage4_instance.execute(
                openrouter_client=mock_client,
                **base_inputs
            )

    @pytest.mark.asyncio
    async def test_research_indicates_blocked(self, stage4_instance, base_inputs):
        """Test 'research indicates' claims are blocked."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Data-Driven Concept",
      "concept_statement": "Research indicates high adoption",
      "mechanism": "Research shows strong demand",
      "why_it_works": "Research indicates market fit",
      "boundary_disclosure": "Standard disclosure"
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without statistical claims",
      "mechanism": "Uses existing shelf space for new choice-support function",
      "why_it_works": "Addresses consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 2",
      "concept_statement": "Another clean concept",
      "mechanism": "Applies Task Unification to simplify consumer choice",
      "why_it_works": "Leverages brand context to address specific consumer need",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="boundary violation.*research indicates"):
            await stage4_instance.execute(
                openrouter_client=mock_client,
                **base_inputs
            )


class TestValidConceptsPass:
    """Test that valid concepts without hallucinations pass validation."""

    @pytest.mark.asyncio
    async def test_clean_concepts_pass_validation(self, stage4_instance, base_inputs):
        """Test concepts without hallucinations pass all validation."""
        valid_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "The Bread Finder Tool",
      "concept_statement": "A 3-question quiz that recommends ONE bread for your family",
      "mechanism": "QR code on shelf connects to quiz, provides personalized recommendation and store location",
      "why_it_works": "Applies Task Unification by assigning choice-simplification task to existing shelf labels, directly addressing consumer decision fatigue identified in trend analysis",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Meal Pairing Guide",
      "concept_statement": "Shelf labels show which bread pairs best with common meals",
      "mechanism": "Visual icons on shelf connect bread to use cases like sandwiches, toast, or soup",
      "why_it_works": "Simplifies choice by connecting product to consumer's intended use, leveraging existing shelf infrastructure for new decision-support function",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "The Daily Bread Pick",
      "concept_statement": "Single spotlight recommendation rotates daily based on seasonal ingredients",
      "mechanism": "Store highlights ONE bread each day with signage explaining context",
      "why_it_works": "Curates choice down to one recommendation, directly addressing overwhelm identified in consumer insights, using existing signage for new task",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=valid_response)

        # Should not raise any errors
        result = await stage4_instance.execute(
            openrouter_client=mock_client,
            **base_inputs
        )

        assert result.boundary_enforcement_applied is True
        assert result.total_concepts == 3
