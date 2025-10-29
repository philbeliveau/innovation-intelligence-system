"""Manual test to generate sample report for visual validation"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.report_generator import generate_full_report, calculate_report_size

# Create sample data
stage_outputs = {
    'stage1': {
        'extractedText': """
        The Savannah Bananas have revolutionized baseball entertainment through their
        innovative 'Banana Ball' format. They've created a unique fan experience that
        combines traditional baseball with circus-like entertainment, selling out every
        game and building a massive social media following.
        """,
        'mechanisms': [
            {
                'title': 'Entertainment-First Baseball',
                'description': 'Reimagined baseball as entertainment spectacle',
                'context': 'Breaking traditional sports boundaries'
            },
            {
                'title': 'Social Media Virality',
                'description': 'Leveraging TikTok and Instagram for reach',
                'context': 'Building audience beyond physical attendance'
            }
        ]
    },
    'stage2': {
        'signals': [
            {
                'category': 'Customer Experience',
                'description': 'Fans as co-creators of entertainment',
                'relevance': 'High - transforms passive to active engagement',
                'mechanismSource': 'Entertainment-First Baseball'
            },
            {
                'category': 'Marketing',
                'description': 'Organic viral content generation',
                'relevance': 'High - zero-cost brand awareness',
                'mechanismSource': 'Social Media Virality'
            }
        ]
    },
    'stage3': {
        'insights': [
            {
                'title': 'Gamification of Traditional Experiences',
                'description': 'Making familiar activities feel new through playful rules',
                'transferability': 'High',
                'signalSources': ['Entertainment-First Baseball', 'Fan Engagement']
            }
        ]
    },
    'stage4': {}
}

opportunity_cards = [
    {
        'title': 'Lactalis Game Day Experience',
        'content': """
## Description
Transform grocery shopping into an interactive game where families compete
for rewards while discovering Lactalis products.

## Actionability
- Pilot in 3 stores within Q1 2025
- Partner with local influencers for launch
- Measure engagement via mobile app downloads

## Visual Description
Colorful in-store signage with QR codes, digital leaderboards showing
top families, prize wheels at checkout.

## Follow-up Prompts
1. How can we integrate this with loyalty programs?
2. What partnerships amplify the experience?
3. How do we measure long-term brand affinity?
        """,
        'description': 'Interactive shopping gamification'
    }
]

# Generate report
report = generate_full_report(
    run_id='manual-test-001',
    company_name='Lactalis Canada',
    document_name='savannah-bananas-analysis.pdf',
    stage_outputs=stage_outputs,
    opportunity_cards=opportunity_cards
)

# Save to file
output_file = Path(__file__).parent / 'sample_report.md'
output_file.write_text(report, encoding='utf-8')

# Print stats
report_size = calculate_report_size(report)
print(f"✅ Sample report generated: {output_file}")
print(f"📊 Report size: {report_size:.2f} KB")
print(f"📝 Report length: {len(report)} characters")
print(f"\nFirst 500 characters:")
print(report[:500])
