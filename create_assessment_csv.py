#!/usr/bin/env python3
"""
Create quality-assessment.csv template with all scenarios ready for manual scoring.
"""

import csv
import json
from pathlib import Path

def create_assessment_csv():
    """Create CSV template for quality assessment."""
    # Load collected opportunities
    with open('data/collected-opportunities.json', 'r') as f:
        opportunities = json.load(f)

    # Define CSV columns
    fieldnames = [
        'scenario_id',
        'brand',
        'input_source',
        'novelty',
        'actionability',
        'relevance',
        'specificity',
        'overall_score',
        'notes'
    ]

    # Create CSV file
    output_file = Path('data/quality-assessment.csv')
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Write row for each opportunity
        for opp in opportunities:
            writer.writerow({
                'scenario_id': opp['scenario_id'],
                'brand': opp['brand'],
                'input_source': opp['input_source'],
                'novelty': '',  # To be scored manually
                'actionability': '',
                'relevance': '',
                'specificity': '',
                'overall_score': '',  # Will be calculated after manual scoring
                'notes': ''
            })

    print(f"✅ Created quality assessment template: {output_file}")
    print(f"📋 Ready for manual scoring of {len(opportunities)} scenarios")
    print(f"\n📊 Next Steps:")
    print(f"   1. Read each opportunity card from the collected files")
    print(f"   2. Score on 4 dimensions using rubric (1-5 scale)")
    print(f"   3. Add notes capturing observations")
    print(f"   4. Calculate overall_score as average of 4 dimensions")

if __name__ == "__main__":
    create_assessment_csv()
