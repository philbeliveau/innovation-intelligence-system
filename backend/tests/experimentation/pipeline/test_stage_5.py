"""Tests for Stage 5: Competitive Intelligence Search

Tests honesty constraints, multi-query strategy, and Perplexity API integration.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.experimentation.stages.stage_5_competitive import Stage5CompetitiveIntelligence
from backend.experimentation.schemas import Stage4Output, DirectionalConcept


@pytest.fixture
def mock_stage4_output():
    """Mock Stage 4 output with 3 concepts."""
    return Stage4Output(
        concepts=[
            DirectionalConcept(
                concept_id="concept-1",
                insight_id="insight-1",
                technique_id="technique-1",
                concept_name="Bread Finder Tool",
                concept_statement="Decision-support tool where consumers answer 3 questions",
                mechanism="QR code on shelf → 3-question quiz → Personalized recommendation",
                why_it_works="Unifies choice-simplification task with existing shelf resource",
                boundary_disclosure="This is a directional concept."
            ),
            DirectionalConcept(
                concept_id="concept-2",
                insight_id="insight-2",
                technique_id="technique-2",
                concept_name="Flavor Discovery App",
                concept_statement="Gamified flavor exploration experience",
                mechanism="Mobile app with AR flavor visualization",
                why_it_works="Makes flavor selection engaging and educational",
                boundary_disclosure="This is a directional concept."
            )
        ],
        total_concepts=2,
        boundary_enforcement_applied=True
    )


@pytest.fixture
def mock_brand_context():
    """Mock brand context."""
    return {
        "brand_name": "St-Méthode",
        "industry": "Bakery/Food & Beverage",
        "country": "Canada",
        "product_portfolio": ["Bread", "Pastries"]
    }


@pytest.fixture
def mock_openrouter_client():
    """Mock OpenRouter client for query generation."""
    client = AsyncMock()
    client.call_llm = AsyncMock(return_value={
        "content": '{"queries": ["bread recommendation quiz QR code", "decision simplification tool retail", "bakery product finder innovation"]}'
    })
    return client


@pytest.mark.asyncio
async def test_stage5_without_perplexity_api_key(mock_stage4_output, mock_brand_context, mock_openrouter_client, monkeypatch):
    """Test Stage 5 graceful degradation when PERPLEXITY_API_KEY not set."""
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)

    stage5 = Stage5CompetitiveIntelligence()
    result = await stage5.execute(
        stage4_output=mock_stage4_output,
        brand_context=mock_brand_context,
        openrouter_client=mock_openrouter_client
    )

    assert result["search_enabled"] is False
    assert result["total_queries_executed"] == 0
    assert len(result["competitive_intel"]) == 2
    for ci in result["competitive_intel"]:
        assert "Competitive search skipped" in ci["novelty_assessment"]


@pytest.mark.asyncio
@patch("backend.experimentation.stages.stage_5_competitive.httpx.AsyncClient")
async def test_stage5_with_perplexity_api(mock_httpx, mock_stage4_output, mock_brand_context, mock_openrouter_client, monkeypatch):
    """Test Stage 5 with Perplexity API enabled."""
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test-api-key")

    # Mock Perplexity API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "Wine Finder quiz at Total Wine stores uses a similar concept."
            }
        }],
        "citations": ["https://example.com/wine-finder"]
    }

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_client_instance.__aexit__.return_value = None
    mock_httpx.return_value = mock_client_instance

    stage5 = Stage5CompetitiveIntelligence()
    result = await stage5.execute(
        stage4_output=mock_stage4_output,
        brand_context=mock_brand_context,
        openrouter_client=mock_openrouter_client
    )

    assert result["search_enabled"] is True
    assert result["total_queries_executed"] == 6  # 2 concepts × 3 queries each
    assert len(result["competitive_intel"]) == 2


@pytest.mark.asyncio
async def test_stage5_query_generation(mock_stage4_output, mock_brand_context, mock_openrouter_client, monkeypatch):
    """Test that Stage 5 generates 3 queries per concept."""
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test-api-key")

    stage5 = Stage5CompetitiveIntelligence()

    # Test query generation for first concept
    queries = await stage5._generate_search_queries(
        concept=mock_stage4_output.concepts[0],
        brand_context=mock_brand_context,
        openrouter_client=mock_openrouter_client
    )

    assert len(queries) == 3
    assert all(isinstance(q, str) for q in queries)
    assert all(len(q) > 5 for q in queries)  # Minimum query length


def test_stage5_parse_queries_json_format():
    """Test parsing queries from JSON format."""
    stage5 = Stage5CompetitiveIntelligence()

    llm_content = '''```json
{
  "queries": [
    "bread recommendation quiz QR code",
    "decision simplification tool retail",
    "bakery product finder innovation"
  ]
}
```'''

    queries = stage5._parse_queries_from_response(llm_content)

    assert len(queries) == 3
    assert queries[0] == "bread recommendation quiz QR code"


def test_stage5_parse_queries_numbered_list():
    """Test parsing queries from numbered list format."""
    stage5 = Stage5CompetitiveIntelligence()

    llm_content = """
