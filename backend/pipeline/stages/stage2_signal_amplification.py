"""
Stage 2: Signal Amplification and Trend Extraction

This module implements Stage 2 of the Innovation Intelligence Pipeline,
which extracts trend patterns from Stage 1 inspiration elements.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any

from langchain.chains import LLMChain

from ..prompts.stage2_prompt import get_prompt_template
from ..utils import create_llm


class Stage2Chain:
    """Stage 2 chain for signal amplification and trend extraction.

    This chain analyzes Stage 1 inspirations to identify underlying trends,
    patterns, and broader contextual signals without relying on external data.

    Attributes:
        chain: Configured LangChain LLMChain for Stage 2
        output_key: Key name for chain output ("stage2_output")
    """

    def __init__(self):
        """Initialize Stage 2 chain with OpenRouter/Claude Sonnet 3.5."""
        self.output_key = "stage2_output"
        self.chain = self._create_chain()

    def _create_chain(self) -> LLMChain:
        """Create and configure the Stage 2 LLMChain.

        Returns:
            Configured LLMChain for Stage 2 processing

        Raises:
            ValueError: If OpenRouter API key or base URL not configured
        """
        # Create LLM using centralized configuration (model from .env)
        llm = create_llm(temperature=0.4, max_tokens=3000)

        # Get prompt template
        prompt = get_prompt_template()

        # Create chain
        chain = LLMChain(
            llm=llm,
            prompt=prompt,
            output_key=self.output_key
        )

        logging.info("Stage 2 chain created successfully")
        return chain

    def run(self, stage1_output: str) -> Dict[str, Any]:
        """Execute Stage 2 chain on Stage 1 output.

        Args:
            stage1_output: Stage 1 inspiration analysis text

        Returns:
            Dictionary with stage2_output key containing trend analysis

        Raises:
            ValueError: If stage1_output is empty or invalid
            Exception: If chain execution fails
        """
        logging.info("Starting Stage 2: Signal Amplification and Trend Extraction")

        # Validate input
        if not stage1_output or not stage1_output.strip():
            logging.error("Stage 1 output is empty or whitespace-only")
            raise ValueError(
                "stage1_output cannot be empty. "
                "Ensure Stage 1 executed successfully before running Stage 2."
            )

        if len(stage1_output) < 100:
            logging.warning(
                f"Stage 1 output is unusually short ({len(stage1_output)} chars). "
                f"Expected at least 100 characters for meaningful analysis."
            )

        logging.debug(f"Stage 1 output length: {len(stage1_output)} characters")

        try:
            result = self.chain.invoke({"stage1_output": stage1_output})
            logging.info("Stage 2 execution completed successfully")
            return result

        except Exception as e:
            logging.error(f"Stage 2 execution failed: {e}", exc_info=True)
            raise

    def save_output(self, output: str, output_dir: Path) -> Path:
        """Save Stage 2 output to file.

        Args:
            output: Stage 2 trend analysis text
            output_dir: Base output directory for this pipeline run

        Returns:
            Path to saved output file

        Raises:
            IOError: If file write fails
        """
        stage2_dir = output_dir / "stage2"
        stage2_dir.mkdir(parents=True, exist_ok=True)

        output_file = stage2_dir / "trend-analysis.md"

        try:
            output_file.write_text(output, encoding='utf-8')
            logging.info(f"Stage 2 output saved: {output_file}")
            return output_file

        except IOError as e:
            logging.error(f"Failed to save Stage 2 output: {e}")
            raise


def create_stage2_chain() -> Stage2Chain:
    """Factory function to create Stage 2 chain.

    Returns:
        Configured Stage2Chain instance

    Example:
        >>> chain = create_stage2_chain()
        >>> result = chain.run(stage1_output)
        >>> chain.save_output(result["stage2_output"], output_dir)
    """
    return Stage2Chain()
