"""Tests for Stage 2: Consumer Insights"""
import pytest
import json
from backend.experimentation.stages.stage_2_insights import Stage2Insights
from backend.experimentation.schemas import (
    Stage0Output,
    Stage1Output,
    Stage2Output,
    BrandEnrichment,
    Trend,
    AbstractionLadder,
    EmotionalDrivers,
    ConsumerInsight
)


@pytest.fixture
def sample_stage0_output():
    """Sample Stage 0 output for testing."""
    brand_context = BrandEnrichment(
        brand_name="Test Bakery",
        industry="Food & Beverage",
        country="Canada",
        product_portfolio=["Bread", "Pastries", "Cakes"],
        positioning="Premium artisan bakery",
        confidence_score=1.0
    )
    return Stage0Output(brand_context=brand_context, enrichment_method="basic")


@pytest.fixture
def sample_stage1_output():
    """Sample Stage 1 output with multiple trends for testing."""
    trend1 = Trend(
        trend_id="witherwill",
        name="Witherwill",
        lifecycle_stage="ACCELERATING",
        evidence=["Decision fatigue in retail", "Choice overload research"],
        weak_signals=["Minimal shelf displays", "Curated selections"],
        emotional_drivers=EmotionalDrivers(
            current_negative=["Decision fatigue", "Overwhelm", "Choice paralysis"],
            aspirational_positive=["Clarity", "Simplicity", "Freedom"]
        ),
        abstraction_ladder=AbstractionLadder(
            L1_domain_specific="Consumers overwhelmed by bread choices",
            L2_category="Shoppers want simplified product selection",
            L3_cross_category="People seek to reduce cognitive load",
            L4_universal="Humans desire mental freedom from trivial choices"
        )
    )

    trend2 = Trend(
        trend_id="strategic-joy",
        name="Strategic Joy",
        lifecycle_stage="EMERGING",
        evidence=["Playful product experiences", "Joy-seeking behavior"],
        weak_signals=["Gamification in retail", "Micro-joy moments"],
        emotional_drivers=EmotionalDrivers(
            current_negative=["Routine", "Monotony"],
            aspirational_positive=["Delight", "Enjoyment", "Freedom"]  # Shared with trend1
        ),
        abstraction_ladder=AbstractionLadder(
            L1_domain_specific="Brands inject playfulness into functional products",
            L2_category="Balance utility with emotional uplift",
            L3_cross_category="Make practical experiences enjoyable",
            L4_universal="People seek pleasure in necessary activities"
        )
    )

    return Stage1Output(trends=[trend1, trend2], total_trends_extracted=2)


def test_stage_2_identify_convergences(sample_stage1_output):
    """Test convergence identification between trends."""
    stage2 = Stage2Insights()

    convergences = stage2._identify_convergences(sample_stage1_output.trends)

    # Should find convergence (both trends share "Freedom" in aspirational_positive)
    assert len(convergences) > 0
    assert any("Freedom" in conv["shared_emotions"] for conv in convergences)


def test_stage_2_no_convergences():
    """Test handling when no convergences exist."""
    stage2 = Stage2Insights()

    # Trends with no shared emotional drivers
    trend1 = Trend(
        trend_id="trend1",
        name="Trend 1",
        lifecycle_stage="EMERGING",
        evidence=["Evidence"],
        weak_signals=["Signal"],
        emotional_drivers=EmotionalDrivers(
            current_negative=["A"],
            aspirational_positive=["B"]
        ),
        abstraction_ladder=AbstractionLadder(
            L1_domain_specific="L1",
            L2_category="L2",
            L3_cross_category="L3",
            L4_universal="L4"
        )
    )

    trend2 = Trend(
        trend_id="trend2",
        name="Trend 2",
        lifecycle_stage="PEAKING",
        evidence=["Evidence"],
        weak_signals=["Signal"],
        emotional_drivers=EmotionalDrivers(
            current_negative=["C"],
            aspirational_positive=["D"]
        ),
        abstraction_ladder=AbstractionLadder(
            L1_domain_specific="L1",
            L2_category="L2",
            L3_cross_category="L3",
            L4_universal="L4"
        )
    )

    convergences = stage2._identify_convergences([trend1, trend2])

    # Should find no convergences
    assert len(convergences) == 0


