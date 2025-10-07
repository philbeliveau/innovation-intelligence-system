#!/usr/bin/env python3
"""
Brand Profile Validation Test Script

This script validates all brand profile YAML files in data/brand-profiles/
against the required schema defined in docs/brand-profile-schema.md.

Tests:
1. YAML syntax validation (files parse without errors)
2. Required field presence (all 9 required fields present)
3. Field type validation (strings vs. lists)
4. List field minimum length validation

Usage:
    python test_brand_profiles.py

Exit codes:
    0 - All tests passed
    1 - One or more tests failed
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any

# Define schema requirements
REQUIRED_FIELDS = {
    'brand_name': str,
    'country': str,
    'industry': str,
    'positioning': str,
    'product_portfolio': list,
    'target_customers': list,
    'recent_innovations': list,
    'strategic_priorities': list,
    'brand_values': list
}

MINIMUM_LIST_LENGTHS = {
    'product_portfolio': 3,
    'target_customers': 2,
    'recent_innovations': 3,
    'strategic_priorities': 3,
    'brand_values': 3
}

BRAND_PROFILES_DIR = Path('data/brand-profiles')
EXPECTED_PROFILES = [
    'lactalis-canada.yaml',
    'mccormick-usa.yaml',
    'columbia-sportswear.yaml',
    'decathlon.yaml'
]


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_yaml_syntax(file_path: Path) -> Dict[str, Any]:
    """
    Validate that file is valid YAML and can be parsed.

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML data as dictionary

    Raises:
        ValidationError: If YAML syntax is invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if data is None:
            raise ValidationError("YAML file is empty")

        if not isinstance(data, dict):
            raise ValidationError("YAML root element must be a dictionary")

        return data

    except yaml.YAMLError as e:
        raise ValidationError(f"YAML syntax error: {e}")
    except Exception as e:
        raise ValidationError(f"Error reading file: {e}")


def validate_required_fields(data: Dict[str, Any], file_name: str) -> None:
    """
    Validate that all required fields are present.

    Args:
        data: Parsed YAML data
        file_name: Name of the file being validated

    Raises:
        ValidationError: If required fields are missing
    """
    missing_fields = []

    for field_name in REQUIRED_FIELDS.keys():
        if field_name not in data:
            missing_fields.append(field_name)

    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )


def validate_field_types(data: Dict[str, Any], file_name: str) -> None:
    """
    Validate that fields have correct data types.

    Args:
        data: Parsed YAML data
        file_name: Name of the file being validated

    Raises:
        ValidationError: If field types are incorrect
    """
    type_errors = []

    for field_name, expected_type in REQUIRED_FIELDS.items():
        if field_name in data:
            actual_value = data[field_name]

            if not isinstance(actual_value, expected_type):
                type_errors.append(
                    f"{field_name}: expected {expected_type.__name__}, "
                    f"got {type(actual_value).__name__}"
                )

    if type_errors:
        raise ValidationError(
            f"Field type errors:\n  - " + "\n  - ".join(type_errors)
        )


def validate_list_lengths(data: Dict[str, Any], file_name: str) -> None:
    """
    Validate that list fields meet minimum length requirements.

    Args:
        data: Parsed YAML data
        file_name: Name of the file being validated

    Raises:
        ValidationError: If lists are too short
    """
    length_errors = []

    for field_name, min_length in MINIMUM_LIST_LENGTHS.items():
        if field_name in data:
            actual_length = len(data[field_name])

            if actual_length < min_length:
                length_errors.append(
                    f"{field_name}: has {actual_length} items, "
                    f"minimum {min_length} required"
                )

    if length_errors:
        raise ValidationError(
            f"List length errors:\n  - " + "\n  - ".join(length_errors)
        )


def validate_profile(file_path: Path) -> bool:
    """
    Run all validation tests on a single brand profile.

    Args:
        file_path: Path to brand profile YAML file

    Returns:
        True if all validations pass, False otherwise
    """
    file_name = file_path.name
    print(f"\n{'='*60}")
    print(f"Validating: {file_name}")
    print('='*60)

    try:
        # Test 1: YAML syntax
        print("✓ YAML syntax validation...", end=' ')
        data = validate_yaml_syntax(file_path)
        print("PASSED")

        # Test 2: Required fields
        print("✓ Required fields validation...", end=' ')
        validate_required_fields(data, file_name)
        print("PASSED")

        # Test 3: Field types
        print("✓ Field type validation...", end=' ')
        validate_field_types(data, file_name)
        print("PASSED")

        # Test 4: List lengths
        print("✓ List length validation...", end=' ')
        validate_list_lengths(data, file_name)
        print("PASSED")

        print(f"\n✅ {file_name}: ALL TESTS PASSED")
        return True

    except ValidationError as e:
        print(f"FAILED")
        print(f"\n❌ {file_name}: VALIDATION FAILED")
        print(f"Error: {e}")
        return False

    except Exception as e:
        print(f"FAILED")
        print(f"\n❌ {file_name}: UNEXPECTED ERROR")
        print(f"Error: {e}")
        return False


def main():
    """Main test execution"""
    print("="*60)
    print("Brand Profile Validation Test Suite")
    print("="*60)
    print(f"Profiles directory: {BRAND_PROFILES_DIR}")
    print(f"Expected profiles: {len(EXPECTED_PROFILES)}")

    # Check that profiles directory exists
    if not BRAND_PROFILES_DIR.exists():
        print(f"\n❌ ERROR: Profiles directory not found: {BRAND_PROFILES_DIR}")
        sys.exit(1)

    # Check that expected profiles exist
    missing_profiles = []
    for profile_name in EXPECTED_PROFILES:
        profile_path = BRAND_PROFILES_DIR / profile_name
        if not profile_path.exists():
            missing_profiles.append(profile_name)

    if missing_profiles:
        print(f"\n❌ ERROR: Missing expected profiles:")
        for profile in missing_profiles:
            print(f"  - {profile}")
        sys.exit(1)

    # Validate each profile
    results = []
    for profile_name in EXPECTED_PROFILES:
        profile_path = BRAND_PROFILES_DIR / profile_name
        passed = validate_profile(profile_path)
        results.append((profile_name, passed))

    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)

    passed_count = sum(1 for _, passed in results if passed)
    failed_count = len(results) - passed_count

    for profile_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {profile_name}")

    print(f"\nTotal: {len(results)} profiles")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")

    # Exit with appropriate code
    if failed_count > 0:
        print("\n❌ VALIDATION FAILED")
        sys.exit(1)
    else:
        print("\n✅ ALL VALIDATIONS PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
