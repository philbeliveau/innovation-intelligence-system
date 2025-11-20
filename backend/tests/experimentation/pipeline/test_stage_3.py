"""Tests for Stage 3: Innovation Technique Matching

Test Coverage:
- Technique library loading and structure validation
- SIT technique matching accuracy
- Defensibility scoring algorithm
- TRIZ conditional application
- Doblin type classification
- Integration with Stage 2 outputs
"""
import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from backend.experimentation.stages.stage_3_techniques import Stage3TechniqueMatching
from backend.experimentation.schemas import (
    Stage2Output,
    ConsumerInsight,
    Stage3Output,
    MatchedTechnique,
    InnovationTechnique
)


@pytest.fixture
def stage3_instance():
    """Create Stage3TechniqueMatching instance."""
    return Stage3TechniqueMatching()


@pytest.fixture
def sample_stage2_output():
    """Sample Stage 2 output with consumer insights."""
    return Stage2Output(
        insights=[
            ConsumerInsight(
                insight_id="insight_001",
                source_trends=["witherwill"],
                consumer_statement="I'm overwhelmed by bread choices - just tell me THE ONE bread for my family",
                functional_need="Simplify decision-making at point of purchase",
                emotional_need="Reduce cognitive load and decision fatigue",
                social_need="Feel confident I'm making the 'right' choice for my family",
                brand_relevance_score=0.85
            )
        ],
        convergence_count=1
    )


@pytest.fixture
def sample_brand_context():
    """Sample brand context."""
    return {
        "brand_name": "St-Méthode",
        "industry": "Bakery",
        "country": "Canada",
        "product_portfolio": ["Artisan bread", "Whole wheat bread", "Gluten-free bread"],
        "positioning": "Quality bakery for health-conscious families"
    }


@pytest.fixture
def mock_llm_response_stage3():
    """Mock LLM response for Stage 3."""
    return {
        "content": """```json
{
  "matched_techniques": [
    {
      "insight_id": "insight_001",
      "primary_technique": {
        "framework": "SIT",
        "technique": "Task Unification",
        "rationale": "Existing shelf labels can be assigned a NEW task: choice simplification",
        "defensibility_score": 0.65
      },
      "secondary_technique": null,
      "doblin_type": "Service",
      "transferability": {
        "L1_domain": "Bakery shelf labels become decision-support tools",
        "L4_universal": "Environmental cues can be repurposed to simplify complex choices"
      }
    }
  ]
}
```"""
    }


class TestTechniqueLibraryLoading:
    """Test technique library loading and validation."""

    def test_load_sit_library(self, stage3_instance):
        """Test SIT library loads correctly."""
        sit_lib = stage3_instance.technique_libraries["SIT TECHNIQUES"]
        assert "techniques" in sit_lib
        assert len(sit_lib["techniques"]) == 5

        # Validate structure of first technique
        first_technique = sit_lib["techniques"][0]
        assert "id" in first_technique
        assert "name" in first_technique
        assert "description" in first_technique
        assert "examples" in first_technique

    def test_load_triz_library(self, stage3_instance):
        """Test TRIZ library loads correctly."""
        triz_lib = stage3_instance.technique_libraries["TRIZ PRINCIPLES"]
        assert "principles" in triz_lib
        assert len(triz_lib["principles"]) == 40

        # Validate usage note exists
        assert "usage_note" in triz_lib

    def test_load_doblin_library(self, stage3_instance):
        """Test Doblin library loads correctly."""
        doblin_lib = stage3_instance.technique_libraries["DOBLIN TYPES"]
        assert "types" in doblin_lib
        assert len(doblin_lib["types"]) == 10

        # Validate categories
        categories = {t["category"] for t in doblin_lib["types"]}
        assert categories == {"Configuration", "Offering", "Experience"}


class TestStage3Execution:
    """Test Stage 3 execution workflow."""

    @pytest.mark.asyncio
    async def test_execute_basic_flow(
        self,
        stage3_instance,
        sample_stage2_output,
        sample_brand_context,
        mock_llm_response_stage3
    ):
        """Test basic execution flow with mocked LLM."""
        # Mock OpenRouter client
        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_llm_response_stage3)

        # Execute Stage 3
        result = await stage3_instance.execute(
            stage2_output=sample_stage2_output,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )

        # Validate output type
        assert isinstance(result, Stage3Output)
        assert len(result.matched_techniques) == 1
        assert result.sit_matches == 1
        assert result.triz_matches == 0

    @pytest.mark.asyncio
    async def test_technique_matching_accuracy(
        self,
        stage3_instance,
        sample_stage2_output,
        sample_brand_context,
        mock_llm_response_stage3
    ):
        """Test that matched techniques are accurate."""
        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_llm_response_stage3)

        result = await stage3_instance.execute(
            stage2_output=sample_stage2_output,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )

        # Validate first matched technique
        match = result.matched_techniques[0]
        assert match.insight_id == "insight_001"
        assert match.primary_technique.framework == "SIT"
        assert match.primary_technique.technique == "Task Unification"
        assert match.doblin_type == "Service"

    @pytest.mark.asyncio
    async def test_defensibility_score_validation(
        self,
        stage3_instance,
        sample_stage2_output,
        sample_brand_context,
        mock_llm_response_stage3
    ):
        """Test defensibility scores are within valid range."""
        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_llm_response_stage3)

        result = await stage3_instance.execute(
            stage2_output=sample_stage2_output,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )

        # Validate defensibility score range
        for match in result.matched_techniques:
            if match.primary_technique.defensibility_score:
                assert 0.0 <= match.primary_technique.defensibility_score <= 1.0


