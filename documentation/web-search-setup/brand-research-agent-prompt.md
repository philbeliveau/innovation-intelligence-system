# Brand Research Agent Prompt

## Mission

Conduct comprehensive web research on 4 CPG/consumer brands to populate pre-existing research data files that will power Stage 4 (Brand Contextualization) of the Innovation Intelligence Pipeline. The research must be thorough, current, and structured to enable AI-driven opportunity generation.

## Target Brands

1. **Lactalis Canada** - Dairy products manufacturer
2. **McCormick USA** - Spices, seasonings, and flavorings
3. **Columbia Sportswear** - Outdoor apparel and equipment
4. **Decathlon** - Sports equipment and apparel retail

## Research Objectives

For each brand, gather intelligence across 8 strategic dimensions:

### 1. Brand Overview & Positioning
- Official brand positioning statement and brand promise
- Core brand values and personality traits
- Brand heritage and founding story (brief)
- Taglines and current brand campaigns
- Target audience demographics and psychographics
- Unique selling propositions (USPs)

### 2. Product Portfolio & Innovation
- Complete product categories and sub-categories
- Flagship products and hero SKUs
- Recent product launches (2023-2025)
- Product innovations and new formats
- Product line expansions or retirements
- Private label vs. branded strategy (if applicable)

### 3. Recent Innovations (Last 18 Months)
**CRITICAL DIMENSION** - This powers opportunity differentiation
- New product launches with descriptions
- Innovation in packaging, formats, or delivery methods
- Technology integrations (apps, smart packaging, IoT)
- Sustainability innovations (materials, processes, circularity)
- Marketing or experience innovations
- Partnership or collaboration announcements
- Awards or recognition for innovation

### 4. Strategic Priorities & Business Strategy
- Publicly stated strategic goals (from annual reports, investor presentations, press releases)
- Growth markets or expansion plans
- Digital transformation initiatives
- Sustainability commitments and targets
- DEI (Diversity, Equity, Inclusion) commitments
- Supply chain or operational priorities

### 5. Target Customers & Market Positioning
- Primary customer segments (demographics: age, income, location)
- Customer psychographics (values, lifestyle, attitudes)
- Evolving customer needs the brand addresses
- Customer pain points the brand solves
- Market position vs. competitors (premium, value, mid-tier)
- Distribution channels (retail, DTC, e-commerce split)

### 6. Sustainability & Social Responsibility
- Environmental sustainability programs and commitments
- Circular economy initiatives (recycling, refill, take-back)
- Ethical sourcing and supply chain transparency
- Community engagement and social impact programs
- Carbon neutrality or net-zero targets
- Certifications (B Corp, Fair Trade, organic, etc.)

### 7. Competitive Context & Market Trends
- Top 3-5 direct competitors
- Competitive advantages and differentiators
- Market challenges or headwinds
- Category trends the brand is responding to
- Consumer behavior shifts affecting the brand
- Regulatory or industry changes impacting strategy

### 8. Recent News & Market Signals (Last 6 Months)
- Major announcements (product launches, partnerships, acquisitions)
- Executive changes or organizational restructuring
- Marketing campaigns or brand activations
- Controversies or reputation issues (if significant)
- Financial performance highlights (if public company)
- Trade press coverage and industry analysis

## Research Quality Standards

### Depth Requirements
- **Minimum 15 data points per dimension** (120+ total facts per brand)
- Prioritize 2023-2025 information; avoid outdated data (pre-2022)
- Include specific examples with dates and details (not generic statements)
- Cite sources when possible (URLs, publication names, dates)

### Source Quality
- **Tier 1 Sources (Prioritize):**
  - Official brand websites (About, Press Room, Sustainability pages)
  - Annual reports and investor presentations
  - Press releases and news sections
  - Official social media accounts (LinkedIn, Twitter for corporate news)

- **Tier 2 Sources (Validate with Tier 1):**
  - Trade publications (Food Dive, Marketing Dive, Retail Dive, AdAge)
  - Business news (Bloomberg, Reuters, WSJ, Forbes)
  - Industry reports (Mintel, Euromonitor summaries)
  - Market research firms (Nielsen, IRI insights)

- **Tier 3 Sources (Use for Context Only):**
  - General news outlets
  - Consumer reviews and social media sentiment
  - Third-party analysis blogs

### Accuracy & Verification
- Cross-reference facts across multiple sources when possible
- Flag information as "unverified" if from single source
- Distinguish between company claims and third-party validation
- Note conflicting information and investigate discrepancies

