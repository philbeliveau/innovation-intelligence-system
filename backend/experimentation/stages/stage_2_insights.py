"""Stage 2: Consumer Insight Synthesis via Trend Convergence

Generates brand-specific consumer insights by identifying multi-trend convergence patterns.
"""
import json
import logging
from typing import List, Dict, Any, Optional

from backend.pipeline.utils import create_llm
from backend.experimentation.schemas import Stage1Output, Stage0Output, Stage2Output, ConsumerInsight
from backend.experimentation.prompt_template_library import load_prompt_template
from backend.experimentation.few_shot_integration import inject_examples_into_stage_prompt


logger = logging.getLogger(__name__)


class Stage2Insights:
    """Consumer insight synthesis stage with convergence analysis."""

    def __init__(self, temperature: float = 0.5, max_tokens: int = 6000):
        """Initialize Stage 2.

        Args:
            temperature: LLM temperature
            max_tokens: Maximum output tokens
        """
        self.llm = create_llm(temperature=temperature, max_tokens=max_tokens)
        self.prompt_template = load_prompt_template("stage_2_convergence")

    async def run(
        self,
        stage1_output: Stage1Output,
        stage0_output: Stage0Output,
        run_id: Optional[str] = None
    ) -> Stage2Output:
        """Generate consumer insights from trends and brand context.

        Args:
            stage1_output: Trends from Stage 1
            stage0_output: Brand context from Stage 0
            run_id: Optional pipeline run ID (for usage tracking)

        Returns:
            Stage2Output with consumer insights

        Raises:
            ValueError: If LLM output cannot be parsed or validated
        """
        logger.info("Running Stage 2: Consumer Insight Synthesis")

        # Identify convergences (trends with shared emotional drivers)
        convergences = self._identify_convergences(stage1_output.trends)
        logger.info(f"Identified {len(convergences)} trend convergences")

        if not convergences:
            logger.warning("No trend convergences found, generating insights from individual trends")
            # Fallback: treat each trend as single-trend "convergence"
            convergences = [{"trends": [trend], "shared_emotions": []} for trend in stage1_output.trends]

        # Inject few-shot examples into prompt
        enhanced_template = inject_examples_into_stage_prompt(
            prompt_template=self.prompt_template,
            stage=2,
            brand_context=stage0_output.brand_context.dict(),
            run_id=run_id
        )
        logger.debug("Few-shot examples injected into Stage 2 prompt")

        # Build prompt with convergences and brand context
        trends_json = json.dumps([trend.dict() for trend in stage1_output.trends], indent=2)
        brand_context_json = json.dumps(stage0_output.brand_context.dict(), indent=2)

        prompt = enhanced_template.format(
            trends=trends_json,
            brand_context=brand_context_json
        )

        # Call LLM
        try:
            from langchain_core.messages import HumanMessage

            messages = [HumanMessage(content=prompt)]
            response = await self.llm.ainvoke(messages)
            llm_output = response.content

            logger.debug(f"LLM response length: {len(llm_output)} characters")

            # Parse JSON output
            insights_data = self._parse_llm_output(llm_output)

            # Validate and construct ConsumerInsight objects
            insights = []
            for insight_dict in insights_data.get("insights", []):
                try:
                    insight = ConsumerInsight(**insight_dict)
                    insights.append(insight)
                except Exception as e:
                    logger.warning(f"Failed to validate insight {insight_dict.get('insight_id', 'unknown')}: {e}")
                    continue

            if not insights:
                raise ValueError("No valid consumer insights generated")

            logger.info(f"Successfully generated {len(insights)} consumer insights")

            return Stage2Output(
                insights=insights,
                convergence_count=len(convergences)
            )

        except Exception as e:
            logger.error(f"Stage 2 failed: {e}", exc_info=True)
            raise

    def _identify_convergences(self, trends: List) -> List[Dict[str, Any]]:
        """Identify trends with shared emotional drivers.

        Args:
            trends: List of Trend objects from Stage 1

        Returns:
            List of convergence dictionaries with trends and shared emotions
        """
        convergences = []

        for i, trend_a in enumerate(trends):
            for trend_b in trends[i+1:]:
                # Check for shared emotional drivers
                shared_current = set(trend_a.emotional_drivers.current_negative) & \
                                set(trend_b.emotional_drivers.current_negative)
                shared_aspirational = set(trend_a.emotional_drivers.aspirational_positive) & \
                                    set(trend_b.emotional_drivers.aspirational_positive)

                if shared_current or shared_aspirational:
                    convergences.append({
                        "trends": [trend_a, trend_b],
                        "shared_emotions": list(shared_current | shared_aspirational)
                    })

        return convergences

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
