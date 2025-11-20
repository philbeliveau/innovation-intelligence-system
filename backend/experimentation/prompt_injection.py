"""Prompt Injection System for Few-Shot Learning (Story 11.3b)

Injects selected examples into prompts with:
- Token limit awareness
- Stage-specific formatting
- Usage tracking
- Feature toggle support
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from backend.experimentation.example_selector import ExampleSelector


class PromptInjector:
    """
    Injects few-shot examples into prompts with token management
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        max_examples: int = 3,
        token_limit: int = 4000,
        enabled: bool = True,
        track_usage: bool = True
    ):
        """
        Initialize prompt injector

        Args:
            storage_path: Path to examples storage
            max_examples: Maximum examples per injection (default 3)
            token_limit: Token budget for examples (default 4000)
            enabled: Feature toggle (default True)
            track_usage: Track example usage (default True)
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.max_examples = max_examples
        self.token_limit = token_limit
        self.enabled = enabled
        self.track_usage = track_usage

        # Usage tracking log
        self.usage_log: List[Dict[str, Any]] = []

        # Initialize example selector
        self.selector = ExampleSelector(storage_path=storage_path)

    def inject_examples(
        self,
        prompt_template: str,
        stage: int,
        brand_context: Dict[str, Any],
        run_id: Optional[str] = None,
        max_examples: Optional[int] = None
    ) -> str:
        """
        Inject relevant examples into prompt template

        Args:
            prompt_template: Prompt template with optional {few_shot_examples} placeholder
            stage: Pipeline stage (0-6)
            brand_context: Brand context for example selection
            run_id: Optional run ID for usage tracking
            max_examples: Override default max examples

        Returns:
            Enhanced prompt with injected examples
        """
        # Feature toggle check
        if not self.enabled:
            return prompt_template.replace("{few_shot_examples}", "")

        # Select relevant examples
        n_examples = max_examples or self.max_examples
        selected_examples = self.selector.select_examples(
            stage=stage,
            brand_context=brand_context,
            max_examples=n_examples
        )

        # Graceful fallback if no examples
        if not selected_examples:
            return prompt_template.replace("{few_shot_examples}", "")

        # Adjust for token limits
        adjusted_examples = adjust_examples_for_token_limit(
            selected_examples,
            prompt_template,
            self.token_limit
        )

        # Format examples for LLM consumption
        formatted_examples = format_examples_for_stage(adjusted_examples, stage)

        # Track usage
        if self.track_usage:
            self._log_usage(
                run_id=run_id,
                stage=stage,
                example_ids=[ex["id"] for ex in adjusted_examples],
                brand_context=brand_context
            )

        # Inject into prompt
        if "{few_shot_examples}" in prompt_template:
            # Replace placeholder
            return prompt_template.replace("{few_shot_examples}", formatted_examples)
        else:
            # Prepend before main content
            return self._prepend_examples(prompt_template, formatted_examples)

    def _prepend_examples(self, prompt: str, examples: str) -> str:
        """
        Prepend examples to prompt if no placeholder exists

        Args:
            prompt: Original prompt
            examples: Formatted examples

        Returns:
            Prompt with examples prepended
        """
        # Find first major section (usually after first ## heading)
        lines = prompt.split('\n')

        # Insert after title, before first ## section
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('## '):
                insert_pos = i
                break

        if insert_pos > 0:
            lines.insert(insert_pos, examples)
            lines.insert(insert_pos + 1, "")  # Add spacing
            return '\n'.join(lines)
        else:
            # Fallback: prepend at beginning
            return f"{examples}\n\n{prompt}"

    def _log_usage(
        self,
        run_id: Optional[str],
        stage: int,
        example_ids: List[str],
        brand_context: Dict[str, Any]
    ):
        """
        Log example usage for tracking

        Args:
            run_id: Pipeline run ID
            stage: Pipeline stage
            example_ids: IDs of examples used
            brand_context: Brand context
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "run_id": run_id,
            "stage": stage,
            "example_ids": example_ids,
            "brand_name": brand_context.get("brand_name"),
            "industry": brand_context.get("industry")
        }
        self.usage_log.append(log_entry)

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics

        Returns:
            Dictionary with usage stats
        """
        if not self.usage_log:
            return {"total_uses": 0}

        # Count example usage
        example_counts = {}
        for entry in self.usage_log:
            for ex_id in entry["example_ids"]:
                example_counts[ex_id] = example_counts.get(ex_id, 0) + 1

        return {
            "total_uses": len(self.usage_log),
            "unique_examples_used": len(example_counts),
            "most_used_examples": sorted(
                example_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }


def format_examples_for_stage(examples: List[Dict[str, Any]], stage: int) -> str:
    """
    Format examples for optimal LLM consumption based on stage

    Args:
        examples: List of selected examples
        stage: Pipeline stage (0-6)

    Returns:
        Formatted examples string
    """
    if not examples:
        return ""

    formatted = "\n## Few-Shot Examples\n\n"
    formatted += "Here are successful examples from similar brands to guide your output:\n\n"

    for i, ex in enumerate(examples, 1):
        formatted += f"### Example {i}"

        # Add brand context if available
        brand = ex.get("brand_context", {})
        if brand.get("brand_name"):
            formatted += f" (Brand: {brand['brand_name']}"
            if brand.get("industry"):
                formatted += f", Industry: {brand['industry']}"
            formatted += ")"

        formatted += "\n\n"

        # Stage-specific formatting
        if stage == 0:
            # Stage 0: Brand Enrichment
            formatted += _format_stage_0_example(ex)
        elif stage == 1:
            # Stage 1: Trend Decomposition
            formatted += _format_stage_1_example(ex)
        elif stage == 2:
            # Stage 2: Consumer Insights
            formatted += _format_stage_2_example(ex)
        elif stage == 3:
            # Stage 3: Technique Matching
            formatted += _format_stage_3_example(ex)
        elif stage == 4:
            # Stage 4: Concept Generation
            formatted += _format_stage_4_example(ex)
        elif stage == 5:
            # Stage 5: Competitive Intelligence
            formatted += _format_stage_5_example(ex)
        elif stage == 6:
            # Stage 6: Packaging
            formatted += _format_stage_6_example(ex)

        formatted += "\n---\n\n"

    formatted += "Now, following the pattern and quality of these examples, process the current input:\n\n"

    return formatted


def _format_stage_0_example(ex: Dict[str, Any]) -> str:
    """Format example for Stage 0 (Brand Enrichment)"""
    output = ex.get("output", {})
    return f"""**Input:** Basic brand profile
