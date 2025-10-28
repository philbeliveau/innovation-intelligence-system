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
        llm = create_llm(temperature=0.3, max_tokens=1800)

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
            Dictionary with stage1_output key containing structured JSON analysis

        Raises:
            Exception: If chain execution fails
        """
        logging.info("Starting Stage 1: Input Processing")
        logging.debug(f"Input text length: {len(input_text)} characters")

        try:
            result = self.chain.invoke({"input_text": input_text})

            # Parse JSON output from LLM
            raw_output = result.get(self.output_key, "")

            # Try to extract JSON if wrapped in markdown code blocks
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_output, re.DOTALL)
            if json_match:
                raw_output = json_match.group(1)

            # Parse JSON
            try:
                parsed_output = json.loads(raw_output)

                # Ensure all required fields exist with defaults
                enhanced_output = {
                    "extractedText": parsed_output.get("extractedText", input_text[:500]),
                    "trendTitle": parsed_output.get("trendTitle", "Innovation Analysis"),
                    "trendImage": parsed_output.get("trendImage"),
                    "coreMechanism": parsed_output.get("coreMechanism", ""),
                    "businessImpact": parsed_output.get("businessImpact", ""),
                    "patternTransfersTo": parsed_output.get("patternTransfersTo", []),
                    "mechanisms": parsed_output.get("mechanisms", []),
                    "abstractionTest": parsed_output.get("abstractionTest", ""),
                    "evidenceStrength": parsed_output.get("evidenceStrength", "MEDIUM"),
                    "cpgRelevance": parsed_output.get("cpgRelevance", "")
                }

                # Store both the structured data and raw text
                result[self.output_key] = enhanced_output
                result['raw_text'] = raw_output

                logging.info("Stage 1 execution completed successfully with structured JSON")
                return result

            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse Stage 1 JSON output: {e}")
                logging.info("Attempting to extract structured data from markdown output...")

                # Try to extract structured fields from markdown format
                parsed_data = self._parse_markdown_output(raw_output, input_text)

                result[self.output_key] = parsed_data
                result['raw_text'] = raw_output

                logging.info("Stage 1 completed with markdown parsing fallback")
                return result

        except Exception as e:
            logging.error(f"Stage 1 execution failed: {e}", exc_info=True)
            raise

    def _parse_markdown_output(self, markdown_text: str, input_text: str) -> Dict[str, Any]:
        """Parse structured fields from markdown-formatted Stage 1 output.

        This handles cases where the LLM returns markdown instead of JSON.

        Args:
            markdown_text: Markdown output from LLM
            input_text: Original input text for fallback

        Returns:
            Dictionary with extracted structured fields
        """
        import re

        # Initialize with defaults
        extracted = {
            "extractedText": input_text[:500],
            "trendTitle": None,
            "trendImage": None,
            "coreMechanism": "",
            "businessImpact": "",
            "patternTransfersTo": [],
            "mechanisms": [],
            "abstractionTest": "",
            "evidenceStrength": "MEDIUM",
            "cpgRelevance": "",
            "stage1_output": markdown_text  # Store full markdown
        }

        # Extract trend title from document
        # Look for title patterns in the input text (first few lines of all-caps text)
        title_lines = []
        for line in input_text.split('\n')[:5]:
            line = line.strip()
            if line and line.isupper() and len(line.split()) <= 4:
                title_lines.append(line)
            elif title_lines:  # Stop after title ends
                break

        if title_lines:
            extracted["trendTitle"] = ' '.join(title_lines)

        # Extract core mechanism from markdown
        # Pattern: Look for "The Underlying Mechanism:" section
        mechanism_match = re.search(
            r'\*\*The Underlying Mechanism:\*\*\s*(.+?)(?=\n\n|\*\*|$)',
            markdown_text,
            re.DOTALL
        )
        if mechanism_match:
            extracted["coreMechanism"] = mechanism_match.group(1).strip()
        else:
            # Fallback: Try first mechanism section
            mech_fallback = re.search(
                r'## Mechanism \d+:.*?\n\n(.+?)(?=\n\n|\*\*)',
                markdown_text,
                re.DOTALL
            )
            if mech_fallback:
                extracted["coreMechanism"] = mech_fallback.group(1).strip()[:500]

        # Extract business impact
        # Pattern: Look for "Why It Works:" section
        impact_match = re.search(
            r'\*\*Why It Works:\*\*\s*(.+?)(?=\n\n|\*\*|$)',
            markdown_text,
            re.DOTALL
        )
        if impact_match:
            extracted["businessImpact"] = impact_match.group(1).strip()

        # Extract CPG relevance
        cpg_match = re.search(
            r'\*\*CPG Relevance:\*\*\s*(.+?)(?=\n\n|$)',
            markdown_text,
            re.DOTALL
        )
        if cpg_match:
            extracted["cpgRelevance"] = cpg_match.group(1).strip()

        # Extract evidence strength
        evidence_match = re.search(
            r'\*\*Evidence Strength:\*\*\s*(HIGH|MEDIUM|LOW)',
            markdown_text
        )
        if evidence_match:
            extracted["evidenceStrength"] = evidence_match.group(1)

        # Extract pattern transfers to (look in CPG Relevance or application sections)
        # First try to find applications mentioned in CPG Relevance
        if extracted["cpgRelevance"]:
            # Look for phrases like "could apply to", "could be applied to", mentions of product types
            app_items = re.findall(
                r'(?:apply|applies|applying|relevant)\s+to\s+([a-z\s,]+?)(?:\.|,\s*while|\s+or\s+)',
                extracted["cpgRelevance"],
                re.IGNORECASE
            )
            if app_items:
                # Split comma-separated items
                all_items = []
                for item in app_items:
                    all_items.extend([x.strip() for x in item.split(',') if x.strip()])
                extracted["patternTransfersTo"] = all_items[:6]
            else:
                # Fallback: Extract key product/category nouns
                product_items = re.findall(
                    r'\b(apps?|kits?|brands?|products?|lines?|launches?|wellness\s+\w+|fitness\s+\w+|food\s+\w+)\b',
                    extracted["cpgRelevance"],
                    re.IGNORECASE
                )
                extracted["patternTransfersTo"] = list(set(product_items))[:6] if product_items else []

        # If still empty, search broadly in the document
        if not extracted["patternTransfersTo"]:
            transfers_section = re.search(
                r'(?:could\s+)?(?:apply|transfer|relevant)\s+to[:\s]+(.+?)(?=\n\n|##|$)',
                markdown_text,
                re.DOTALL | re.IGNORECASE
            )
            if transfers_section:
                items = re.findall(r'(?:[-•]\s*)?([a-z\s]+)(?:,|\n|$)', transfers_section.group(1), re.IGNORECASE)
                extracted["patternTransfersTo"] = [item.strip() for item in items if item.strip() and len(item.strip()) > 3][:6]

        logging.info(f"Extracted structured data: trendTitle={extracted['trendTitle']}, "
                    f"coreMechanism length={len(extracted['coreMechanism'])}, "
                    f"businessImpact length={len(extracted['businessImpact'])}")

        return extracted

    def save_output(self, output: str, output_dir: Path, selected_track: int = 1) -> Path:
        """Save Stage 1 output to markdown and JSON files.

        This saves both the full markdown analysis AND a JSON file with
        the top 2 selected tracks for use in the web UI horizontal pipeline.

        Args:
            output: Stage 1 analysis text
            output_dir: Base output directory for this pipeline run
            selected_track: Track selection (1 or 2) from UI, defaults to 1

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
                "selected_track": selected_track,  # Single selected track (1 or 2)
                "track_1": tracks[0] if len(tracks) > 0 else self._empty_track(1),
                "track_2": tracks[1] if len(tracks) > 1 else self._empty_track(2),
                "completed_at": datetime.now().isoformat()
            }

            json_file.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
            logging.info(f"Stage 1 JSON output saved: {json_file} (selected_track={selected_track})")

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
