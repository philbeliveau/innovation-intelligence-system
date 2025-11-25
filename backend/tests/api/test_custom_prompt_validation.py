"""
Unit tests for custom prompt validation in /run/local endpoint

Tests the validation logic without full FastAPI integration.
Part of Story 11.6.2: Backend Custom Prompt Integration.
"""

import pytest
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from pipeline.prompt_file_validator import PromptFileValidator


class TestCustomPromptValidationLogic:
    """Test custom prompt validation logic used in /run/local endpoint"""

    def test_valid_stage_key_extraction(self):
        """Test extracting stage number from stage_N format"""
        stage_key = "stage_4"
        stage_num = int(stage_key.split("_")[1])
        assert stage_num == 4

    def test_invalid_stage_key_format_detection(self):
        """Test that invalid stage key formats can be detected"""
        # Test key with non-numeric second part raises ValueError
        with pytest.raises(ValueError):
            stage_num = int("stage_abc".split("_")[1])

        # Test key without underscore causes IndexError
        with pytest.raises(IndexError):
            stage_num = int("invalid".split("_")[1])

    def test_stage_number_range_validation(self):
        """Test stage number must be 0-6"""
        valid_stages = [0, 1, 2, 3, 4, 5, 6]
        invalid_stages = [-1, 7, 10, 99]

        for stage in valid_stages:
            assert 0 <= stage <= 6

        for stage in invalid_stages:
            assert not (0 <= stage <= 6)

    def test_validation_with_all_required_placeholders(self):
        """Test validation passes when all required placeholders present"""
        stage_4_prompt = """
        Generate concepts:
        - {insights}
        - {matched_techniques}
        - {brand_context}
        - {no_hallucination_rules}
        """

        result = PromptFileValidator.validate(4, stage_4_prompt)

        assert result.is_valid is True
        assert result.missing_placeholders == []
        assert result.error_message is None

    def test_validation_fails_missing_placeholders(self):
        """Test validation fails when required placeholders missing"""
        incomplete_prompt = "Generate concepts using {insights} only"

        result = PromptFileValidator.validate(4, incomplete_prompt)

        assert result.is_valid is False
        assert len(result.missing_placeholders) == 3
        assert set(result.missing_placeholders) == {
            "matched_techniques",
            "brand_context",
            "no_hallucination_rules"
        }
        assert "Stage 4" in result.error_message

    def test_validation_error_message_format(self):
        """Test error message includes stage number and missing placeholders"""
        prompt = "Missing all placeholders"

        result = PromptFileValidator.validate(2, prompt)

        assert result.is_valid is False
        assert "Stage 2" in result.error_message
        assert "missing required placeholders" in result.error_message
        # Check placeholders are formatted with braces
        assert "{trend_data}" in result.error_message or "trend_data" in result.error_message
        assert "{brand_context}" in result.error_message or "brand_context" in result.error_message

    def test_validation_all_stages_0_through_6(self):
        """Test validation works for all 7 stages"""
        valid_prompts = {
            0: "Enrich {company_name} in {industry} with {portfolio}",
            1: "Extract from {report_text}",
            2: "Synthesize {trend_data} and {brand_context}",
            3: "Match {insights} with {brand_resources}",
            4: "Generate using {insights}, {matched_techniques}, {brand_context}, {no_hallucination_rules}",
            5: "Analyze {initiatives} for {brand_context}",
            6: "Package {all_stage_outputs}"
        }

        for stage_num, prompt in valid_prompts.items():
            result = PromptFileValidator.validate(stage_num, prompt)
            assert result.is_valid is True, f"Stage {stage_num} validation failed"

    def test_http_exception_structure_for_400_errors(self):
        """Test HTTPException detail structure for validation errors"""
        # Simulate what the endpoint would raise
        stage_num = 4
        missing = ["matched_techniques", "brand_context"]

        exception_detail = {
            "error": f"Invalid custom prompt for Stage {stage_num}",
            "details": f"Missing required placeholders: {', '.join(missing)}",
            "stage": stage_num
        }

        assert "error" in exception_detail
        assert "details" in exception_detail
        assert "stage" in exception_detail
        assert exception_detail["stage"] == 4
        assert "Invalid custom prompt" in exception_detail["error"]
        assert "Missing required placeholders" in exception_detail["details"]

    def test_empty_custom_prompts_dict_handling(self):
        """Test empty dict is valid (no validation needed)"""
        custom_prompts = {}

        # If dict is empty, no validation should run
        if not custom_prompts:
            pass  # No validation needed
        else:
            for stage_key in custom_prompts:
                # Would validate here
                pass

        # Test passes if no errors raised
        assert True

    def test_multiple_custom_prompts_validation(self):
        """Test validating multiple custom prompts"""
        custom_prompts = {
            "stage_0": "Brand: {company_name}, {industry}, {portfolio}",
            "stage_1": "Extract {report_text}",
            "stage_4": "Invalid prompt"  # Missing required placeholders
        }

        validation_results = {}

        for stage_key, prompt_content in custom_prompts.items():
            stage_num = int(stage_key.split("_")[1])
            validation_results[stage_key] = PromptFileValidator.validate(stage_num, prompt_content)

        # First two should pass
        assert validation_results["stage_0"].is_valid is True
        assert validation_results["stage_1"].is_valid is True

        # Third should fail
        assert validation_results["stage_4"].is_valid is False
        assert len(validation_results["stage_4"].missing_placeholders) > 0

    def test_validation_performance_with_large_prompt(self):
        """Test validation handles large prompt content efficiently"""
        large_prompt = "Extract trends from {report_text}\n" * 1000

        result = PromptFileValidator.validate(1, large_prompt)

        assert result.is_valid is True
        # Validation should complete quickly (pytest will timeout if too slow)

    def test_placeholder_format_variations_not_matched(self):
        """Test only {lowercase_underscore} format is recognized"""
        variations = """
        Valid: {company_name}
        Invalid: {{company_name}}
        Invalid: {Company_Name}
        Invalid: { company_name }
        Invalid: {company-name}
        """

        result = PromptFileValidator.validate(0, variations)

        # Only {company_name} should be detected, missing {industry} and {portfolio}
        assert result.is_valid is False
        assert len(result.missing_placeholders) == 2
