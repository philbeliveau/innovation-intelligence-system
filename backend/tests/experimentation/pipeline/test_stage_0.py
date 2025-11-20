"""Tests for Stage 0: Brand Enrichment"""
import pytest
from backend.experimentation.stages.stage_0_enrichment import Stage0Enrichment
from backend.experimentation.schemas import Stage0Output, BrandEnrichment


@pytest.fixture
def sample_brand_profile():
    """Sample brand profile for testing."""
    return {
        "brand_name": "Test Brand",
        "company_name": "Test Company",
        "industry": "Food & Beverage",
        "country": "Canada",
        "portfolio": ["Product A", "Product B", "Product C"],
        "positioning": "Premium quality products"
    }


@pytest.mark.asyncio
async def test_stage_0_basic_enrichment(sample_brand_profile):
    """Test basic enrichment without external search."""
    stage0 = Stage0Enrichment(enrichment_mode="basic")

    result = await stage0.run_basic(sample_brand_profile)

    # Validate output type
    assert isinstance(result, Stage0Output)
    assert result.enrichment_method == "basic"

    # Validate brand context
    assert result.brand_context.brand_name == "Test Brand"
    assert result.brand_context.industry == "Food & Beverage"
    assert result.brand_context.country == "Canada"
    assert len(result.brand_context.product_portfolio) == 3
    assert result.brand_context.positioning == "Premium quality products"
    assert result.brand_context.confidence_score == 1.0  # High confidence for basic


@pytest.mark.asyncio
async def test_stage_0_handles_missing_fields():
    """Test that Stage 0 handles missing optional fields gracefully."""
    minimal_profile = {
        "brand_name": "Minimal Brand",
        "industry": "Test Industry",
        "country": "USA",
        "portfolio": ["Product 1"]
    }

    stage0 = Stage0Enrichment(enrichment_mode="basic")
    result = await stage0.run_basic(minimal_profile)

    # Should complete without positioning
    assert result.brand_context.brand_name == "Minimal Brand"
    assert result.brand_context.positioning is None


@pytest.mark.asyncio
async def test_stage_0_fallback_field_names():
    """Test that Stage 0 handles different field naming conventions."""
    profile_with_alt_names = {
        "company_name": "Alt Name Brand",  # Alternative to brand_name
        "industry": "Retail",
        "country": "UK",
        "product_portfolio": ["Item 1", "Item 2"]  # Alternative to portfolio
    }

    stage0 = Stage0Enrichment(enrichment_mode="basic")
    result = await stage0.run_basic(profile_with_alt_names)

    assert result.brand_context.brand_name == "Alt Name Brand"
    assert len(result.brand_context.product_portfolio) == 2


def test_stage_0_schema_validation():
    """Test that BrandEnrichment schema validates correctly."""
    valid_data = {
        "brand_name": "Valid Brand",
        "industry": "Tech",
        "country": "USA",
        "product_portfolio": ["Product A"],
        "confidence_score": 0.95
    }

    enrichment = BrandEnrichment(**valid_data)
    assert enrichment.brand_name == "Valid Brand"
    assert enrichment.confidence_score == 0.95


def test_stage_0_schema_rejects_invalid_confidence():
    """Test that confidence_score must be between 0.0 and 1.0."""
    with pytest.raises(ValueError):
        BrandEnrichment(
            brand_name="Test",
            industry="Test",
            country="Test",
            product_portfolio=[],
            confidence_score=1.5  # Invalid - exceeds 1.0
        )
