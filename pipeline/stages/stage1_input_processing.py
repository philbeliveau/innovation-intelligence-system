"""
Stage 1: Input Processing and Inspiration Identification

This module implements Stage 1 of the Innovation Intelligence Pipeline,
which extracts key inspiration elements from input documents.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from langchain.chains import LLMChain

from ..prompts.stage1_prompt import get_prompt_template
from ..utils import create_llm


class Stage1Chain:
    """Stage 1 chain for input processing and inspiration identification.

    This chain analyzes input documents to extract the TOP 2 key inspiration
    tracks that could inform innovation strategies.

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
        # Create LLM using centralized configuration (model from .env)
        llm = create_llm(temperature=0.3, max_tokens=2500)

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
        """Save Stage 1 output to markdown and JSON files.

        This saves both the full markdown analysis AND a JSON file with
        the top 2 selected tracks for use in the web UI horizontal pipeline.

        Args:
            output: Stage 1 analysis text
            output_dir: Base output directory for this pipeline run

        Returns:
            Path to saved markdown output file

        Raises:
            IOError: If file write fails
        """
        stage1_dir = output_dir / "stage1"
        stage1_dir.mkdir(parents=True, exist_ok=True)

        # Save markdown (existing format)
        output_file = stage1_dir / "inspiration-analysis.md"

        try:
            output_file.write_text(output, encoding='utf-8')
            logging.info(f"Stage 1 output saved: {output_file}")

            # Parse and save JSON for web UI (top 2 tracks only)
            tracks = self._parse_tracks(output)
            json_file = stage1_dir / "inspirations.json"

            json_data = {
                "selected_tracks": [1, 2],  # Only top 2 tracks selected
                "track_1": tracks[0] if len(tracks) > 0 else self._empty_track(1),
                "track_2": tracks[1] if len(tracks) > 1 else self._empty_track(2),
                "completed_at": datetime.now().isoformat()
            }

            json_file.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
            logging.info(f"Stage 1 JSON output saved: {json_file}")

            return output_file

        except IOError as e:
            logging.error(f"Failed to save Stage 1 output: {e}")
            raise

    def _parse_tracks(self, output: str) -> list:
        """Extract top 2 inspiration tracks from LLM markdown output.

        Expected format:
        ## Track 1: [Title]
        [Summary paragraph]

        ## Track 2: [Title]
        [Summary paragraph]

        Args:
            output: Markdown output from LLM

        Returns:
            List of track dictionaries with title and summary
        """
        import re

        tracks = []

        # Match Track 1 and Track 2 sections
        track_pattern = r'## Track (\d+): (.+?)\n\n(.+?)(?=\n\n##|\Z)'
        matches = re.findall(track_pattern, output, re.DOTALL)

        for track_num, title, summary in matches[:2]:  # Only first 2 tracks
            tracks.append({
                "title": title.strip(),
                "summary": summary.strip()[:200] + "..." if len(summary.strip()) > 200 else summary.strip(),
                "icon_url": ""  # Placeholder for future icon support
            })

        return tracks

    def _empty_track(self, track_num: int) -> dict:
        """Generate empty track placeholder if parsing fails.

        Args:
            track_num: Track number (1 or 2)

        Returns:
            Empty track dictionary
        """
        return {
            "title": f"Inspiration Track {track_num}",
            "summary": "Unable to parse - see full markdown output for details",
            "icon_url": ""
        }


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
