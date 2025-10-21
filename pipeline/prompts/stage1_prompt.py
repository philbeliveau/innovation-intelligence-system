"""
Stage 1: Mechanism Extraction (Latent Factor Identification)

Enhanced prompt that extracts transferable innovation mechanisms
using abstraction ladder and structural pattern recognition.
"""

from langchain.prompts import PromptTemplate


def get_prompt_template() -> PromptTemplate:
    """Get enhanced Stage 1 prompt for mechanism extraction.

    Returns:
        PromptTemplate configured for mechanism extraction
    """

    template = """You are an expert innovation strategist specializing in cross-industry pattern recognition and transferable insight extraction.

INPUT DOCUMENT:
{input_text}

TASK:
Extract the 2-3 most important MECHANISMS from this document - the underlying patterns that make innovations work, not just surface observations.

CRITICAL: BANNED WORDS
Never use: "interesting," "innovative," "unique," "creative," "inspiring," "better," "improved," "disruptive," "revolutionary"
If you use these words, you haven't thought deeply enough.

EXTRACTION METHODOLOGY:

1. IDENTIFY THE CONCRETE INNOVATION
   - What specific company/brand/product is discussed?
   - What exactly did they launch or change?
   - What measurable impact did it have?

2. CLIMB THE ABSTRACTION LADDER
   Ask repeatedly: "Why does this work?"
   - Level 1: What specific action was taken?
   - Level 2: What problem did that action solve?
   - Level 3: What fundamental human need or market dynamic does this address?
   - Level 4: What is the universal principle that ANY industry could apply?

3. IDENTIFY THE MECHANISM TYPE
   Which specific innovation mechanism was used?
   □ UNBUNDLED - Separated and served only the most valuable part
   □ COMBINED - Merged two previously separate categories/solutions
   □ REMOVED FRICTION - Eliminated specific steps in customer journey
   □ CHANGED MODEL - Altered business model rather than product
   □ REFRAMED - Repositioned the category or value proposition
   □ DEMOCRATIZED - Made exclusive/expensive accessible to masses
   □ PREMIUMIZED - Added layers of value to justify higher price
   □ DIGITIZED ANALOG - Moved physical process to digital
   □ HUMANIZED DIGITAL - Added human touch to digital experience
   □ TIME-SHIFTED - Changed when/how often consumption happens

4. QUANTIFY THE CONSTRAINT ELIMINATED
   Be specific about what constraint was removed:
   - TIME: Reduced from X to Y (be specific)
   - COST: Decreased by X% or $Y amount
   - KNOWLEDGE: Eliminated need for [specific expertise]
   - ACCESS: Made available where/when it wasn't
   - EFFORT: Reduced steps from X to Y

OUTPUT FORMAT:
Extract exactly 2-3 mechanisms (quality over quantity):

## Mechanism 1: [Descriptive Title of the Pattern]

**Concrete Example:** [Specific company/product and what they did - 1-2 sentences]

**The Underlying Mechanism:** [The transferable pattern in abstract terms - explain HOW it works structurally, not what was done specifically]

**Mechanism Type:** [One from the list above]

**Constraint Eliminated:** [Specific, quantified constraint that was removed]

**Why It Works:** [The fundamental psychological, economic, or strategic principle that makes this mechanism effective across industries]

**Structural Pattern:** [Abstract formula: "When [condition X exists], eliminating [constraint Y] by [mechanism Z] creates [value type]"]

---

## Mechanism 2: [Descriptive Title of the Pattern]

[Same structure as above]

---

[Optional Mechanism 3 if truly distinct and valuable]

## Extraction Quality Check

**Abstraction Test:** [Can these mechanisms be explained to someone in a completely different industry? Yes/No with explanation]

**Evidence Strength:** [Rate the quality of evidence in the document: HIGH/MEDIUM/LOW with rationale]

**CPG Relevance:** [Initial assessment of how these mechanisms might apply to consumer packaged goods]

IMPORTANT:
- Extract mechanisms, not observations
- Focus on HOW things work, not WHAT happened
- Ensure each mechanism is truly transferable (could work in multiple industries)
- Quantify constraints wherever possible
- Be ruthlessly specific while maintaining abstraction
- If you can't extract 2 strong mechanisms, state why and extract what you can
"""

    return PromptTemplate(
        input_variables=["input_text"],
        template=template
    )