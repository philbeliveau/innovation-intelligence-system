"""
Stage 5: Opportunity Synthesis (Actionable Cards)

Enhanced prompt focused on generating retail-ready CPG opportunities
with clear mechanisms and speed-to-market focus.
"""

from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


def get_output_parser() -> StructuredOutputParser:
    """Get structured output parser for 5 opportunity cards.

    Returns:
        StructuredOutputParser configured to extract 5 opportunities
    """

    response_schemas = [
        ResponseSchema(
            name="opportunities",
            description="Array of exactly 5 innovation opportunities",
            type="array"
        )
    ]

    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    return parser


def get_prompt_template() -> PromptTemplate:
    """Get enhanced Stage 5 prompt for CPG opportunity generation.

    Returns:
        PromptTemplate configured for Stage 5 processing
    """

    parser = get_output_parser()
    format_instructions = parser.get_format_instructions()

    template = """You are a CPG innovation strategist generating retail-ready opportunities for immediate execution.

BRAND-SPECIFIC CPG OPPORTUNITIES (FROM STAGE 4):
{stage4_output}

BRAND: {brand_name}
INPUT SOURCE: {input_source}

TASK:
Generate exactly 5 distinct, retail-ready innovation opportunities that can be pitched to buyers within 90 days.

CPG INNOVATION REALITY CHECK:
- Innovation teams have 2-5 people, not 50
- Quarterly pipeline reviews demand concepts NOW
- Retail buyers need to see it, understand it, and want it in 30 seconds
- Budget is $50K for research, not $500K
- Success = on shelf in 12 months at Target/Walmart

THE 5 OPPORTUNITIES MUST SPAN THESE PATTERNS:
1. **Better-For-You** - Protein+, sugar-, clean label
2. **Premium** - 2x price, craft story, better ingredients
3. **Convenience** - RTD, portable, no-prep
4. **Format** - New form factor for consumption
5. **Occasion** - New when/where to consume

OUTPUT STRUCTURE FOR EACH OPPORTUNITY:

**title**: [8 words max - must be specific and compelling]

**innovation_type**: [Choose ONE: Better-For-You, Premium, Convenience, Format, Occasion]

**description**: [3 paragraphs:
  - Para 1: WHAT - The specific product/innovation. Be concrete about form, flavor, package.
  - Para 2: WHO & WHY - Target consumer and the problem you're solving. Include price point.
  - Para 3: HOW - The mechanism from insights that makes this work. Why NOW is the time.]

**actionability_items**: [Exactly 3 next steps, each ultra-specific:
  - "Schedule co-packer visit with [specific type] facility by [date]"
  - "Conduct pricing study with [specific retailer] buyers on [specific claim]"
  - "Source [specific ingredient] samples from [type of supplier]"
  NOT vague like "Do research" or "Find partners"]

**visual_description**: [1 sentence describing the product on shelf. What does the package look like? Where in store is it?]

**follow_up_prompts**: [Exactly 2 questions that retail buyers would ask:
  - "How does this compare to [specific competitor product] on shelf?"
  - "What's your velocity projection vs [category benchmark]?"
  - "Why wouldn't [bigger competitor] just copy this?"]

**retail_metrics**: [Key data points for buyers:
  - Price point: $X.XX
  - Target velocity: X units/store/week
  - Gross margin: XX%
  - Launch timeline: X months]

CPG OPPORTUNITY QUALITY CRITERIA:
✓ Can explain to Walmart buyer in 30 seconds
✓ Uses existing co-packer capabilities (no new lines)
✓ <$500K total investment to launch
✓ Fits current shelf sets (no new category creation)
✓ Clear advantage vs. specific competitor on shelf
✓ Leverages mechanism from original insights
✓ Achievable in 12 months or less

FORBIDDEN:
✗ Science fiction ingredients that don't exist
✗ Categories that require refrigeration if brand doesn't do cold chain
✗ Subscription models for brands without DTC
✗ Premium plays for value brands (or vice versa)
✗ Complex education required for consumer understanding

{format_instructions}

IMPORTANT:
- Generate EXACTLY 5 opportunities spanning different CPG patterns
- Each must be explainable to a retail buyer in 30 seconds
- Each must be launchable with <$500K in <12 months
- Each must include specific retail metrics
- Focus on SPEED and SIMPLICITY over perfection
- This is about getting on shelf at Target, not winning innovation awards
"""

    return PromptTemplate(
        input_variables=["stage4_output", "brand_name", "input_source"],
        template=template,
        partial_variables={"format_instructions": format_instructions}
    )