## Output Format

For each brand, create a structured markdown file: `{brand-name}-research.md`

```markdown
# {Brand Name} - Comprehensive Brand Research
**Research Date:** {YYYY-MM-DD}
**Researcher:** {Agent/Human Name}
**Sources Reviewed:** {Number}

---

## 1. Brand Overview & Positioning

### Official Positioning
- {Positioning statement or brand promise}
- {Source: URL or document}

### Brand Values
- {Value 1}
- {Value 2}
- {Value 3}

### Target Audience
- **Demographics:** {Age, income, location}
- **Psychographics:** {Values, lifestyle, attitudes}

### Current Campaigns
- **Campaign Name:** {Description, launch date, key message}
- {Source: URL}

---

## 2. Product Portfolio & Innovation

### Core Product Categories
1. {Category 1}: {Brief description, key products}
2. {Category 2}: {Brief description, key products}
3. {Category 3}: {Brief description, key products}

### Flagship Products
- **{Product Name}:** {Description, why it's flagship}
- **{Product Name}:** {Description, why it's flagship}

### Recent Product Launches (2023-2025)
- **{Product Name}** (Launch: {Date}): {Description, innovation angle, target customer}
  - {Source: URL}
- **{Product Name}** (Launch: {Date}): {Description, innovation angle, target customer}
  - {Source: URL}

---

## 3. Recent Innovations (Last 18 Months)

### Product Innovations
- **{Innovation Name}** ({Date}): {Description, impact, differentiation}
  - {Source: URL}

### Packaging & Format Innovations
- **{Innovation}** ({Date}): {Description, sustainability or convenience angle}

### Technology Integrations
- **{Technology/Platform}** ({Date}): {Description, customer benefit}

### Sustainability Innovations
- **{Initiative}** ({Date}): {Description, environmental impact}

### Marketing & Experience Innovations
- **{Campaign/Experience}** ({Date}): {Description, engagement approach}

### Partnerships & Collaborations
- **{Partner Name}** ({Date}): {Purpose, product/initiative, outcome}

### Awards & Recognition
- **{Award}** ({Date}): {Awarding body, criteria, significance}

---

## 4. Strategic Priorities & Business Strategy

### Stated Strategic Goals
- **{Goal 1}:** {Description, timeline, rationale}
  - {Source: Annual report, investor presentation, press release}
- **{Goal 2}:** {Description, timeline, rationale}

### Growth Initiatives
- {Market expansion, product innovation, acquisition strategy}

### Digital Transformation
- {E-commerce, DTC, technology platforms, data analytics}

### Sustainability Commitments
- **{Commitment}:** {Target date, metrics, progress}

### Operational Priorities
- {Supply chain, manufacturing, cost optimization}

---

## 5. Target Customers & Market Positioning

### Primary Customer Segments
- **Segment 1:** {Demographics, psychographics, needs, behaviors}
- **Segment 2:** {Demographics, psychographics, needs, behaviors}

### Customer Pain Points Addressed
- {Pain point 1 → Brand solution}
- {Pain point 2 → Brand solution}

### Market Positioning
- **Price Tier:** {Premium, mid-tier, value}
- **Positioning vs. Competitors:** {Differentiation, unique position}

### Distribution Strategy
- **Retail:** {Channel types, key partners}
- **E-commerce:** {Own site, marketplaces, digital share}
- **DTC:** {Strategy, channels, importance}

---

## 6. Sustainability & Social Responsibility

### Environmental Sustainability
- **{Program/Initiative}:** {Description, impact, timeline}
- **{Program/Initiative}:** {Description, impact, timeline}

### Circular Economy
- {Recycling programs, refill systems, take-back initiatives}

### Ethical Sourcing
- {Supplier standards, certifications, transparency measures}

### Social Impact
- {Community programs, charitable giving, employee initiatives}

### Targets & Certifications
- **Carbon Target:** {Net-zero by YYYY, interim targets}
- **Certifications:** {B Corp, Fair Trade, Organic, etc.}

---

## 7. Competitive Context & Market Trends

### Top Competitors
1. **{Competitor 1}:** {Why competitive, market position}
2. **{Competitor 2}:** {Why competitive, market position}
3. **{Competitor 3}:** {Why competitive, market position}

### Competitive Advantages
- {Advantage 1: technology, scale, brand equity, etc.}
- {Advantage 2}

### Market Challenges
- {Challenge 1: regulatory, supply chain, consumer shift}
- {Challenge 2}

### Category Trends
- **{Trend 1}:** {Description, brand response}
- **{Trend 2}:** {Description, brand response}

### Consumer Behavior Shifts
- {Shift 1: health, sustainability, convenience → Impact on brand}

---

## 8. Recent News & Market Signals (Last 6 Months)

### Major Announcements
- **{Date}:** {Announcement - product launch, partnership, acquisition}
  - {Source: URL}

### Marketing Campaigns
- **{Campaign Name}** ({Date}): {Description, channels, message}

### Executive Changes
- **{Date}:** {Change description, implications}

### Financial Performance
- **{Quarter/Year}:** {Revenue, growth, key metrics, strategic implications}

### Trade Press Coverage
- **{Date}:** {Publication, headline, key points}
  - {Source: URL}

### Industry Analysis
- {Analyst perspective, market position assessment, future outlook}

---

## Research Methodology

### Sources Consulted
1. {Official website - URL}
2. {Annual report YYYY - URL}
3. {Press releases - URL}
4. {Trade publication articles - URLs}
5. {Industry reports - Names}

### Search Queries Used
- "{Brand name} recent innovations 2024 2025"
- "{Brand name} sustainability strategy"
- "{Brand name} product launches 2024"
- "{Brand name} target market strategy"
- "{Brand name} annual report 2024"
- "{Brand name} investor presentation"

### Research Limitations
- {Any information gaps or areas with limited public data}
- {Conflicting information that couldn't be resolved}

---

## Key Insights Summary (For Pipeline Context)

### Innovation DNA
{2-3 sentences: What types of innovations does this brand pursue? Product, process, marketing, sustainability? What's their innovation philosophy?}

### Strategic North Star
{2-3 sentences: What's driving this brand's strategy? Growth markets, sustainability, customer experience, technology, cost optimization?}

### Opportunity Whitespace
{2-3 sentences: Based on research, where might this brand have unaddressed opportunities or gaps in their current strategy?}

---

**Research Completed:** {Date}
**Total Sources:** {Number}
**Confidence Level:** {High/Medium/Low - with rationale}
```

