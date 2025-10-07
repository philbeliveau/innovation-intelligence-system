#!/usr/bin/env python3
"""
Analyze quality assessment results for business validation.
Generates comprehensive metrics and insights for Story 4.4.
"""

import csv
from pathlib import Path
from collections import defaultdict

def load_assessment_data():
    """Load quality assessment CSV."""
    data = []
    with open('data/quality-assessment.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert scores to numeric
            row['novelty'] = int(row['novelty'])
            row['actionability'] = int(row['actionability'])
            row['relevance'] = int(row['relevance'])
            row['specificity'] = int(row['specificity'])
            row['overall_score'] = float(row['overall_score'])
            data.append(row)
    return data

def calculate_overall_metrics(data):
    """Calculate overall quality metrics."""
    total = len(data)
    overall_scores = [d['overall_score'] for d in data]

    avg_overall = sum(overall_scores) / total
    passing = sum(1 for score in overall_scores if score >= 3.0)
    passing_pct = (passing / total) * 100

    return {
        'total_assessed': total,
        'avg_overall_score': round(avg_overall, 2),
        'passing_count': passing,
        'passing_percentage': round(passing_pct, 1),
        'meets_avg_target': avg_overall >= 3.5,
        'meets_passing_target': passing_pct >= 70
    }

def calculate_dimension_breakdown(data):
    """Calculate average scores by dimension."""
    dimensions = ['novelty', 'actionability', 'relevance', 'specificity']
    breakdown = {}

    for dim in dimensions:
        scores = [d[dim] for d in data]
        avg = sum(scores) / len(scores)
        breakdown[dim] = {
            'average': round(avg, 2),
            'min': min(scores),
            'max': max(scores),
            'count_5': sum(1 for s in scores if s == 5),
            'count_4': sum(1 for s in scores if s == 4),
            'count_3': sum(1 for s in scores if s == 3),
            'count_2': sum(1 for s in scores if s == 2),
            'count_1': sum(1 for s in scores if s == 1)
        }

    return breakdown

def identify_top_performers(data, n=5):
    """Identify top N highest-scoring opportunities."""
    sorted_data = sorted(data, key=lambda x: x['overall_score'], reverse=True)
    return sorted_data[:n]

def identify_bottom_performers(data, n=5):
    """Identify bottom N lowest-scoring opportunities."""
    sorted_data = sorted(data, key=lambda x: x['overall_score'])
    return sorted_data[:n]

def analyze_by_brand(data):
    """Analyze scores grouped by brand."""
    by_brand = defaultdict(list)

    for record in data:
        by_brand[record['brand']].append(record['overall_score'])

    brand_analysis = {}
    for brand, scores in by_brand.items():
        brand_analysis[brand] = {
            'count': len(scores),
            'avg_score': round(sum(scores) / len(scores), 2),
            'min': round(min(scores), 1),
            'max': round(max(scores), 1)
        }

    return brand_analysis

def analyze_by_input_source(data):
    """Analyze scores grouped by input source."""
    by_source = defaultdict(list)

    for record in data:
        by_source[record['input_source']].append(record['overall_score'])

    source_analysis = {}
    for source, scores in by_source.items():
        source_analysis[source] = {
            'count': len(scores),
            'avg_score': round(sum(scores) / len(scores), 2),
            'min': round(min(scores), 1),
            'max': round(max(scores), 1)
        }

    return source_analysis

def generate_analysis_report():
    """Generate comprehensive analysis report."""
    print("📊 QUALITY ASSESSMENT ANALYSIS REPORT")
    print("="*80)

    # Load data
    data = load_assessment_data()

    # Overall Metrics
    print("\n## 1. OVERALL METRICS")
    print("-"*80)
    overall = calculate_overall_metrics(data)
    print(f"Total Opportunities Assessed: {overall['total_assessed']}")
    print(f"Average Overall Score: {overall['avg_overall_score']}")
    print(f"Target: ≥3.5 → {'✅ MET' if overall['meets_avg_target'] else '❌ MISSED'}")
    print(f"\nPassing Rate (≥3.0): {overall['passing_count']}/{overall['total_assessed']} ({overall['passing_percentage']}%)")
    print(f"Target: ≥70% → {'✅ MET' if overall['meets_passing_target'] else '❌ MISSED'}")

    # Dimension Breakdown
    print("\n## 2. DIMENSION BREAKDOWN")
    print("-"*80)
    breakdown = calculate_dimension_breakdown(data)

    print(f"\n{'Dimension':<15} {'Avg':<8} {'Min':<8} {'Max':<8} {'Distribution'}")
    print("-"*80)
    for dim, stats in breakdown.items():
        dist = f"5:{stats['count_5']} 4:{stats['count_4']} 3:{stats['count_3']} 2:{stats['count_2']} 1:{stats['count_1']}"
        print(f"{dim.capitalize():<15} {stats['average']:<8.2f} {stats['min']:<8} {stats['max']:<8} {dist}")

    # Strengths and Weaknesses
    print("\n## 3. STRENGTHS AND WEAKNESSES")
    print("-"*80)
    # Sort dimensions by average
    sorted_dims = sorted(breakdown.items(), key=lambda x: x[1]['average'], reverse=True)

    print("\n**Strongest Dimensions:**")
    for i, (dim, stats) in enumerate(sorted_dims[:2], 1):
        print(f"{i}. {dim.capitalize()}: {stats['average']:.2f} avg")

    print("\n**Weakest Dimensions:**")
    for i, (dim, stats) in enumerate(reversed(sorted_dims[-2:]), 1):
        print(f"{i}. {dim.capitalize()}: {stats['average']:.2f} avg")

    # Top Performers
    print("\n## 4. TOP 5 HIGHEST-SCORING OPPORTUNITIES")
    print("-"*80)
    print("(For Story 4.5 Executive Package)")
    print()
    top_5 = identify_top_performers(data, 5)
    for i, opp in enumerate(top_5, 1):
        print(f"{i}. Score {opp['overall_score']:.1f} | {opp['input_source']} → {opp['brand']}")
        print(f"   Scenario: {opp['scenario_id']}")
        print(f"   N:{opp['novelty']} A:{opp['actionability']} R:{opp['relevance']} S:{opp['specificity']}")
        print()

    # Bottom Performers
    print("\n## 5. LOWEST-SCORING OPPORTUNITIES (Need Improvement)")
    print("-"*80)
    bottom_5 = identify_bottom_performers(data, 5)
    for i, opp in enumerate(bottom_5, 1):
        print(f"{i}. Score {opp['overall_score']:.1f} | {opp['input_source']} → {opp['brand']}")
        print(f"   Issue: {opp['notes']}")

    # By Brand Analysis
    print("\n## 6. PERFORMANCE BY BRAND")
    print("-"*80)
    brand_analysis = analyze_by_brand(data)
    print(f"\n{'Brand':<25} {'Count':<8} {'Avg Score':<12} {'Range'}")
    print("-"*80)
    for brand, stats in sorted(brand_analysis.items(), key=lambda x: x[1]['avg_score'], reverse=True):
        print(f"{brand:<25} {stats['count']:<8} {stats['avg_score']:<12.2f} {stats['min']:.1f} - {stats['max']:.1f}")

    # By Input Source Analysis
    print("\n## 7. PERFORMANCE BY INPUT SOURCE")
    print("-"*80)
    source_analysis = analyze_by_input_source(data)
    print(f"\n{'Input Source':<25} {'Count':<8} {'Avg Score':<12} {'Range'}")
    print("-"*80)
    for source, stats in sorted(source_analysis.items(), key=lambda x: x[1]['avg_score'], reverse=True):
        print(f"{source:<25} {stats['count']:<8} {stats['avg_score']:<12.2f} {stats['min']:.1f} - {stats['max']:.1f}")

    # Summary
    print("\n## 8. SUMMARY")
    print("="*80)
    if overall['meets_avg_target'] and overall['meets_passing_target']:
        print("✅ QUALITY TARGETS MET")
        print("   - Pipeline demonstrates ability to generate quality opportunities")
        print("   - Average score exceeds minimum threshold")
        print("   - High passing rate indicates consistent quality")
    else:
        print("⚠️  QUALITY TARGETS PARTIALLY MET")
        if not overall['meets_avg_target']:
            print(f"   - Average score ({overall['avg_overall_score']}) below target (3.5)")
        if not overall['meets_passing_target']:
            print(f"   - Passing rate ({overall['passing_percentage']}%) below target (70%)")

    # Save top 5 for Story 4.5
    print("\n💾 Saving top 5 opportunities for Story 4.5 handoff...")
    top_5_file = Path('data/top-5-opportunities.json')
    import json
    with open(top_5_file, 'w') as f:
        json.dump([{
            'rank': i,
            'scenario_id': opp['scenario_id'],
            'brand': opp['brand'],
            'input_source': opp['input_source'],
            'overall_score': opp['overall_score'],
            'scores': {
                'novelty': opp['novelty'],
                'actionability': opp['actionability'],
                'relevance': opp['relevance'],
                'specificity': opp['specificity']
            },
            'notes': opp['notes']
        } for i, opp in enumerate(top_5, 1)], f, indent=2)

    print(f"✅ Saved to: {top_5_file}")

if __name__ == "__main__":
    generate_analysis_report()
