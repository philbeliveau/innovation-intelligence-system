"""
Trend Filtering and Prioritization System
Filter and prioritize trends before processing through the pipeline
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class LifecycleStage(Enum):
    """Trend lifecycle stages"""
    EMERGING = "EMERGING"
    ACCELERATING = "ACCELERATING"
    PEAKING = "PEAKING"
    DECLINING = "DECLINING"  # Sometimes mentioned
    UNKNOWN = "UNKNOWN"


@dataclass
class TrendScore:
    """Container for trend scoring results"""
    trend_name: str
    total_score: float
    component_scores: Dict[str, float]
    relevance_reasons: List[str]
    recommendation: str  # PROCESS, MAYBE, SKIP
    priority_rank: int


class TrendFilter:
    """
    Filters and prioritizes trends based on multiple criteria.
    Helps focus pipeline on most relevant trends for brand/category.
    """

    def __init__(self, filter_config: Optional[Dict] = None):
        """Initialize with filtering configuration"""

        self.config = filter_config or {
            "lifecycle_preference": ["EMERGING", "ACCELERATING"],
            "min_relevance_score": 0.6,
            "max_trends_to_process": 5,
            "required_emotions": [],
            "excluded_emotions": [],
            "brand_fit_keywords": [],
            "category_keywords": []
        }

    def filter_trends(
        self,
        trends: List[Dict],
        brand_context: Dict,
        strategy: str = "balanced"
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter trends into process and skip lists

        Args:
            trends: List of trend objects from Stage 1
            brand_context: Brand profile information
            strategy: "aggressive" (few trends), "balanced", or "inclusive" (many trends)

        Returns:
            Tuple of (trends_to_process, trends_to_skip)
        """

        # Score all trends
        scored_trends = []
        for trend in trends:
            score = self.score_trend(trend, brand_context)
            scored_trends.append((trend, score))

        # Sort by score
        scored_trends.sort(key=lambda x: x[1].total_score, reverse=True)

        # Apply strategy
        if strategy == "aggressive":
            threshold = 0.8
            max_trends = 3
        elif strategy == "inclusive":
            threshold = 0.4
            max_trends = 7
        else:  # balanced
            threshold = self.config["min_relevance_score"]
            max_trends = self.config["max_trends_to_process"]

        # Split into process and skip
        trends_to_process = []
        trends_to_skip = []

        for i, (trend, score) in enumerate(scored_trends):
            if score.total_score >= threshold and len(trends_to_process) < max_trends:
                trend["relevance_score"] = score.total_score
                trend["relevance_reasons"] = score.relevance_reasons
                trend["priority_rank"] = i + 1
                trends_to_process.append(trend)
            else:
                trend["skip_reason"] = score.recommendation
                trends_to_skip.append(trend)

        return trends_to_process, trends_to_skip

    def score_trend(self, trend: Dict, brand_context: Dict) -> TrendScore:
        """
        Score a single trend for relevance to brand

        Scoring components:
        1. Lifecycle fit (0-1)
        2. Emotional relevance (0-1)
        3. Brand keyword match (0-1)
        4. Abstraction quality (0-1)
        5. Industry fit (0-1)
        """

        scores = {}
        reasons = []

        # 1. Lifecycle Stage Scoring
        lifecycle = trend.get("lifecycle_stage", "UNKNOWN")
        if lifecycle in self.config["lifecycle_preference"]:
            scores["lifecycle"] = 1.0
            reasons.append(f"{lifecycle} stage aligns with strategy")
        elif lifecycle == "PEAKING":
            scores["lifecycle"] = 0.3
            reasons.append("PEAKING - may be too late to capitalize")
        elif lifecycle == "EMERGING":
            scores["lifecycle"] = 0.7
            reasons.append("EMERGING - early but risky")
        else:
            scores["lifecycle"] = 0.5

        # 2. Emotional Driver Relevance
        emotional_score = self.score_emotional_relevance(trend)
        scores["emotional"] = emotional_score
        if emotional_score > 0.7:
            reasons.append("Strong emotional alignment")

        # 3. Brand/Category Keyword Match
        keyword_score = self.score_keyword_match(trend, brand_context)
        scores["keywords"] = keyword_score
        if keyword_score > 0.5:
            reasons.append("Keywords match brand/category")

        # 4. Abstraction Level Quality
        abstraction_score = self.score_abstraction_levels(trend, brand_context)
        scores["abstraction"] = abstraction_score
        if abstraction_score > 0.7:
            reasons.append("Clear L1-L4 progression relevant to brand")

        # 5. Industry Fit
        industry_score = self.score_industry_fit(trend, brand_context)
        scores["industry"] = industry_score
        if industry_score > 0.6:
            reasons.append(f"Applicable to {brand_context.get('industry', 'industry')}")

        # Calculate total score (weighted average)
        weights = {
            "lifecycle": 0.25,
            "emotional": 0.20,
            "keywords": 0.15,
            "abstraction": 0.25,
            "industry": 0.15
        }

        total_score = sum(scores[k] * weights[k] for k in weights.keys())

        # Determine recommendation
        if total_score >= 0.8:
            recommendation = "PROCESS - High relevance"
        elif total_score >= 0.6:
            recommendation = "PROCESS - Good fit"
        elif total_score >= 0.4:
            recommendation = "MAYBE - Consider if capacity"
        else:
            recommendation = "SKIP - Low relevance"

        return TrendScore(
            trend_name=trend.get("trend_name", "Unknown"),
            total_score=total_score,
            component_scores=scores,
            relevance_reasons=reasons,
            recommendation=recommendation,
            priority_rank=0  # Set later
        )

    def score_emotional_relevance(self, trend: Dict) -> float:
        """Score emotional driver relevance"""

        drivers = trend.get("emotional_drivers", {})
        current_negative = drivers.get("current_negative", [])
        aspirational_positive = drivers.get("aspirational_positive", [])

        score = 0.5  # Base score

        # Check required emotions
        if self.config["required_emotions"]:
            matches = sum(
                1 for emotion in self.config["required_emotions"]
                if emotion in current_negative or emotion in aspirational_positive
            )
            score = matches / len(self.config["required_emotions"])

        # Penalize excluded emotions
        if self.config["excluded_emotions"]:
            excluded_found = any(
                emotion in current_negative or emotion in aspirational_positive
                for emotion in self.config["excluded_emotions"]
            )
            if excluded_found:
                score *= 0.3

        # Bonus for rich emotional landscape
        total_emotions = len(current_negative) + len(aspirational_positive)
        if total_emotions >= 6:
            score = min(score * 1.2, 1.0)

        return score

    def score_keyword_match(self, trend: Dict, brand_context: Dict) -> float:
        """Score keyword matches in trend content"""

        # Combine all trend text
        trend_text = json.dumps(trend).lower()

        # Brand keywords
        brand_keywords = self.config.get("brand_fit_keywords", [])
        brand_keywords.extend([
            brand_context.get("name", "").lower(),
            brand_context.get("industry", "").lower()
        ])

        # Category keywords
        category_keywords = self.config.get("category_keywords", [])

        all_keywords = brand_keywords + category_keywords
        all_keywords = [k for k in all_keywords if k]  # Remove empty

        if not all_keywords:
            return 0.5  # Neutral if no keywords

        # Count matches
        matches = sum(1 for keyword in all_keywords if keyword in trend_text)
        score = min(matches / max(len(all_keywords), 1), 1.0)

        return score

    def score_abstraction_levels(self, trend: Dict, brand_context: Dict) -> float:
        """Score quality and relevance of L1-L4 abstractions"""

        levels = trend.get("abstraction_levels", {})

        if not levels:
            return 0.0

        score = 0.0

        # Check L1 is specific and actionable
        L1 = levels.get("L1", "")
        if L1:
            # Look for CPG/product specific terms
            cpg_terms = ["product", "package", "SKU", "brand", "retail", "shelf"]
            if any(term in L1.lower() for term in cpg_terms):
                score += 0.3

        # Check L4 is truly universal
        L4 = levels.get("L4", "")
        if L4:
            universal_terms = ["human", "universal", "fundamental", "principle", "need"]
            if any(term in L4.lower() for term in universal_terms):
                score += 0.3

        # Check progression exists
        if all(f"L{i}" in levels for i in range(1, 5)):
            score += 0.2

        # Check relevance to industry
        industry = brand_context.get("industry", "").lower()
        if industry and industry in json.dumps(levels).lower():
            score += 0.2

        return min(score, 1.0)

    def score_industry_fit(self, trend: Dict, brand_context: Dict) -> float:
        """Score how well trend fits the brand's industry"""

        industry = brand_context.get("industry", "").lower()

        # Industry-specific scoring rules
        industry_rules = {
            "bakery": ["food", "bread", "fresh", "artisan", "craft"],
            "dairy": ["milk", "cheese", "yogurt", "nutrition", "protein"],
            "snacks": ["convenient", "portable", "indulgence", "treat"],
            "beverages": ["drink", "hydration", "refresh", "energy"],
            "meat": ["protein", "meal", "cooking", "preparation"]
        }

        # Get relevant keywords for industry
        relevant_keywords = []
        for key, keywords in industry_rules.items():
            if key in industry:
                relevant_keywords.extend(keywords)
                break

        if not relevant_keywords:
            return 0.5  # Neutral if no specific rules

        # Check trend content
        trend_text = json.dumps(trend).lower()
        matches = sum(1 for keyword in relevant_keywords if keyword in trend_text)

        score = min(matches / max(len(relevant_keywords), 1) * 2, 1.0)

        return score

    def prioritize_trend_combinations(
        self,
        trends: List[Dict]
    ) -> List[Tuple[Dict, Dict, float]]:
        """
        Prioritize trend pairs for Stage 2 convergence

        Returns list of (trend1, trend2, combination_score)
        """

        combinations = []

        for i, trend_a in enumerate(trends):
            for trend_b in trends[i + 1:]:
                combo_score = self.score_combination(trend_a, trend_b)
                combinations.append((trend_a, trend_b, combo_score))

        # Sort by combination score
        combinations.sort(key=lambda x: x[2], reverse=True)

        return combinations

    def score_combination(self, trend_a: Dict, trend_b: Dict) -> float:
        """Score how well two trends work together"""

        score = 0.0

        # 1. Complementary lifecycle stages
        lifecycle_a = trend_a.get("lifecycle_stage")
        lifecycle_b = trend_b.get("lifecycle_stage")

        if lifecycle_a == "EMERGING" and lifecycle_b == "ACCELERATING":
            score += 0.3  # Good hedge
        elif lifecycle_a == "ACCELERATING" and lifecycle_b == "ACCELERATING":
            score += 0.25  # Validated
        elif lifecycle_a == lifecycle_b:
            score += 0.1  # Same stage
        else:
            score += 0.05

        # 2. Emotional overlap
        emotions_a = set(
            trend_a.get("emotional_drivers", {}).get("current_negative", []) +
            trend_a.get("emotional_drivers", {}).get("aspirational_positive", [])
        )
        emotions_b = set(
            trend_b.get("emotional_drivers", {}).get("current_negative", []) +
            trend_b.get("emotional_drivers", {}).get("aspirational_positive", [])
        )

        overlap = len(emotions_a & emotions_b)
        if overlap > 0:
            score += min(overlap * 0.1, 0.3)

        # 3. Different abstraction strengths
        # Good if trends offer different L1-L4 strengths
        if trend_a.get("abstraction_levels", {}).get("L1") and \
           trend_b.get("abstraction_levels", {}).get("L3"):
            score += 0.2  # Complementary abstractions

        # 4. Name dissimilarity (avoid redundant trends)
        name_a = trend_a.get("trend_name", "").lower()
        name_b = trend_b.get("trend_name", "").lower()

        if name_a and name_b and not any(word in name_b for word in name_a.split()):
            score += 0.2  # Different concepts

        return min(score, 1.0)

    def create_filter_report(
        self,
        all_trends: List[Dict],
        processed: List[Dict],
        skipped: List[Dict]
    ) -> str:
        """Create a report explaining filtering decisions"""

        report = "=" * 50 + "\n"
        report += "TREND FILTERING REPORT\n"
        report += "=" * 50 + "\n\n"

        report += f"Total Trends Found: {len(all_trends)}\n"
        report += f"Trends to Process: {len(processed)}\n"
        report += f"Trends Skipped: {len(skipped)}\n\n"

        report += "TRENDS TO PROCESS:\n"
        report += "-" * 30 + "\n"
        for trend in processed:
            report += f"\n✅ {trend.get('trend_name')} (Priority #{trend.get('priority_rank', 'N/A')})\n"
            report += f"   Relevance Score: {trend.get('relevance_score', 0):.2f}\n"
            report += f"   Lifecycle: {trend.get('lifecycle_stage')}\n"
            reasons = trend.get('relevance_reasons', [])
            if reasons:
                report += f"   Reasons: {', '.join(reasons[:2])}\n"

        if skipped:
            report += "\n\nTRENDS SKIPPED:\n"
            report += "-" * 30 + "\n"
            for trend in skipped:
                report += f"\n❌ {trend.get('trend_name')}\n"
                report += f"   Reason: {trend.get('skip_reason', 'Below threshold')}\n"

        report += "\n" + "=" * 50 + "\n"

        return report


