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
Extract the PRIMARY MECHANISM from this document - the underlying pattern that makes innovations work, not just surface observations. Then identify 1-2 additional mechanisms if they are truly distinct.

OUTPUT MUST BE VALID JSON following this exact structure:
{{
  "extractedText": "Concise summary of the input document (150-300 words max)",
  "trendTitle": "The main innovation/trend being analyzed",
  "trendImage": null,
  "coreMechanism": "The primary transferable pattern in one clear sentence",
  "businessImpact": "Quantified business value (include metrics if available)",
  "patternTransfersTo": ["Industry 1", "Industry 2", "Industry 3", "Industry 4"],
  "mechanisms": [
    {{
      "title": "Descriptive title of mechanism 1",
      "concreteExample": "Specific company/product and what they did (1-2 sentences)",
      "underlyingMechanism": "The transferable pattern explained",
      "mechanismType": "One of: UNBUNDLED, COMBINED, REMOVED_FRICTION, CHANGED_MODEL, REFRAMED, DEMOCRATIZED, PREMIUMIZED, DIGITIZED_ANALOG, HUMANIZED_DIGITAL, TIME_SHIFTED",
      "constraintEliminated": "Specific quantified constraint removed",
      "whyItWorks": "Fundamental principle across industries",
      "structuralPattern": "Abstract formula"
    }}
  ],
  "abstractionTest": "Can these mechanisms be explained to someone in a different industry? (Yes/No with explanation)",
  "evidenceStrength": "HIGH/MEDIUM/LOW with rationale",
  "cpgRelevance": "Assessment of applicability to consumer packaged goods"
}}

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
   Choose from:
   - UNBUNDLED - Separated and served only the most valuable part
   - COMBINED - Merged two previously separate categories/solutions
   - REMOVED_FRICTION - Eliminated specific steps in customer journey
   - CHANGED_MODEL - Altered business model rather than product
   - REFRAMED - Repositioned the category or value proposition
   - DEMOCRATIZED - Made exclusive/expensive accessible to masses
   - PREMIUMIZED - Added layers of value to justify higher price
   - DIGITIZED_ANALOG - Moved physical process to digital
   - HUMANIZED_DIGITAL - Added human touch to digital experience
   - TIME_SHIFTED - Changed when/how often consumption happens

4. QUANTIFY THE CONSTRAINT ELIMINATED
   Be specific:
   - TIME: Reduced from X to Y
   - COST: Decreased by X% or $Y amount
   - KNOWLEDGE: Eliminated need for [specific expertise]
   - ACCESS: Made available where/when it wasn't
   - EFFORT: Reduced steps from X to Y

CRITICAL REQUIREMENTS:
- OUTPUT MUST BE VALID JSON (use double quotes, escape special characters)
- BE CONCISE: Tight, focused prose - no redundancy or filler
- Extract 1-3 mechanisms (quality over quantity)
- Focus on HOW things work, not WHAT happened
- Ensure mechanisms are truly transferable across industries
- Quantify constraints wherever possible
- Be ruthlessly specific while maintaining abstraction

Return ONLY the JSON object, no additional text before or after.
"""

    return PromptTemplate(
        input_variables=["input_text"],
        template=template
    )