**Output Enrichment:**
- Positioning: {output.get('enrichment', {}).get('positioning', 'N/A')}
- Competitive Landscape: {output.get('enrichment', {}).get('competitive_landscape', 'N/A')}
"""


def _format_stage_1_example(ex: Dict[str, Any]) -> str:
    """Format example for Stage 1 (Trend Decomposition)"""
    inp = ex.get("input", {})
    output = ex.get("output", {})

    report_excerpt = str(inp.get("report_text", ""))[:200] + "..."
    trends = output.get("trends", [])

    formatted = f"**Input Report Excerpt:**\n{report_excerpt}\n\n"
    formatted += f"**Extracted Trends:** {len(trends)} trend(s)\n"

    if trends:
        trend = trends[0]
        formatted += f"- Trend: {trend.get('name', 'Unknown')}\n"
        formatted += f"- Lifecycle: {trend.get('lifecycle_stage', 'Unknown')}\n"
        formatted += f"- Emotional Drivers: {', '.join(trend.get('emotional_drivers', {}).get('current_negative', [])[:2])}\n"

    return formatted


def _format_stage_2_example(ex: Dict[str, Any]) -> str:
    """Format example for Stage 2 (Consumer Insights)"""
    output = ex.get("output", {})

    if isinstance(output, dict) and "consumer_statement" in output:
        return f"""**Consumer Insight Generated:**
"{output.get('consumer_statement', 'N/A')}"
- Functional Need: {output.get('functional_need', 'N/A')}
- Emotional Need: {output.get('emotional_need', 'N/A')}
"""
    elif isinstance(output, dict) and "insights" in output:
        insights = output["insights"]
        if insights:
            insight = insights[0]
            return f"""**Consumer Insight Generated:**
"{insight.get('consumer_statement', 'N/A')}"
"""
    return "**Output:** Consumer insight generated"


def _format_stage_3_example(ex: Dict[str, Any]) -> str:
    """Format example for Stage 3 (Technique Matching)"""
    output = ex.get("output", {})

    if isinstance(output, dict) and "primary_technique" in output:
        tech = output.get("primary_technique", {})
        return f"""**Technique Matched:**
