"""Tests for Stage 6: Opportunity Card Packaging

Tests markdown formatting, 30-second pitch structure, and no-hallucination disclosure.
"""
import pytest
from unittest.mock import AsyncMock
from backend.experimentation.stages.stage_6_packaging import Stage6OpportunityCards
from backend.experimentation.schemas import (
    Stage1Output,
    Stage2Output,
    Stage3Output,
    Stage4Output,
    Trend,
    ConsumerInsight,
    MatchedTechnique,
    DirectionalConcept,
    TrendTimeline,
    EmotionalDrivers,
    AbstractionLadder,
    InnovationTechnique,
    TechniqueTransferability
)


@pytest.fixture
def mock_stage1_output():
    """Mock Stage 1 output with trends."""
    return Stage1Output(
        trends=[
            Trend(
                trend_id="trend-1",
                name="Witherwill",
                lifecycle_stage="ACCELERATING",
                timeline=TrendTimeline(emergence_year=2024, peak_year=2027),
                evidence=["Decision fatigue reports", "Ping minimalism searches"],
                weak_signals=["Longing to be free from responsibility"],
                emotional_drivers=EmotionalDrivers(
                    current_negative=["Overwhelm", "Decision fatigue"],
                    aspirational_positive=["Clarity", "Simplicity", "Freedom"]
                ),
                abstraction_ladder=AbstractionLadder(
                    L1_domain_specific="Consumers overwhelmed by bread choices",
                    L2_category="Shoppers want simplified product selection",
                    L3_cross_category="People seek to reduce cognitive load in daily decisions",
                    L4_universal="Humans desire mental freedom from trivial choices"
                )
            )
        ],
        total_trends_extracted=1
    )


@pytest.fixture
def mock_stage2_output():
    """Mock Stage 2 output with insights."""
    return Stage2Output(
        insights=[
            ConsumerInsight(
                insight_id="insight-1",
                source_trends=["trend-1"],
                consumer_statement="I'm overwhelmed by bread choices - just tell me THE ONE bread for my family",
                functional_need="Simplify decision-making at point of purchase",
                emotional_need="Reduce cognitive load and decision fatigue",
                social_need="Feel confident I'm making the 'right' choice",
                brand_relevance_score=0.85
            )
        ],
        convergence_count=1
    )


@pytest.fixture
def mock_stage3_output():
    """Mock Stage 3 output with matched techniques."""
    return Stage3Output(
        matched_techniques=[
            MatchedTechnique(
                insight_id="insight-1",
                primary_technique=InnovationTechnique(
                    framework="SIT",
                    technique="Task Unification",
                    rationale="Existing shelf/packaging can take on choice-simplification task",
                    defensibility_score=0.7
                ),
                doblin_type="Service",
                transferability=TechniqueTransferability(
                    L1_domain="Bakery decision support",
                    L4_universal="Choice simplification mechanism"
                )
            )
        ],
        sit_matches=1,
        triz_matches=0
    )


@pytest.fixture
def mock_stage4_output():
    """Mock Stage 4 output with concepts."""
    return Stage4Output(
        concepts=[
            DirectionalConcept(
                concept_id="concept-1",
                insight_id="insight-1",
                technique_id="technique-1",
                concept_name="Le Guide St-Méthode (The Bread Finder Tool)",
                concept_statement="Decision-support tool where consumers answer 3 questions and receive ONE St-Méthode bread recommendation",
                mechanism="QR code on shelf → 3-question quiz → Personalized recommendation → Product location",
                why_it_works="Unifies choice-simplification task with existing shelf resource, reducing decision fatigue",
                boundary_disclosure="This is a directional concept. No financial projections included."
            )
        ],
        total_concepts=1,
        boundary_enforcement_applied=True
    )


