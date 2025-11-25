"""
Prompt File Validator for Custom Prompt Upload System

Validates custom prompt content for required placeholders before pipeline execution.
Part of Story 11.6.2: Backend Custom Prompt Integration.
"""

import re
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of prompt validation"""
    is_valid: bool
    missing_placeholders: List[str]
    error_message: Optional[str]


class PromptFileValidator:
    """
    Validates custom prompt content for required placeholders.

    Uses regex pattern matching to ensure all required placeholders
    are present in custom prompt content before pipeline execution.
    """

    # Required placeholders per stage (from Story 11.6.2 AC)
    REQUIRED_PLACEHOLDERS = {
        0: ["company_name", "industry", "portfolio"],
        1: ["report_text"],
        2: ["trend_data", "brand_context"],
        3: ["insights", "brand_resources"],
        4: ["insights", "matched_techniques", "brand_context", "no_hallucination_rules"],
        5: ["initiatives", "brand_context"],
        6: ["all_stage_outputs"]
    }

    @classmethod
    def validate(cls, stage: int, content: str) -> ValidationResult:
        """
        Validate custom prompt content for required placeholders.

        Args:
            stage: Stage number (0-6)
            content: Custom prompt content string

        Returns:
            ValidationResult with is_valid, missing_placeholders, and error_message

        Example:
            >>> result = PromptFileValidator.validate(4, "Generate concepts using {insights}")
            >>> print(result.is_valid)
            False
            >>> print(result.missing_placeholders)
            ['matched_techniques', 'brand_context', 'no_hallucination_rules']
        """
        # Get required placeholders for this stage
        required = cls.REQUIRED_PLACEHOLDERS.get(stage, [])

        # Extract placeholders from content using regex pattern: {placeholder_name}
        # Pattern matches: {lowercase_letters_and_underscores}
        found_placeholders = set(re.findall(r'\{([a-z_]+)\}', content))

        # Check for missing required placeholders
        missing = [p for p in required if p not in found_placeholders]

        if missing:
            # Format missing placeholders with braces for clarity
            missing_formatted = ', '.join(f'{{{p}}}' for p in missing)
            return ValidationResult(
                is_valid=False,
                missing_placeholders=missing,
                error_message=f"Stage {stage} missing required placeholders: {missing_formatted}"
            )

        # Validation passed (extra placeholders are allowed)
        return ValidationResult(
            is_valid=True,
            missing_placeholders=[],
            error_message=None
        )