## Execution Instructions

### Research Workflow
1. **Start with official sources:** Brand website, investor relations, press room
2. **Expand to trade press:** Search trade publications for recent coverage
3. **Review financial documents:** Annual reports, 10-Ks (if public), investor presentations
4. **Monitor social/digital:** LinkedIn company page, Twitter for news, YouTube for campaigns
5. **Competitor context:** Quick scan of top 3 competitors for positioning context
6. **Synthesize insights:** Write Key Insights Summary section

### Time Allocation per Brand
- **Target: 2-3 hours of deep research per brand**
- Official sources: 45 min
- Trade press & news: 45 min
- Financial/strategy docs: 30 min
- Synthesis & writing: 30 min

### Quality Checkpoints
- [ ] Minimum 15 data points per section (120+ total)
- [ ] 80%+ of information from 2023-2025
- [ ] All claims have source citations
- [ ] Recent innovations section has 8+ specific examples
- [ ] No generic statements ("focuses on quality") without evidence
- [ ] Key Insights Summary is specific to THIS brand (not boilerplate)

## Deliverables

Create 4 research files in `/docs/web-search-setup/`:

1. `lactalis-canada-research.md`
2. `mccormick-usa-research.md`
3. `columbia-sportswear-research.md`
4. `decathlon-research.md`

Plus summary document:
5. `research-summary.md` - Overview of all 4 brands with cross-brand insights

---

## Agent Capabilities Required

To execute this research effectively, you should:

- **Web search proficiency:** Use advanced search operators, find authoritative sources
- **Source evaluation:** Distinguish primary from secondary sources, assess credibility
- **Information synthesis:** Extract signal from noise, identify patterns
- **Business acumen:** Understand strategy, competitive positioning, market dynamics
- **Writing clarity:** Present findings in structured, scannable format
- **Efficiency:** Balance depth with speed (2-3 hours per brand)

---

## Success Criteria

Research is complete when:

1. All 4 brand research files created with complete sections
2. Each file contains 120+ specific, sourced facts
3. Recent innovations section has rich, detailed examples (8+ per brand)
4. Key Insights Summary provides actionable context for AI opportunity generation
5. Research enables Stage 4 to generate brand-specific, differentiated strategic insights
6. Another researcher could validate findings from cited sources

---

**NOW BEGIN RESEARCH:** Start with Lactalis Canada, then proceed to McCormick USA, Columbia Sportswear, and Decathlon. Create structured markdown files in `/docs/web-search-setup/` following the format above.
