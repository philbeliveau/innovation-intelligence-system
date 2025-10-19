# Brand Profile Schema Documentation

## Overview

Brand profiles are stored as YAML files in the `data/brand-profiles/` directory. Each profile contains standardized information about a brand to enable Stage 4 opportunity contextualization in the Innovation Intelligence System pipeline.

## Schema Version

**Version:** 1.0
**Last Updated:** 2025-10-07

## Required Fields

All brand profile YAML files must contain the following fields:

### `brand_name` (string)

**Description:** Official name of the brand or company.

**Format:** Plain text string
**Example:** `"Lactalis Canada"`

**Guidelines:**
- Use official brand name as it appears in company materials
- Include country/region if part of official brand identity (e.g., "Lactalis Canada" not just "Lactalis")

---

### `country` (string)

**Description:** Primary country or region of operation for this brand profile.

**Format:** Country name or "Country (Global)" for multinational headquarters
**Example:** `"United States"` or `"France (Global)"`

**Guidelines:**
- Use full country names, not ISO codes
- For global brands, specify headquarters country with "(Global)" designation
- For regional subsidiaries, use the specific country/region

---

### `industry` (string)

**Description:** Primary industry or sector classification.

**Format:** Industry name, may include sub-sector separated by " / "
**Example:** `"Dairy / Food & Beverage"` or `"Outdoor Apparel & Footwear"`

**Guidelines:**
- Start with primary industry, add sub-sector for specificity
- Use commonly recognized industry classifications
- Keep concise (1-3 components maximum)

---

### `positioning` (string)

**Description:** Brand's market positioning and value proposition, typically 1-2 sentences.

**Format:** Descriptive text (1-2 sentences, ~150-250 characters)
**Example:** `"Canada's premier dairy company with over 140 years of heritage, combining authentic quality products with ESG leadership and systematic innovation across traditional dairy, lactose-free, plant-based, and organic categories."`

**Guidelines:**
- Capture core positioning statement and competitive differentiation
- Include heritage/credentials if relevant
- Mention key strategic elements (innovation approach, market position, scope)
- Keep professional and factual

---

### `product_portfolio` (list of strings)

**Description:** List of major product lines, brands, or categories offered by the company.

**Format:** Array of strings, each describing a product line or brand
**Example:**
```yaml
product_portfolio:
  - "Cracker Barrel - Premium cheese including sweet and signature blends"
  - "Black Diamond - Cheese products including Cheestrings"
  - "Astro - Traditional and high-protein yogurt products"
```

**Guidelines:**
- List 5-15 major product lines or brands
- Format: "Brand/Product Name - Brief description"
- Include flagship products and key categories
- For multi-brand companies, list sub-brands
- For single-brand companies, list product categories
- Order by importance/revenue contribution when possible

---

### `target_customers` (list of strings)

**Description:** Key customer segments the brand serves, with demographic and psychographic details.

**Format:** Array of strings, each describing a customer segment
**Example:**
```yaml
target_customers:
  - "Health-conscious families (30-55 years, $75K+ household income) seeking nutritious, high-quality dairy with clean ingredients"
  - "Flexitarian consumers (25-45 years, urban/suburban) seeking both dairy and plant-based options for dietary flexibility"
```

**Guidelines:**
- List 3-6 primary customer segments
- Include demographics (age, income, location) in parentheses
- Include psychographics (motivations, values, behaviors) in main text
- Be specific and actionable for opportunity contextualization
- Focus on segments that drive majority of business

---

### `recent_innovations` (list of strings)

**Description:** Significant innovations, product launches, or strategic initiatives from the last 18-24 months.

**Format:** Array of strings, each describing an innovation with context
**Example:**
```yaml
recent_innovations:
  - "Enjoy plant-based product line launch (May 2024) leveraging dairy infrastructure for efficient market entry"
  - "Zero-carbon ready distribution centre in Oshawa, Ontario enhancing supply chain sustainability and capacity"
  - "Packaging lightweighting program avoiding 191,345 tons of packaging with zero PVC elimination for enhanced recyclability"
```

**Guidelines:**
- List 5-10 most significant recent innovations
- Include timeframe (month/year) when available
- Cover product innovations, technology, sustainability, partnerships, marketing
- Provide context on significance and impact
- Prioritize innovations that signal strategic direction

---

### `strategic_priorities` (list of strings)

**Description:** Current strategic goals, initiatives, and business priorities.

**Format:** Array of strings, each describing a strategic priority
**Example:**
```yaml
strategic_priorities:
  - "ESG Leadership - Advance Environmental, Social, and Governance framework with Science-Based Targets initiative validation"
  - "Product Portfolio Diversification - Expand beyond traditional dairy into lactose-free, plant-based, high-protein, and organic segments"
  - "Digital Transformation - Grow e-commerce integration (40% sales volume starting online) and omnichannel presence"
```

**Guidelines:**
- List 5-10 current strategic priorities
- Format: "Priority Name - Detailed description with metrics/targets when available"
- Include quantitative targets when publicly stated
- Cover growth, innovation, sustainability, operational priorities
- Focus on medium-term (1-3 year) strategic direction

---

### `brand_values` (list of strings)

**Description:** Core values, principles, and attributes that define the brand's identity and culture.

