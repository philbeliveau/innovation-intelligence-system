"""Stage 1: Multi-Trend Decomposition with L1-L4 Abstraction Ladder

Extracts trends from report text with full abstraction levels for transferability.
"""
import json
import logging
from typing import List, Dict, Any, Optional

from backend.pipeline.utils import create_llm
from backend.experimentation.schemas import Stage1Output, Trend, Stage0Output
from backend.experimentation.prompt_template_library import load_prompt_template
from backend.experimentation.few_shot_integration import inject_examples_into_stage_prompt


logger = logging.getLogger(__name__)


class Stage1Decomposition:
    """Trend decomposition stage with L1-L4 abstraction ladder."""

    def __init__(self, temperature: float = 0.3, max_tokens: int = 8000):
        """Initialize Stage 1.

        Args:
            temperature: LLM temperature (lower = more deterministic)
            max_tokens: Maximum output tokens
        """
        self.llm = create_llm(temperature=temperature, max_tokens=max_tokens)
        self.prompt_template = load_prompt_template("stage_1_extraction")

    async def run(
        self,
        report_text: str,
        brand_context: Optional[Stage0Output] = None,
        run_id: Optional[str] = None,
        custom_prompt_content: Optional[str] = None
    ) -> Stage1Output:
        """Extract trends with L1-L4 abstraction from report.

        Args:
            report_text: Full text content from trend report PDF
            brand_context: Optional brand context from Stage 0 (for few-shot selection)
            run_id: Optional pipeline run ID (for usage tracking)
            custom_prompt_content: Optional custom prompt template (Story 11.6.2)

        Returns:
            Stage1Output with structured trend objects

        Raises:
            ValueError: If LLM output cannot be parsed or validated
        """
        logger.info("Running Stage 1: Trend Decomposition with L1-L4 abstraction")

        # Use custom prompt if provided, otherwise use default template with few-shot
        if custom_prompt_content:
            # Custom prompt provided - use directly without few-shot injection
            prompt = custom_prompt_content.format(report_text=report_text)
            logger.debug("Using custom prompt for Stage 1")
        elif brand_context:
            # Inject few-shot examples if brand context available
            enhanced_template = inject_examples_into_stage_prompt(
                prompt_template=self.prompt_template,
                stage=1,
                brand_context=brand_context.brand_context.dict(),
                run_id=run_id
            )
            prompt = enhanced_template.format(report_text=report_text)
            logger.debug("Few-shot examples injected into Stage 1 prompt")
        else:
            # Fallback: use original template without examples
            prompt = self.prompt_template.format(report_text=report_text)
            logger.debug("No brand context provided, skipping few-shot injection")

        # Call LLM
        try:
            from langchain_core.messages import HumanMessage

            messages = [HumanMessage(content=prompt)]
            response = await self.llm.ainvoke(messages)
            llm_output = response.content

            logger.debug(f"LLM response length: {len(llm_output)} characters")

            # Parse JSON output
            trends_data = self._parse_llm_output(llm_output)

            # Validate and construct Trend objects
            trends = []
            for trend_dict in trends_data.get("trends", []):
                try:
                    trend = Trend(**trend_dict)
                    trends.append(trend)
                except Exception as e:
                    logger.warning(f"Failed to validate trend {trend_dict.get('trend_id', 'unknown')}: {e}")
                    continue

            if not trends:
                raise ValueError("No valid trends extracted from report")

            logger.info(f"Successfully extracted {len(trends)} trends")

            return Stage1Output(
                trends=trends,
                total_trends_extracted=len(trends)
            )

        except Exception as e:
            logger.error(f"Stage 1 failed: {e}", exc_info=True)
            raise

    def _parse_llm_output(self, llm_output: str) -> Dict[str, Any]:
        """Parse LLM JSON output with error handling.

        Args:
            llm_output: Raw LLM response text

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If JSON cannot be parsed
        """
        # Try to extract JSON from markdown code blocks
        if "```json" in llm_output:
            json_start = llm_output.find("```json") + 7
            json_end = llm_output.find("```", json_start)
            json_text = llm_output[json_start:json_end].strip()
        elif "```" in llm_output:
            json_start = llm_output.find("```") + 3
            json_end = llm_output.find("```", json_start)
            json_text = llm_output[json_start:json_end].strip()
        else:
            json_text = llm_output.strip()

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON output: {e}")
            logger.debug(f"Raw output:\n{llm_output[:500]}...")
            raise ValueError(f"Invalid JSON from LLM: {e}")