@pytest.fixture
def mock_stage5_output():
    """Mock Stage 5 output with competitive intel."""
    return {
        "competitive_intel": [
            {
                "concept_id": "concept-1",
                "search_queries": ["bread recommendation quiz", "decision tool retail", "product finder grocery"],
                "findings": [
                    {
                        "match_type": "Analogous",
                        "query": "wine recommendation quiz",
                        "description": "Total Wine uses a Wine Finder quiz.",
                        "source_urls": ["https://example.com/wine-finder"],
                        "what_we_know": "Total Wine launched quiz in 2020.",
                        "what_we_infer": "Similar concept could apply to bread."
                    }
                ],
                "novelty_assessment": "Analogous solutions exist in other categories, but not in bakery domain"
            }
        ],
        "search_enabled": True,
        "total_queries_executed": 3
    }


@pytest.fixture
def mock_brand_context():
    """Mock brand context."""
    return {
        "brand_name": "St-Méthode",
        "industry": "Bakery/Food & Beverage",
        "country": "Canada",
        "product_portfolio": ["Bread", "Pastries"],
        "positioning": "Quality bakery products for Canadian families"
    }


@pytest.fixture
def mock_openrouter_client():
    """Mock OpenRouter client."""
    client = AsyncMock()
    client.call_llm = AsyncMock(return_value={
        "content": '''# 💡 Le Guide St-Méthode (The Bread Finder Tool)

## 🎯 Consumer Insight
> "I'm overwhelmed by bread choices - just tell me THE ONE bread for my family"

**Functional Need:** Simplify decision-making at point of purchase
**Emotional Need:** Reduce cognitive load and decision fatigue
**Social Need:** Feel confident I'm making the 'right' choice

---

## ⚙️ Mechanism (SIT: Task Unification)
QR code on shelf → 3-question quiz → Personalized recommendation → Product location

**How It Works:**
- Scan QR code on shelf
- Answer 3 questions
- Receive one personalized recommendation

---

## 📈 Why Now?
**Trend:** Witherwill (ACCELERATING)
- **Evidence:** Decision fatigue reports, Ping minimalism searches
- **Timeline:** Emerging 2024, peaking 2027

---

## 🏢 Why St-Méthode?
Quality bakery products with strong Canadian presence.

**Brand Assets:**
- Bread expertise
- Canadian market knowledge

---

## 🔍 Competitive Landscape
Analogous solutions exist in other categories (Wine Finder at Total Wine).

**Novelty Assessment:** Novel in bakery domain

---

## ⚠️ Boundary Disclosure
This is a directional concept. No financial projections included.

---

**Generated:** 2025-01-20T10:00:00
**Pipeline Version:** 7-Stage SIT-Based Extraction
**Source Trend Report:** Test Report'''
    })
    return client


@pytest.mark.asyncio
async def test_stage6_generates_opportunity_cards(
    mock_stage1_output,
    mock_stage2_output,
    mock_stage3_output,
    mock_stage4_output,
    mock_stage5_output,
    mock_brand_context,
    mock_openrouter_client
):
    """Test that Stage 6 generates opportunity cards successfully."""
    stage6 = Stage6OpportunityCards()

    result = await stage6.execute(
        stage1_output=mock_stage1_output,
        stage2_output=mock_stage2_output,
        stage3_output=mock_stage3_output,
        stage4_output=mock_stage4_output,
        stage5_output=mock_stage5_output,
        brand_context=mock_brand_context,
        openrouter_client=mock_openrouter_client,
        source_report_name="Test Report"
    )

    assert result.total_cards == 1
    assert len(result.opportunity_cards) == 1
    assert result.markdown_format_validated is True


@pytest.mark.asyncio
async def test_stage6_card_has_all_required_sections(
    mock_stage1_output,
    mock_stage2_output,
    mock_stage3_output,
    mock_stage4_output,
    mock_stage5_output,
    mock_brand_context,
    mock_openrouter_client
):
    """Test that generated card has all required sections."""
    stage6 = Stage6OpportunityCards()

    result = await stage6.execute(
        stage1_output=mock_stage1_output,
        stage2_output=mock_stage2_output,
        stage3_output=mock_stage3_output,
        stage4_output=mock_stage4_output,
        stage5_output=mock_stage5_output,
        brand_context=mock_brand_context,
        openrouter_client=mock_openrouter_client,
        source_report_name="Test Report"
    )

    card = result.opportunity_cards[0]
    markdown = card.markdown_content

    # Check for required sections
    assert "# 💡" in markdown  # Concept Name
    assert "## 🎯 Consumer Insight" in markdown
    assert "## ⚙️ Mechanism" in markdown
    assert "## 📈 Why Now" in markdown
    assert "## 🏢 Why" in markdown  # Brand name varies
    assert "## 🔍 Competitive Landscape" in markdown
    assert "## ⚠️ Boundary Disclosure" in markdown


