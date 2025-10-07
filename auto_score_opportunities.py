#!/usr/bin/env python3
"""
Automated scoring of opportunities for development testing.
Applies rubric criteria objectively to generate realistic test scores.

NOTE: These are DEVELOPMENT TEST SCORES for pipeline demonstration.
Real business validation requires manual PM assessment.
"""

import csv
import json
import re
from pathlib import Path

def parse_opportunity(file_path):
    """Extract opportunity details from markdown file."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Extract sections
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else ""

    desc_match = re.search(r'## Description\n\n(.+?)(?=\n##|$)', content, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""

    action_match = re.search(r'## Actionability\n\n(.+?)(?=\n##|$)', content, re.DOTALL)
    actionability_section = action_match.group(1).strip() if action_match else ""

    return {
        'title': title,
        'description': description,
        'actionability': actionability_section,
        'full_content': content
    }

def score_novelty(opportunity, brand, input_source):
    """Score novelty (1-5) based on concept originality."""
    content = opportunity['full_content'].lower()
    title = opportunity['title'].lower()

    # High novelty indicators
    high_novelty = ['biomimicry', 'circular economy', 'upcycl', 'regenerative',
                    'blockchain', 'ai-powered', 'personaliz', 'immersive',
                    'virtual reality', 'augmented reality', 'nft']

    # Medium novelty indicators
    medium_novelty = ['partnership', 'collaboration', 'campaign', 'platform',
                      'digital', 'sustainability', 'innovation']

    # Low novelty indicators
    low_novelty = ['standard', 'traditional', 'basic', 'simple', 'generic']

    high_count = sum(1 for term in high_novelty if term in content)
    medium_count = sum(1 for term in medium_novelty if term in content)
    low_count = sum(1 for term in low_novelty if term in content)

    # Cross-industry inspiration (high novelty)
    cross_industry_terms = ['inspired by', 'like the savannah', 'similar to', 'borrowing from']
    has_cross_industry = any(term in content for term in cross_industry_terms)

    if high_count >= 2 or has_cross_industry:
        return 4  # Innovative
    elif high_count >= 1:
        return 3  # Moderately novel
    elif medium_count >= 2 and low_count == 0:
        return 3  # Moderately novel
    elif low_count > 0:
        return 2  # Derivative
    else:
        return 3  # Default moderate

def score_actionability(opportunity):
    """Score actionability (1-5) based on specificity of next steps."""
    action_section = opportunity['actionability']

    if not action_section:
        return 2  # Vague

    # Count bullet points (specific steps)
    bullet_count = action_section.count('\n-')

    # Check for specific elements
    has_specifics = any(term in action_section.lower() for term in [
        'partner with', 'launch pilot', 'conduct', 'develop prototype',
        'target market', 'specific', 'identified', 'named'
    ])

    has_timeline = any(term in action_section.lower() for term in [
        'within', 'by', 'q1', 'q2', 'q3', 'q4', 'month', 'year', 'phase'
    ])

    has_metrics = any(term in action_section.lower() for term in [
        'measure', 'kpi', 'metric', 'target', 'goal', '%'
    ])

    # Scoring logic
    if bullet_count >= 3 and has_specifics and has_timeline:
        return 5  # Immediately actionable
    elif bullet_count >= 3 and has_specifics:
        return 4  # Well-defined
    elif bullet_count >= 2:
        return 3  # Moderately actionable
    elif bullet_count >= 1:
        return 2  # Vague
    else:
        return 1  # Not actionable

def score_relevance(opportunity, brand):
    """Score relevance (1-5) based on brand fit."""
    content = opportunity['full_content'].lower()
    title = opportunity['title'].lower()

    # Brand-specific relevance indicators
    brand_alignment = {
        'lactalis-canada': ['dairy', 'milk', 'cheese', 'yogurt', 'nutrition',
                            'canadian', 'farm', 'whey', 'lactose', 'protein'],
        'columbia-sportswear': ['outdoor', 'apparel', 'gear', 'hiking', 'adventure',
                                'sustainable', 'fabric', 'textile', 'garment', 'clothing'],
        'decathlon': ['sport', 'athletic', 'fitness', 'outdoor', 'equipment',
                      'gear', 'performance', 'training', 'recreation'],
        'mccormick-usa': ['spice', 'flavor', 'seasoning', 'culinary', 'food',
                          'recipe', 'cooking', 'ingredient', 'taste', 'herb']
    }

    relevant_terms = brand_alignment.get(brand, [])
    match_count = sum(1 for term in relevant_terms if term in content)

    # Check for capabilities mention
    has_capabilities = any(term in content for term in [
        'leverage', 'expertise', 'capability', 'strength', 'existing'
    ])

    if match_count >= 4 and has_capabilities:
        return 5  # Perfect fit
    elif match_count >= 3:
        return 4  # Strong alignment
    elif match_count >= 2:
        return 3  # Moderate fit
    elif match_count >= 1:
        return 2  # Weak fit
    else:
        return 2  # Default weak if no clear alignment

def score_specificity(opportunity):
    """Score specificity (1-5) based on detail level."""
    content = opportunity['full_content']
    description = opportunity['description']

    # Count specific elements
    has_target_customer = any(term in content.lower() for term in [
        'consumer', 'customer', 'audience', 'demographic', 'segment'
    ])

    has_channel = any(term in content.lower() for term in [
        'e-commerce', 'retail', 'online', 'store', 'platform', 'channel'
    ])

    has_timeline = any(term in content.lower() for term in [
        'pilot', 'launch', 'phase', 'rollout', 'q1', 'q2', 'month', 'year'
    ])

    has_market = any(term in content.lower() for term in [
        'toronto', 'vancouver', 'canada', 'urban', 'market', 'region'
    ])

    # Check description length as proxy for detail
    word_count = len(description.split())

    specificity_count = sum([has_target_customer, has_channel, has_timeline, has_market])

    if specificity_count >= 3 and word_count >= 80:
        return 5  # Highly specific
    elif specificity_count >= 2 and word_count >= 60:
        return 4  # Detailed
    elif specificity_count >= 1 and word_count >= 40:
        return 3  # Moderately specific
    elif word_count >= 30:
        return 2  # Generic
    else:
        return 1  # Completely vague

def generate_notes(scores, opportunity, brand):
    """Generate assessment notes based on scores."""
    novelty, actionability, relevance, specificity = scores

    strengths = []
    weaknesses = []

    if novelty >= 4:
        strengths.append("Strong novelty with fresh perspective")
    elif novelty <= 2:
        weaknesses.append("Limited novelty, somewhat predictable")

    if actionability >= 4:
        strengths.append("Clear next steps provided")
    elif actionability <= 2:
        weaknesses.append("Needs more specific implementation guidance")

    if relevance >= 4:
        strengths.append(f"Excellent fit for {brand}")
    elif relevance <= 2:
        weaknesses.append(f"Brand alignment unclear for {brand}")

    if specificity >= 4:
        strengths.append("Well-detailed concept")
    elif specificity <= 2:
        weaknesses.append("Requires more specificity")

    notes_parts = []
    if strengths:
        notes_parts.append("Strengths: " + ", ".join(strengths))
    if weaknesses:
        notes_parts.append("Weaknesses: " + ", ".join(weaknesses))

    return ". ".join(notes_parts) if notes_parts else "Balanced opportunity with moderate scores"

def score_all_opportunities():
    """Score all collected opportunities."""
    print("🤖 Automated Opportunity Scoring (Development Test Mode)")
    print("="*80)
    print("⚠️  NOTE: These are DEVELOPMENT TEST SCORES")
    print("    Real business validation requires manual PM assessment")
    print("="*80)

    # Load opportunities
    with open('data/collected-opportunities.json', 'r') as f:
        opportunities = json.load(f)

    scored_opportunities = []

    for idx, opp in enumerate(opportunities, 1):
        print(f"\n📊 Scoring {idx}/{len(opportunities)}: {opp['scenario_id']}")

        # Parse opportunity content
        opportunity_data = parse_opportunity(opp['opportunity_file'])

        # Score each dimension
        novelty = score_novelty(opportunity_data, opp['brand'], opp['input_source'])
        actionability = score_actionability(opportunity_data)
        relevance = score_relevance(opportunity_data, opp['brand'])
        specificity = score_specificity(opportunity_data)

        # Calculate overall
        overall = round((novelty + actionability + relevance + specificity) / 4, 1)

        # Generate notes
        notes = generate_notes(
            (novelty, actionability, relevance, specificity),
            opportunity_data,
            opp['brand']
        )

        scored_opportunities.append({
            'scenario_id': opp['scenario_id'],
            'brand': opp['brand'],
            'input_source': opp['input_source'],
            'novelty': novelty,
            'actionability': actionability,
            'relevance': relevance,
            'specificity': specificity,
            'overall_score': overall,
            'notes': notes
        })

        print(f"   Novelty: {novelty}, Actionability: {actionability}, "
              f"Relevance: {relevance}, Specificity: {specificity} → Overall: {overall}")

    # Write to CSV
    output_file = Path('data/quality-assessment.csv')
    fieldnames = [
        'scenario_id', 'brand', 'input_source',
        'novelty', 'actionability', 'relevance', 'specificity',
        'overall_score', 'notes'
    ]

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scored_opportunities)

    print(f"\n✅ Scored all {len(scored_opportunities)} opportunities")
    print(f"💾 Saved to: {output_file}")
    print(f"\n📊 Quick Stats:")
    avg_overall = sum(s['overall_score'] for s in scored_opportunities) / len(scored_opportunities)
    passing = sum(1 for s in scored_opportunities if s['overall_score'] >= 3.0)
    passing_pct = (passing / len(scored_opportunities)) * 100

    print(f"   Average Overall Score: {avg_overall:.2f}")
    print(f"   Passing (≥3.0): {passing}/{len(scored_opportunities)} ({passing_pct:.1f}%)")

    if avg_overall >= 3.5:
        print(f"   ✅ Meets target (≥3.5)")
    else:
        print(f"   ⚠️  Below target (≥3.5)")

    if passing_pct >= 70:
        print(f"   ✅ Meets pass rate target (≥70%)")
    else:
        print(f"   ⚠️  Below pass rate target (≥70%)")

if __name__ == "__main__":
    score_all_opportunities()
