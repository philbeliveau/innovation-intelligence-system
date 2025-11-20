"""Tests for Stage 4: Directional Concept Generation

Test Coverage:
- Concept count validation (3-5 concepts)
- No-hallucination boundary enforcement
- Boundary disclosure presence
- Integration with Stage 2 and Stage 3 outputs
- Concept quality validation
- Performance requirements
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
    TechniqueTransferability,
    Stage4Output,
    DirectionalConcept
)


@pytest.fixture
def stage4_instance():
    """Create Stage4ConceptGeneration instance."""
    return Stage4ConceptGeneration()


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
def sample_stage3_output():
    """Sample Stage 3 output with matched techniques."""
    return Stage3Output(
        matched_techniques=[
            MatchedTechnique(
                insight_id="insight_001",
                primary_technique=InnovationTechnique(
                    framework="SIT",
                    technique="Task Unification",
                    rationale="Shelf labels can perform choice-simplification task",
                    defensibility_score=0.65
                ),
                secondary_technique=None,
                doblin_type="Service",
                transferability=TechniqueTransferability(
                    L1_domain="Bakery shelf labels become decision-support tools",
                    L4_universal="Environmental cues repurposed to simplify choices"
                )
            )
        ],
        sit_matches=1,
        triz_matches=0
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
def mock_llm_response_stage4_valid():
    """Mock valid LLM response for Stage 4 with 3 concepts."""
    return {
        "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "The Bread Finder Tool",
      "concept_statement": "A 3-question quiz that recommends THE ONE bread for your family",
      "mechanism": "QR code on shelf → 3-question quiz → Personalized recommendation → Product location",
      "why_it_works": "Applies Task Unification by assigning choice-simplification task to existing shelf labels. Reduces decision fatigue.",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Bread Pairing Guide",
      "concept_statement": "Shelf labels show which bread pairs best with common meals (sandwiches, toast, soup)",
      "mechanism": "Visual pairing icons on shelf → Consumer matches meal type to icon → Product recommendation displayed",
      "why_it_works": "Simplifies choice by connecting bread to use case. Leverages existing shelf labels to perform decision-support task.",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "The Daily Bread Pick",
      "concept_statement": "Single spotlight recommendation rotates daily based on seasonal ingredients and family needs",
      "mechanism": "Store highlights ONE bread each day → Signage explains why (e.g., 'perfect for fall soups') → Reduces choice overload",
      "why_it_works": "Curates choice down to one recommendation, directly addressing overwhelm. Uses existing signage for new task.",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
    }


@pytest.fixture
def mock_llm_response_stage4_hallucination():
    """Mock LLM response with hallucinated content (should fail validation)."""
    return {
        "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "The Bread Finder Tool",
      "concept_statement": "A 3-question quiz that could capture 15% market share",
      "mechanism": "QR code on shelf generating $5M revenue in year 1",
      "why_it_works": "Studies show 80% of consumers want this. No other brand has done this.",
      "boundary_disclosure": "This is a directional concept."
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Valid Concept 1",
      "concept_statement": "A concept without hallucinations",
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


class TestConceptCountValidation:
    """Test concept count requirements (3-5 concepts)."""

    @pytest.mark.asyncio
    async def test_valid_concept_count(
        self,
        stage4_instance,
        sample_stage2_output,
        sample_stage3_output,
        sample_brand_context,
        mock_llm_response_stage4_valid
    ):
        """Test execution with valid concept count (3-5)."""
        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_llm_response_stage4_valid)

        result = await stage4_instance.execute(
            stage2_output=sample_stage2_output,
            stage3_output=sample_stage3_output,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )

        assert isinstance(result, Stage4Output)
        assert 3 <= result.total_concepts <= 5
        assert len(result.concepts) == result.total_concepts

    @pytest.mark.asyncio
    async def test_too_few_concepts_raises_error(
        self,
        stage4_instance,
        sample_stage2_output,
        sample_stage3_output,
        sample_brand_context
    ):
        """Test that < 3 concepts raises error."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Only One Concept",
      "concept_statement": "This is the only concept",
      "mechanism": "Some mechanism",
      "why_it_works": "It works somehow",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="generated only.*concepts. Expected 3-5"):
            await stage4_instance.execute(
                stage2_output=sample_stage2_output,
                stage3_output=sample_stage3_output,
                brand_context=sample_brand_context,
                openrouter_client=mock_client
            )

    @pytest.mark.asyncio
    async def test_too_many_concepts_trimmed(
        self,
        stage4_instance,
        sample_stage2_output,
        sample_stage3_output,
        sample_brand_context
    ):
        """Test that > 5 concepts are trimmed to 5."""
        # Generate 7 concepts
        concepts = []
        for i in range(7):
            concepts.append({
                "insight_id": "insight_001",
                "technique_id": "task_unification",
                "concept_name": f"Concept {i+1}",
                "concept_statement": f"Statement {i+1}",
                "mechanism": f"Mechanism {i+1}",
                "why_it_works": f"Rationale {i+1}",
                "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
            })

        import json
        mock_response = {"content": f"```json\n{json.dumps({'concepts': concepts})}\n```"}
        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        result = await stage4_instance.execute(
            stage2_output=sample_stage2_output,
            stage3_output=sample_stage3_output,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )

        # Should be trimmed to 5
        assert result.total_concepts == 5
        assert len(result.concepts) == 5


