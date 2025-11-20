"""Stage 6: Opportunity Card Packaging

Formats directional concepts into 30-second pitch markdown cards.

CARD STRUCTURE (30-second pitch format):
1. Concept Name: Clear, memorable name
2. Consumer Insight: The problem being solved (functional/emotional/social needs)
3. Mechanism: How it works (SIT technique application)
4. Why Now: Trend evidence + lifecycle stage
5. Why This Brand: Brand-specific fit
6. Competitive Landscape: Summary from Stage 5
7. No-Hallucination Disclosure: Explicit boundary statement

Process:
1. For each concept, gather all context (trends, insights, techniques, competitive intel)
2. Generate markdown card using template
3. Validate markdown structure
4. Include explicit boundary disclosure

Performance Target: < 30 seconds (3-5 cards)
"""
import json
import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..schemas import (
    Stage1Output,
    Stage2Output,
    Stage3Output,
    Stage4Output,
    Stage6Output,
    OpportunityCard,
    DirectionalConcept
)
from ..prompt_template_library import load_prompt_template
from ..few_shot_integration import inject_examples_into_stage_prompt


class Stage6OpportunityCards:
    """Stage 6: Format concepts into markdown opportunity cards."""

    CARD_TEMPLATE = """# 💡 {concept_name}

## 🎯 Consumer Insight
> "{consumer_statement}"

**Functional Need:** {functional_need}
**Emotional Need:** {emotional_need}
**Social Need:** {social_need}

---

## ⚙️ Mechanism ({technique_framework}: {technique_name})
{mechanism_description}

**How It Works:**
{mechanism_steps}

---

## 📈 Why Now?
**Trend:** {trend_name} ({lifecycle_stage})
- **Evidence:** {trend_evidence}
- **Timeline:** Emerging {emergence_year}, peaking {peak_year}
- **Emotional Shift:** From "{negative_emotion}" → To "{positive_emotion}"

---

## 🏢 Why {brand_name}?
{brand_fit_rationale}

**Brand Assets:**
{brand_assets}

---

## 🔍 Competitive Landscape
{competitive_summary}

**Novelty Assessment:** {novelty_assessment}

---

## ⚠️ Boundary Disclosure
This is a **directional concept** generated from trend analysis and systematic innovation techniques. It does NOT include:
- Financial projections or ROI estimates
- Detailed implementation plans
- Market validation or customer research
- Competitive claims beyond documented search results

**Next Steps:** Validate with customer research, financial modeling, and feasibility assessment.

---

**Generated:** {timestamp}
**Pipeline Version:** 7-Stage SIT-Based Extraction
**Source Trend Report:** {source_report}
"""

    async def execute(
        self,
        stage1_output: Stage1Output,
        stage2_output: Stage2Output,
        stage3_output: Stage3Output,
        stage4_output: Stage4Output,
        stage5_output: Dict[str, Any],
        brand_context: Dict[str, Any],
        openrouter_client: Any,
        source_report_name: str = "Unknown Report",
        run_id: Optional[str] = None
    ) -> Stage6Output:
        """Execute Stage 6: Opportunity Card Packaging.

        Args:
            stage1_output: Trends from Stage 1
            stage2_output: Consumer insights from Stage 2
            stage3_output: Matched techniques from Stage 3
            stage4_output: Directional concepts from Stage 4
            stage5_output: Competitive intelligence from Stage 5
            brand_context: Enriched brand profile from Stage 0
            run_id: Optional pipeline run ID (for usage tracking)
            openrouter_client: OpenRouter API client (for card generation)
            source_report_name: Name of source trend report

        Returns:
            Stage6Output with markdown opportunity cards
        """
        opportunity_cards = []

        for concept in stage4_output.concepts:
            # Gather all context for this concept
            context = self._gather_concept_context(
                concept=concept,
                stage1_output=stage1_output,
                stage2_output=stage2_output,
                stage3_output=stage3_output,
                stage5_output=stage5_output,
                brand_context=brand_context
            )

            # Add run_id to context for few-shot injection
            context["run_id"] = run_id

            # Generate markdown card
            markdown_card = await self._generate_opportunity_card(
                concept=concept,
                context=context,
                openrouter_client=openrouter_client,
                source_report_name=source_report_name
            )

            # Parse card sections for structured access
            card_sections = self._parse_card_sections(markdown_card)

            opportunity_cards.append(
                OpportunityCard(
                    card_id=str(uuid.uuid4()),
                    concept_id=concept.concept_id,
                    markdown_content=markdown_card,
                    card_sections=card_sections
                )
            )

        # Validate markdown format
        markdown_valid = all(
            self._validate_markdown_structure(card.markdown_content)
            for card in opportunity_cards
        )

        return Stage6Output(
            opportunity_cards=opportunity_cards,
            total_cards=len(opportunity_cards),
            markdown_format_validated=markdown_valid
        )

    def _gather_concept_context(
        self,
        concept: DirectionalConcept,
        stage1_output: Stage1Output,
        stage2_output: Stage2Output,
        stage3_output: Stage3Output,
        stage5_output: Dict[str, Any],
        brand_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather all context needed for opportunity card generation.

        Args:
            concept: Directional concept from Stage 4
            stage1_output: Trends
            stage2_output: Consumer insights
            stage3_output: Matched techniques
            stage5_output: Competitive intelligence
            brand_context: Brand profile

        Returns:
            Dict with all context for card generation
        """
        # Find related insight
        insight = next(
            (ins for ins in stage2_output.insights if ins.insight_id == concept.insight_id),
            None
        )

        # Find related technique
        technique = next(
            (tech for tech in stage3_output.matched_techniques if tech.insight_id == concept.insight_id),
            None
        )

        # Find related trends (via insight)
        trend_ids = insight.source_trends if insight else []
        trends = [
            trend for trend in stage1_output.trends
            if trend.trend_id in trend_ids
        ]

        # Find competitive intel for this concept
        competitive_intel = next(
            (ci for ci in stage5_output.get("competitive_intel", []) if ci.get("concept_id") == concept.concept_id),
            None
        )

        return {
            "concept": concept,
            "insight": insight,
            "technique": technique,
            "trends": trends,
            "competitive_intel": competitive_intel,
            "brand_context": brand_context
        }

    async def _generate_opportunity_card(
        self,
        concept: DirectionalConcept,
        context: Dict[str, Any],
        openrouter_client: Any,
        source_report_name: str
    ) -> str:
        """Generate markdown opportunity card using LLM.

        Args:
            concept: Directional concept
            context: All context data
            openrouter_client: OpenRouter API client
            source_report_name: Name of source trend report

        Returns:
            Markdown-formatted opportunity card
        """
        # Load prompt template
        prompt_template = load_prompt_template("stage_6_packaging")

        # Inject few-shot examples
        enhanced_template = inject_examples_into_stage_prompt(
            prompt_template=prompt_template,
            stage=6,
            brand_context=context["brand_context"],
            run_id=context.get("run_id")
        )

        # Build prompt with all context
        prompt = enhanced_template.format(
            concept=json.dumps(concept.model_dump(), indent=2),
            insight=json.dumps(context["insight"].model_dump() if context["insight"] else {}, indent=2),
            technique=json.dumps(context["technique"].model_dump() if context["technique"] else {}, indent=2),
            trends=json.dumps([t.model_dump() for t in context["trends"]], indent=2),
            competitive_intel=json.dumps(context["competitive_intel"] if context["competitive_intel"] else {}, indent=2),
            brand_context=json.dumps(context["brand_context"], indent=2),
            card_template=self.CARD_TEMPLATE,
            source_report=source_report_name,
            timestamp=datetime.now().isoformat()
        )

        # Call LLM
        response = await openrouter_client.call_llm(
            prompt=prompt,
            model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-5-sonnet-20240620"),
            max_tokens=4000,
            temperature=0.5
        )

        markdown_content = response["content"]

        # Extract markdown if wrapped in code blocks
        if "```markdown" in markdown_content:
            start = markdown_content.find("```markdown") + 11
            end = markdown_content.find("```", start)
            markdown_content = markdown_content[start:end].strip()
        elif "```" in markdown_content:
            start = markdown_content.find("```") + 3
            end = markdown_content.find("```", start)
            markdown_content = markdown_content[start:end].strip()

        return markdown_content

    def _parse_card_sections(self, markdown_content: str) -> Dict[str, str]:
        """Parse markdown card into structured sections.

        Args:
            markdown_content: Full markdown card

        Returns:
            Dict with section names as keys and content as values
        """
        sections = {}
        current_section = None
        current_content = []

        lines = markdown_content.split("\n")
        for line in lines:
            # Detect section headers
            if line.startswith("# 💡"):
                sections["concept_name"] = line.replace("# 💡", "").strip()
                current_section = "concept_name"
            elif line.startswith("## 🎯 Consumer Insight"):
                current_section = "consumer_insight"
                current_content = []
            elif line.startswith("## ⚙️ Mechanism"):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "mechanism"
                current_content = []
            elif line.startswith("## 📈 Why Now"):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "why_now"
                current_content = []
            elif line.startswith("## 🏢 Why"):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "why_brand"
                current_content = []
            elif line.startswith("## 🔍 Competitive Landscape"):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "competitive_landscape"
                current_content = []
            elif line.startswith("## ⚠️ Boundary Disclosure"):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "boundary_disclosure"
                current_content = []
            else:
                if current_section:
                    current_content.append(line)

        # Add last section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _validate_markdown_structure(self, markdown_content: str) -> bool:
        """Validate that markdown card has all required sections.

        Args:
            markdown_content: Full markdown card

        Returns:
            True if all required sections present
        """
        required_sections = [
            "# 💡",  # Concept Name
            "## 🎯 Consumer Insight",
            "## ⚙️ Mechanism",
            "## 📈 Why Now",
            "## 🏢 Why",  # Brand name varies
            "## 🔍 Competitive Landscape",
            "## ⚠️ Boundary Disclosure"
        ]

        for section in required_sections:
            if section not in markdown_content:
                print(f"Warning: Missing section '{section}' in opportunity card")
                return False

        return True
