#!/usr/bin/env python3
"""
Validate brand differentiation across same input source.
Analyzes whether opportunities meaningfully vary by brand context.
"""

import json
import re
from pathlib import Path

def parse_opportunity(file_path):
    """Extract opportunity details from markdown file."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Extract title
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else ""

    # Extract description
    desc_match = re.search(r'## Description\n\n(.+?)(?=\n##|$)', content, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""

    # Extract actionability
    action_match = re.search(r'## Actionability\n\n(.+?)(?=\n##|$)', content, re.DOTALL)
    actionability = action_match.group(1).strip() if action_match else ""

    return {
        'title': title,
        'description': description,
        'actionability': actionability
    }

def compare_opportunities_for_input(input_source, opportunities_data):
    """Compare opportunities from same input across different brands."""
    # Filter opportunities for this input source
    relevant_opps = [opp for opp in opportunities_data if opp['input_source'] == input_source]

    if len(relevant_opps) < 2:
        return None

    print(f"\n{'='*80}")
    print(f"INPUT SOURCE: {input_source}")
    print(f"{'='*80}")
    print(f"Brands analyzed: {len(relevant_opps)}")
    print()

    # Parse each opportunity
    parsed_opps = []
    for opp in relevant_opps:
        parsed = parse_opportunity(opp['opportunity_file'])
        parsed['brand'] = opp['brand']
        parsed_opps.append(parsed)

    # Display side-by-side comparison
    print(f"{'Brand':<25} {'Opportunity Title'}")
    print("-"*80)
    for opp in parsed_opps:
        print(f"{opp['brand']:<25} {opp['title']}")

    # Analyze differentiation
    print(f"\n## DIFFERENTIATION ANALYSIS\n")

    # 1. Title uniqueness
    titles = [opp['title'] for opp in parsed_opps]
    unique_titles = len(set(titles))
    print(f"**Title Uniqueness:** {unique_titles}/{len(titles)} unique titles")
    if unique_titles == len(titles):
        print("   ✅ Each brand received a distinct opportunity concept")
    else:
        print("   ⚠️  Some brands received similar concepts")

    # 2. Content analysis
    print(f"\n**Content Differentiation:**")
    for opp in parsed_opps:
        brand_mentions = opp['description'].count(opp['brand'].replace('-', ' ').title())
        brand_mentions += opp['description'].count(opp['brand'].replace('-', ' '))

        # Check for brand-specific elements
        brand_specific_indicators = 0

        # Lactalis-specific
        if opp['brand'] == 'lactalis-canada':
            lactalis_terms = ['dairy', 'milk', 'cheese', 'yogurt', 'lactalis', 'whey', 'lactose']
            brand_specific_indicators = sum(1 for term in lactalis_terms if term in opp['description'].lower())

        # Columbia-specific
        elif opp['brand'] == 'columbia-sportswear':
            columbia_terms = ['outdoor', 'apparel', 'gear', 'columbia', 'hiking', 'fabric', 'garment']
            brand_specific_indicators = sum(1 for term in columbia_terms if term in opp['description'].lower())

        # Decathlon-specific
        elif opp['brand'] == 'decathlon':
            decathlon_terms = ['sport', 'athletic', 'fitness', 'decathlon', 'equipment', 'training']
            brand_specific_indicators = sum(1 for term in decathlon_terms if term in opp['description'].lower())

        # McCormick-specific
        elif opp['brand'] == 'mccormick-usa':
            mccormick_terms = ['spice', 'flavor', 'seasoning', 'mccormick', 'culinary', 'recipe', 'taste']
            brand_specific_indicators = sum(1 for term in mccormick_terms if term in opp['description'].lower())

        print(f"\n   {opp['brand']}:")
        print(f"      Title: {opp['title']}")
        print(f"      Brand-specific terms: {brand_specific_indicators}")
        if brand_specific_indicators >= 2:
            print(f"      ✅ Strong brand contextualization")
        elif brand_specific_indicators >= 1:
            print(f"      ⚠️  Moderate brand contextualization")
        else:
            print(f"      ❌ Weak brand contextualization")

    # 3. Overall assessment
    print(f"\n## OVERALL DIFFERENTIATION ASSESSMENT\n")

    if unique_titles == len(titles):
        print("✅ **Concept Differentiation:** Each brand received unique opportunity concepts")
    else:
        print("⚠️  **Concept Differentiation:** Some overlap in opportunity concepts")

    total_brand_specific = sum(1 for opp in parsed_opps
                               if check_brand_contextualization(opp['description'], opp['brand']))

    contextualization_pct = (total_brand_specific / len(parsed_opps)) * 100

    print(f"✅ **Brand Contextualization:** {total_brand_specific}/{len(parsed_opps)} "
          f"({contextualization_pct:.0f}%) opportunities show strong brand context")

    if contextualization_pct >= 75:
        print("   → Pipeline successfully differentiates by brand")
    elif contextualization_pct >= 50:
        print("   → Pipeline shows moderate brand differentiation")
    else:
        print("   → Pipeline needs improvement in brand differentiation")

    return {
        'input_source': input_source,
        'brands_analyzed': len(parsed_opps),
        'unique_titles': unique_titles,
        'total_titles': len(titles),
        'contextualization_pct': contextualization_pct,
        'differentiation_quality': 'Strong' if contextualization_pct >= 75 else 'Moderate' if contextualization_pct >= 50 else 'Weak'
    }

def check_brand_contextualization(description, brand):
    """Check if description shows strong brand contextualization."""
    desc_lower = description.lower()

    brand_terms = {
        'lactalis-canada': ['dairy', 'milk', 'cheese', 'yogurt', 'lactalis', 'whey', 'lactose', 'canadian'],
        'columbia-sportswear': ['outdoor', 'apparel', 'gear', 'columbia', 'hiking', 'fabric', 'garment', 'clothing'],
        'decathlon': ['sport', 'athletic', 'fitness', 'decathlon', 'equipment', 'training', 'performance'],
        'mccormick-usa': ['spice', 'flavor', 'seasoning', 'mccormick', 'culinary', 'recipe', 'taste', 'herb']
    }

    terms = brand_terms.get(brand, [])
    matches = sum(1 for term in terms if term in desc_lower)

    return matches >= 2  # Strong if at least 2 brand-specific terms

def main():
    """Main differentiation validation."""
    print("🔍 BRAND DIFFERENTIATION VALIDATION")
    print("="*80)
    print("Analyzing whether opportunities vary meaningfully by brand context\n")

    # Load opportunities
    with open('data/collected-opportunities.json', 'r') as f:
        opportunities = json.load(f)

    # Find input sources with multiple brands
    from collections import defaultdict
    by_input = defaultdict(list)
    for opp in opportunities:
        by_input[opp['input_source']].append(opp)

    # Select input sources with 4 brands (complete coverage)
    complete_inputs = {k: v for k, v in by_input.items() if len(v) >= 4}

    print(f"Found {len(complete_inputs)} input sources with ≥4 brand variations:")
    for input_source in complete_inputs.keys():
        print(f"  - {input_source}")

    # Analyze differentiation for each
    results = []
    for input_source, opps in list(complete_inputs.items())[:3]:  # Analyze top 3
        result = compare_opportunities_for_input(input_source, opportunities)
        if result:
            results.append(result)

    # Summary
    print(f"\n\n{'='*80}")
    print("DIFFERENTIATION VALIDATION SUMMARY")
    print(f"{'='*80}\n")

    if results:
        avg_contextualization = sum(r['contextualization_pct'] for r in results) / len(results)
        total_unique = sum(r['unique_titles'] for r in results)
        total_titles = sum(r['total_titles'] for r in results)
        unique_pct = (total_unique / total_titles) * 100

        print(f"Input sources analyzed: {len(results)}")
        print(f"Average brand contextualization: {avg_contextualization:.1f}%")
        print(f"Unique titles: {total_unique}/{total_titles} ({unique_pct:.1f}%)")

        if avg_contextualization >= 75 and unique_pct >= 75:
            print(f"\n✅ **DIFFERENTIATION VALIDATED**")
            print(f"   Pipeline successfully generates brand-specific opportunities")
            print(f"   Opportunities vary meaningfully by brand context")
        elif avg_contextualization >= 50:
            print(f"\n⚠️  **DIFFERENTIATION MODERATE**")
            print(f"   Pipeline shows some brand differentiation")
            print(f"   Improvement needed in brand contextualization")
        else:
            print(f"\n❌ **DIFFERENTIATION WEAK**")
            print(f"   Pipeline struggles with brand differentiation")
            print(f"   Significant improvement needed")

        # Save results
        with open('data/differentiation-validation.json', 'w') as f:
            json.dump({
                'summary': {
                    'inputs_analyzed': len(results),
                    'avg_contextualization': round(avg_contextualization, 1),
                    'unique_title_pct': round(unique_pct, 1),
                    'differentiation_validated': avg_contextualization >= 75 and unique_pct >= 75
                },
                'details': results
            }, f, indent=2)

        print(f"\n💾 Saved validation results to: data/differentiation-validation.json")

if __name__ == "__main__":
    main()