# Configuration presets for different strategies
FILTER_PRESETS = {
    "early_innovation": {
        "lifecycle_preference": ["EMERGING"],
        "min_relevance_score": 0.7,
        "max_trends_to_process": 3,
        "required_emotions": [],
        "excluded_emotions": ["anxious", "fearful"],
    },
    "validated_trends": {
        "lifecycle_preference": ["ACCELERATING"],
        "min_relevance_score": 0.6,
        "max_trends_to_process": 5,
        "required_emotions": [],
        "excluded_emotions": [],
    },
    "broad_exploration": {
        "lifecycle_preference": ["EMERGING", "ACCELERATING", "PEAKING"],
        "min_relevance_score": 0.4,
        "max_trends_to_process": 7,
        "required_emotions": [],
        "excluded_emotions": [],
    },
    "emotional_focus": {
        "lifecycle_preference": ["EMERGING", "ACCELERATING"],
        "min_relevance_score": 0.5,
        "max_trends_to_process": 4,
        "required_emotions": ["joy", "carefree", "confident"],
        "excluded_emotions": ["stressed", "overwhelmed"],
    }
}


# Helper functions for integration
def filter_trends_for_pipeline(
    trends: List[Dict],
    brand_context: Dict,
    preset: str = "balanced",
    custom_config: Dict = None
) -> Tuple[List[Dict], str]:
    """
    Filter trends and return processed list with report

    Args:
        trends: Raw trends from Stage 1
        brand_context: Brand profile
        preset: One of the FILTER_PRESETS keys or "custom"
        custom_config: Custom configuration if preset="custom"
    """

    # Get configuration
    if preset == "custom" and custom_config:
        config = custom_config
    elif preset in FILTER_PRESETS:
        config = FILTER_PRESETS[preset]
    else:
        config = None  # Use defaults

    # Create filter
    filter_system = TrendFilter(config)

    # Filter trends
    to_process, to_skip = filter_system.filter_trends(
        trends,
        brand_context,
        strategy="balanced"
    )

    # Create report
    report = filter_system.create_filter_report(trends, to_process, to_skip)

    return to_process, report


