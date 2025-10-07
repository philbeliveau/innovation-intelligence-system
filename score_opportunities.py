#!/usr/bin/env python3
"""
Interactive scoring assistant for quality assessment.
Guides PM through manual scoring of each opportunity using the rubric.
"""

import csv
import json
from pathlib import Path

def read_opportunity_content(file_path):
    """Read and display opportunity content."""
    with open(file_path, 'r') as f:
        content = f.read()
    return content

def display_opportunity(opp_num, total, scenario_id, brand, input_source, file_path):
    """Display opportunity card for scoring."""
    print("\n" + "="*80)
    print(f"OPPORTUNITY {opp_num}/{total}")
    print("="*80)
    print(f"Scenario ID: {scenario_id}")
    print(f"Brand: {brand}")
    print(f"Input Source: {input_source}")
    print(f"File: {file_path}")
    print("-"*80)

    content = read_opportunity_content(file_path)
    print(content)
    print("-"*80)

def get_score(dimension_name):
    """Prompt for score with validation."""
    while True:
        try:
            score = input(f"{dimension_name} (1-5): ").strip()
            if score == '':
                return None
            score_int = int(score)
            if 1 <= score_int <= 5:
                return score_int
            else:
                print("❌ Score must be between 1 and 5")
        except ValueError:
            print("❌ Please enter a number between 1 and 5")

def calculate_overall_score(novelty, actionability, relevance, specificity):
    """Calculate average score."""
    if all(s is not None for s in [novelty, actionability, relevance, specificity]):
        return round((novelty + actionability + relevance + specificity) / 4, 1)
    return None

def score_opportunities():
    """Interactive scoring session."""
    print("🎯 Quality Assessment Scoring Assistant")
    print("="*80)
    print("\n📖 Reference: docs/opportunity-quality-rubric.md")
    print("📝 Output: data/quality-assessment.csv")
    print("\nInstructions:")
    print("  - Score each dimension 1-5 based on rubric")
    print("  - Add notes capturing key observations")
    print("  - Press Enter to skip an opportunity (resume later)")
    print("  - Type 'quit' to save progress and exit\n")

    # Load opportunities
    with open('data/collected-opportunities.json', 'r') as f:
        opportunities = json.load(f)

    # Load existing scores if any
    existing_scores = {}
    csv_file = Path('data/quality-assessment.csv')
    if csv_file.exists():
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['novelty']:  # If already scored
                    existing_scores[row['scenario_id']] = row

    # Track new scores
    new_scores = []
    scored_count = len(existing_scores)

    for idx, opp in enumerate(opportunities, 1):
        scenario_id = opp['scenario_id']

        # Skip if already scored
        if scenario_id in existing_scores:
            print(f"⏭️  Skipping {scenario_id} (already scored)")
            continue

        # Display opportunity
        display_opportunity(
            idx, len(opportunities),
            scenario_id,
            opp['brand'],
            opp['input_source'],
            opp['opportunity_file']
        )

        # Get scores
        print("\n📊 SCORING (refer to rubric):")
        novelty = get_score("Novelty")
        if novelty is None:
            print("⏸️  Skipped - will resume later")
            continue

        actionability = get_score("Actionability")
        relevance = get_score("Relevance")
        specificity = get_score("Specificity")

        # Calculate overall
        overall = calculate_overall_score(novelty, actionability, relevance, specificity)

        # Get notes
        print("\n📝 Notes (observations, strengths, weaknesses):")
        notes = input("> ").strip()

        # Save score
        score_record = {
            'scenario_id': scenario_id,
            'brand': opp['brand'],
            'input_source': opp['input_source'],
            'novelty': novelty,
            'actionability': actionability,
            'relevance': relevance,
            'specificity': specificity,
            'overall_score': overall,
            'notes': notes
        }

        new_scores.append(score_record)
        scored_count += 1

        print(f"\n✅ Scored {scored_count}/{len(opportunities)}")

        # Check if user wants to continue
        if idx < len(opportunities):
            continue_input = input("\nContinue to next opportunity? (y/n): ").strip().lower()
            if continue_input == 'n' or continue_input == 'quit':
                break

    # Write all scores to CSV
    if new_scores:
        fieldnames = [
            'scenario_id', 'brand', 'input_source',
            'novelty', 'actionability', 'relevance', 'specificity',
            'overall_score', 'notes'
        ]

        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            # Write existing scores
            for score in existing_scores.values():
                writer.writerow(score)

            # Write new scores
            for score in new_scores:
                writer.writerow(score)

        print(f"\n💾 Saved {len(new_scores)} new scores to {csv_file}")
        print(f"📊 Total scored: {scored_count}/{len(opportunities)}")

        if scored_count < len(opportunities):
            print(f"⚠️  {len(opportunities) - scored_count} opportunities remaining")
            print("   Run this script again to resume scoring")
    else:
        print("\n⚠️  No new scores recorded")

    print("\n✅ Scoring session complete")

if __name__ == "__main__":
    score_opportunities()
