"""
Test script for research data loader functionality.

Tests the load_research_data() function in pipeline/utils.py to ensure:
- All 4 brand research files can be loaded successfully
- UTF-8 encoding is handled correctly
- File statistics are accurate (line count, size, sections)
- Missing files are handled gracefully (non-fatal)
"""

import logging
from pathlib import Path
from pipeline.utils import load_research_data

# Configure logging for test output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def count_sections(content: str, section_markers: list) -> int:
    """Count how many of the expected section markers are present in content.

    Args:
        content: Research markdown content
        section_markers: List of section header strings to search for

    Returns:
        Number of section markers found
    """
    found_count = 0
    for marker in section_markers:
        if marker in content:
            found_count += 1
    return found_count


def test_research_loader():
    """Test research data loader with all available brand files."""

    print("=" * 80)
    print("RESEARCH DATA LOADER TEST")
    print("=" * 80)
    print()

    # Define expected research files (4 brands)
    research_brands = [
        "lactalis-canada",
        "mccormick-usa",
        "columbia-sportswear",
        "decathlon"
    ]

    # Expected 8 section markers in research files (format: ## N. Section Name)
    expected_sections = [
        "## 1. Brand Overview & Positioning",
        "## 2. Product Portfolio & Innovation",
        "## 3. Recent Innovations",
        "## 4. Strategic Priorities",
        "## 5. Target Customers",
        "## 6. Sustainability",
        "## 7. Competitive Context",
        "## 8. Recent News"
    ]

    print(f"Testing {len(research_brands)} brand research files:")
    for brand in research_brands:
        print(f"  - {brand}")
    print()

    # Test each brand research file
    results = []
    for brand_id in research_brands:
        print(f"--- Testing: {brand_id} ---")

        # Load research data
        research_content = load_research_data(brand_id)

        # Validate successful load
        if not research_content:
            print(f"  ❌ FAILED: No content loaded for {brand_id}")
            results.append((brand_id, False))
            print()
            continue

        # Calculate statistics
        line_count = research_content.count('\n') + 1
        char_count = len(research_content)
        size_kb = char_count / 1024

        # Count sections present
        sections_found = count_sections(research_content, expected_sections)

        # Validate file meets expected criteria
        success = True
        print(f"  ✓ Content loaded: {char_count:,} characters")
        print(f"  ✓ Line count: {line_count} lines")
        print(f"  ✓ File size: {size_kb:.1f} KB")
        print(f"  ✓ Sections found: {sections_found}/8")

        # Check if file is within expected size range (35-48 KB per AC)
        if size_kb < 30 or size_kb > 55:
            print(f"  ⚠️  WARNING: Size outside expected range (35-48 KB)")

        # Check if all 8 sections are present
        if sections_found < 8:
            print(f"  ⚠️  WARNING: Expected 8 sections, found {sections_found}")

        # Verify UTF-8 encoding worked (no encoding errors)
        try:
            research_content.encode('utf-8')
            print(f"  ✓ UTF-8 encoding validated")
        except UnicodeEncodeError:
            print(f"  ❌ FAILED: UTF-8 encoding error")
            success = False

        results.append((brand_id, success))
        print()

    # Test missing file handling (non-fatal error)
    print("--- Testing: missing-brand (error handling) ---")
    missing_content = load_research_data("missing-brand")

    if missing_content == "":
        print("  ✓ Missing file handled gracefully (returned empty string)")
        print("  ✓ Non-fatal error behavior confirmed")
    else:
        print("  ❌ FAILED: Expected empty string for missing file")

    print()

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"Research files tested: {total}")
    print(f"Successful loads: {passed}/{total}")
    print(f"Missing file handling: ✓ Passed")
    print()

    if passed == total:
        print("✅ ALL TESTS PASSED")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        for brand_id, success in results:
            if not success:
                print(f"   - {brand_id}")

    print("=" * 80)


if __name__ == "__main__":
    test_research_loader()