class TestNoHallucinationBoundaries:
    """Test no-hallucination boundary enforcement."""

    @pytest.mark.asyncio
    async def test_financial_hallucination_detected(
        self,
        stage4_instance,
        sample_stage2_output,
        sample_stage3_output,
        sample_brand_context,
        mock_llm_response_stage4_hallucination
    ):
        """Test that financial hallucinations are detected and raise error."""
        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_llm_response_stage4_hallucination)

        with pytest.raises(ValueError, match="boundary violation|missing proper boundary disclosure"):
            await stage4_instance.execute(
                stage2_output=sample_stage2_output,
                stage3_output=sample_stage3_output,
                brand_context=sample_brand_context,
                openrouter_client=mock_client
            )

    @pytest.mark.asyncio
    async def test_competitive_claim_hallucination_detected(
        self,
        stage4_instance,
        sample_stage2_output,
        sample_stage3_output,
        sample_brand_context
    ):
        """Test that competitive hallucinations are detected."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "First-to-Market Tool",
      "concept_statement": "We'll be the first brand to do this",
      "mechanism": "No other company has thought of this",
      "why_it_works": "Only brand that can execute this",
      "boundary_disclosure": "This is a directional concept."
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

        with pytest.raises(ValueError, match="boundary violation|missing proper boundary disclosure"):
            await stage4_instance.execute(
                stage2_output=sample_stage2_output,
                stage3_output=sample_stage3_output,
                brand_context=sample_brand_context,
                openrouter_client=mock_client
            )

    @pytest.mark.asyncio
    async def test_statistical_hallucination_detected(
        self,
        stage4_instance,
        sample_stage2_output,
        sample_stage3_output,
        sample_brand_context
    ):
        """Test that statistical hallucinations are detected."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "Research-Backed Tool",
      "concept_statement": "Studies show 75% of consumers want this",
      "mechanism": "Research indicates high adoption",
      "why_it_works": "85% of shoppers prefer this approach",
      "boundary_disclosure": "This is a directional concept."
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

        with pytest.raises(ValueError, match="boundary violation|missing proper boundary disclosure"):
            await stage4_instance.execute(
                stage2_output=sample_stage2_output,
                stage3_output=sample_stage3_output,
                brand_context=sample_brand_context,
                openrouter_client=mock_client
            )


