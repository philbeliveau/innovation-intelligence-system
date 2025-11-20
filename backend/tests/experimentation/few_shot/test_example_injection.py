"""Tests for few-shot example injection into prompts (Story 11.3b)

Tests prompt formatting, token management, and stage integration.
"""
import pytest
from pathlib import Path
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "experimentation"))

from example_selector import ExampleSelector
from prompt_injection import (
    PromptInjector,
    format_examples_for_stage,
    inject_examples_into_prompt,
    estimate_token_count,
    adjust_examples_for_token_limit
)


@pytest.fixture
def temp_storage():
    """Create temporary storage directory for tests"""
    temp_dir = tempfile.mkdtemp()

    # Create stage directories with sample examples
    storage_path = Path(temp_dir)
    stage_dir = storage_path / "stage_1"
    stage_dir.mkdir(parents=True)

    # Create sample example
    example = {
        "id": "example_test_001",
        "created_at": datetime.now().isoformat(),
        "stage": 1,
        "quality_score": "good",
        "usage_count": 0,
        "last_used_at": None,
        "brand_context": {
            "brand_name": "Test Brand",
            "industry": "Dairy",
            "country": "Canada",
            "product_portfolio": ["Milk", "Cheese"]
        },
        "input": {
            "report_text": "Sample trend report about wellness..."
        },
        "prompt_used": "Extract trends...",
        "output": {
            "trends": [
                {
                    "name": "Wellness Focus",
                    "lifecycle_stage": "ACCELERATING"
                }
            ]
        },
        "metadata": {"pipeline_version": "1.0"}
    }

    with open(stage_dir / f"{example['id']}.json", 'w') as f:
        json.dump(example, f)

    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_prompt_template():
    """Sample prompt template with placeholder"""
    return """# Stage 1: Trend Extraction

## Context
Extract trends from the report.

{few_shot_examples}

## Input Report
{report_text}

## Output Format
Return JSON with extracted trends."""


@pytest.fixture
def sample_prompt_no_placeholder():
    """Sample prompt without placeholder"""
    return """# Stage 1: Trend Extraction

## Context
Extract trends from the report.

## Input Report
{report_text}

## Output Format
Return JSON with extracted trends."""


class TestPromptInjector:
    """Test suite for PromptInjector"""

    def test_initialization(self, temp_storage):
        """Test injector initialization"""
        injector = PromptInjector(storage_path=temp_storage)
        assert injector.storage_path == Path(temp_storage)
        assert injector.max_examples == 3
        assert injector.token_limit == 4000

    def test_inject_with_placeholder(self, temp_storage, sample_prompt_template):
        """Test injection with {few_shot_examples} placeholder"""
        injector = PromptInjector(storage_path=temp_storage)

        brand_context = {
            "brand_name": "Similar Brand",
            "industry": "Dairy",
            "country": "Canada",
            "product_portfolio": ["Yogurt"]
        }

        enhanced_prompt = injector.inject_examples(
            prompt_template=sample_prompt_template,
            stage=1,
            brand_context=brand_context
        )

        # Should contain formatted examples
        assert "example_test_001" in enhanced_prompt or "Example" in enhanced_prompt
        assert "{few_shot_examples}" not in enhanced_prompt

    def test_inject_without_placeholder(self, temp_storage, sample_prompt_no_placeholder):
        """Test injection without placeholder (prepend mode)"""
        injector = PromptInjector(storage_path=temp_storage)

        brand_context = {
            "brand_name": "Similar Brand",
            "industry": "Dairy",
            "country": "Canada",
            "product_portfolio": ["Yogurt"]
        }

        enhanced_prompt = injector.inject_examples(
            prompt_template=sample_prompt_no_placeholder,
            stage=1,
            brand_context=brand_context
        )

        # Should prepend examples before Context section
        assert "Example" in enhanced_prompt or "example_test_001" in enhanced_prompt

    def test_inject_no_examples_available(self, temp_storage, sample_prompt_template):
        """Test graceful fallback when no examples available"""
        injector = PromptInjector(storage_path=temp_storage)

        brand_context = {"brand_name": "Test", "industry": "Unknown"}

        # Request stage with no examples
        enhanced_prompt = injector.inject_examples(
            prompt_template=sample_prompt_template,
            stage=5,  # No examples for this stage
            brand_context=brand_context
        )

        # Should return original prompt without examples section
        assert "{few_shot_examples}" not in enhanced_prompt
        assert "Extract trends from the report" in enhanced_prompt

    def test_feature_toggle_disabled(self, temp_storage, sample_prompt_template):
        """Test that FEW_SHOT_ENABLED=false disables injection"""
        injector = PromptInjector(
            storage_path=temp_storage,
            enabled=False
        )

        brand_context = {"brand_name": "Test", "industry": "Dairy"}

        enhanced_prompt = injector.inject_examples(
            prompt_template=sample_prompt_template,
            stage=1,
            brand_context=brand_context
        )

        # Should remove placeholder but not add examples
        assert "{few_shot_examples}" not in enhanced_prompt
        assert "Example 1" not in enhanced_prompt
        # Core content should still be present
        assert "Extract trends from the report" in enhanced_prompt


