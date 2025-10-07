#!/usr/bin/env python3
"""
Collect opportunity cards from Story 4.3 batch execution for quality assessment.
Selects one representative opportunity (opportunity-1.md) from each successful scenario.
"""

import os
import json
from pathlib import Path

# Base directory for test outputs
TEST_OUTPUTS_DIR = Path("data/test-outputs")

# Failed scenarios from batch summary
FAILED_SCENARIOS = [
    "premium-fast-food-columbia-sportswear-20251007-161820",
    "cat-dad-campaign-mccormick-usa-20251007-165319"
]

def extract_scenario_info(dir_name):
    """Extract input_source and brand from directory name."""
    # Format: {input-source}-{brand}-{timestamp}
    # Example: savannah-bananas-lactalis-canada-20251007-160745

    # Find where brand starts (brands are: lactalis-canada, columbia-sportswear, decathlon, mccormick-usa)
    brands = ['lactalis-canada', 'columbia-sportswear', 'decathlon', 'mccormick-usa']

    for brand in brands:
        if brand in dir_name:
            # Split at brand to separate input_source and timestamp
            before_brand = dir_name.split(brand)[0].rstrip('-')
            return before_brand, brand

    return None, None

def collect_opportunities():
    """Collect one opportunity per successful scenario."""
    opportunities = []

    # Get all scenario directories
    for item in TEST_OUTPUTS_DIR.iterdir():
        if not item.is_dir():
            continue

        dir_name = item.name

        # Skip failed scenarios
        if dir_name in FAILED_SCENARIOS:
            print(f"⏭️  Skipping failed scenario: {dir_name}")
            continue

        # Skip integration test directories
        if 'integration-test' in dir_name:
            continue

        # Check if this is a valid scenario directory
        stage5_dir = item / "stage5"
        if not stage5_dir.exists():
            continue

        # Select opportunity-1.md as representative
        opp_file = stage5_dir / "opportunity-1.md"
        if not opp_file.exists():
            print(f"⚠️  Warning: {dir_name} missing opportunity-1.md")
            continue

        # Extract scenario information
        input_source, brand = extract_scenario_info(dir_name)

        if input_source and brand:
            opportunities.append({
                'scenario_id': dir_name,
                'input_source': input_source,
                'brand': brand,
                'opportunity_file': str(opp_file),
                'opportunity_number': 1
            })
            print(f"✅ Collected: {input_source} → {brand}")
        else:
            print(f"⚠️  Warning: Could not parse {dir_name}")

    # Sort by input_source and brand for organized assessment
    opportunities.sort(key=lambda x: (x['input_source'], x['brand']))

    return opportunities

def main():
    """Main execution."""
    print("🔍 Collecting opportunity cards from Story 4.3 outputs...\n")

    opportunities = collect_opportunities()

    print(f"\n📊 Summary:")
    print(f"   Total scenarios collected: {len(opportunities)}")
    print(f"   Expected: 22 (24 total - 2 failed)")

    if len(opportunities) == 22:
        print(f"   ✅ All successful scenarios collected!")
    else:
        print(f"   ⚠️  Count mismatch - review warnings above")

    # Save to JSON for reference
    output_file = Path("data/collected-opportunities.json")
    with open(output_file, 'w') as f:
        json.dump(opportunities, f, indent=2)

    print(f"\n💾 Saved collection manifest to: {output_file}")

    # Print breakdown by input source
    print(f"\n📋 Breakdown by input source:")
    input_sources = {}
    for opp in opportunities:
        source = opp['input_source']
        if source not in input_sources:
            input_sources[source] = 0
        input_sources[source] += 1

    for source, count in sorted(input_sources.items()):
        print(f"   {source}: {count} scenarios")

if __name__ == "__main__":
    main()