1. Direct: bread recommendation quiz QR code
2. Analogous: decision simplification tool retail
3. Competitive: bakery product finder innovation
"""

    queries = stage5._parse_queries_from_response(llm_content)

    assert len(queries) == 3
    assert "bread recommendation" in queries[0]


def test_stage5_classify_match_type_novel():
    """Test novelty classification for 'no results' content."""
    stage5 = Stage5CompetitiveIntelligence()

    content = "No similar concepts found in the market."
    match_type = stage5._classify_match_type(content, "test query")

    assert match_type == "Novel"


def test_stage5_classify_match_type_direct():
    """Test direct match classification."""
    stage5 = Stage5CompetitiveIntelligence()

    content = "A similar product exists called Wine Finder Quiz."
    match_type = stage5._classify_match_type(content, "test query")

    assert match_type == "Direct Match"


def test_stage5_classify_match_type_analogous():
    """Test analogous match classification."""
    stage5 = Stage5CompetitiveIntelligence()

    content = "Some companies use recommendation tools in different categories."
    match_type = stage5._classify_match_type(content, "test query")

    assert match_type == "Analogous"


def test_stage5_separate_knowledge_inference():
    """Test separation of 'what we know' vs 'what we infer'."""
    stage5 = Stage5CompetitiveIntelligence()

    content = "Total Wine launched their Wine Finder tool in 2020. This suggests that similar tools could work for bread."
    citations = ["https://example.com/wine-finder"]

    what_we_know, what_we_infer = stage5._separate_knowledge_inference(content, citations)

    assert "Total Wine" in what_we_know
    assert "2020" in what_we_know
    assert "suggests" in what_we_infer


def test_stage5_assess_novelty_direct_matches():
    """Test novelty assessment with direct matches."""
    stage5 = Stage5CompetitiveIntelligence()

    findings = [
        {"match_type": "Direct Match", "description": "Test 1"},
        {"match_type": "Analogous", "description": "Test 2"},
        {"match_type": "Novel", "description": "Test 3"}
    ]

    assessment = stage5._assess_novelty(findings)

    assert "Direct matches found" in assessment


def test_stage5_assess_novelty_analogous_only():
    """Test novelty assessment with only analogous matches."""
    stage5 = Stage5CompetitiveIntelligence()

    findings = [
        {"match_type": "Analogous", "description": "Test 1"},
        {"match_type": "Analogous", "description": "Test 2"}
    ]

    assessment = stage5._assess_novelty(findings)

    assert "Analogous solutions exist" in assessment


def test_stage5_assess_novelty_novel():
    """Test novelty assessment with no matches."""
    stage5 = Stage5CompetitiveIntelligence()

    findings = [
        {"match_type": "Novel", "description": "Test 1"},
        {"match_type": "Novel", "description": "Test 2"}
    ]

    assessment = stage5._assess_novelty(findings)

    assert "Novel concept" in assessment
