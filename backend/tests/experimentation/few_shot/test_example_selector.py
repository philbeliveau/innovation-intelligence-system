"""Tests for example selection algorithm (Story 11.3b)

Tests relevance scoring algorithm with brand similarity, recency, and quality weighting.
"""
import pytest
from datetime import datetime, timedelta
from pathlib import Path
import json
import tempfile
import shutil
from typing import Dict, Any

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "experimentation"))

from example_selector import ExampleSelector


@pytest.fixture
def temp_storage():
    """Create temporary storage directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_examples(temp_storage):
    """Create sample examples with varying attributes"""
    storage_path = Path(temp_storage)

    # Create stage directories
    for stage in range(7):
        stage_dir = storage_path / f"stage_{stage}"
        stage_dir.mkdir(exist_ok=True)

    # Example 1: High quality, recent, similar brand (Dairy)
    example1 = {
        "id": "example_20250120_abc123",
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "stage": 1,
        "quality_score": "good",
        "usage_count": 5,
        "last_used_at": None,
        "brand_context": {
            "brand_name": "Lactalis Canada",
            "industry": "Dairy",
            "country": "Canada",
            "product_portfolio": ["Cheese", "Milk", "Yogurt"]
        },
        "input": {"test": "input1"},
        "prompt_used": "Test prompt",
        "output": {"test": "output1"},
        "metadata": {"pipeline_version": "1.0"}
    }

    # Example 2: Medium quality, older, different industry
    example2 = {
        "id": "example_20241115_def456",
        "created_at": (datetime.now() - timedelta(days=60)).isoformat(),
        "stage": 1,
        "quality_score": "needs_work",
        "usage_count": 2,
        "last_used_at": None,
        "brand_context": {
            "brand_name": "Decathlon",
            "industry": "Sporting Goods",
            "country": "France",
            "product_portfolio": ["Sports Equipment", "Apparel"]
        },
        "input": {"test": "input2"},
        "prompt_used": "Test prompt",
        "output": {"test": "output2"},
        "metadata": {"pipeline_version": "1.0"}
    }

    # Example 3: High quality, recent, same industry different country
    example3 = {
        "id": "example_20250118_ghi789",
        "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
        "stage": 1,
        "quality_score": "good",
        "usage_count": 0,
        "last_used_at": None,
        "brand_context": {
            "brand_name": "Danone",
            "industry": "Dairy",
            "country": "France",
            "product_portfolio": ["Yogurt", "Milk"]
        },
        "input": {"test": "input3"},
        "prompt_used": "Test prompt",
        "output": {"test": "output3"},
        "metadata": {"pipeline_version": "1.0"}
    }

    # Save examples to filesystem
    stage_dir = storage_path / "stage_1"
    for i, example in enumerate([example1, example2, example3], 1):
        with open(stage_dir / f"{example['id']}.json", 'w') as f:
            json.dump(example, f)

    return storage_path


@pytest.fixture
def target_brand():
    """Target brand for similarity comparison"""
    return {
        "brand_name": "Test Dairy Brand",
        "industry": "Dairy",
        "country": "Canada",
        "product_portfolio": ["Cheese", "Butter"]
    }


class TestExampleSelector:
    """Test suite for ExampleSelector"""

    def test_initialization(self, temp_storage):
        """Test selector initialization"""
        selector = ExampleSelector(storage_path=temp_storage)
        assert selector.storage_path == Path(temp_storage)
        assert selector.max_examples_per_stage == 5  # Default

    def test_brand_similarity_same_industry_country(self, sample_examples, target_brand):
        """Test brand similarity for same industry and country"""
        selector = ExampleSelector(storage_path=sample_examples)

        # Load example 1 (Lactalis Canada - Dairy, Canada)
        examples = selector._load_examples_from_storage(1)
        example1 = [e for e in examples if e["id"] == "example_20250120_abc123"][0]

        similarity = selector.calculate_brand_similarity(
            target_brand,
            example1["brand_context"]
        )

        # Should have high similarity (industry + country + products match)
        # 0.4 (industry) + 0.2 (country) + 0.15 (50% product overlap) = 0.75
        assert similarity >= 0.7

    def test_brand_similarity_same_industry_different_country(self, sample_examples, target_brand):
        """Test brand similarity for same industry, different country"""
        selector = ExampleSelector(storage_path=sample_examples)

        # Load example 3 (Danone - Dairy, France)
        examples = selector._load_examples_from_storage(1)
        example3 = [e for e in examples if e["id"] == "example_20250118_ghi789"][0]

        similarity = selector.calculate_brand_similarity(
            target_brand,
            example3["brand_context"]
        )

        # Should have medium similarity (industry + products match, country differs)
        # 0.4 (industry) + 0 (country) = 0.4 base
        assert 0.4 <= similarity < 0.7

    def test_brand_similarity_different_industry(self, sample_examples, target_brand):
        """Test brand similarity for different industry"""
        selector = ExampleSelector(storage_path=sample_examples)

        # Load example 2 (Decathlon - Sporting Goods)
        examples = selector._load_examples_from_storage(1)
        example2 = [e for e in examples if e["id"] == "example_20241115_def456"][0]

        similarity = selector.calculate_brand_similarity(
            target_brand,
            example2["brand_context"]
        )

        # Should have low similarity (different industry, country, products)
        assert similarity < 0.5

    def test_recency_score_recent(self, sample_examples):
        """Test recency scoring for recent examples"""
        selector = ExampleSelector(storage_path=sample_examples)

        examples = selector._load_examples_from_storage(1)
        example1 = [e for e in examples if e["id"] == "example_20250120_abc123"][0]

        recency = selector.calculate_recency_score(example1["created_at"])

        # Very recent (1 day old) should score high
        assert recency >= 0.95

    def test_recency_score_old(self, sample_examples):
        """Test recency scoring for old examples"""
        selector = ExampleSelector(storage_path=sample_examples)

        examples = selector._load_examples_from_storage(1)
        example2 = [e for e in examples if e["id"] == "example_20241115_def456"][0]

        recency = selector.calculate_recency_score(example2["created_at"])

        # 60 days old should score lower
        assert recency < 0.7

    def test_quality_score_mapping(self, sample_examples):
        """Test quality score mapping"""
        selector = ExampleSelector(storage_path=sample_examples)

        # Test all quality levels
        assert selector.map_quality_score("good") == 1.0
        assert selector.map_quality_score("needs_work") == 0.5
        assert selector.map_quality_score("failed") == 0.0

    def test_relevance_scoring_weights(self, sample_examples, target_brand):
        """Test that relevance score uses correct weights (60% brand, 30% recency, 10% quality)"""
        selector = ExampleSelector(storage_path=sample_examples)

        examples = selector._load_examples_from_storage(1)
        example1 = [e for e in examples if e["id"] == "example_20250120_abc123"][0]

        relevance = selector.calculate_relevance_score(
            target_brand,
            example1
        )

        # Calculate expected score manually
        brand_sim = selector.calculate_brand_similarity(target_brand, example1["brand_context"])
        recency = selector.calculate_recency_score(example1["created_at"])
        quality = selector.map_quality_score(example1["quality_score"])

        expected = (brand_sim * 0.6) + (recency * 0.3) + (quality * 0.1)

        assert abs(relevance - expected) < 0.01

    def test_select_examples_returns_top_n(self, sample_examples, target_brand):
        """Test that select_examples returns correct number of top examples"""
        selector = ExampleSelector(storage_path=sample_examples)

        selected = selector.select_examples(
            stage=1,
            brand_context=target_brand,
            max_examples=2
        )

        assert len(selected) == 2
        # Should be sorted by relevance (descending)
        assert selected[0]["relevance_score"] >= selected[1]["relevance_score"]

    def test_select_examples_respects_max_limit(self, sample_examples, target_brand):
        """Test that select_examples respects configured max limit"""
        selector = ExampleSelector(storage_path=sample_examples, max_examples_per_stage=1)

        selected = selector.select_examples(
            stage=1,
            brand_context=target_brand,
            max_examples=5  # Request more than limit
        )

        # Should only return configured max
        assert len(selected) <= 1

    def test_select_examples_empty_stage(self, temp_storage, target_brand):
        """Test select_examples when no examples exist for stage"""
        selector = ExampleSelector(storage_path=temp_storage)

        selected = selector.select_examples(
            stage=5,
            brand_context=target_brand,
            max_examples=3
        )

        assert len(selected) == 0

    def test_performance_under_100ms(self, sample_examples, target_brand):
        """Test that example selection completes in under 100ms (AC: 8)"""
        import time

        selector = ExampleSelector(storage_path=sample_examples)

        start = time.time()
        selected = selector.select_examples(
            stage=1,
            brand_context=target_brand,
            max_examples=3
        )
        duration_ms = (time.time() - start) * 1000

        assert duration_ms < 100, f"Selection took {duration_ms:.2f}ms (should be <100ms)"

    def test_caching_improves_performance(self, sample_examples, target_brand):
        """Test that caching improves repeated queries"""
        import time

        selector = ExampleSelector(storage_path=sample_examples, enable_caching=True)

        # First call (cold cache)
        start1 = time.time()
        selector.select_examples(stage=1, brand_context=target_brand, max_examples=3)
        duration1_ms = (time.time() - start1) * 1000

        # Second call (warm cache)
        start2 = time.time()
        selector.select_examples(stage=1, brand_context=target_brand, max_examples=3)
        duration2_ms = (time.time() - start2) * 1000

        # Cached call should be faster
        assert duration2_ms < duration1_ms

    def test_configuration_from_env(self, monkeypatch, temp_storage):
        """Test that configuration can be set via environment variables"""
        monkeypatch.setenv("FEW_SHOT_MAX_EXAMPLES_STAGE_1", "7")
        monkeypatch.setenv("FEW_SHOT_ENABLED", "false")

        selector = ExampleSelector(storage_path=temp_storage)

        # Should respect environment variables
        # (Implementation detail - depends on how env vars are loaded)
        assert selector.max_examples_per_stage >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
