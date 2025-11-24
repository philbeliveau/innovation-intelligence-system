"""Test script to verify formatters work with actual stage data"""
from pipeline.output_formatters import format_stage_output

# Test Stage 5 with typical opportunity structure
test_stage5_output = {
    "opportunities": [
        {
            "title": "Test Opportunity 1",
            "description": "A test opportunity description",
            "innovation_type": "product",
            "actionability_items": ["Step 1", "Step 2"],
            "visual_description": "Visual test",
            "follow_up_prompts": ["Question 1?", "Question 2?"],
            "markdown": "---\nopportunity_id: opp-01\ntags: product\n---\n\n# Test Opportunity 1\n\n## Description\n\nA test opportunity description\n\n## Actionability\n\n- Step 1\n- Step 2\n"
        },
        {
            "title": "Test Opportunity 2",
            "description": "Another test opportunity",
            "innovation_type": "service",
            "actionability_items": ["Action A", "Action B"],
            "markdown": "---\nopportunity_id: opp-02\ntags: service\n---\n\n# Test Opportunity 2\n\n## Description\n\nAnother test opportunity\n"
        }
    ]
}

print("Testing Stage 5 formatter...")
print("=" * 80)
result = format_stage_output(5, test_stage5_output)
print(f"\nResult Type: {type(result)}")
print(f"Result Length: {len(result)} chars")
print(f"\nFirst 500 chars:")
print(result[:500])
print("\n" + "=" * 80)

# Check if it's properly formatted markdown (not JSON code block)
if result.strip().startswith('```json'):
    print("\n❌ FAIL: Formatter returned JSON code block!")
elif result.strip().startswith('# Stage 5'):
    print("\n✅ PASS: Formatter returned proper markdown!")
    # Verify opportunities markdown is included
    if "Test Opportunity 1" in result and "Test Opportunity 2" in result:
        print("✅ PASS: Both opportunities included in output!")
    else:
        print("⚠️  WARNING: Opportunities not found in output")
else:
    print(f"\n⚠️  UNEXPECTED: Output starts with: {result[:50]}")