class TestTRIZConditionalApplication:
    """Test TRIZ is only applied when SIT is insufficient."""

    @pytest.mark.asyncio
    async def test_triz_not_applied_when_sit_sufficient(
        self,
        stage3_instance,
        sample_stage2_output,
        sample_brand_context,
        mock_llm_response_stage3
    ):
        """Test TRIZ is not applied when SIT is sufficient."""
        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_llm_response_stage3)

        result = await stage3_instance.execute(
            stage2_output=sample_stage2_output,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )

        # Validate no TRIZ secondary techniques
        assert result.triz_matches == 0
        for match in result.matched_techniques:
            assert match.secondary_technique is None

    @pytest.mark.asyncio
    async def test_triz_applied_when_needed(self, stage3_instance, sample_brand_context):
        """Test TRIZ is applied for complex technical problems."""
        # Create insight requiring TRIZ
        complex_insight = Stage2Output(
            insights=[
                ConsumerInsight(
                    insight_id="insight_complex",
                    source_trends=["trend_001"],
                    consumer_statement="I need packaging that adapts to temperature changes",
                    functional_need="Temperature-responsive packaging",
                    emotional_need="Trust in product freshness",
                    social_need="Environmental responsibility",
                    brand_relevance_score=0.70
                )
            ],
            convergence_count=1
        )

        # Mock LLM response with TRIZ
        mock_response = {
            "content": """```json
{
  "matched_techniques": [
    {
      "insight_id": "insight_complex",
      "primary_technique": {
        "framework": "SIT",
        "technique": "Attribute Dependency",
        "rationale": "Link packaging properties to temperature",
        "defensibility_score": 0.80
      },
      "secondary_technique": {
        "framework": "TRIZ",
        "technique": "Phase Transitions",
        "rationale": "SIT alone doesn't address the technical complexity of material phase changes"
      },
      "doblin_type": "Product Performance",
      "transferability": {
        "L1_domain": "Temperature-responsive food packaging",
        "L4_universal": "Material properties adapt to environmental conditions"
      }
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        result = await stage3_instance.execute(
            stage2_output=complex_insight,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )

        # Validate TRIZ was applied
        assert result.triz_matches == 1
        assert result.matched_techniques[0].secondary_technique is not None
        assert result.matched_techniques[0].secondary_technique.framework == "TRIZ"


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_invalid_json_response(
        self,
        stage3_instance,
        sample_stage2_output,
        sample_brand_context
    ):
        """Test handling of invalid JSON response from LLM."""
        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value={"content": "Invalid JSON"})

        with pytest.raises(ValueError, match="Failed to parse Stage 3 LLM response"):
            await stage3_instance.execute(
                stage2_output=sample_stage2_output,
                brand_context=sample_brand_context,
                openrouter_client=mock_client
            )

    @pytest.mark.asyncio
    async def test_missing_required_fields(
        self,
        stage3_instance,
        sample_stage2_output,
        sample_brand_context
    ):
        """Test handling of LLM response missing required fields."""
        mock_response = {
            "content": """```json
{
  "matched_techniques": [
    {
      "insight_id": "insight_001"
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError):
            await stage3_instance.execute(
                stage2_output=sample_stage2_output,
                brand_context=sample_brand_context,
                openrouter_client=mock_client
            )


class TestPerformance:
    """Test performance requirements."""

    @pytest.mark.asyncio
    async def test_execution_time_under_90_seconds(
        self,
        stage3_instance,
        sample_stage2_output,
        sample_brand_context,
        mock_llm_response_stage3
    ):
        """Test Stage 3 completes within 90 seconds."""
        import time

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_llm_response_stage3)

        start_time = time.time()
        await stage3_instance.execute(
            stage2_output=sample_stage2_output,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )
        elapsed = time.time() - start_time

        # Should be very fast with mocked LLM
        assert elapsed < 1.0  # Mocked should be instant
