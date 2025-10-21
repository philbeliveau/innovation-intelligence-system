"""
Stage 3: General Translation to Universal Lessons

This module implements Stage 3 of the Innovation Intelligence Pipeline,
which translates inspirations and trends into brand-agnostic universal principles.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any

from langchain.chains import LLMChain

from ..prompts.stage3_prompt import get_prompt_template
from ..utils import create_llm


class Stage3Chain:
    """Stage 3 chain for general translation to universal lessons.

    This chain synthesizes Stage 1 inspirations and Stage 2 trends to generate
    universal, brand-agnostic lessons applicable across industries.

    Attributes:
        chain: Configured LangChain LLMChain for Stage 3
        output_key: Key name for chain output ("stage3_output")
    """

    def __init__(self):
        """Initialize Stage 3 chain with OpenRouter/Claude Sonnet 3.5."""
        self.output_key = "stage3_output"
        self.chain = self._create_chain()

    def _create_chain(self) -> LLMChain:
        """Create and configure the Stage 3 LLMChain.

        Returns:
            Configured LLMChain for Stage 3 processing

        Raises:
            ValueError: If OpenRouter API key or base URL not configured
        """
        # Create LLM using centralized configuration (model from .env)
        llm = create_llm(temperature=0.5, max_tokens=3500)

        # Get prompt template
        prompt = get_prompt_template()

        # Create chain
        chain = LLMChain(
            llm=llm,
            prompt=prompt,
            output_key=self.output_key
        )

        logging.info("Stage 3 chain created successfully")
        return chain

    def run(self, stage1_output: str, stage2_output: str) -> Dict[str, Any]:
        """Execute Stage 3 chain on Stage 1 and Stage 2 outputs.

        Args:
            stage1_output: Stage 1 inspiration analysis text
            stage2_output: Stage 2 trend analysis text

        Returns:
            Dictionary with stage3_output key containing universal lessons

        Raises:
            ValueError: If stage1_output or stage2_output is empty or invalid
            Exception: If chain execution fails
        """
        logging.info("Starting Stage 3: General Translation to Universal Lessons")

        # Validate inputs
        if not stage1_output or not stage1_output.strip():
            logging.error("Stage 1 output is empty or whitespace-only")
            raise ValueError(
                "stage1_output cannot be empty. "
                "Ensure Stage 1 executed successfully before running Stage 3."
            )

        if not stage2_output or not stage2_output.strip():
            logging.error("Stage 2 output is empty or whitespace-only")
            raise ValueError(
                "stage2_output cannot be empty. "
                "Ensure Stage 2 executed successfully before running Stage 3."
            )

        if len(stage1_output) < 100:
            logging.warning(
                f"Stage 1 output is unusually short ({len(stage1_output)} chars). "
                f"Expected at least 100 characters for meaningful synthesis."
            )

        if len(stage2_output) < 100:
            logging.warning(
                f"Stage 2 output is unusually short ({len(stage2_output)} chars). "
                f"Expected at least 100 characters for meaningful synthesis."
            )

        logging.debug(f"Stage 1 output length: {len(stage1_output)} characters")
        logging.debug(f"Stage 2 output length: {len(stage2_output)} characters")

        try:
            result = self.chain.invoke({
                "stage1_output": stage1_output,
                "stage2_output": stage2_output
            })
            logging.info("Stage 3 execution completed successfully")
            return result

        except Exception as e:
            logging.error(f"Stage 3 execution failed: {e}", exc_info=True)
            raise

    def save_output(self, output: str, output_dir: Path) -> Path:
        """Save Stage 3 output to file.

        Args:
            output: Stage 3 universal lessons text
            output_dir: Base output directory for this pipeline run

        Returns:
            Path to saved output file

        Raises:
            IOError: If file write fails
        """
        stage3_dir = output_dir / "stage3"
        stage3_dir.mkdir(parents=True, exist_ok=True)

        output_file = stage3_dir / "universal-lessons.md"

        try:
            output_file.write_text(output, encoding='utf-8')
            logging.info(f"Stage 3 output saved: {output_file}")
            return output_file

        except IOError as e:
            logging.error(f"Failed to save Stage 3 output: {e}")
            raise


def create_stage3_chain() -> Stage3Chain:
    """Factory function to create Stage 3 chain.

    Returns:
        Configured Stage3Chain instance

    Example:
        >>> chain = create_stage3_chain()
        >>> result = chain.run(stage1_output, stage2_output)
        >>> chain.save_output(result["stage3_output"], output_dir)
    """
    return Stage3Chain()
