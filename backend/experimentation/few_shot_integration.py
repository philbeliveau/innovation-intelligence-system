"""Few-Shot Integration Helper for Pipeline Stages (Story 11.3b)

Provides utilities for stages to inject few-shot examples into prompts.
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path

from backend.experimentation.prompt_injection import PromptInjector


# Global injector instance (lazy loaded)
_injector: Optional[PromptInjector] = None


def get_injector() -> PromptInjector:
    """
    Get or create global PromptInjector instance

    Returns:
        PromptInjector instance
    """
    global _injector

    if _injector is None:
        # Check environment variable for feature toggle
        enabled = os.environ.get("FEW_SHOT_ENABLED", "true").lower() == "true"

        # Get configuration from environment
        max_examples = int(os.environ.get("FEW_SHOT_MAX_EXAMPLES", "3"))
        token_limit = int(os.environ.get("FEW_SHOT_TOKEN_LIMIT", "4000"))

        _injector = PromptInjector(
            max_examples=max_examples,
            token_limit=token_limit,
            enabled=enabled
        )

    return _injector


def inject_examples_into_stage_prompt(
    prompt_template: str,
    stage: int,
    brand_context: Dict[str, Any],
    run_id: Optional[str] = None
) -> str:
    """
    Inject few-shot examples into stage prompt

    This is the main integration point for stages.

    Args:
        prompt_template: Loaded prompt template (with {few_shot_examples} placeholder)
        stage: Pipeline stage number (0-6)
        brand_context: Brand context from Stage 0
        run_id: Optional pipeline run ID for usage tracking

    Returns:
        Enhanced prompt with injected examples (or original if disabled)

    Example:
        ```python
        from prompt_template_library import load_prompt_template
        from few_shot_integration import inject_examples_into_stage_prompt

        # In stage implementation
        prompt_template = load_prompt_template("stage_1_extraction")
        enhanced_prompt = inject_examples_into_stage_prompt(
            prompt_template=prompt_template,
            stage=1,
            brand_context=brand_enrichment.dict(),
            run_id=run_id
        )
        ```
    """
    injector = get_injector()

    return injector.inject_examples(
        prompt_template=prompt_template,
        stage=stage,
        brand_context=brand_context,
        run_id=run_id
    )


def get_usage_stats() -> Dict[str, Any]:
    """
    Get usage statistics for examples

    Returns:
        Dictionary with usage stats
    """
    injector = get_injector()
    return injector.get_usage_stats()


def is_few_shot_enabled() -> bool:
    """
    Check if few-shot learning is enabled

    Returns:
        True if enabled, False otherwise
    """
    return os.environ.get("FEW_SHOT_ENABLED", "true").lower() == "true"


# Configuration getters
def get_max_examples() -> int:
    """Get configured max examples per stage"""
    return int(os.environ.get("FEW_SHOT_MAX_EXAMPLES", "3"))


def get_token_limit() -> int:
    """Get configured token limit for examples"""
    return int(os.environ.get("FEW_SHOT_TOKEN_LIMIT", "4000"))


if __name__ == "__main__":
    # Test the integration
    print("Few-Shot Integration Configuration")
    print("=" * 50)
    print(f"Enabled: {is_few_shot_enabled()}")
    print(f"Max Examples: {get_max_examples()}")
    print(f"Token Limit: {get_token_limit()}")

    # Test injection
    test_prompt = """# Stage 1: Test

{few_shot_examples}

Extract trends from: {report_text}"""

    test_brand = {
        "brand_name": "Test Co",
        "industry": "Dairy",
        "country": "Canada",
        "product_portfolio": ["Milk"]
    }

    enhanced = inject_examples_into_stage_prompt(
        prompt_template=test_prompt,
        stage=1,
        brand_context=test_brand,
        run_id="test_001"
    )

    print("\nEnhanced Prompt (first 300 chars):")
    print(enhanced[:300])
    print("...")

    print("\nUsage Stats:")
    import json
    print(json.dumps(get_usage_stats(), indent=2))
