# 6. Data Models

## 6.1 Brand Profile Schema (YAML)

```yaml
# data/brand-profiles/{brand-id}.yaml

brand_name: "Lactalis Canada"
brand_id: "lactalis-canada"
country: "Canada"
industry: "Food & Beverage - Dairy"
positioning: "Premium dairy products with heritage craftsmanship and local sourcing"

product_portfolio:
  - "Cheese (Lactantia, Black Diamond, Cheestrings)"
  - "Butter and spreads"
  - "Milk and cream products"

target_customers:
  - "Health-conscious families"
  - "Premium food enthusiasts"
  - "Convenience seekers"

recent_innovations:
  - "Plant-based cheese alternatives launch (2024)"
  - "Sustainable packaging initiative"
  - "Lactose-free product line expansion"

strategic_priorities:
  - "Sustainability and carbon neutrality by 2030"
  - "Digital customer engagement"
  - "Premium product line expansion"

brand_values:
  - "Quality craftsmanship"
  - "Canadian heritage"
  - "Sustainability"
  - "Innovation"

research_data_path: "docs/web-search-setup/lactalis-canada-research.md"
```

**Note:** Brand profiles provide high-level context, but comprehensive research data is loaded separately from `docs/web-search-setup/` (see section 6.2).

## 6.2 Brand Research Data Structure (Markdown)

**Location:** `docs/web-search-setup/{brand-id}-research.md`

**Purpose:** Comprehensive, pre-researched brand intelligence that powers Stage 4 contextualization. This is the **critical differentiation data** that enables the pipeline to generate meaningfully different opportunities for each brand from the same input.

**File Structure:**

Each brand research file contains 8 strategic dimensions with ~46 subsections:

```markdown
# {Brand Name} - Comprehensive Brand Research
**Research Date:** 2025-10-07
**Researcher:** Claude (Innovation Intelligence System)
**Sources Reviewed:** 45+

# 1. Brand Overview & Positioning
## Official Positioning
## Brand Values
## Iconic Brand Portfolio
## Target Audience
## Current Campaigns (2024-2025)

# 2. Product Portfolio & Innovation
## Core Product Categories
## Flagship Products
## Recent Product Launches (2023-2025)

# 3. Recent Innovations (Last 18 Months)
## Product Innovations
## Sustainability Innovations
## Technology Innovations
## Marketing & Experience Innovations
## Partnership Innovations

# 4. Strategic Priorities & Business Strategy
## Publicly Stated Goals
## Growth Markets & Expansion Plans
## Digital Transformation Initiatives
## Sustainability Commitments & Targets

# 5. Target Customers & Market Positioning
## Demographics
## Psychographics
## Purchase Behaviors & Preferences
## Customer Journey Insights

# 6. Sustainability & Social Responsibility
## ESG Commitments
## Certifications & Standards
## Circular Economy Initiatives
## Community Engagement

# 7. Competitive Context & Market Trends
## Key Competitors
## Industry Dynamics
## Consumer Trends Affecting Brand
## Market Opportunities & Threats

# 8. Recent News & Market Signals (Last 6 Months)
## Press Releases & Announcements
## Media Coverage
## Analyst Reports
## Social Media Trends

# Research Methodology
[Research approach and source types]

# Key Insights Summary (For Pipeline Context)
[Executive summary of most relevant insights for opportunity generation]
```

**File Statistics:**
- **Size:** ~550-720 lines per brand (35-48KB)
- **Sources:** 45+ cited sources per brand (news, press releases, industry reports, company websites)
- **Content Depth:** ~46 subsections with specific examples, data points, and strategic insights
- **Recency:** Focus on 2023-2025 innovations and last 6 months of news
- **Citation Format:** URLs provided for source verification

**Available Research Files:**
- `lactalis-canada-research.md` (545 lines, 36.7KB)
- `mccormick-usa-research.md` (720 lines, 48.1KB)
- `columbia-sportswear-research.md` (574 lines, 43.1KB)
- `decathlon-research.md` (603 lines, 44.9KB)

**Stage 4 Loading Pattern:**

```python
def load_brand_research(brand_id):
    """Load comprehensive brand research from markdown file."""
    research_path = Path(f"docs/web-search-setup/{brand_id}-research.md")

    if not research_path.exists():
        logging.warning(f"Research file not found: {research_path}")
        return ""

    research_content = research_path.read_text(encoding='utf-8')

    # Optional: Extract key sections for token efficiency
    # Could parse specific sections (e.g., Recent Innovations, Strategic Priorities)
    # For MVP: Load entire file into Stage 4 prompt context

    return research_content
```

**Critical Notes:**
- Research files are **pre-generated** and **static** - no live web search during pipeline execution
- Files must be updated manually/periodically to maintain currency
- Missing research file is **non-fatal** - Stage 4 proceeds with brand profile only (degraded mode)
- Research content is injected directly into Stage 4 LLM prompt for contextualization

## 6.3 Input Manifest Schema (YAML)

```yaml
# data/input-manifest.yaml

inputs:
  - id: "savannah-bananas"
    filename: "savannah-bananas.pdf"
    type: "case_study"
    description: "Baseball team creating fan entertainment experience"
    industry: "Sports & Entertainment"

  - id: "premium-fast-food"
    filename: "premium-fast-food-trend.pdf"
    type: "trend_report"
    description: "Premiumization trend in fast food industry"
    industry: "Food & Beverage"
```

## 6.4 Opportunity Card Schema (Markdown + Frontmatter)

```markdown
---
opportunity_id: "savannah-bananas-lactalis-001"
brand: "lactalis-canada"
input_source: "savannah-bananas"
timestamp: "2025-10-07T14:23:45Z"
tags: ["customer-experience", "entertainment", "brand-building"]
stage4_insight_source: "Brand contextualization analysis - experiential marketing for dairy products"
---

# Interactive Dairy Farm Virtual Tours

# Description

Create immersive virtual farm tours that transform dairy product education into entertainment, mirroring Savannah Bananas' approach of turning a commodity experience (baseball) into must-see entertainment. Lactalis can leverage its Canadian heritage farms to create engaging digital experiences that build brand loyalty while educating consumers about sustainable dairy practices.

The experience would feature 360-degree farm tours, meet-the-farmer video series, and interactive cheese-making demonstrations. This addresses growing consumer demand for transparency and connection to food sources while differentiating Lactalis products in competitive dairy aisles.

# Actionability

- Partner with 3-5 heritage supplier farms to film immersive video content (Q1 2026)
- Develop mobile-first web experience with QR codes on premium product packaging
- Create monthly "Meet Your Farmer" livestream events with Q&A sessions
- Integrate with existing loyalty program to reward engagement
- Pilot with Black Diamond cheese line before expanding portfolio-wide

# Visual Description

Split-screen image: Left side shows traditional cheese aging cave with warm lighting and wooden shelves, right side shows modern family watching virtual tour on tablet in kitchen. QR code visible on cheese package. Warm, inviting color palette emphasizing heritage and technology harmony.

# Follow-up Prompts

1. How might we measure the ROI of virtual farm tours on brand perception and purchase intent?
2. What partnerships with Canadian tourism boards or agricultural organizations could amplify this initiative?
3. How could we extend this experience into retail environments or special events?
```

---
