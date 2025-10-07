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
5. Edge case validation (empty values, malformed data)

Usage:
    pytest test_brand_profiles.py -v

    Or for legacy standalone mode:
    python test_brand_profiles.py

Exit codes:
    0 - All tests passed
    1 - One or more tests failed
"""

import logging
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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

# Configuration - can be overridden by environment or config file
PROJECT_ROOT = Path(__file__).parent
BRAND_PROFILES_DIR = PROJECT_ROOT / 'data' / 'brand-profiles'
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

    Example:
        >>> data = validate_yaml_syntax(Path("data/brand-profiles/test.yaml"))
        >>> assert isinstance(data, dict)
    """
    if not file_path.exists():
        logging.error(f"Brand profile file not found: {file_path}")
        raise ValidationError(f"File not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if data is None:
            raise ValidationError("YAML file is empty")

        if not isinstance(data, dict):
            raise ValidationError("YAML root element must be a dictionary")

        logging.debug(f"Successfully parsed YAML: {file_path.name}")
        return data

    except yaml.YAMLError as e:
        logging.error(f"YAML syntax error in {file_path}: {e}")
        raise ValidationError(f"YAML syntax error: {e}")
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
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


# ============ Pytest-compatible test functions ============

def test_brand_profiles_directory_exists():
    """Test that brand profiles directory exists."""
    assert BRAND_PROFILES_DIR.exists(), \
        f"Brand profiles directory not found: {BRAND_PROFILES_DIR}"
    logging.info(f"✓ Brand profiles directory exists: {BRAND_PROFILES_DIR}")


def test_all_expected_profiles_exist():
    """Test that all expected brand profile files exist."""
    missing_profiles = []
    for profile_name in EXPECTED_PROFILES:
        profile_path = BRAND_PROFILES_DIR / profile_name
        if not profile_path.exists():
            missing_profiles.append(profile_name)

    assert len(missing_profiles) == 0, \
        f"Missing expected profiles: {', '.join(missing_profiles)}"
    logging.info(f"✓ All {len(EXPECTED_PROFILES)} expected profiles exist")


def test_lactalis_canada_yaml_syntax():
    """Test Lactalis Canada profile YAML syntax."""
    profile_path = BRAND_PROFILES_DIR / 'lactalis-canada.yaml'
    data = validate_yaml_syntax(profile_path)
    assert isinstance(data, dict)
    logging.info("✓ Lactalis Canada: YAML syntax valid")


def test_lactalis_canada_required_fields():
    """Test Lactalis Canada profile has all required fields."""
    profile_path = BRAND_PROFILES_DIR / 'lactalis-canada.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_required_fields(data, profile_path.name)
    logging.info("✓ Lactalis Canada: All required fields present")


def test_lactalis_canada_field_types():
    """Test Lactalis Canada profile has correct field types."""
    profile_path = BRAND_PROFILES_DIR / 'lactalis-canada.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_field_types(data, profile_path.name)
    logging.info("✓ Lactalis Canada: Field types correct")


def test_lactalis_canada_list_lengths():
    """Test Lactalis Canada profile lists meet minimum lengths."""
    profile_path = BRAND_PROFILES_DIR / 'lactalis-canada.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_list_lengths(data, profile_path.name)
    logging.info("✓ Lactalis Canada: List lengths adequate")


def test_mccormick_usa_yaml_syntax():
    """Test McCormick USA profile YAML syntax."""
    profile_path = BRAND_PROFILES_DIR / 'mccormick-usa.yaml'
    data = validate_yaml_syntax(profile_path)
    assert isinstance(data, dict)
    logging.info("✓ McCormick USA: YAML syntax valid")


def test_mccormick_usa_required_fields():
    """Test McCormick USA profile has all required fields."""
    profile_path = BRAND_PROFILES_DIR / 'mccormick-usa.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_required_fields(data, profile_path.name)
    logging.info("✓ McCormick USA: All required fields present")


def test_mccormick_usa_field_types():
    """Test McCormick USA profile has correct field types."""
    profile_path = BRAND_PROFILES_DIR / 'mccormick-usa.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_field_types(data, profile_path.name)
    logging.info("✓ McCormick USA: Field types correct")


def test_mccormick_usa_list_lengths():
    """Test McCormick USA profile lists meet minimum lengths."""
    profile_path = BRAND_PROFILES_DIR / 'mccormick-usa.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_list_lengths(data, profile_path.name)
    logging.info("✓ McCormick USA: List lengths adequate")


def test_columbia_sportswear_yaml_syntax():
    """Test Columbia Sportswear profile YAML syntax."""
    profile_path = BRAND_PROFILES_DIR / 'columbia-sportswear.yaml'
    data = validate_yaml_syntax(profile_path)
    assert isinstance(data, dict)
    logging.info("✓ Columbia Sportswear: YAML syntax valid")


def test_columbia_sportswear_required_fields():
    """Test Columbia Sportswear profile has all required fields."""
    profile_path = BRAND_PROFILES_DIR / 'columbia-sportswear.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_required_fields(data, profile_path.name)
    logging.info("✓ Columbia Sportswear: All required fields present")


def test_columbia_sportswear_field_types():
    """Test Columbia Sportswear profile has correct field types."""
    profile_path = BRAND_PROFILES_DIR / 'columbia-sportswear.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_field_types(data, profile_path.name)
    logging.info("✓ Columbia Sportswear: Field types correct")


def test_columbia_sportswear_list_lengths():
    """Test Columbia Sportswear profile lists meet minimum lengths."""
    profile_path = BRAND_PROFILES_DIR / 'columbia-sportswear.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_list_lengths(data, profile_path.name)
    logging.info("✓ Columbia Sportswear: List lengths adequate")


def test_decathlon_yaml_syntax():
    """Test Decathlon profile YAML syntax."""
    profile_path = BRAND_PROFILES_DIR / 'decathlon.yaml'
    data = validate_yaml_syntax(profile_path)
    assert isinstance(data, dict)
    logging.info("✓ Decathlon: YAML syntax valid")


def test_decathlon_required_fields():
    """Test Decathlon profile has all required fields."""
    profile_path = BRAND_PROFILES_DIR / 'decathlon.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_required_fields(data, profile_path.name)
    logging.info("✓ Decathlon: All required fields present")


def test_decathlon_field_types():
    """Test Decathlon profile has correct field types."""
    profile_path = BRAND_PROFILES_DIR / 'decathlon.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_field_types(data, profile_path.name)
    logging.info("✓ Decathlon: Field types correct")


def test_decathlon_list_lengths():
    """Test Decathlon profile lists meet minimum lengths."""
    profile_path = BRAND_PROFILES_DIR / 'decathlon.yaml'
    data = validate_yaml_syntax(profile_path)
    validate_list_lengths(data, profile_path.name)
    logging.info("✓ Decathlon: List lengths adequate")


def test_no_empty_string_values():
    """Test that no profile contains empty string values in required fields."""
    for profile_name in EXPECTED_PROFILES:
        profile_path = BRAND_PROFILES_DIR / profile_name
        data = validate_yaml_syntax(profile_path)

        # Check string fields
        for field in ['brand_name', 'country', 'industry', 'positioning']:
            value = data.get(field, '')
            assert value and value.strip(), \
                f"{profile_name}: {field} is empty or whitespace"

        # Check list fields have non-empty items
        for field in ['product_portfolio', 'target_customers', 'recent_innovations',
                      'strategic_priorities', 'brand_values']:
            items = data.get(field, [])
            for item in items:
                assert item and item.strip(), \
                    f"{profile_name}: {field} contains empty item"

    logging.info("✓ All profiles: No empty values detected")


def test_positioning_length_reasonable():
    """Test that positioning statements are reasonable length (not too short or long)."""
    for profile_name in EXPECTED_PROFILES:
        profile_path = BRAND_PROFILES_DIR / profile_name
        data = validate_yaml_syntax(profile_path)
        positioning = data.get('positioning', '')

        # Should be at least 50 characters and no more than 500
        assert 50 <= len(positioning) <= 500, \
            f"{profile_name}: positioning length {len(positioning)} not in range 50-500"

    logging.info("✓ All profiles: Positioning statements have reasonable length")


if __name__ == '__main__':
    main()