- Framework: {tech.get('framework', 'N/A')}
- Technique: {tech.get('technique', 'N/A')}
- Rationale: {tech.get('rationale', 'N/A')[:150]}...
"""
    return "**Output:** Innovation technique matched"


def _format_stage_4_example(ex: Dict[str, Any]) -> str:
    """Format example for Stage 4 (Concept Generation)"""
    output = ex.get("output", {})

    if isinstance(output, dict) and "concept_name" in output:
        return f"""**Concept Generated:**
- Name: {output.get('concept_name', 'N/A')}
- Statement: {output.get('concept_statement', 'N/A')[:150]}...
- Mechanism: {output.get('mechanism', 'N/A')[:150]}...
"""
    return "**Output:** Directional concept generated"


def _format_stage_5_example(ex: Dict[str, Any]) -> str:
    """Format example for Stage 5 (Competitive Intelligence)"""
    output = ex.get("output", {})
    return f"""**Competitive Analysis:**
- Search Queries Used: {len(output.get('search_queries', []))}
- Findings: {len(output.get('findings', []))} competitive findings
- Novelty Assessment: {output.get('novelty_assessment', 'N/A')[:100]}...
"""


def _format_stage_6_example(ex: Dict[str, Any]) -> str:
    """Format example for Stage 6 (Packaging)"""
    output = ex.get("output", {})
    return f"""**Opportunity Card:**
- Card ID: {output.get('card_id', 'N/A')}
- Sections: {len(output.get('card_sections', {}))}
- Format: Markdown
"""


def estimate_token_count(text: str) -> int:
    """
    Estimate token count for text (rough approximation)

    Args:
        text: Text to estimate

    Returns:
        Estimated token count
    """
    # Rough estimate: 1 token ≈ 4 characters
    return len(text) // 4


def adjust_examples_for_token_limit(
    examples: List[Dict[str, Any]],
    prompt_template: str,
    token_limit: int
) -> List[Dict[str, Any]]:
    """
    Adjust number of examples to fit within token limit

    Args:
        examples: Selected examples
        prompt_template: Base prompt template
        token_limit: Maximum tokens for examples

    Returns:
        Adjusted list of examples
    """
    if not examples:
        return []

    # Estimate base prompt tokens
    base_tokens = estimate_token_count(prompt_template)

    # Reserve tokens for examples
    available_tokens = token_limit - base_tokens

    if available_tokens <= 0:
        return []

    # Try to fit examples within limit
    adjusted = []
    used_tokens = 0

    for ex in examples:
        # Estimate example size
        ex_str = json.dumps(ex, indent=2)
        ex_tokens = estimate_token_count(ex_str)

        if used_tokens + ex_tokens <= available_tokens:
            adjusted.append(ex)
            used_tokens += ex_tokens
        else:
            break

    return adjusted


def inject_examples_into_prompt(
    prompt_template: str,
    stage: int,
    brand_context: Dict[str, Any],
    storage_path: Optional[str] = None,
    max_examples: int = 3,
    run_id: Optional[str] = None
) -> str:
    """
    Convenience function for injecting examples into prompts

    Args:
        prompt_template: Prompt template
        stage: Pipeline stage (0-6)
        brand_context: Brand context
        storage_path: Optional storage path
        max_examples: Maximum examples to inject
        run_id: Optional run ID for tracking

    Returns:
        Enhanced prompt with examples
    """
    injector = PromptInjector(storage_path=storage_path, max_examples=max_examples)

    return injector.inject_examples(
        prompt_template=prompt_template,
        stage=stage,
        brand_context=brand_context,
        run_id=run_id
    )


if __name__ == "__main__":
    # Test the injector
    print("Testing Prompt Injector")
    print("=" * 50)

    test_prompt = """# Stage 1: Trend Extraction

## Context
Extract trends from the report.

{few_shot_examples}

## Input Report
{report_text}

## Output Format
Return JSON with extracted trends."""

    test_brand = {
        "brand_name": "Test Dairy Co",
        "industry": "Dairy",
        "country": "Canada",
        "product_portfolio": ["Cheese", "Milk"]
    }

    injector = PromptInjector()

    enhanced = injector.inject_examples(
        prompt_template=test_prompt,
        stage=1,
        brand_context=test_brand,
        run_id="test_001"
    )

    print("\nEnhanced Prompt (first 500 chars):")
    print(enhanced[:500])
    print("...")

    print("\nUsage Stats:")
    print(json.dumps(injector.get_usage_stats(), indent=2))