@pytest.mark.asyncio
async def test_stage6_card_includes_boundary_disclosure(
    mock_stage1_output,
    mock_stage2_output,
    mock_stage3_output,
    mock_stage4_output,
    mock_stage5_output,
    mock_brand_context,
    mock_openrouter_client
):
    """Test that boundary disclosure is included in every card."""
    stage6 = Stage6OpportunityCards()

    result = await stage6.execute(
        stage1_output=mock_stage1_output,
        stage2_output=mock_stage2_output,
        stage3_output=mock_stage3_output,
        stage4_output=mock_stage4_output,
        stage5_output=mock_stage5_output,
        brand_context=mock_brand_context,
        openrouter_client=mock_openrouter_client,
        source_report_name="Test Report"
    )

    card = result.opportunity_cards[0]

    # Check boundary disclosure section exists
    assert "boundary_disclosure" in card.card_sections
    assert len(card.card_sections["boundary_disclosure"]) > 50


def test_stage6_parse_card_sections():
    """Test parsing markdown card into structured sections."""
    stage6 = Stage6OpportunityCards()

    markdown = """# 💡 Test Concept

## 🎯 Consumer Insight
> "Test insight"

**Functional Need:** Test need

---

## ⚙️ Mechanism (SIT: Task Unification)
Test mechanism

---

## 📈 Why Now?
Test timing

---

## 🏢 Why TestBrand?
Test brand fit

---

## 🔍 Competitive Landscape
Test competitive

---

## ⚠️ Boundary Disclosure
This is a directional concept."""

    sections = stage6._parse_card_sections(markdown)

    assert "concept_name" in sections
    assert "consumer_insight" in sections
    assert "mechanism" in sections
    assert "why_now" in sections
    assert "why_brand" in sections
    assert "competitive_landscape" in sections
    assert "boundary_disclosure" in sections


def test_stage6_validate_markdown_structure_valid():
    """Test markdown structure validation with valid card."""
    stage6 = Stage6OpportunityCards()

    markdown = """# 💡 Test Concept
## 🎯 Consumer Insight
## ⚙️ Mechanism
## 📈 Why Now
## 🏢 Why TestBrand
## 🔍 Competitive Landscape
## ⚠️ Boundary Disclosure"""

    is_valid = stage6._validate_markdown_structure(markdown)

    assert is_valid is True


def test_stage6_validate_markdown_structure_missing_section():
    """Test markdown structure validation with missing section."""
    stage6 = Stage6OpportunityCards()

    markdown = """# 💡 Test Concept
## 🎯 Consumer Insight
## ⚙️ Mechanism
## 📈 Why Now"""

    is_valid = stage6._validate_markdown_structure(markdown)

    assert is_valid is False


def test_stage6_gather_concept_context(
    mock_stage1_output,
    mock_stage2_output,
    mock_stage3_output,
    mock_stage4_output,
    mock_stage5_output,
    mock_brand_context
):
    """Test gathering all context for a concept."""
    stage6 = Stage6OpportunityCards()

    concept = mock_stage4_output.concepts[0]

    context = stage6._gather_concept_context(
        concept=concept,
        stage1_output=mock_stage1_output,
        stage2_output=mock_stage2_output,
        stage3_output=mock_stage3_output,
        stage5_output=mock_stage5_output,
        brand_context=mock_brand_context
    )

    assert context["concept"] == concept
    assert context["insight"] is not None
    assert context["technique"] is not None
    assert len(context["trends"]) == 1
    assert context["competitive_intel"] is not None
    assert context["brand_context"] == mock_brand_context