class TestBoundaryDisclosurePresence:
    """Test boundary disclosure is present in all concepts."""

    @pytest.mark.asyncio
    async def test_boundary_disclosure_required(
        self,
        stage4_instance,
        sample_stage2_output,
        sample_stage3_output,
        sample_brand_context
    ):
        """Test that missing boundary disclosure raises error."""
        mock_response = {
            "content": """```json
{
  "concepts": [
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "No Disclosure Concept 1",
      "concept_statement": "Valid statement",
      "mechanism": "Valid mechanism",
      "why_it_works": "Valid rationale",
      "boundary_disclosure": ""
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "No Disclosure Concept 2",
      "concept_statement": "Valid statement",
      "mechanism": "Valid mechanism",
      "why_it_works": "Valid rationale",
      "boundary_disclosure": ""
    },
    {
      "insight_id": "insight_001",
      "technique_id": "task_unification",
      "concept_name": "No Disclosure Concept 3",
      "concept_statement": "Valid statement",
      "mechanism": "Valid mechanism",
      "why_it_works": "Valid rationale",
      "boundary_disclosure": ""
    }
  ]
}
```"""
        }

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="missing proper boundary disclosure"):
            await stage4_instance.execute(
                stage2_output=sample_stage2_output,
                stage3_output=sample_stage3_output,
                brand_context=sample_brand_context,
                openrouter_client=mock_client
            )

    @pytest.mark.asyncio
    async def test_boundary_disclosure_content_valid(
        self,
        stage4_instance,
        sample_stage2_output,
        sample_stage3_output,
        sample_brand_context,
        mock_llm_response_stage4_valid
    ):
        """Test that valid boundary disclosure passes validation."""
        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_llm_response_stage4_valid)

        result = await stage4_instance.execute(
            stage2_output=sample_stage2_output,
            stage3_output=sample_stage3_output,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )

        # All concepts should have boundary disclosure
        for concept in result.concepts:
            assert len(concept.boundary_disclosure) >= 50
            assert "does not include" in concept.boundary_disclosure.lower()


class TestConceptQuality:
    """Test concept quality validation."""

    @pytest.mark.asyncio
    async def test_concepts_have_required_fields(
        self,
        stage4_instance,
        sample_stage2_output,
        sample_stage3_output,
        sample_brand_context,
        mock_llm_response_stage4_valid
    ):
        """Test all concepts have required fields."""
        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_llm_response_stage4_valid)

        result = await stage4_instance.execute(
            stage2_output=sample_stage2_output,
            stage3_output=sample_stage3_output,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )

        for concept in result.concepts:
            assert concept.concept_id
            assert concept.concept_name
            assert concept.concept_statement
            assert concept.mechanism
            assert concept.why_it_works
            assert concept.boundary_disclosure

    @pytest.mark.asyncio
    async def test_boundary_enforcement_flag_set(
        self,
        stage4_instance,
        sample_stage2_output,
        sample_stage3_output,
        sample_brand_context,
        mock_llm_response_stage4_valid
    ):
        """Test boundary_enforcement_applied flag is set."""
        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_llm_response_stage4_valid)

        result = await stage4_instance.execute(
            stage2_output=sample_stage2_output,
            stage3_output=sample_stage3_output,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )

        assert result.boundary_enforcement_applied is True


class TestPerformance:
    """Test performance requirements."""

    @pytest.mark.asyncio
    async def test_execution_time_under_90_seconds(
        self,
        stage4_instance,
        sample_stage2_output,
        sample_stage3_output,
        sample_brand_context,
        mock_llm_response_stage4_valid
    ):
        """Test Stage 4 completes within 90 seconds."""
        import time

        mock_client = AsyncMock()
        mock_client.call_llm = AsyncMock(return_value=mock_llm_response_stage4_valid)

        start_time = time.time()
        await stage4_instance.execute(
            stage2_output=sample_stage2_output,
            stage3_output=sample_stage3_output,
            brand_context=sample_brand_context,
            openrouter_client=mock_client
        )
        elapsed = time.time() - start_time

        # Should be very fast with mocked LLM
        assert elapsed < 1.0  # Mocked should be instant