**Format:** Array of strings, each describing a brand value with supporting details
**Example:**
```yaml
brand_values:
  - "Sustainability - Environmental stewardship, zero-carbon infrastructure, circular packaging, climate action"
  - "Quality & Heritage - 140+ years of Canadian dairy excellence with authentic, premium products"
  - "Innovation - First-mover in lactose-free, plant-based, and high-protein categories within Canadian dairy market"
```

**Guidelines:**
- List 4-6 core brand values
- Format: "Value Name - Supporting evidence and manifestations"
- Provide concrete examples of how values are expressed
- Avoid generic statements; be specific to the brand
- Connect values to observable behaviors and initiatives

---

## File Naming Convention

Brand profile files should be named using lowercase with hyphens:

**Format:** `{brand-name}.yaml`

**Examples:**
- `lactalis-canada.yaml`
- `mccormick-usa.yaml`
- `columbia-sportswear.yaml`
- `decathlon.yaml`

**Guidelines:**
- Use all lowercase
- Replace spaces with hyphens
- Remove special characters (apostrophes, ampersands, etc.)
- Use descriptive names that identify the brand clearly

---

## Complete Example

```yaml
brand_name: Lactalis Canada
country: Canada
industry: Dairy / Food & Beverage
positioning: "Canada's premier dairy company with over 140 years of heritage, combining authentic quality products with ESG leadership and systematic innovation across traditional dairy, lactose-free, plant-based, and organic categories."

product_portfolio:
  - "Cracker Barrel - Premium cheese including sweet and signature blends"
  - "Black Diamond - Cheese products including Cheestrings"
  - "Balderson - Premium aged cheddar varieties"
  - "Astro - Traditional and high-protein yogurt products"
  - "Lactantia - Premium butter and dairy products"
  - "Olympic Organic - Certified organic yogurt and drinkable yogurt for kids"
  - "P'tit Québec - Quebec-focused dairy brand with community initiatives"
  - "Enjoy - Plant-based product line (launched May 2024)"

target_customers:
  - "Health-conscious families (30-55 years, $75K+ household income) seeking nutritious, high-quality dairy with clean ingredients"
  - "Flexitarian consumers (25-45 years, urban/suburban) seeking both dairy and plant-based options for dietary flexibility"
  - "Lactose-intolerant/sensitive consumers requiring digestive-friendly dairy alternatives without taste compromise"
  - "Organic-focused parents (30-50 years) prioritizing certified organic products for children's nutrition"

recent_innovations:
  - "Enjoy plant-based product line launch (May 2024) leveraging dairy infrastructure for efficient market entry"
  - "Lactose-free portfolio expansion - cheese and butter products for digestive-friendly dairy consumption"
  - "High-protein, low-sugar yogurt with natural ingredients targeting health-conscious and fitness-oriented consumers"
  - "Zero-carbon ready distribution centre in Oshawa, Ontario enhancing supply chain sustainability and capacity"
  - "Packaging lightweighting program avoiding 191,345 tons of packaging with zero PVC elimination for enhanced recyclability"

strategic_priorities:
  - "ESG Leadership - Advance Environmental, Social, and Governance framework with Science-Based Targets initiative validation"
  - "Product Portfolio Diversification - Expand beyond traditional dairy into lactose-free, plant-based, high-protein, and organic segments"
  - "Emissions Reduction - Continue lowering scope 1 and 2 emissions intensity beyond 10.3% achieved since 2019"
  - "Digital Transformation - Grow e-commerce integration (40% sales volume starting online) and omnichannel presence"
  - "Circular Economy - Zero PVC packaging, material reduction, enhanced recyclability across all products"

brand_values:
  - "Sustainability - Environmental stewardship, zero-carbon infrastructure, circular packaging, climate action"
  - "Quality & Heritage - 140+ years of Canadian dairy excellence with authentic, premium products"
  - "Community Engagement - Supporting Canadian dairy farmers, local communities, and organic farming initiatives"
  - "Responsibility - Ethical sourcing, animal welfare (NFACC membership), stakeholder collaboration"
  - "Innovation - First-mover in lactose-free, plant-based, and high-protein categories within Canadian dairy market"
```

---

## Validation Requirements

All brand profiles must:

1. **Parse as valid YAML** - No syntax errors when loaded with PyYAML
2. **Contain all required fields** - All 9 required fields must be present
3. **Use correct data types** - Strings for single values, lists for arrays
4. **Meet length guidelines** - Positioning should be 1-2 sentences; lists should have recommended number of items
5. **Be factual and current** - Information should be accurate and recent (last 18-24 months for innovations)

---

## Usage in Pipeline

Brand profiles are loaded in **Stage 4: Opportunity Contextualization** to:

1. Match opportunities to relevant brands based on industry, product portfolio, and strategic priorities
2. Customize opportunity descriptions using brand-specific terminology and positioning
3. Align opportunities with stated strategic priorities and recent innovation patterns
4. Target messaging to specific customer segments defined in the profile
5. Reference recent innovations to show how new opportunities build on existing momentum

---

## Maintenance

Brand profiles should be updated:

- **Quarterly:** Review strategic priorities and recent innovations
- **Annually:** Update all fields for accuracy and relevance
- **As needed:** Major product launches, strategic shifts, leadership changes

Last schema update: 2025-10-07