class TestExampleFormatting:
    """Test example formatting for LLM consumption"""

    def test_format_stage_1_examples(self):
        """Test formatting for stage 1 (trend extraction)"""
        examples = [
            {
                "id": "ex1",
                "input": {"report_text": "Wellness trends emerging..."},
                "output": {"trends": [{"name": "Wellness", "lifecycle_stage": "EMERGING"}]},
                "relevance_score": 0.9
            }
        ]

        formatted = format_examples_for_stage(examples, stage=1)

        assert "Example 1" in formatted
        assert "Wellness" in formatted
        assert "EMERGING" in formatted

    def test_format_stage_2_examples(self):
        """Test formatting for stage 2 (consumer insights)"""
        examples = [
            {
                "id": "ex1",
                "brand_context": {"brand_name": "Test Brand"},
                "input": {"trends": ["Wellness"]},
                "output": {"consumer_statement": "I want healthier options"},
                "relevance_score": 0.85
            }
        ]

        formatted = format_examples_for_stage(examples, stage=2)

        assert "Example 1" in formatted
        assert "Test Brand" in formatted
        assert "healthier options" in formatted

    def test_format_includes_metadata(self):
        """Test that formatting includes helpful metadata"""
        examples = [
            {
                "id": "ex1",
                "brand_context": {"brand_name": "Brand A", "industry": "Dairy"},
                "input": {"test": "input"},
                "output": {"test": "output"},
                "relevance_score": 0.92
            }
        ]

        formatted = format_examples_for_stage(examples, stage=1)

        # Should include brand context
        assert "Brand A" in formatted or "Dairy" in formatted


class TestTokenManagement:
    """Test token counting and example adjustment"""

    def test_estimate_token_count(self):
        """Test token estimation"""
        text = "This is a test prompt with some content."
        tokens = estimate_token_count(text)

        # Rough estimate: ~1 token per 4 characters
        expected = len(text) // 4
        assert abs(tokens - expected) < 5

    def test_adjust_examples_for_token_limit(self):
        """Test that examples are truncated to fit token limit"""
        examples = [
            {"id": f"ex{i}", "content": "x" * 1000} for i in range(10)
        ]

        adjusted = adjust_examples_for_token_limit(
            examples,
            prompt_template="Base prompt",
            token_limit=500
        )

        # Should return fewer examples to fit limit
        assert len(adjusted) < len(examples)

    def test_adjust_examples_no_truncation_needed(self):
        """Test that examples are not truncated if within limit"""
        examples = [
            {"id": "ex1", "content": "short"}
        ]

        adjusted = adjust_examples_for_token_limit(
            examples,
            prompt_template="Base prompt",
            token_limit=5000
        )

        # Should return all examples
        assert len(adjusted) == len(examples)


class TestUsageTracking:
    """Test usage tracking for examples"""

    def test_track_example_usage(self, temp_storage):
        """Test that example usage is tracked"""
        injector = PromptInjector(storage_path=temp_storage, track_usage=True)

        brand_context = {"brand_name": "Test", "industry": "Dairy", "country": "Canada"}

        # Inject examples (should trigger usage tracking)
        prompt = "Test prompt\n\n{few_shot_examples}"
        enhanced = injector.inject_examples(prompt, stage=1, brand_context=brand_context)

        # Verify tracking occurred
        assert hasattr(injector, 'usage_log')
        assert len(injector.usage_log) > 0

    def test_usage_log_includes_metadata(self, temp_storage):
        """Test that usage log includes run_id and example_ids"""
        injector = PromptInjector(storage_path=temp_storage, track_usage=True)

        brand_context = {"brand_name": "Test", "industry": "Dairy", "country": "Canada"}

        enhanced = injector.inject_examples(
            "Test prompt\n\n{few_shot_examples}",
            stage=1,
            brand_context=brand_context,
            run_id="test_run_123"
        )

        # Check usage log
        if injector.usage_log:
            log_entry = injector.usage_log[-1]
            assert "run_id" in log_entry
            assert "example_ids" in log_entry
            assert "stage" in log_entry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
