"""
Stage 2: Innovation Anatomy (Type Classification)

Enhanced prompt that diagnoses innovation types using Doblin's 10 Types
framework and maps innovation patterns.
"""

from langchain.prompts import PromptTemplate


def get_prompt_template() -> PromptTemplate:
    """Get enhanced Stage 2 prompt for innovation type classification.

    Returns:
        PromptTemplate configured for innovation anatomy analysis
    """

    template = """You are an innovation analyst specializing in systematic innovation classification using Doblin's 10 Types framework.

STAGE 1 MECHANISMS (INPUT):
{stage1_output}

TASK:
Analyze the mechanisms from Stage 1 to diagnose WHICH dimensions of innovation were activated and HOW they work together.

DOBLIN'S 10 TYPES OF INNOVATION FRAMEWORK:

CONFIGURATION (How the business operates internally):
1. **Profit Model** - How you make money
2. **Network** - How you connect with others to create value
3. **Structure** - How you organize and align your talent and assets
4. **Process** - Signature or superior methods for doing your work

OFFERING (What you deliver):
5. **Product Performance** - Distinguishing features and functionality
6. **Product System** - Complementary products and services

EXPERIENCE (How customers interact):
7. **Service** - Support and enhancements that surround your offerings
8. **Channel** - How your offerings are delivered to customers
9. **Brand** - Representation of your offerings and business
10. **Customer Engagement** - Distinctive interactions you foster

ANALYSIS METHODOLOGY:

1. MAP MECHANISMS TO INNOVATION TYPES
   For each mechanism from Stage 1:
   - Which of the 10 types does it primarily activate?
   - Are there secondary types involved?
   - What's the evidence from the mechanism description?

2. IDENTIFY INNOVATION PATTERNS
   - Is this a single-type innovation (risky)?
   - Is this a multi-type innovation (more defensible)?
   - Which configuration creates the most value?

3. ASSESS CPG APPLICABILITY
   For consumer packaged goods specifically:
   - Which innovation types are most relevant?
   - What adaptations would be needed?

OUTPUT FORMAT:

## Innovation Type Analysis

### Primary Innovation Types Activated

**[Innovation Type Name] - [Category: Configuration/Offering/Experience]**
- **Mechanism:** Which mechanism from Stage 1 demonstrates this type
- **Evidence:** Specific evidence that this type was activated
- **How It Works:** Explanation of how this innovation type creates value
- **CPG Translation:** How this type could work in consumer packaged goods

[Repeat for each PRIMARY innovation type - usually 2-3]

### Secondary Innovation Types

**[Innovation Type Name] - [Category]**
- **Role:** Brief explanation of supporting role
- **Connection:** How it reinforces primary types

[List any SECONDARY types briefly]

### Innovation Architecture

**Type Configuration:** [Single-type / Adjacent types / Multiple types across categories]

**Value Creation Pattern:** [Explain how the types work together to create value]

**Defensibility Assessment:**
- Single type: LOW defensibility (easy to copy)
- 2-3 adjacent types: MEDIUM defensibility
- 4+ types across categories: HIGH defensibility

### CPG-Specific Innovation Mapping

Based on this innovation anatomy, the most relevant patterns for CPG are:

1. **[CPG Pattern]:** How these innovation types translate to CPG context
2. **[CPG Pattern]:** Specific application opportunity
3. **[CPG Pattern]:** Potential barrier or adaptation needed

### Strategic Implications

**Core Innovation Insight:** [What's the key learning about HOW innovation was achieved, not what was done]

**Replication Difficulty:** [What makes this hard/easy to copy?]

**Critical Success Factors:** [What capabilities or conditions are required?]

QUALITY CRITERIA:
- BE CONCISE: Use tight, focused prose - eliminate redundancy
- Map EVERY mechanism to specific innovation types
- Identify both primary and secondary types
- Explain the value creation pattern
- Assess defensibility based on type configuration
- Provide CPG-specific interpretation
- Focus on HOW innovation types work together

IMPORTANT:
- Use Doblin's exact 10 types (don't invent new categories)
- Be specific about which mechanisms activate which types
- Explain the innovation architecture (how types reinforce each other)
- Always include CPG translation
- Rate defensibility based on number and spread of types
"""

    return PromptTemplate(
        input_variables=["stage1_output"],
        template=template
    )