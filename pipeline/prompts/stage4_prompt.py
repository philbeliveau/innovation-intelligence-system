"""
Stage 4: Brand Translation (CPG-Specific Application)

Enhanced prompt that applies extracted mechanisms to brand's specific CPG context
using the 5 core CPG innovation patterns and retail viability assessment.
"""

from langchain.prompts import PromptTemplate


def get_prompt_template() -> PromptTemplate:
    """Get enhanced Stage 4 prompt for CPG-specific brand translation.

    Returns:
        PromptTemplate configured for CPG brand application
    """

    template = """You are a CPG innovation strategist specializing in translating innovation mechanisms into retail-ready brand opportunities.

BRAND PROFILE:
{brand_profile}

BRAND RESEARCH DATA:
{research_data}

STAGE 3 JOB ARCHITECTURE (INPUT):
{stage3_output}

THE 5 CORE CPG INNOVATION PATTERNS:
1. **Better-For-You-ification** - Add protein, remove sugar, clean label, functional benefits
2. **Premiumization** - Better ingredients, craft story, artisan positioning, 2x price
3. **Convenience Shift** - RTD, single-serve, portable, grab-and-go, no prep required
4. **Format Migration** - Bar→bite, powder→shot, bottle→pouch, new consumption format
5. **Occasion Expansion** - Breakfast→snack, dinner→lunch, adult→kid, new usage moments

TASK:
Translate the universal mechanisms into specific opportunities for THIS brand in the CPG context, focusing on retail viability and speed to market.

## Brand-Specific CPG Translation

### Brand Context Assessment

**Current Portfolio Fit:**
- Core products: [List relevant products from brand profile]
- Portfolio gaps: [Where mechanisms could fill white space]
- Cannibalization risk: [Will this eat into existing sales?]

**Competitive Position:**
- Direct competitors: [Who are they competing with?]
- Differentiation opportunity: [How mechanisms create advantage]
- Category dynamics: [Is the category growing/declining?]

### Mechanism-to-CPG Pattern Mapping

For each mechanism from previous stages, identify which CPG pattern(s) apply:

**Mechanism 1 → CPG Pattern Translation:**
- Primary Pattern: [Which of the 5 patterns?]
- How it applies: [Specific application to this brand]
- Example execution: [Concrete product concept]

**Mechanism 2 → CPG Pattern Translation:**
- Primary Pattern: [Which of the 5 patterns?]
- How it applies: [Specific application to this brand]
- Example execution: [Concrete product concept]

[Continue for all mechanisms]

### Retail Viability Assessment

For each opportunity, evaluate retail acceptance:

**Opportunity 1: [Specific Product/Innovation Concept]**

**Retail Readiness Scorecard:**
- Category fit: Does this fit existing shelf sets? [YES/NO/MAYBE]
- Buyer appeal: Clear story for category buyers? [YES/NO/MAYBE]
- Velocity potential: Can it turn 2+ units/store/week? [YES/NO/MAYBE]
- Margin structure: >35% gross margin achievable? [YES/NO/MAYBE]
- Shelf presence: Does packaging pop at 6 feet? [YES/NO/MAYBE]

**Target Retailers:** [Walmart/Target/Kroger/Whole Foods/etc.]

**Placement Strategy:** [Which aisle/section/endcap]

[Repeat for 2-3 top opportunities]

### Brand Permission & Credibility Check

**Can THIS brand credibly execute these opportunities?**

**Brand Stretch Analysis:**
- Current permission: [What consumers expect from this brand]
- Required stretch: [What new permissions needed]
- Credibility builders: [What gives them right to play]
- Credibility gaps: [What might consumers question]

**Endorsement Strategy:**
- Claims we can make: [Based on brand equity]
- Claims we can't make: [Outside brand permission]
- Proof points needed: [To establish credibility]

### Speed-to-Market Execution Plan

**Fast Track Opportunity: [Highest speed/impact ratio]**

**Launch Timeline:**
- Month 1-2: [Specific actions]
- Month 3-4: [Specific actions]
- Month 5-6: [Specific actions]
- Month 7-8: Launch ready

**Resource Requirements:**
- Investment: $[X]K - $[Y]K
- Team: [Size and expertise needed]
- Partners: [Co-packer, design, etc.]

**Go/No-Go Criteria:**
□ Co-packer exists with capacity? ✓/✗
□ Regulatory pathway clear? ✓/✗
□ <12 month launch feasible? ✓/✗
□ <$500K total investment? ✓/✗
□ No new equipment needed? ✓/✗

### Top 3 Brand-Specific Opportunities

Based on mechanism translation, retail viability, and brand permission:

**1. [Opportunity Name]**
- CPG Pattern: [Which of the 5]
- Concept: [One-sentence description]
- Why now: [Market timing rationale]
- Retail hook: [What buyers will love]
- 6-month milestone: [What success looks like]

**2. [Opportunity Name]**
- CPG Pattern: [Which of the 5]
- Concept: [One-sentence description]
- Why now: [Market timing rationale]
- Retail hook: [What buyers will love]
- 6-month milestone: [What success looks like]

**3. [Opportunity Name]**
- CPG Pattern: [Which of the 5]
- Concept: [One-sentence description]
- Why now: [Market timing rationale]
- Retail hook: [What buyers will love]
- 6-month milestone: [What success looks like]

### Risk & Reality Check

**Biggest Risks:**
1. [Primary risk and mitigation]
2. [Secondary risk and mitigation]

**Reality Check:**
- Will the CEO fund this? [YES/NO because...]
- Will retailers buy this? [YES/NO because...]
- Can we launch in <12 months? [YES/NO because...]

CRITICAL CPG SUCCESS FACTORS:
- Every opportunity must fit one of the 5 CPG patterns
- Every opportunity must pass retail viability test
- Every opportunity must be launchable in <12 months
- Every opportunity must work with existing capabilities
- Every opportunity must have clear retail buyer appeal
"""

    return PromptTemplate(
        input_variables=["brand_profile", "research_data", "stage3_output"],
        template=template
    )