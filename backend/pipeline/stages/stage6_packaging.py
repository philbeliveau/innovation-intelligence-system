"""
Stage 6: Export and Packaging

This module implements Stage 6 of the Innovation Intelligence Pipeline,
which creates an executive summary combining all pipeline stages into
a final deliverable format.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime


class Stage6Chain:
    """Stage 6 chain for export and packaging.

    This chain combines outputs from all previous stages into an
    executive summary with opportunity scorecard.

    Attributes:
        output_key: Key name for chain output ("stage6_output")
    """

    def __init__(self):
        """Initialize Stage 6 chain."""
        self.output_key = "stage6_output"
        logging.info("Stage 6 chain initialized")

    def run(
        self,
        brand_context: Dict[str, Any],
        extraction: Dict[str, Any],
        signals: Dict[str, Any],
        insights: Dict[str, Any],
        ideation: Dict[str, Any],
        opportunities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Stage 6 to create executive summary.

        Args:
            brand_context: Stage 0 output (brand profile)
            extraction: Stage 1 output (mechanisms extracted)
            signals: Stage 2 output (trend signals)
            insights: Stage 3 output (consumer insights)
            ideation: Stage 4 output (brand-specific concepts)
            opportunities: Stage 5 output (opportunity cards)

        Returns:
            Dictionary with stage6_output containing executive summary
        """
        logging.info("Starting Stage 6: Export and Packaging")

        try:
            # Extract key metrics
            brand_name = brand_context.get("company_name", "Unknown Brand")
            num_mechanisms = len(extraction.get("mechanisms", []))
            num_signals = len(signals.get("signals", []))
            num_insights = len(insights.get("insights", []))
            num_concepts = len(ideation.get("preliminary", []))
            num_opportunities = len(opportunities.get("opportunities", []))

            # Build scorecard
            scorecard = {
                "brand_name": brand_name,
                "generation_date": datetime.now().isoformat(),
                "pipeline_stats": {
                    "mechanisms_extracted": num_mechanisms,
                    "signals_identified": num_signals,
                    "insights_generated": num_insights,
                    "preliminary_concepts": num_concepts,
                    "final_opportunities": num_opportunities
                },
                "top_opportunities": []
            }

            # Extract top 3 opportunities
            opp_list = opportunities.get("opportunities", [])
            for idx, opp in enumerate(opp_list[:3], start=1):
                scorecard["top_opportunities"].append({
                    "rank": idx,
                    "title": opp.get("title", f"Opportunity {idx}"),
                    "type": opp.get("innovation_type", "Unknown"),
                    "summary": opp.get("description", "")[:150] + "..."
                })

            # Build executive summary structure
            summary = {
                "title": f"{brand_name} Innovation Intelligence Report",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "scorecard": scorecard,
                "methodology": {
                    "stage_0": "Brand context analysis",
                    "stage_1": "Mechanism extraction from trend reports",
                    "stage_2": "Signal amplification and pattern identification",
                    "stage_3": "General consumer insight synthesis",
                    "stage_4": "Brand-specific concept ideation",
                    "stage_5": "Retail-ready opportunity generation"
                },
                "next_steps": [
                    "Review top opportunities with innovation team",
                    "Select 1-2 opportunities for deeper validation",
                    "Conduct consumer testing on selected concepts",
                    "Develop business cases for prioritized initiatives"
                ]
            }

            logging.info(
                f"Stage 6 completed: {num_opportunities} opportunities packaged for {brand_name}"
            )

            return {
                self.output_key: summary
            }

        except Exception as e:
            logging.error(f"Stage 6 execution failed: {e}", exc_info=True)
            raise


def create_stage6_chain() -> Stage6Chain:
    """Factory function to create Stage 6 chain.

    Returns:
        Configured Stage6Chain instance
    """
    return Stage6Chain()
