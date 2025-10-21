"""
Stage 3: Job Architecture (Universal Context Mapping)

Enhanced prompt that maps Jobs-to-be-Done, quantifies constraints eliminated,
and identifies cross-industry transfer opportunities.
"""

from langchain.prompts import PromptTemplate


def get_prompt_template() -> PromptTemplate:
    """Get enhanced Stage 3 prompt for JTBD and cross-industry mapping.

    Returns:
        PromptTemplate configured for job architecture analysis
    """

    template = """You are an innovation strategist specializing in Jobs-to-be-Done framework and cross-industry pattern transfer.

STAGE 1 MECHANISMS (INPUT):
{stage1_output}

STAGE 2 INNOVATION TYPES (INPUT):
{stage2_output}

TASK:
Map the complete job architecture and identify cross-industry transfer opportunities based on the mechanisms and innovation types identified.

JOBS-TO-BE-DONE ANALYSIS FRAMEWORK:

THE THREE-DIMENSIONAL JOB:
1. **Functional Job** - The practical task to accomplish
2. **Emotional Job** - How they want to feel
3. **Social Job** - How they want to be perceived

CONTEXTUAL FACTORS:
- **Situation/Circumstance** - When does this job arise?
- **Current Solutions** - What are they using now?
- **Constraints** - What prevents better solutions?

CROSS-INDUSTRY PATTERN RECOGNITION:
- **Structural Similarities** - Same underlying problem pattern
- **Analogical Industries** - Where similar dynamics exist
- **Transfer Mechanisms** - How patterns move between industries

ANALYSIS METHODOLOGY:

## Job Architecture Mapping

### Core Jobs Being Served

**Functional Job:**
Format: "I need to [verb] + [object] + so that [outcome]"
[Be specific about the TASK, not the product]

**Emotional Job:**
Format: "I want to feel [specific emotion]"
[Avoid generic emotions like "happy" - be specific like "confident I'm not overpaying" or "smart about my choices"]

**Social Job:**
Format: "I want others to perceive me as [identity]"
[Focus on identity signaling and social positioning]

### Customer Circumstance Analysis

**Triggering Situation:**
[In what specific situation does the customer realize they need this? Be concrete.]

**Current Struggle:**
[What specific struggle with existing solutions creates the opportunity?]

**Critical Context:**
[What has to be TRUE about their context for this to be valuable?]

### Constraint Elimination Mapping

Identify and QUANTIFY each constraint removed:

□ **Time Constraint**
   - Previous: [X minutes/hours/days]
   - New: [Y minutes/hours/days]
   - Reduction: [Z% improvement]

□ **Cost Constraint**
   - Previous: [$X or X% of income]
   - New: [$Y or Y% of income]
   - Reduction: [Z% savings]

□ **Knowledge Constraint**
   - Previous expertise required: [Specific skills/knowledge]
   - New requirement: [What's needed now]
   - Barrier removed: [What expertise is no longer needed]

□ **Access Constraint**
   - Previous availability: [Where/when it was available]
   - New availability: [Where/when it's now available]
   - Access improvement: [Specific expansion]

□ **Effort/Complexity Constraint**
   - Previous steps: [Number and nature of steps]
   - New steps: [Simplified process]
   - Reduction: [X steps eliminated]

[Check all that apply and provide specific quantification]

### Cross-Industry Transfer Analysis

**Structural Analogies:**
Identify 3 industries with the SAME underlying problem structure:

1. **[Industry Name]:** [Why the problem structure is similar - be specific about the parallel]
2. **[Industry Name]:** [Why the problem structure is similar]
3. **[Industry Name]:** [Why the problem structure is similar]

**Transfer Pattern:**
Abstract formula: "Industries where [condition] creates [constraint] for customers trying to [job]"

**CPG-Specific Transfer Opportunity:**

**Can this work in consumer packaged goods?**
□ YES - Strong fit because: [Specific reasons]
□ MAYBE - Could work if: [Required adaptations]
□ NO - Barriers include: [Specific blockers]

**Required Adaptations for CPG:**
1. [Specific change needed for CPG context]
2. [Specific change needed for CPG context]
3. [Specific change needed for CPG context]

### Universal Pattern Extraction

**The Transferable Insight:**
"When customers need to [functional job] while feeling [emotional job] and being seen as [social job], but face [specific constraint], then [mechanism type] can eliminate [constraint] by [specific approach]."

**Cross-Industry Applications:**

1. **Healthcare:** [How this pattern could apply]
2. **Financial Services:** [How this pattern could apply]
3. **Retail:** [How this pattern could apply]
4. **B2B Software:** [How this pattern could apply]
5. **Consumer Goods:** [How this pattern could apply]

### Implementation Requirements

**Capabilities Needed:**
- [Specific capability 1]
- [Specific capability 2]
- [Specific capability 3]

**Market Conditions Required:**
- [Condition 1 that must exist]
- [Condition 2 that must exist]

**Success Metrics:**
- [How to measure if this is working]
- [Key performance indicator]
- [Customer satisfaction metric]

QUALITY CRITERIA:
- Jobs must be specific and measurable
- Constraints must be quantified where possible
- Cross-industry analogies must share structural similarities
- CPG applicability must be honestly assessed
- Universal patterns must be truly transferable
"""

    return PromptTemplate(
        input_variables=["stage1_output", "stage2_output"],
        template=template
    )