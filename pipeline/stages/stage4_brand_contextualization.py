"""
Stage 4: Brand Contextualization with Research Data

This module implements Stage 4 of the Innovation Intelligence Pipeline,
which customizes universal lessons from Stage 3 for a specific brand using
brand profile data and comprehensive pre-existing research.
"""

import logging
import os
import yaml
from pathlib import Path
from typing import Dict, Any

from langchain.chains import LLMChain

from ..prompts.stage4_prompt import get_prompt_template
from ..utils import create_llm


class Stage4Chain:
    """Stage 4 chain for brand contextualization with research data.

    This chain takes universal lessons from Stage 3 and customizes them for
    a specific brand using brand profile (YAML) and comprehensive research
    data (markdown files).

    Attributes:
        chain: Configured LangChain LLMChain for Stage 4
        output_key: Key name for chain output ("stage4_output")
    """

    def __init__(self):
        """Initialize Stage 4 chain with OpenRouter/Claude Sonnet 3.5."""
        self.output_key = "stage4_output"
        self.chain = self._create_chain()

    def _create_chain(self) -> LLMChain:
        """Create and configure the Stage 4 LLMChain.

        Returns:
            Configured LLMChain for Stage 4 processing

        Raises:
            ValueError: If OpenRouter API key or base URL not configured
        """
        # Create LLM using centralized configuration (model from .env)
        llm = create_llm(temperature=0.5, max_tokens=4000)

        # Get prompt template
        prompt = get_prompt_template()

        # Create chain
        chain = LLMChain(
            llm=llm,
            prompt=prompt,
            output_key=self.output_key
        )

        logging.info("Stage 4 chain created successfully")
        return chain

    def run(
        self,
        stage3_output: str,
        brand_profile: Dict[str, Any],
        research_data: str
    ) -> Dict[str, Any]:
        """Execute Stage 4 chain to generate brand-specific insights.

        Args:
            stage3_output: Stage 3 universal lessons text
            brand_profile: Brand profile dictionary from YAML
            research_data: Comprehensive brand research markdown content
                          (empty string if unavailable - graceful degradation)

        Returns:
            Dictionary with stage4_output key containing brand-specific insights

        Raises:
            ValueError: If stage3_output or brand_profile is invalid
            Exception: If chain execution fails
        """
        logging.info("Starting Stage 4: Brand Contextualization with Research Data")

        # Validate stage3_output
        if not stage3_output or not stage3_output.strip():
            logging.error("Stage 3 output is empty or whitespace-only")
            raise ValueError(
                "stage3_output cannot be empty. "
                "Ensure Stage 3 executed successfully before running Stage 4."
            )

        if len(stage3_output) < 200:
            logging.warning(
                f"Stage 3 output is unusually short "
                f"({len(stage3_output)} chars). "
                f"Expected at least 200 characters for meaningful "
                f"contextualization."
            )

        # Validate brand_profile
        if not brand_profile or not isinstance(brand_profile, dict):
            logging.error("Brand profile is empty or not a dictionary")
            raise ValueError(
                "brand_profile must be a non-empty dictionary. "
                "Ensure brand profile loaded successfully."
            )

        # Format brand profile as YAML text for injection
        brand_profile_text = yaml.dump(
            brand_profile,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True
        )

        # Handle graceful degradation for missing research data
        if not research_data or not research_data.strip():
            logging.warning(
                "Research data is empty. Proceeding with brand profile "
                "only. Stage 4 output quality may be reduced."
            )
            research_data_text = (
                "[No research data available - "
                "relying on brand profile only]"
            )
        else:
            research_data_text = research_data
            research_size_kb = len(research_data) / 1024
            logging.info(
                f"Research data loaded: {research_size_kb:.1f} KB "
                f"({len(research_data)} characters)"
            )

        logging.debug(
            f"Stage 3 output length: {len(stage3_output)} characters"
        )
        logging.debug(f"Brand profile keys: {list(brand_profile.keys())}")
        research_status = (
            'Available' if research_data.strip() else 'Missing'
        )
        logging.debug(f"Research data status: {research_status}")

        try:
            result = self.chain.invoke({
                "stage3_output": stage3_output,
                "brand_profile": brand_profile_text,
                "research_data": research_data_text
            })
            logging.info("Stage 4 execution completed successfully")
            return result

        except Exception as e:
            logging.error(f"Stage 4 execution failed: {e}", exc_info=True)
            raise

    def save_output(self, output: str, output_dir: Path) -> Path:
        """Save Stage 4 output to file.

        Args:
            output: Stage 4 brand-specific insights text
            output_dir: Base output directory for this pipeline run

        Returns:
            Path to saved output file

        Raises:
            IOError: If file write fails
        """
        stage4_dir = output_dir / "stage4"
        stage4_dir.mkdir(parents=True, exist_ok=True)

        output_file = stage4_dir / "brand-contextualization.md"

        try:
            output_file.write_text(output, encoding='utf-8')
            logging.info(f"Stage 4 output saved: {output_file}")
            return output_file

        except IOError as e:
            logging.error(f"Failed to save Stage 4 output: {e}")
            raise


def create_stage4_chain() -> Stage4Chain:
    """Factory function to create Stage 4 chain.

    Returns:
        Configured Stage4Chain instance

    Example:
        >>> from pipeline.utils import load_brand_profile, load_research_data
        >>> chain = create_stage4_chain()
        >>> brand_profile = load_brand_profile("lactalis-canada")
        >>> research_data = load_research_data("lactalis-canada")
        >>> result = chain.run(stage3_output, brand_profile, research_data)
        >>> chain.save_output(result["stage4_output"], output_dir)
    """
    return Stage4Chain()
