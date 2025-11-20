"""
Automatic Quality Scoring System
Scores pipeline outputs to identify high-quality results without manual review
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class QualityMetrics:
    """Container for quality scores and explanations"""
    overall_score: float
    component_scores: Dict[str, float]
    explanations: Dict[str, str]
    passed: bool
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class QualityScorer:
    """
    Scores outputs from each pipeline stage based on multiple criteria.
    Helps identify which prompts and configurations produce best results.
    """

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        """Initialize with custom quality thresholds"""
        self.thresholds = thresholds or {
            "stage_1": 0.7,  # Minimum score for Stage 1
            "stage_2": 0.75,
            "stage_3": 0.7,
            "stage_4": 0.8,
            "overall": 0.75
        }

    def score_stage_1_trends(self, trends: List[Dict]) -> QualityMetrics:
        """
        Score Stage 1: Trend Extraction
        Evaluates completeness and quality of trend decomposition
        """

        scores = {}
        explanations = {}

        # 1. Quantity Check (0-1)
        trend_count = len(trends)
        scores['quantity'] = min(trend_count / 5.0, 1.0)  # Expect ~5 trends
        explanations['quantity'] = f"Extracted {trend_count} trends (target: 3-6)"

        # 2. Completeness Check (each trend has required fields)
        complete_trends = 0
        for trend in trends:
            has_name = bool(trend.get('trend_name'))
            has_lifecycle = trend.get('lifecycle_stage') in ['EMERGING', 'ACCELERATING', 'PEAKING']
            has_emotions = (
                'emotional_drivers' in trend and
                'current_negative' in trend['emotional_drivers'] and
                'aspirational_positive' in trend['emotional_drivers']
            )
            has_abstraction = (
                'abstraction_levels' in trend and
                all(f'L{i}' in trend.get('abstraction_levels', {}) for i in range(1, 5))
            )

            if all([has_name, has_lifecycle, has_emotions, has_abstraction]):
                complete_trends += 1

        scores['completeness'] = complete_trends / max(len(trends), 1)
        explanations['completeness'] = f"{complete_trends}/{len(trends)} trends have all required fields"

        # 3. Abstraction Quality (L1-L4 progression)
        abstraction_scores = []
        for trend in trends:
            levels = trend.get('abstraction_levels', {})
            if len(levels) == 4:
                # Check if abstractions ascend from concrete to universal
                l1_concrete = len(levels.get('L1', '')) > 10  # Has content
                l4_universal = len(levels.get('L4', '')) > 10
                l1_specific = 'CPG' in levels.get('L1', '') or 'product' in levels.get('L1', '').lower()
                l4_broad = any(word in levels.get('L4', '').lower()
                             for word in ['principle', 'universal', 'fundamental', 'human'])

                if l1_concrete and l4_universal and l1_specific and l4_broad:
                    abstraction_scores.append(1.0)
                elif l1_concrete and l4_universal:
                    abstraction_scores.append(0.7)
                else:
                    abstraction_scores.append(0.3)
            else:
                abstraction_scores.append(0.0)

        scores['abstraction_quality'] = sum(abstraction_scores) / max(len(abstraction_scores), 1)
        explanations['abstraction_quality'] = f"L1-L4 progression quality: {scores['abstraction_quality']:.2f}"

        # 4. Emotional Driver Richness
        emotion_scores = []
        for trend in trends:
            drivers = trend.get('emotional_drivers', {})
            neg_count = len(drivers.get('current_negative', []))
            pos_count = len(drivers.get('aspirational_positive', []))

            # Good: 2-4 emotions each
            if 2 <= neg_count <= 4 and 2 <= pos_count <= 4:
                emotion_scores.append(1.0)
            elif neg_count >= 1 and pos_count >= 1:
                emotion_scores.append(0.6)
            else:
                emotion_scores.append(0.2)

        scores['emotional_richness'] = sum(emotion_scores) / max(len(emotion_scores), 1)
        explanations['emotional_richness'] = f"Emotional driver completeness: {scores['emotional_richness']:.2f}"

        # Calculate overall score
        overall = sum(scores.values()) / len(scores)
        passed = overall >= self.thresholds['stage_1']

        return QualityMetrics(
            overall_score=overall,
            component_scores=scores,
            explanations=explanations,
            passed=passed
        )

    def score_stage_2_insights(
        self,
        insights: List[Dict],
        brand_context: Dict
    ) -> QualityMetrics:
        """
        Score Stage 2: Consumer Insight Synthesis
        Evaluates convergence quality and brand relevance
        """

        scores = {}
        explanations = {}

        # 1. Insight Count
        insight_count = len(insights)
        scores['quantity'] = min(insight_count / 3.0, 1.0)  # Expect ~3 insights
        explanations['quantity'] = f"Generated {insight_count} insights (target: 2-4)"

        # 2. Convergence Quality (uses multiple trends)
        convergence_scores = []
        for insight in insights:
            primary = insight.get('primary_trend')
            secondary = insight.get('secondary_trend')

            if primary and secondary and primary != secondary:
                convergence_scores.append(1.0)
            elif primary or secondary:
                convergence_scores.append(0.5)
            else:
                convergence_scores.append(0.0)

        scores['convergence'] = sum(convergence_scores) / max(len(convergence_scores), 1)
        explanations['convergence'] = f"Multi-trend convergence: {scores['convergence']:.2f}"

        # 3. Brand Specificity
        brand_name = brand_context.get('name', '').lower()
        brand_industry = brand_context.get('industry', '').lower()

        brand_scores = []
        for insight in insights:
            statement = insight.get('insight_statement', '').lower()

            # Check if insight mentions brand or industry
            mentions_brand = brand_name in statement if brand_name else False
            mentions_industry = any(word in statement for word in brand_industry.split())
            is_specific = len(statement) > 50  # Not too generic

            if mentions_brand and is_specific:
                brand_scores.append(1.0)
            elif mentions_industry and is_specific:
                brand_scores.append(0.7)
            elif is_specific:
                brand_scores.append(0.4)
            else:
                brand_scores.append(0.1)

        scores['brand_relevance'] = sum(brand_scores) / max(len(brand_scores), 1)
        explanations['brand_relevance'] = f"Brand-specific insights: {scores['brand_relevance']:.2f}"

        # 4. Consumer Needs Completeness
        needs_scores = []
        for insight in insights:
            needs = insight.get('consumer_needs', {})

            has_functional = bool(needs.get('functional'))
            has_emotional = bool(needs.get('emotional'))
            has_social = bool(needs.get('social'))

            if all([has_functional, has_emotional, has_social]):
                needs_scores.append(1.0)
            elif sum([has_functional, has_emotional, has_social]) >= 2:
                needs_scores.append(0.6)
            else:
                needs_scores.append(0.2)

        scores['needs_completeness'] = sum(needs_scores) / max(len(needs_scores), 1)
        explanations['needs_completeness'] = f"Consumer needs (F/E/S): {scores['needs_completeness']:.2f}"

        # 5. Lifecycle Strategy Present
        strategy_scores = []
        for insight in insights:
            has_lifecycle = bool(insight.get('lifecycle_strategy'))
            has_relevance = insight.get('brand_relevance') in ['HIGH', 'MEDIUM', 'LOW']

            if has_lifecycle and has_relevance:
                strategy_scores.append(1.0)
            elif has_lifecycle or has_relevance:
                strategy_scores.append(0.5)
            else:
                strategy_scores.append(0.0)

        scores['strategic_thinking'] = sum(strategy_scores) / max(len(strategy_scores), 1)
        explanations['strategic_thinking'] = f"Strategic elements: {scores['strategic_thinking']:.2f}"

        # Calculate overall
        overall = sum(scores.values()) / len(scores)
        passed = overall >= self.thresholds['stage_2']

        return QualityMetrics(
            overall_score=overall,
            component_scores=scores,
            explanations=explanations,
            passed=passed
        )

    def score_stage_3_techniques(self, technique_output: Dict) -> QualityMetrics:
        """
        Score Stage 3: Technique Library Matching
        Evaluates technique selection and application specificity
        """

        scores = {}
        explanations = {}

        # 1. Primary Technique Selected
        has_technique = bool(technique_output.get('primary_technique'))
        scores['technique_selected'] = 1.0 if has_technique else 0.0
        explanations['technique_selected'] = f"Technique: {technique_output.get('primary_technique', 'None')}"

        # 2. Application Specificity
        application = technique_output.get('application', '')
        app_length = len(application)
        is_specific = app_length > 50
        has_details = any(keyword in application.lower()
                         for keyword in ['assign', 'remove', 'combine', 'divide', 'correlate'])

        if is_specific and has_details:
            scores['application_quality'] = 1.0
        elif is_specific:
            scores['application_quality'] = 0.6
        else:
            scores['application_quality'] = 0.2

        explanations['application_quality'] = f"Application detail: {app_length} chars"

        # 3. CPG Example Provided
        has_example = bool(technique_output.get('cpg_example'))
        scores['example_provided'] = 1.0 if has_example else 0.3
        explanations['example_provided'] = "CPG example: " + ("Yes" if has_example else "No")

        # 4. Feasibility Assessment
        feasibility = technique_output.get('feasibility')
        if feasibility in ['HIGH', 'MEDIUM', 'LOW']:
            scores['feasibility_assessed'] = 1.0
            explanations['feasibility_assessed'] = f"Feasibility: {feasibility}"
        else:
            scores['feasibility_assessed'] = 0.0
            explanations['feasibility_assessed'] = "Feasibility: Not assessed"

        # Calculate overall
        overall = sum(scores.values()) / len(scores)
        passed = overall >= self.thresholds['stage_3']

        return QualityMetrics(
            overall_score=overall,
            component_scores=scores,
            explanations=explanations,
            passed=passed
        )

    def score_stage_4_concept(
        self,
        concept_output: Dict,
        creativity_target: float = 0.7
    ) -> QualityMetrics:
        """
        Score Stage 4: Directional Concept Generation
        Evaluates concept completeness, creativity, and actionability
        """

        scores = {}
        explanations = {}

        # 1. Concept Name Quality
        concept_name = concept_output.get('concept_name', '')
        name_words = len(concept_name.split())

        if 2 <= name_words <= 5 and concept_name:
            scores['name_quality'] = 1.0
        elif concept_name:
            scores['name_quality'] = 0.5
        else:
            scores['name_quality'] = 0.0

        explanations['name_quality'] = f"Name: '{concept_name}' ({name_words} words)"

        # 2. Tagline Present and Compelling
        tagline = concept_output.get('tagline', '')
        if len(tagline) > 10:
            scores['tagline_quality'] = 1.0
        elif tagline:
            scores['tagline_quality'] = 0.5
        else:
            scores['tagline_quality'] = 0.0

        explanations['tagline_quality'] = f"Tagline: {len(tagline)} chars"

        # 3. Description Completeness
        description = concept_output.get('description', {})
        required_fields = ['what', 'who', 'why_now', 'why_this_brand']
        present_fields = sum(1 for field in required_fields if description.get(field))

        scores['description_completeness'] = present_fields / len(required_fields)
        explanations['description_completeness'] = f"Description fields: {present_fields}/{len(required_fields)}"

        # 4. Budget and Timeline Realism
        budget = concept_output.get('estimated_budget', '')
        timeline = concept_output.get('timeline', '')

        realistic_budget = ('40' in budget or '50' in budget or '60' in budget or 'K' in budget)
        realistic_timeline = ('month' in timeline.lower() or 'year' in timeline.lower())

        if realistic_budget and realistic_timeline:
            scores['feasibility'] = 1.0
        elif realistic_budget or realistic_timeline:
            scores['feasibility'] = 0.5
        else:
            scores['feasibility'] = 0.2

        explanations['feasibility'] = f"Budget: {budget}, Timeline: {timeline}"

        # 5. Innovation Level (based on concept name and description)
        # Simple heuristic: look for innovation indicators
        full_text = f"{concept_name} {tagline} {json.dumps(description)}".lower()
        innovation_words = ['ai', 'smart', 'digital', 'automated', 'personalized',
                          'gamified', 'interactive', 'dynamic', 'adaptive', 'predictive']
        innovation_count = sum(1 for word in innovation_words if word in full_text)

        if creativity_target > 0.7:  # High creativity desired
            scores['innovation'] = min(innovation_count / 3.0, 1.0)
        else:  # Conservative approach
            scores['innovation'] = 1.0 if innovation_count <= 2 else 0.5

        explanations['innovation'] = f"Innovation indicators: {innovation_count}"

        # Calculate overall
        overall = sum(scores.values()) / len(scores)
        passed = overall >= self.thresholds['stage_4']

        return QualityMetrics(
            overall_score=overall,
            component_scores=scores,
            explanations=explanations,
            passed=passed
        )

    def score_full_pipeline(
        self,
        stage_outputs: Dict[str, Any],
        brand_context: Dict,
        creativity_level: float = 0.7
    ) -> Dict[str, QualityMetrics]:
        """
        Score all stages and provide overall pipeline score
        """

        results = {}

        # Score each stage
        if 'stage_1' in stage_outputs:
            results['stage_1'] = self.score_stage_1_trends(stage_outputs['stage_1'])

        if 'stage_2' in stage_outputs:
            results['stage_2'] = self.score_stage_2_insights(
                stage_outputs['stage_2'],
                brand_context
            )

        if 'stage_3' in stage_outputs:
            results['stage_3'] = self.score_stage_3_techniques(stage_outputs['stage_3'])

        if 'stage_4' in stage_outputs:
            results['stage_4'] = self.score_stage_4_concept(
                stage_outputs['stage_4'],
                creativity_level
            )

        # Calculate overall pipeline score
        if results:
            overall_scores = [r.overall_score for r in results.values()]
            pipeline_score = sum(overall_scores) / len(overall_scores)
            pipeline_passed = pipeline_score >= self.thresholds['overall']

            results['pipeline'] = QualityMetrics(
                overall_score=pipeline_score,
                component_scores={stage: r.overall_score for stage, r in results.items()},
                explanations={
                    'summary': f"Pipeline average: {pipeline_score:.2f}",
                    'passed_stages': sum(1 for r in results.values() if r.passed),
                    'total_stages': len(results)
                },
                passed=pipeline_passed
            )

        return results

    def get_improvement_suggestions(self, metrics: QualityMetrics, stage: str) -> List[str]:
        """
        Provide specific suggestions for improving low-scoring areas
        """

        suggestions = []

        for component, score in metrics.component_scores.items():
            if score < 0.7:  # Below threshold
                if stage == "stage_1" and component == "abstraction_quality":
                    suggestions.append(
                        "Improve L1-L4 abstraction: Ensure L1 is CPG-specific and L4 is universal principle"
                    )
                elif stage == "stage_2" and component == "brand_relevance":
                    suggestions.append(
                        f"Make insights more brand-specific: Mention brand name or industry explicitly"
                    )
                elif stage == "stage_2" and component == "convergence":
                    suggestions.append(
                        "Ensure each insight combines 2+ trends (primary and secondary)"
                    )
                elif stage == "stage_3" and component == "application_quality":
                    suggestions.append(
                        "Provide more detailed application: Explain exactly how technique applies to this brand"
                    )
                elif stage == "stage_4" and component == "description_completeness":
                    suggestions.append(
                        "Complete all description fields: what, who, why_now, why_this_brand"
                    )

        return suggestions

    def format_report(self, metrics_dict: Dict[str, QualityMetrics]) -> str:
        """
        Format quality scores into readable report
        """

        report = "=" * 50 + "\n"
        report += "PIPELINE QUALITY REPORT\n"
        report += "=" * 50 + "\n\n"

        for stage, metrics in metrics_dict.items():
            if stage == "pipeline":
                report += "\n" + "=" * 50 + "\n"
                report += f"OVERALL PIPELINE SCORE: {metrics.overall_score:.2f} "
                report += "✅ PASSED\n" if metrics.passed else "❌ NEEDS IMPROVEMENT\n"
                report += "=" * 50 + "\n"
            else:
                report += f"\n{stage.upper()}:\n"
                report += f"  Overall: {metrics.overall_score:.2f} "
                report += "✅\n" if metrics.passed else "❌\n"

                # Component scores
                for component, score in metrics.component_scores.items():
                    indicator = "✓" if score >= 0.7 else "✗"
                    report += f"  {indicator} {component}: {score:.2f}\n"

                # Suggestions if needed
                suggestions = self.get_improvement_suggestions(metrics, stage)
                if suggestions:
                    report += "  Suggestions:\n"
                    for suggestion in suggestions:
                        report += f"    - {suggestion}\n"

        return report


# Usage functions for integration
def score_pipeline_output(
    stage_outputs: Dict,
    brand_context: Dict,
    creativity_level: float = 0.7
) -> Dict[str, QualityMetrics]:
    """Score complete pipeline output"""

    scorer = QualityScorer()
    return scorer.score_full_pipeline(stage_outputs, brand_context, creativity_level)


def get_quality_report(
    stage_outputs: Dict,
    brand_context: Dict
) -> str:
    """Get formatted quality report"""

    scorer = QualityScorer()
    metrics = scorer.score_full_pipeline(stage_outputs, brand_context)
    return scorer.format_report(metrics)


if __name__ == "__main__":
    # Test scoring
    test_outputs = {
        "stage_1": [
            {
                "trend_name": "Strategic Joy",
                "lifecycle_stage": "EMERGING",
                "emotional_drivers": {
                    "current_negative": ["stressed", "overwhelmed"],
                    "aspirational_positive": ["carefree", "inspired"]
                },
                "abstraction_levels": {
                    "L1": "CPG products that gamify healthy eating",
                    "L2": "Food brands using playfulness",
                    "L3": "Pleasure activism",
                    "L4": "Joy as universal human need"
                }
            }
        ],
        "stage_2": [
            {
                "insight_statement": "Bakery customers want simplified joy",
                "primary_trend": "Witherwill",
                "secondary_trend": "Strategic Joy",
                "consumer_needs": {
                    "functional": "Easier decisions",
                    "emotional": "Feel carefree",
                    "social": "Appear sophisticated"
                },
                "brand_relevance": "HIGH"
            }
        ]
    }

    scorer = QualityScorer()
    results = scorer.score_full_pipeline(
        test_outputs,
        {"name": "Test Brand", "industry": "Bakery"}
    )

    print(scorer.format_report(results))