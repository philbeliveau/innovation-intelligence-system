"""
Stage 3: General Translation to Universal Lessons

This module defines the prompt template for Stage 3 of the Innovation
Intelligence Pipeline. Stage 3 synthesizes Stage 1 inspirations and Stage 2
trends into universal, brand-agnostic lessons.
"""

from langchain.prompts import PromptTemplate


def get_prompt_template() -> PromptTemplate:
    """Get Stage 3 prompt template for universal lesson generation.

    Returns:
        PromptTemplate configured for Stage 3 processing

    Example:
        >>> template = get_prompt_template()
        >>> chain = LLMChain(llm=llm, prompt=template)
    """

    template = """You are an innovation strategist synthesizing insights into universal principles that can be applied across industries.

STAGE 1 INSPIRATIONS (INPUT):
{stage1_output}

STAGE 2 TRENDS (INPUT):
{stage2_output}

TASK:
Synthesize the Stage 1 inspirations and Stage 2 trends into 5-7 universal lessons that are completely brand-agnostic and applicable across industries.

CRITICAL DE-CONTEXTUALIZATION REQUIREMENT:
- REMOVE all specific brand names, company names, and industry references
- REMOVE specific product names, sports references, or contextual details
- EXTRACT the underlying principle that makes the approach work
- TRANSLATE to universal language applicable to any industry (CPG, retail, services, B2B, etc.)

SYNTHESIS METHODOLOGY:
1. Review both Stage 1 inspirations and Stage 2 trends to identify core principles
2. Ask: "What underlying human need, business principle, or strategic pattern explains this?"
3. Strip away all context: if it mentions baseball → what's the universal principle?
4. Frame each lesson as a timeless principle, not a trend observation
5. Optional: Reference innovation frameworks (TRIZ, SIT, biomimicry) if they help explain the principle

INNOVATION FRAMEWORK REFERENCES (Optional):
- **TRIZ Principles**: Systematic innovation patterns (segmentation, asymmetry, universality, nested dolls, counterweight, preliminary action, etc.)
- **SIT (Structured Inventive Thinking)**: Subtraction, multiplication, division, task unification, attribute dependency
- **Biomimicry**: Nature-inspired solutions (adaptation, resilience, optimization, ecosystem thinking)

Use these frameworks ONLY if they genuinely illuminate the universal principle. Do not force-fit frameworks.

OUTPUT FORMAT:
Structure your analysis as markdown with the following sections:

# Universal Lessons

## 1. [Lesson Title - Universal Principle Name]

**The Principle:** [Clear, concise statement of the universal principle - should be applicable to any industry]

**Why It Works:** [Psychological, strategic, or business explanation for why this principle is effective. What human need or market dynamic does it address?]

**Where It Could Apply:** [3-5 concrete examples of how this principle could be applied in different industries - be specific about the application, not just industry names]

**Innovation Framework Connection:** [Optional - only if TRIZ, SIT, or biomimicry genuinely relates to this principle]

---

## 2. [Lesson Title - Universal Principle Name]

**The Principle:** [Clear, concise statement]

**Why It Works:** [Explanation of effectiveness]

**Where It Could Apply:** [3-5 concrete application examples across industries]

**Innovation Framework Connection:** [Optional framework reference]

---

[Continue for 5-7 lessons total]

# Synthesis Notes

**Core Themes:** [What overarching patterns emerge across these universal lessons? How do they relate to each other?]

**Strategic Value:** [Why are these lessons valuable for innovation work? What makes them actionable rather than generic advice?]

**De-contextualization Quality Check:** [Confirm that all brand/industry/product-specific references have been removed. Note any remaining context that should be eliminated.]

UNIVERSAL LESSON QUALITY CRITERIA:
- **Truly Universal**: Could apply to CPG, retail, healthcare, financial services, B2B software, manufacturing, etc.
- **Actionable**: Specific enough to guide action, not generic platitudes like "focus on the customer"
- **Principle-Based**: Explains WHY something works, not just WHAT was done
- **De-contextualized**: Zero mentions of specific brands, industries, products, or contextual details from the input
- **Strategic**: Provides insight that innovation teams can build upon

IMPORTANT:
- Generate exactly 5-7 universal lessons (no more, no less)
- Each lesson MUST be completely brand-agnostic (no brand/industry/product mentions)
- Each lesson MUST be actionable and specific (not generic advice)
- Each lesson MUST explain WHY it works (psychological/strategic rationale)
- Each lesson MUST show WHERE it applies with concrete examples across industries
- Use innovation frameworks (TRIZ/SIT/biomimicry) ONLY when genuinely relevant
- Ensure output follows the exact markdown structure above
- In De-contextualization Quality Check, verify zero brand/industry-specific language remains
"""

    return PromptTemplate(
        input_variables=["stage1_output", "stage2_output"],
        template=template
    )