@pytest.mark.asyncio
async def test_stage_2_generates_insights(mocker, sample_stage0_output, sample_stage1_output):
    """Test that Stage 2 generates consumer insights."""
    stage2 = Stage2Insights()

    # Mock LLM output
    mock_llm_output = {
        "insights": [
            {
                "insight_id": "insight-1",
                "source_trends": ["witherwill", "strategic-joy"],
                "consumer_statement": "I'm overwhelmed by bread choices - just tell me THE ONE bread for my family",
                "functional_need": "Simplify decision-making at point of purchase",
                "emotional_need": "Reduce cognitive load and achieve clarity",
                "social_need": "Feel confident making the right choice for my family",
                "brand_relevance_score": 0.9
            }
        ],
        "convergence_count": 1
    }

    mock_response = mocker.Mock()
    mock_response.content = json.dumps(mock_llm_output)
    stage2.llm = mocker.Mock()
    stage2.llm.ainvoke = mocker.AsyncMock(return_value=mock_response)
    stage2.prompt_template = "{trends}\n{brand_context}"

    result = await stage2.run(sample_stage1_output, sample_stage0_output)

    # Validate output
    assert isinstance(result, Stage2Output)
    assert len(result.insights) == 1
    assert isinstance(result.insights[0], ConsumerInsight)
    assert result.insights[0].brand_relevance_score == 0.9


def test_consumer_insight_schema_validation():
    """Test that ConsumerInsight schema validates correctly."""
    valid_insight = {
        "insight_id": "test-insight",
        "source_trends": ["trend1", "trend2"],
        "consumer_statement": "I want to simplify my shopping experience",
        "functional_need": "Reduce time spent shopping",
        "emotional_need": "Feel less stressed",
        "social_need": "Appear organized",
        "brand_relevance_score": 0.85
    }

    insight = ConsumerInsight(**valid_insight)
    assert insight.insight_id == "test-insight"
    assert len(insight.source_trends) == 2
    assert insight.brand_relevance_score == 0.85


def test_consumer_insight_schema_rejects_invalid_score():
    """Test that brand_relevance_score must be between 0.0 and 1.0."""
    with pytest.raises(ValueError):
        ConsumerInsight(
            insight_id="test",
            source_trends=["trend1"],
            consumer_statement="Statement",
            functional_need="Need",
            emotional_need="Emotion",
            social_need="Social",
            brand_relevance_score=1.2  # Invalid
        )


@pytest.mark.asyncio
async def test_stage_2_handles_no_convergences(mocker):
    """Test Stage 2 fallback when no convergences found."""
    stage2 = Stage2Insights()

    # Trends with no convergences
    brand_context = BrandEnrichment(
        brand_name="Test", industry="Test", country="Test",
        product_portfolio=[], confidence_score=1.0
    )
    stage0_out = Stage0Output(brand_context=brand_context, enrichment_method="basic")

    trend = Trend(
        trend_id="solo-trend",
        name="Solo Trend",
        lifecycle_stage="EMERGING",
        evidence=["E"],
        weak_signals=["S"],
        emotional_drivers=EmotionalDrivers(
            current_negative=["Neg"],
            aspirational_positive=["Pos"]
        ),
        abstraction_ladder=AbstractionLadder(
            L1_domain_specific="L1", L2_category="L2",
            L3_cross_category="L3", L4_universal="L4"
        )
    )
    stage1_out = Stage1Output(trends=[trend], total_trends_extracted=1)

    # Mock LLM to return valid insight
    mock_response = mocker.Mock()
    mock_response.content = json.dumps({
        "insights": [{
            "insight_id": "fallback-insight",
            "source_trends": ["solo-trend"],
            "consumer_statement": "Test statement",
            "functional_need": "Functional",
            "emotional_need": "Emotional",
            "social_need": "Social",
            "brand_relevance_score": 0.7
        }],
        "convergence_count": 0
    })
    stage2.llm = mocker.Mock()
    stage2.llm.ainvoke = mocker.AsyncMock(return_value=mock_response)
    stage2.prompt_template = "{trends}\n{brand_context}"

    result = await stage2.run(stage1_out, stage0_out)

    # Should still generate insights using fallback (single-trend insights)
    assert len(result.insights) >= 1
