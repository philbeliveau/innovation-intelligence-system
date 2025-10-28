"""
Stage 5: Opportunity Generation Chain

This module implements Stage 5 of the Innovation Intelligence Pipeline,
which generates exactly 5 distinct, actionable innovation opportunities
from brand-specific insights (Stage 4 output).
"""

import logging
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from langchain.chains import LLMChain

from ..prompts.stage5_prompt import get_prompt_template, get_output_parser
from ..utils import create_llm


class Stage5Chain:
    """Stage 5 chain for opportunity generation.

    This chain takes brand-specific insights from Stage 4 and generates
    exactly 5 distinct, actionable innovation opportunities spanning
    different innovation types (product, service, marketing, experience,
    partnership).

    Attributes:
        chain: Configured LangChain LLMChain for Stage 5
        parser: StructuredOutputParser to extract 5 opportunities
        jinja_env: Jinja2 environment for template rendering
        output_key: Key name for chain output ("stage5_output")
    """

    def __init__(self, template_dir: Path = None):
        """Initialize Stage 5 chain with OpenRouter/Claude Sonnet 4.5.

        Args:
            template_dir: Directory containing Jinja2 templates
                         (defaults to project root/templates)
        """
        self.output_key = "stage5_output"
        self.parser = get_output_parser()
        self.chain = self._create_chain()

        # Set up Jinja2 environment for opportunity card rendering
        if template_dir is None:
            # Default to templates/ in project root
            project_root = Path(__file__).parent.parent.parent
            template_dir = project_root / "templates"

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        logging.info(f"Stage 5 Jinja2 templates loaded from: {template_dir}")

    def _create_chain(self) -> LLMChain:
        """Create and configure the Stage 5 LLMChain.

        Uses temperature=0.7 for higher creativity in opportunity generation.

        Returns:
            Configured LLMChain for Stage 5 processing

        Raises:
            ValueError: If OpenRouter API key or base URL not configured
        """
        # Create LLM with temperature=0.7 for creative opportunity generation
        llm = create_llm(temperature=0.7, max_tokens=3200)

        # Get prompt template
        prompt = get_prompt_template()

        # Create chain
        chain = LLMChain(
            llm=llm,
            prompt=prompt,
            output_key=self.output_key
        )

        logging.info(
            "Stage 5 chain created successfully (temperature=0.7 for creativity)"
        )
        return chain

    def run(
        self,
        stage4_output: str,
        brand_name: str,
        input_source: str,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """Execute Stage 5 chain to generate 5 opportunity cards.

        Args:
            stage4_output: Stage 4 brand-specific insights text
            brand_name: Name of the brand (e.g., "Lactalis Canada")
            input_source: Original input source (e.g., "Savannah Bananas")
            max_retries: Maximum number of retry attempts on parse failure (default: 2)

        Returns:
            Dictionary with:
                - stage5_output: Raw LLM output text
                - opportunities: List of 5 parsed opportunity dictionaries

        Raises:
            ValueError: If stage4_output is invalid or parsing fails after retries
            Exception: If chain execution fails
        """
        logging.info("Starting Stage 5: Opportunity Generation Chain")

        # Validate stage4_output
        if not stage4_output or not stage4_output.strip():
            logging.error("Stage 4 output is empty or whitespace-only")
            raise ValueError(
                "stage4_output cannot be empty. "
                "Ensure Stage 4 executed successfully before running Stage 5."
            )

        if len(stage4_output) < 500:
            logging.warning(
                f"Stage 4 output is unusually short "
                f"({len(stage4_output)} chars). "
                f"Expected at least 500 characters for meaningful "
                f"opportunity generation."
            )

        logging.debug(
            f"Stage 4 output length: {len(stage4_output)} characters"
        )
        logging.debug(f"Brand: {brand_name}, Input Source: {input_source}")

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logging.warning(f"Retry attempt {attempt}/{max_retries} for Stage 5")

                # Execute chain
                result = self.chain.invoke({
                    "stage4_output": stage4_output,
                    "brand_name": brand_name,
                    "input_source": input_source
                })

                raw_output = result[self.output_key]

                # Save raw output for debugging
                self._save_raw_output_debug(raw_output, input_source, attempt)

                # Parse structured output to extract 5 opportunities
                try:
                    parsed_output = self.parser.parse(raw_output)
                    opportunities = parsed_output.get('opportunities', [])

                    # Validate exactly 5 opportunities
                    if len(opportunities) != 5:
                        logging.error(
                            f"Expected exactly 5 opportunities, got {len(opportunities)}"
                        )
                        raise ValueError(
                            f"Stage 5 must generate exactly 5 opportunities. "
                            f"Got {len(opportunities)} instead."
                        )

                    logging.info(
                        f"Stage 5 execution completed: {len(opportunities)} "
                        f"opportunities generated"
                    )

                    # Render each opportunity to markdown for frontend display
                    opportunities_with_markdown = self._add_markdown_to_opportunities(
                        opportunities, brand_name, input_source
                    )

                    # Return both raw output and parsed opportunities with markdown
                    return {
                        "stage5_output": raw_output,
                        "opportunities": opportunities_with_markdown
                    }

                except Exception as parse_error:
                    logging.error(
                        f"Failed to parse Stage 5 output: {parse_error}",
                        exc_info=True
                    )
                    # Log full output for debugging (not truncated)
                    logging.debug(f"Full raw output length: {len(raw_output)} chars")
                    logging.debug(f"Raw output (first 1000 chars): {raw_output[:1000]}")
                    logging.debug(f"Raw output (around error char 6059): {raw_output[6000:6200] if len(raw_output) > 6200 else 'N/A'}")

                    # Attempt JSON repair
                    logging.info("Attempting to repair malformed JSON...")
                    repaired_output = self._attempt_json_repair(raw_output)

                    if repaired_output:
                        try:
                            parsed_output = self.parser.parse(repaired_output)
                            opportunities = parsed_output.get('opportunities', [])

                            if len(opportunities) == 5:
                                logging.warning("JSON repair successful! Continuing with repaired output.")
                                return {
                                    "stage5_output": repaired_output,
                                    "opportunities": opportunities
                                }
                        except Exception as repair_error:
                            logging.error(f"JSON repair failed: {repair_error}")

                    # If we have retries left, continue loop; otherwise raise
                    last_error = parse_error
                    if attempt < max_retries:
                        logging.info(f"Will retry Stage 5 execution (attempt {attempt + 2}/{max_retries + 1})")
                        continue
                    else:
                        raise ValueError(
                            f"Failed to parse Stage 5 output after {max_retries + 1} attempts: "
                            f"{parse_error}"
                        )

            except ValueError as ve:
                # Re-raise ValueError (parsing failures)
                raise
            except Exception as e:
                logging.error(f"Stage 5 execution failed: {e}", exc_info=True)
                last_error = e
                if attempt < max_retries:
                    logging.info(f"Will retry Stage 5 execution (attempt {attempt + 2}/{max_retries + 1})")
                    continue
                else:
                    raise

        # Should not reach here, but just in case
        raise ValueError(
            f"Stage 5 failed after {max_retries + 1} attempts. Last error: {last_error}"
        )

    def _save_raw_output_debug(
        self,
        raw_output: str,
        input_source: str,
        attempt: int = 0
    ) -> None:
        """Save raw LLM output to file for debugging.

        Args:
            raw_output: Raw text output from LLM
            input_source: Input source identifier for filename
            attempt: Retry attempt number (0 for first attempt)
        """
        try:
            debug_dir = Path("data/test-outputs") / input_source / "stage5_debug"
            debug_dir.mkdir(parents=True, exist_ok=True)

            attempt_suffix = f"_attempt{attempt}" if attempt > 0 else ""
            debug_file = debug_dir / f"raw_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}{attempt_suffix}.txt"
            debug_file.write_text(raw_output, encoding='utf-8')

            logging.debug(f"Raw output saved to: {debug_file}")
        except Exception as e:
            logging.warning(f"Failed to save raw output debug file: {e}")

    def _attempt_json_repair(self, raw_output: str) -> Optional[str]:
        """Attempt to repair common JSON formatting errors from LLM output.

        Args:
            raw_output: Malformed JSON string from LLM

        Returns:
            Repaired JSON string if successful, None otherwise
        """
        try:
            # Extract JSON from markdown code block if present
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = raw_output

            # Common repair strategies
            repaired = json_str

            # 1. Fix missing commas between array elements (most common LLM error)
            # Pattern: }\n\s*{ should be },\n{
            repaired = re.sub(r'\}\s*\n\s*\{', '},\n{', repaired)

            # 2. Fix missing commas between object properties
            # Pattern: "\n\s*" should be ",\n"
            repaired = re.sub(r'"\s*\n\s*"', '",\n"', repaired)

            # 3. Fix unescaped quotes in strings (basic attempt)
            # This is tricky - only handle apostrophes for now
            # Pattern: 's in strings should be \'s
            # (Skip this for now as it's complex)

            # 4. Remove trailing commas before closing braces/brackets
            repaired = re.sub(r',\s*\}', '}', repaired)
            repaired = re.sub(r',\s*\]', ']', repaired)

            # Validate the repair worked
            json.loads(repaired)
            logging.info("JSON repair successful")
            return f"```json\n{repaired}\n```"

        except json.JSONDecodeError as e:
            logging.error(f"JSON repair validation failed: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error during JSON repair: {e}")
            return None

    def _add_markdown_to_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        brand_name: str,
        input_source: str
    ) -> List[Dict[str, Any]]:
        """Add rendered markdown content to each opportunity.

        Args:
            opportunities: List of opportunity dictionaries
            brand_name: Name of the brand
            input_source: Original input source

        Returns:
            List of opportunities with 'markdown' field added
        """
        # Load opportunity card template
        template = self.jinja_env.get_template('opportunity-card.md.j2')
        timestamp = datetime.now().isoformat()

        opportunities_with_markdown = []

        for idx, opportunity in enumerate(opportunities, start=1):
            # Generate opportunity metadata
            opportunity_id = f"opp-{idx:02d}"

            # Extract innovation type for tags
            innovation_type = opportunity.get('innovation_type', 'Unknown')
            tags_list = [
                innovation_type.lower(),
                brand_name.lower().replace(' ', '-'),
                input_source.lower().replace(' ', '-')
            ]
            tags = ', '.join(tags_list)

            # Prepare template context
            context = {
                'opportunity_id': opportunity_id,
                'brand': brand_name,
                'input_source': input_source,
                'timestamp': timestamp,
                'tags': tags,
                'title': opportunity.get('title', f'Opportunity {idx}'),
                'description': opportunity.get('description', ''),
                'actionability_items': opportunity.get('actionability_items', []),
                'visual_description': opportunity.get('visual_description', ''),
                'follow_up_prompts': opportunity.get('follow_up_prompts', []),
                'retail_metrics': opportunity.get('retail_metrics', '')
            }

            # Render template to markdown
            rendered_markdown = template.render(**context)

            # Add markdown to opportunity dict
            opportunity_with_markdown = opportunity.copy()
            opportunity_with_markdown['markdown'] = rendered_markdown
            opportunities_with_markdown.append(opportunity_with_markdown)

        return opportunities_with_markdown

    def render_opportunity_cards(
        self,
        opportunities: List[Dict[str, Any]],
        brand_name: str,
        input_source: str,
        output_dir: Path
    ) -> List[Path]:
        """Render 5 opportunity cards using Jinja2 template.

        Args:
            opportunities: List of 5 opportunity dictionaries
            brand_name: Name of the brand
            input_source: Original input source
            output_dir: Base output directory for this pipeline run

        Returns:
            List of 5 paths to rendered opportunity card files

        Raises:
            ValueError: If opportunities list is not exactly 5
            IOError: If file write fails
        """
        if len(opportunities) != 5:
            raise ValueError(
                f"Expected exactly 5 opportunities, got {len(opportunities)}"
            )

        logging.info("Rendering 5 opportunity cards using Jinja2 template")

        # Create stage5 output directory
        stage5_dir = output_dir / "stage5"
        stage5_dir.mkdir(parents=True, exist_ok=True)

        # Load opportunity card template
        template = self.jinja_env.get_template('opportunity-card.md.j2')

        rendered_files = []
        timestamp = datetime.now().isoformat()

        for idx, opportunity in enumerate(opportunities, start=1):
            # Generate opportunity metadata
            opportunity_id = f"opp-{idx:02d}"

            # Extract innovation type for tags
            innovation_type = opportunity.get('innovation_type', 'Unknown')
            tags_list = [
                innovation_type.lower(),
                brand_name.lower().replace(' ', '-'),
                input_source.lower().replace(' ', '-')
            ]
            tags = ', '.join(tags_list)

            # Prepare template context
            context = {
                'opportunity_id': opportunity_id,
                'brand': brand_name,
                'input_source': input_source,
                'timestamp': timestamp,
                'tags': tags,
                'title': opportunity.get('title', f'Opportunity {idx}'),
                'description': opportunity.get('description', ''),
                'actionability_items': opportunity.get('actionability_items', []),
                'visual_description': opportunity.get('visual_description', ''),
                'follow_up_prompts': opportunity.get('follow_up_prompts', [])
            }

            # Render template
            rendered_content = template.render(**context)

            # Save to file
            output_file = stage5_dir / f"opportunity-{idx}.md"
            try:
                output_file.write_text(rendered_content, encoding='utf-8')
                rendered_files.append(output_file)
                logging.info(
                    f"Opportunity {idx} rendered: {output_file} "
                    f"({innovation_type})"
                )

            except IOError as e:
                logging.error(
                    f"Failed to save opportunity {idx}: {e}"
                )
                raise

        logging.info(
            f"All 5 opportunity cards rendered successfully in {stage5_dir}"
        )
        return rendered_files

    def generate_summary_file(
        self,
        opportunities: List[Dict[str, Any]],
        output_dir: Path
    ) -> Path:
        """Generate summary file listing all 5 opportunities.

        Args:
            opportunities: List of 5 opportunity dictionaries
            output_dir: Base output directory for this pipeline run

        Returns:
            Path to generated summary file

        Raises:
            ValueError: If opportunities list is not exactly 5
            IOError: If file write fails
        """
        if len(opportunities) != 5:
            raise ValueError(
                f"Expected exactly 5 opportunities, got {len(opportunities)}"
            )

        logging.info("Generating opportunities summary file")

        stage5_dir = output_dir / "stage5"
        stage5_dir.mkdir(parents=True, exist_ok=True)

        summary_file = stage5_dir / "opportunities-summary.md"

        # Build summary content
        summary_lines = [
            "# Innovation Opportunities Summary\n",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"Total Opportunities: {len(opportunities)}\n",
            "\n---\n\n"
        ]

        for idx, opportunity in enumerate(opportunities, start=1):
            title = opportunity.get('title', f'Opportunity {idx}')
            innovation_type = opportunity.get('innovation_type', 'Unknown')
            description = opportunity.get('description', '')

            # Extract first sentence for one-line description
            first_sentence = description.split('.')[0].strip() if description else 'No description available'
            if len(first_sentence) > 120:
                first_sentence = first_sentence[:117] + '...'

            summary_lines.append(
                f"## {idx}. {title}\n\n"
                f"**Type:** {innovation_type}\n\n"
                f"**Quick Overview:** {first_sentence}\n\n"
                f"**Details:** [opportunity-{idx}.md](opportunity-{idx}.md)\n\n"
                f"---\n\n"
            )

        summary_content = ''.join(summary_lines)

        try:
            summary_file.write_text(summary_content, encoding='utf-8')
            logging.info(f"Summary file generated: {summary_file}")
            return summary_file

        except IOError as e:
            logging.error(f"Failed to save summary file: {e}")
            raise


def create_stage5_chain(template_dir: Path = None) -> Stage5Chain:
    """Factory function to create Stage 5 chain.

    Args:
        template_dir: Optional directory containing Jinja2 templates

    Returns:
        Configured Stage5Chain instance

    Example:
        >>> chain = create_stage5_chain()
        >>> result = chain.run(stage4_output, "Lactalis Canada", "Savannah Bananas")
        >>> opportunities = result['opportunities']
        >>> chain.render_opportunity_cards(opportunities, "Lactalis Canada", "Savannah Bananas", output_dir)
        >>> chain.generate_summary_file(opportunities, output_dir)
    """
    return Stage5Chain(template_dir=template_dir)