def get_best_trend_pairs(
    trends: List[Dict],
    n_pairs: int = 5
) -> List[Tuple[Dict, Dict]]:
    """Get the best trend pairs for convergence"""

    filter_system = TrendFilter()
    combinations = filter_system.prioritize_trend_combinations(trends)

    # Return top N pairs
    return [(a, b) for a, b, score in combinations[:n_pairs]]


if __name__ == "__main__":
    # Test filtering
    test_trends = [
        {
            "trend_name": "Strategic Joy",
            "lifecycle_stage": "EMERGING",
            "emotional_drivers": {
                "current_negative": ["stressed"],
                "aspirational_positive": ["joyful", "carefree"]
            },
            "abstraction_levels": {
                "L1": "CPG products with gamification",
                "L4": "Joy as universal human need"
            }
        },
        {
            "trend_name": "Witherwill",
            "lifecycle_stage": "ACCELERATING",
            "emotional_drivers": {
                "current_negative": ["overwhelmed"],
                "aspirational_positive": ["simple", "grounded"]
            },
            "abstraction_levels": {
                "L1": "Minimalist product lines",
                "L4": "Simplicity as luxury"
            }
        },
        {
            "trend_name": "Digital Fatigue",
            "lifecycle_stage": "PEAKING",
            "emotional_drivers": {
                "current_negative": ["exhausted", "disconnected"],
                "aspirational_positive": ["present", "authentic"]
            }
        }
    ]

    test_brand = {
        "name": "TestBrand",
        "industry": "Bakery"
    }

    # Test filtering
    filter_system = TrendFilter(FILTER_PRESETS["early_innovation"])
    processed, skipped = filter_system.filter_trends(test_trends, test_brand)

    print(f"Processing {len(processed)} trends:")
    for trend in processed:
        print(f"  - {trend['trend_name']}: {trend.get('relevance_score', 0):.2f}")

    print(f"\nSkipping {len(skipped)} trends")

    # Test combination scoring
    pairs = get_best_trend_pairs(processed)
    print(f"\nBest trend pairs:")
    for t1, t2 in pairs:
        print(f"  - {t1['trend_name']} + {t2['trend_name']}")