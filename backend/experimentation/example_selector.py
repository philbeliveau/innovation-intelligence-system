"""Example Selection Algorithm for Few-Shot Learning (Story 11.3b)

Implements intelligent example selection based on:
- Brand similarity (60% weight)
- Recency (30% weight)
- Quality score (10% weight)

Performance target: <100ms per selection
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import os
from functools import lru_cache


class ExampleSelector:
    """
    Selects most relevant few-shot examples for pipeline stages
    based on weighted relevance scoring.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        max_examples_per_stage: int = 5,
        enable_caching: bool = True
    ):
        """
        Initialize example selector

        Args:
            storage_path: Path to successful_examples directory
            max_examples_per_stage: Maximum examples to return (default 5)
            enable_caching: Enable LRU caching for performance (default True)
        """
        if storage_path is None:
            # Default to successful_examples directory
            self.storage_path = Path(__file__).parent / "successful_examples"
        else:
            self.storage_path = Path(storage_path)

        self.max_examples_per_stage = max_examples_per_stage
        self.enable_caching = enable_caching

        # Relevance scoring weights (Story 11.3b AC: 2)
        self.BRAND_SIMILARITY_WEIGHT = 0.6
        self.RECENCY_WEIGHT = 0.3
        self.QUALITY_WEIGHT = 0.1

        # Recency decay parameters
        self.RECENCY_DECAY_DAYS = 90  # Examples decay to 0 after 90 days

        # Quality score mapping
        self.QUALITY_SCORES = {
            "good": 1.0,
            "needs_work": 0.5,
            "failed": 0.0
        }

    def select_examples(
        self,
        stage: int,
        brand_context: Dict[str, Any],
        max_examples: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Select most relevant examples for a stage

        Args:
            stage: Pipeline stage (0-6)
            brand_context: Target brand context for similarity
            max_examples: Override default max examples

        Returns:
            List of selected examples with relevance scores (sorted descending)
        """
        # Use the LOWER of max_examples or configured limit
        if max_examples is None:
            limit = self.max_examples_per_stage
        else:
            limit = min(max_examples, self.max_examples_per_stage)

        # Load examples from storage
        examples = self._load_examples_from_storage(stage)

        if not examples:
            return []

        # Calculate relevance scores
        scored_examples = []
        for example in examples:
            relevance = self.calculate_relevance_score(brand_context, example)
            scored_examples.append({
                **example,
                "relevance_score": relevance
            })

        # Sort by relevance (descending)
        scored_examples.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Return top N
        return scored_examples[:limit]

    def calculate_relevance_score(
        self,
        target_brand: Dict[str, Any],
        example: Dict[str, Any]
    ) -> float:
        """
        Calculate weighted relevance score

        Formula: relevance = (brand_sim * 0.6) + (recency * 0.3) + (quality * 0.1)

        Args:
            target_brand: Target brand context
            example: Example to score

        Returns:
            Relevance score (0.0-1.0)
        """
        brand_sim = self.calculate_brand_similarity(
            target_brand,
            example.get("brand_context", {})
        )

        recency = self.calculate_recency_score(
            example.get("created_at")
        )

        quality = self.map_quality_score(
            example.get("quality_score", "needs_work")
        )

        relevance = (
            brand_sim * self.BRAND_SIMILARITY_WEIGHT +
            recency * self.RECENCY_WEIGHT +
            quality * self.QUALITY_WEIGHT
        )

        return min(1.0, max(0.0, relevance))

    def calculate_brand_similarity(
        self,
        target_brand: Dict[str, Any],
        example_brand: Dict[str, Any]
    ) -> float:
        """
        Calculate brand similarity score (0.0-1.0)

        Considers:
        - Industry match (40%)
        - Geography/country match (20%)
        - Product portfolio overlap (30%)
        - Brand size/positioning similarity (10%)

        Args:
            target_brand: Target brand context
            example_brand: Example's brand context

        Returns:
            Similarity score (0.0-1.0)
        """
        if not example_brand:
            return 0.0

        score = 0.0

        # Industry match (40%)
        target_industry = target_brand.get("industry", "").lower()
        example_industry = example_brand.get("industry", "").lower()
        if target_industry == example_industry:
            score += 0.4

        # Country/geography match (20%)
        target_country = target_brand.get("country", "").lower()
        example_country = example_brand.get("country", "").lower()
        if target_country == example_country:
            score += 0.2

        # Product portfolio overlap (30%)
        target_products = set([p.lower() for p in target_brand.get("product_portfolio", [])])
        example_products = set([p.lower() for p in example_brand.get("product_portfolio", [])])

        if target_products and example_products:
            overlap = len(target_products & example_products)
            # Use intersection over smaller set for better overlap credit
            smaller_set_size = min(len(target_products), len(example_products))
            if smaller_set_size > 0:
                overlap_ratio = overlap / smaller_set_size
                score += 0.3 * overlap_ratio

        # Brand positioning similarity (10%)
        # Simple heuristic: check if positioning keywords overlap
        target_positioning = target_brand.get("positioning", "").lower()
        example_positioning = example_brand.get("positioning", "").lower()

        if target_positioning and example_positioning:
            target_keywords = set(target_positioning.split())
            example_keywords = set(example_positioning.split())
            if target_keywords & example_keywords:
                score += 0.1

        return min(1.0, score)

    def calculate_recency_score(self, created_at: Optional[str]) -> float:
        """
        Calculate recency score with linear decay

        Examples decay linearly over 90 days:
        - 0 days old: 1.0
        - 45 days old: 0.5
        - 90 days old: 0.0

        Args:
            created_at: ISO 8601 timestamp

        Returns:
            Recency score (0.0-1.0)
        """
        if not created_at:
            return 0.5  # Default to medium recency if unknown

        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age_days = (datetime.now() - created).days

            if age_days < 0:
                return 1.0  # Future timestamp (shouldn't happen)

            if age_days >= self.RECENCY_DECAY_DAYS:
                return 0.0

            # Linear decay
            recency = 1.0 - (age_days / self.RECENCY_DECAY_DAYS)
            return max(0.0, min(1.0, recency))

        except (ValueError, AttributeError):
            return 0.5  # Default if parsing fails

    def map_quality_score(self, quality_tag: str) -> float:
        """
        Map quality tag to numeric score

        Args:
            quality_tag: "good", "needs_work", or "failed"

        Returns:
            Quality score (0.0-1.0)
        """
        return self.QUALITY_SCORES.get(quality_tag.lower(), 0.5)

    def _load_examples_from_storage(self, stage: int) -> List[Dict[str, Any]]:
        """
        Load all examples for a stage from filesystem

        Args:
            stage: Pipeline stage (0-6)

        Returns:
            List of example dictionaries
        """
        stage_dir = self.storage_path / f"stage_{stage}"

        if not stage_dir.exists():
            return []

        examples = []
        for example_file in stage_dir.glob("example_*.json"):
            try:
                with open(example_file, 'r') as f:
                    example = json.load(f)
                    examples.append(example)
            except Exception as e:
                print(f"Warning: Failed to load {example_file}: {e}")
                continue

        return examples

    @lru_cache(maxsize=128)
    def _cached_load_examples(self, stage: int) -> tuple:
        """
        Cached version of _load_examples_from_storage for performance

        Args:
            stage: Pipeline stage

        Returns:
            Tuple of examples (for hashability)
        """
        if not self.enable_caching:
            return tuple()

        examples = self._load_examples_from_storage(stage)
        # Convert to tuple for caching
        return tuple(json.dumps(e, sort_keys=True) for e in examples)


# Helper function for integration
def select_relevant_examples(
    stage: int,
    brand_context: Dict[str, Any],
    max_examples: int = 3,
    storage_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function for selecting relevant examples

    Args:
        stage: Pipeline stage (0-6)
        brand_context: Brand context for similarity matching
        max_examples: Maximum examples to return (default 3)
        storage_path: Optional custom storage path

    Returns:
        List of selected examples with relevance scores
    """
    selector = ExampleSelector(storage_path=storage_path)
    return selector.select_examples(stage, brand_context, max_examples)


if __name__ == "__main__":
    # Test the selector
    import sys
    from pathlib import Path

    # Test with sample brand
    test_brand = {
        "brand_name": "Test Dairy Co",
        "industry": "Dairy",
        "country": "Canada",
        "product_portfolio": ["Cheese", "Milk", "Yogurt"]
    }

    selector = ExampleSelector()

    print("Testing Example Selector")
    print("=" * 50)

    for stage in range(7):
        print(f"\nStage {stage}:")
        selected = selector.select_examples(
            stage=stage,
            brand_context=test_brand,
            max_examples=3
        )

        if selected:
            print(f"  Found {len(selected)} examples")
            for i, ex in enumerate(selected, 1):
                print(f"  {i}. {ex['id']} (relevance: {ex['relevance_score']:.3f})")
                print(f"     Brand: {ex['brand_context'].get('brand_name')}")
                print(f"     Quality: {ex.get('quality_score')}")
                print(f"     Created: {ex.get('created_at')[:10]}")
        else:
            print("  No examples found")
