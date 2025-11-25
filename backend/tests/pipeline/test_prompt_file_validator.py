"""
Unit tests for PromptFileValidator

Tests validation logic for custom prompt content.
Part of Story 11.6.2: Backend Custom Prompt Integration.
"""

import pytest
from backend.pipeline.prompt_file_validator import PromptFileValidator, ValidationResult


class TestPromptFileValidator:
    """Test suite for PromptFileValidator class"""

    def test_validate_stage_0_valid_prompt(self):
        """Test Stage 0 validation with all required placeholders"""
        content = """
        Enrich brand profile for {company_name} in {industry}.
        Portfolio: {portfolio}
        """
        result = PromptFileValidator.validate(0, content)

        assert result.is_valid is True
        assert result.missing_placeholders == []
        assert result.error_message is None

    def test_validate_stage_1_valid_prompt(self):
        """Test Stage 1 validation with report_text placeholder"""
        content = "Extract trends from: {report_text}"
        result = PromptFileValidator.validate(1, content)

        assert result.is_valid is True
        assert result.missing_placeholders == []
        assert result.error_message is None

    def test_validate_stage_4_valid_prompt(self):
        """Test Stage 4 validation with all 4 required placeholders"""
        content = """
        Generate concepts using:
        - Insights: {insights}
        - Techniques: {matched_techniques}
        - Brand: {brand_context}
        - Rules: {no_hallucination_rules}
        """
        result = PromptFileValidator.validate(4, content)

        assert result.is_valid is True
        assert result.missing_placeholders == []
        assert result.error_message is None

    def test_validate_missing_single_placeholder(self):
        """Test validation fails when one placeholder is missing"""
        content = "Extract trends without placeholder"
        result = PromptFileValidator.validate(1, content)

        assert result.is_valid is False
        assert result.missing_placeholders == ["report_text"]
        assert "Stage 1" in result.error_message
        assert "{report_text}" in result.error_message

    def test_validate_missing_multiple_placeholders(self):
        """Test validation fails with multiple missing placeholders"""
        content = "Generate concepts using {insights} only"
        result = PromptFileValidator.validate(4, content)

        assert result.is_valid is False
        assert set(result.missing_placeholders) == {
            "matched_techniques",
            "brand_context",
            "no_hallucination_rules"
        }
        assert "Stage 4" in result.error_message
        assert "missing required placeholders" in result.error_message

    def test_validate_extra_placeholders_allowed(self):
        """Test validation passes when extra (non-required) placeholders present"""
        content = """
        Extract trends from {report_text}
        Additional context: {extra_field}
        Custom instructions: {another_extra}
        """
        result = PromptFileValidator.validate(1, content)

        # Extra placeholders should not cause validation to fail
        assert result.is_valid is True
        assert result.missing_placeholders == []
        assert result.error_message is None

    def test_validate_case_sensitive_placeholders(self):
        """Test placeholder matching is case-sensitive (lowercase only)"""
        content = """
        Company: {COMPANY_NAME}
        Industry: {Industry}
        Portfolio: {portfolio}
        """
        result = PromptFileValidator.validate(0, content)

        # Only {portfolio} should match (lowercase), uppercase variants ignored
        assert result.is_valid is False
        assert set(result.missing_placeholders) == {"company_name", "industry"}

    def test_validate_placeholder_with_underscores(self):
        """Test placeholders with underscores are matched correctly"""
        content = "Rules: {no_hallucination_rules} and context: {brand_context}"
        result = PromptFileValidator.validate(5, content)

        # Should find both placeholders despite underscores
        assert result.is_valid is False
        assert result.missing_placeholders == ["initiatives"]

    def test_validate_empty_content(self):
        """Test validation fails for empty content"""
        result = PromptFileValidator.validate(1, "")

        assert result.is_valid is False
        assert result.missing_placeholders == ["report_text"]
        assert result.error_message is not None

    def test_validate_all_stages_have_requirements(self):
        """Test all stages 0-6 have placeholder requirements defined"""
        for stage_num in range(7):
            assert stage_num in PromptFileValidator.REQUIRED_PLACEHOLDERS
            assert len(PromptFileValidator.REQUIRED_PLACEHOLDERS[stage_num]) > 0

    def test_validate_stage_6_all_stage_outputs(self):
        """Test Stage 6 requires all_stage_outputs placeholder"""
        content = "Package results from {all_stage_outputs}"
        result = PromptFileValidator.validate(6, content)

        assert result.is_valid is True
        assert result.missing_placeholders == []

    def test_validate_placeholder_format_strict(self):
        """Test only {lowercase_underscore} format is matched"""
        content = """
        Valid: {company_name}
        Invalid formats:
        - {{company_name}}  (double braces)
        - {Company_Name}     (mixed case)
        - { company_name }   (spaces)
        - {company-name}     (hyphens)
        """
        result = PromptFileValidator.validate(0, content)

        # Only {company_name} should match
        assert result.is_valid is False
        assert set(result.missing_placeholders) == {"industry", "portfolio"}

    def test_validation_result_dataclass_structure(self):
        """Test ValidationResult dataclass has correct structure"""
        result = ValidationResult(
            is_valid=False,
            missing_placeholders=["field1", "field2"],
            error_message="Test error"
        )

        assert hasattr(result, "is_valid")
        assert hasattr(result, "missing_placeholders")
        assert hasattr(result, "error_message")
        assert result.is_valid is False
        assert result.missing_placeholders == ["field1", "field2"]
        assert result.error_message == "Test error"

    def test_validate_invalid_stage_number(self):
        """Test validation handles invalid stage numbers gracefully"""
        content = "Some content {placeholder}"
        result = PromptFileValidator.validate(99, content)

        # Should return valid for unknown stages (no requirements)
        assert result.is_valid is True
        assert result.missing_placeholders == []

    def test_validate_stage_2_both_placeholders(self):
        """Test Stage 2 requires both trend_data and brand_context"""
        content_partial = "Analyze {trend_data}"
        result_partial = PromptFileValidator.validate(2, content_partial)

        assert result_partial.is_valid is False
        assert result_partial.missing_placeholders == ["brand_context"]

        content_complete = "Analyze {trend_data} for {brand_context}"
        result_complete = PromptFileValidator.validate(2, content_complete)

        assert result_complete.is_valid is True
        assert result_complete.missing_placeholders == []

    def test_validate_stage_3_both_placeholders(self):
        """Test Stage 3 requires insights and brand_resources"""
        content = "Match techniques for {insights} using {brand_resources}"
        result = PromptFileValidator.validate(3, content)

        assert result.is_valid is True
        assert result.missing_placeholders == []
