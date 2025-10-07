#!/usr/bin/env python3
"""
Test Stage 4 graceful degradation when research data is missing.

This test verifies that Stage 4 can proceed with only brand profile data
when research data is unavailable (AC 9).
"""

import logging
from pathlib import Path
from dotenv import load_dotenv

from pipeline.stages.stage4_brand_contextualization import create_stage4_chain
from pipeline.utils import load_brand_profile

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_graceful_degradation():
    """Test Stage 4 with missing research data."""

    print("=" * 60)
    print("Testing Stage 4 Graceful Degradation (AC 9)")
    print("=" * 60)

    # Sample Stage 3 output (minimal for testing)
    stage3_output = """# Universal Lessons

## 1. Experience-First Value Creation

**The Principle:** Create value through memorable experiences rather than just product features.

**Why It Works:** Customers pay premium for experiences that deliver emotional connection.

**Where It Could Apply:** Retail, hospitality, food service, entertainment.

---

## 2. Strategic Constraint-Driven Innovation

**The Principle:** Use intentional limitations to drive creative solutions.

**Why It Works:** Constraints force focus and creative problem-solving.

**Where It Could Apply:** Product design, service delivery, business models.
"""

    # Load brand profile
    print("\n1. Loading brand profile...")
    brand_profile = load_brand_profile("lactalis-canada")
    print(f"   ✓ Brand profile loaded: {brand_profile.get('company_name', 'N/A')}")

    # Test with empty research data (graceful degradation scenario)
    print("\n2. Testing with EMPTY research data (graceful degradation)...")
    research_data = ""  # Empty string simulates missing research file

    # Create and run Stage 4 chain
    print("\n3. Creating Stage 4 chain...")
    stage4_chain = create_stage4_chain()
    print("   ✓ Stage 4 chain created")

    print("\n4. Running Stage 4 with empty research data...")
    try:
        result = stage4_chain.run(stage3_output, brand_profile, research_data)
        stage4_output = result[stage4_chain.output_key]

        print("   ✓ Stage 4 execution completed successfully")
        print(f"   ✓ Output length: {len(stage4_output)} characters")

        # Verify output contains brand-specific content
        if "lactalis" in stage4_output.lower() or brand_profile.get('company_name', '').lower() in stage4_output.lower():
            print("   ✓ Output contains brand-specific references")
        else:
            print("   ⚠ Output may lack brand-specific references")

        # Save output for review
        output_file = Path("test_output_graceful_degradation.md")
        output_file.write_text(stage4_output, encoding='utf-8')
        print(f"\n5. Output saved to: {output_file}")

        print("\n" + "=" * 60)
        print("✓ GRACEFUL DEGRADATION TEST PASSED")
        print("  Stage 4 executed successfully with missing research data")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_graceful_degradation()
    exit(0 if success else 1)
