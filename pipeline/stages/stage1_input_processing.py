"""
Stage 1: Input Processing and Inspiration Identification

This module implements Stage 1 of the Innovation Intelligence Pipeline,
which extracts key inspiration elements from input documents.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any

from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

from ..prompts.stage1_prompt import get_prompt_template


class Stage1Chain:
    """Stage 1 chain for input processing and inspiration identification.

    This chain analyzes input documents to extract 3-5 key inspiration
    elements that could inform innovation strategies.

    Attributes:
        chain: Configured LangChain LLMChain for Stage 1
        output_key: Key name for chain output ("stage1_output")
    """

    def __init__(self):
        """Initialize Stage 1 chain with OpenRouter/Claude Sonnet 4.5."""
        self.output_key = "stage1_output"
        self.chain = self._create_chain()

    def _create_chain(self) -> LLMChain:
        """Create and configure the Stage 1 LLMChain.

        Returns:
            Configured LLMChain for Stage 1 processing

        Raises:
            ValueError: If OpenRouter API key or base URL not configured
        """
        # Validate environment variables
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL")

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not set. "
                "Please configure in .env file (see .env.template)"
            )

        if not base_url:
            raise ValueError(
                "OPENROUTER_BASE_URL not set. "
                "Please configure in .env file (see .env.template)"
            )

        # Configure ChatOpenAI for OpenRouter with Claude 3.5 Sonnet
        # NOTE: Story specified Claude Sonnet 4.5 (anthropic/claude-sonnet-4.5-20250514)
        # but using Claude 3.5 Sonnet as it's the currently available model
        llm = ChatOpenAI(
            model="anthropic/claude-3.5-sonnet",
            temperature=0.3,  # Consistent analysis
            max_tokens=2500,
            openai_api_key=api_key,
            base_url=base_url  # Updated from deprecated openai_api_base
        )

        logging.debug(
            f"Stage 1 LLM configured: model=anthropic/claude-3.5-sonnet, "
            f"temperature=0.3, max_tokens=2500"
        )

        # Get prompt template
        prompt = get_prompt_template()

        # Create chain
        chain = LLMChain(
            llm=llm,
            prompt=prompt,
            output_key=self.output_key
        )

        logging.info("Stage 1 chain created successfully")
        return chain

    def run(self, input_text: str) -> Dict[str, Any]:
        """Execute Stage 1 chain on input text.

        Args:
            input_text: Input document text content

        Returns:
            Dictionary with stage1_output key containing analysis

        Raises:
            Exception: If chain execution fails
        """
        logging.info("Starting Stage 1: Input Processing")
        logging.debug(f"Input text length: {len(input_text)} characters")

        try:
            result = self.chain.invoke({"input_text": input_text})
            logging.info("Stage 1 execution completed successfully")
            return result

        except Exception as e:
            logging.error(f"Stage 1 execution failed: {e}", exc_info=True)
            raise

    def save_output(self, output: str, output_dir: Path) -> Path:
        """Save Stage 1 output to file.

        Args:
            output: Stage 1 analysis text
            output_dir: Base output directory for this pipeline run

        Returns:
            Path to saved output file

        Raises:
            IOError: If file write fails
        """
        stage1_dir = output_dir / "stage1"
        stage1_dir.mkdir(parents=True, exist_ok=True)

        output_file = stage1_dir / "inspiration-analysis.md"

        try:
            output_file.write_text(output, encoding='utf-8')
            logging.info(f"Stage 1 output saved: {output_file}")
            return output_file

        except IOError as e:
            logging.error(f"Failed to save Stage 1 output: {e}")
            raise


def create_stage1_chain() -> Stage1Chain:
    """Factory function to create Stage 1 chain.

    Returns:
        Configured Stage1Chain instance

    Example:
        >>> chain = create_stage1_chain()
        >>> result = chain.run(input_text)
        >>> chain.save_output(result["stage1_output"], output_dir)
    """
    return Stage1Chain()
