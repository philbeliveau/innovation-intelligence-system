"""Tests for Stage 1: Trend Decomposition"""
import pytest
import json
from backend.experimentation.stages.stage_1_decomposition import Stage1Decomposition
from backend.experimentation.schemas import Stage1Output, Trend


@pytest.fixture
def sample_report_text():
    """Sample trend report text for testing."""
    return """
    TREND: Strategic Joy
    Lifecycle: ACCELERATING (emerging 2023, peak 2027)

    Consumers are experiencing decision fatigue and overwhelm in daily life. They feel
    trapped by routine and lack spontaneity. They aspire to find clarity, simplicity,
    and moments of delight in everyday experiences.

    Evidence:
    - 67% of consumers report decision fatigue in grocery shopping (Mintel 2024)
    - Growth in "joy-seeking" social media content (+45% YoY)
    - Brands like Nike launching playful product experiences

    Weak signals:
    - Emerging gamification in mundane tasks
    - Rise of "micro-joy" moments in marketing
    """


@pytest.fixture
def mock_llm_output():
    """Mock LLM JSON output for testing parsing."""
    return {
        "trends": [
            {
                "trend_id": "strategic-joy-2024",
                "name": "Strategic Joy",
                "lifecycle_stage": "ACCELERATING",
                "timeline": {
                    "emergence_year": 2023,
                    "peak_year": 2027
                },
                "evidence": [
                    "67% of consumers report decision fatigue (Mintel 2024)",
                    "Growth in joy-seeking social media content (+45% YoY)",
                    "Nike launching playful product experiences"
                ],
                "weak_signals": [
                    "Emerging gamification in mundane tasks",
                    "Rise of micro-joy moments in marketing"
                ],
                "emotional_drivers": {
                    "current_negative": ["Decision fatigue", "Overwhelm", "Routine"],
                    "aspirational_positive": ["Clarity", "Simplicity", "Delight"]
                },
                "abstraction_ladder": {
                    "L1_domain_specific": "CPG brands want to inject playfulness into functional products",
                    "L2_category": "Consumer brands want to balance utility with emotional uplift",
                    "L3_cross_category": "Organizations want to make practical experiences more enjoyable",
                    "L4_universal": "People seek to find pleasure in necessary activities"
                }
            }
        ]
    }


def test_stage_1_parse_json_from_markdown():
    """Test parsing JSON from markdown code blocks."""
    stage1 = Stage1Decomposition()

    # Test with markdown code block
    markdown_output = '```json\n{"trends": []}\n```'
    result = stage1._parse_llm_output(markdown_output)
    assert result == {"trends": []}

    # Test with plain code block
    plain_output = '```\n{"trends": []}\n```'
    result = stage1._parse_llm_output(plain_output)
    assert result == {"trends": []}

    # Test with raw JSON
    raw_output = '{"trends": []}'
    result = stage1._parse_llm_output(raw_output)
    assert result == {"trends": []}


def test_stage_1_parse_invalid_json():
    """Test that invalid JSON raises ValueError."""
    stage1 = Stage1Decomposition()

    with pytest.raises(ValueError, match="Invalid JSON from LLM"):
        stage1._parse_llm_output("This is not JSON {invalid}")


def test_trend_schema_validation(mock_llm_output):
    """Test that Trend schema validates correctly."""
    trend_data = mock_llm_output["trends"][0]
    trend = Trend(**trend_data)

    # Validate all fields
    assert trend.trend_id == "strategic-joy-2024"
    assert trend.name == "Strategic Joy"
    assert trend.lifecycle_stage == "ACCELERATING"
    assert trend.timeline.emergence_year == 2023
    assert trend.timeline.peak_year == 2027
    assert len(trend.evidence) == 3
    assert len(trend.weak_signals) == 2
    assert "Decision fatigue" in trend.emotional_drivers.current_negative
    assert "Clarity" in trend.emotional_drivers.aspirational_positive
    assert trend.abstraction_ladder.L4_universal.startswith("People seek")


def test_trend_schema_missing_abstraction_ladder():
    """Test that Trend schema requires abstraction ladder."""
    incomplete_trend = {
        "trend_id": "test-trend",
        "name": "Test Trend",
        "lifecycle_stage": "EMERGING",
        "evidence": ["Test evidence"],
        "weak_signals": ["Test signal"],
        "emotional_drivers": {
            "current_negative": ["Negative"],
            "aspirational_positive": ["Positive"]
        }
        # Missing abstraction_ladder!
    }

    with pytest.raises(ValueError):
        Trend(**incomplete_trend)


@pytest.mark.asyncio
async def test_stage_1_validates_output(mocker, mock_llm_output):
    """Test that Stage 1 validates LLM output and constructs Trend objects."""
    stage1 = Stage1Decomposition()

    # Mock LLM call
    mock_response = mocker.Mock()
    mock_response.content = json.dumps(mock_llm_output)
    stage1.llm = mocker.Mock()
    stage1.llm.ainvoke = mocker.AsyncMock(return_value=mock_response)

    # Mock prompt template
    stage1.prompt_template = "{report_text}"

    result = await stage1.run("Sample report text")

    # Validate output type
    assert isinstance(result, Stage1Output)
    assert result.total_trends_extracted == 1
    assert len(result.trends) == 1
    assert isinstance(result.trends[0], Trend)


@pytest.mark.asyncio
async def test_stage_1_handles_partial_invalid_trends(mocker):
    """Test that Stage 1 skips invalid trends but processes valid ones."""
    stage1 = Stage1Decomposition()

    # Mixed valid and invalid trends
    mixed_output = {
        "trends": [
            {  # Valid trend
                "trend_id": "valid-trend",
                "name": "Valid Trend",
                "lifecycle_stage": "EMERGING",
                "evidence": ["Evidence"],
                "weak_signals": ["Signal"],
                "emotional_drivers": {
                    "current_negative": ["Neg"],
                    "aspirational_positive": ["Pos"]
                },
                "abstraction_ladder": {
                    "L1_domain_specific": "L1",
                    "L2_category": "L2",
                    "L3_cross_category": "L3",
                    "L4_universal": "L4"
                }
            },
            {  # Invalid trend (missing abstraction_ladder)
                "trend_id": "invalid-trend",
                "name": "Invalid Trend",
                "lifecycle_stage": "PEAKING"
            }
        ]
    }

    mock_response = mocker.Mock()
    mock_response.content = json.dumps(mixed_output)
    stage1.llm = mocker.Mock()
    stage1.llm.ainvoke = mocker.AsyncMock(return_value=mock_response)
    stage1.prompt_template = "{report_text}"

    result = await stage1.run("Sample report")

    # Should process only the valid trend
    assert len(result.trends) == 1
    assert result.trends[0].trend_id == "valid-trend"
