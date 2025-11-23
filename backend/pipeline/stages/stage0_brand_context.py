"""
Stage 0: Brand Context Generation

This module implements Stage 0 of the Innovation Intelligence Pipeline,
which formats brand profile information into a structured markdown display.
"""

import logging
from typing import Dict, Any


class Stage0Chain:
    """Stage 0 chain for brand context generation.

    This chain formats brand profile data into markdown for display
    in the Gradio UI.

    Attributes:
        output_key: Key name for chain output ("stage0_output")
    """

    def __init__(self):
        """Initialize Stage 0 chain."""
        self.output_key = "stage0_output"
        logging.info("Stage 0 chain initialized")

    def run(self, brand_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Stage 0 to generate brand context markdown.

        Args:
            brand_profile: Brand profile dictionary from YAML or manual entry

        Returns:
            Dictionary with stage0_output containing brand context data
        """
        logging.info("Starting Stage 0: Brand Context Generation")

        try:
            # Extract brand fields
            brand_name = brand_profile.get("brand_name", "Unknown Brand")
            industry = brand_profile.get("industry", "Not specified")
            country = brand_profile.get("country", "Not specified")
            portfolio = brand_profile.get("product_portfolio", [])

            # Optional fields
            positioning = brand_profile.get("positioning", "")
            target_customers = brand_profile.get("target_customers", "")
            recent_innovations = brand_profile.get("recent_innovations", "")

            # Format portfolio
            if isinstance(portfolio, list):
                portfolio_text = "\n".join([f"- {item}" for item in portfolio])
            else:
                portfolio_text = str(portfolio)

            # Build structured output
            output_data = {
                "company_name": brand_name,
                "industry": industry,
                "geography": country,
                "product_portfolio": portfolio_text,
                "positioning": positioning,
                "target_customers": target_customers,
                "recent_innovations": recent_innovations
            }

            logging.info(f"Stage 0 completed for brand: {brand_name}")

            return {
                self.output_key: output_data
            }

        except Exception as e:
            logging.error(f"Stage 0 execution failed: {e}", exc_info=True)
            raise


def create_stage0_chain() -> Stage0Chain:
    """Factory function to create Stage 0 chain.

    Returns:
        Configured Stage0Chain instance
    """
    return Stage0Chain()
