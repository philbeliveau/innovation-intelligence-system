"""Stage 4: Directional Concept Generation

Generates 3-5 directional concepts with strict no-hallucination boundaries.

NO-HALLUCINATION CONSTRAINTS (CRITICAL):
- ❌ No financial projections (TAM, revenue, market share, ROI)
- ❌ No unverified competitive claims ("NO brand does this")
- ❌ No invented market statistics
- ❌ No detailed business plans or go-to-market strategies
- ✅ ONLY synthesize from provided inputs (trend + insight + technique)
- ✅ Focus on DIRECTION not implementation details

Process:
1. Apply SIT technique to consumer insight
2. Generate 3-5 directional concepts (not detailed specs)
3. For each concept:
   - What is it? (1 sentence)
   - How does it work? (mechanism only)
   - Why does it address the insight?
4. Include explicit boundary disclosure

Performance Target: < 90 seconds
"""
import json
import os
import uuid
from typing import Dict, Any, List, Optional
from ..schemas import (
    Stage2Output,
    Stage3Output,
    Stage4Output,
    DirectionalConcept
)
from ..prompt_template_library import load_prompt_template
from ..few_shot_integration import inject_examples_into_stage_prompt


class Stage4ConceptGeneration:
    """Stage 4: Generate directional concepts with no-hallucination boundaries."""

    BOUNDARY_DISCLOSURE_TEMPLATE = (
        "This is a directional concept generated from trend analysis and systematic "
        "innovation techniques. It does NOT include: financial projections or ROI estimates, "
        "detailed implementation plans, market validation or customer research, or "
        "competitive claims beyond documented search results."
    )

    async def execute(
        self,
        stage2_output: Stage2Output,
        stage3_output: Stage3Output,
        brand_context: Dict[str, Any],
        openrouter_client: Any,
        run_id: Optional[str] = None,
        custom_prompt_content: Optional[str] = None
    ) -> Stage4Output:
        """Execute Stage 4: Directional Concept Generation.

        Args:
            stage2_output: Consumer insights from Stage 2
            stage3_output: Matched techniques from Stage 3
            brand_context: Enriched brand profile from Stage 0
            openrouter_client: OpenRouter API client
            run_id: Optional pipeline run ID (for usage tracking)
            custom_prompt_content: Optional custom prompt template (Story 11.6.2)

        Returns:
            Stage4Output with 3-5 directional concepts
        """
        # Use custom prompt if provided, otherwise load default template
        if custom_prompt_content:
            # Custom prompt provided - use directly without few-shot injection
            prompt_template = custom_prompt_content
        else:
            # Load default prompt template
            prompt_template = load_prompt_template("stage_4_concept_generation")

            # Inject few-shot examples (only for default templates)
            prompt_template = inject_examples_into_stage_prompt(
                prompt_template=prompt_template,
                stage=4,
                brand_context=brand_context,
                run_id=run_id
            )

        # Build prompt with no-hallucination constraints embedded
        prompt = prompt_template.format(
            insights=json.dumps([insight.model_dump() for insight in stage2_output.insights], indent=2),
            matched_techniques=json.dumps(
                [match.model_dump() for match in stage3_output.matched_techniques],
                indent=2
            ),
            brand_context=json.dumps(brand_context, indent=2),
            no_hallucination_rules=self._get_no_hallucination_rules()
        )

        # Call LLM with explicit boundary constraints
        response = await openrouter_client.call_llm(
            prompt=prompt,
            model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-5-sonnet-20240620"),
            max_tokens=8000,
            temperature=0.7
        )

        # Parse response and validate boundary compliance
        concepts = self._parse_llm_response(response["content"])

        # Enforce concept count (3-5)
        if len(concepts) < 3:
            raise ValueError(f"Stage 4 generated only {len(concepts)} concepts. Expected 3-5.")
        if len(concepts) > 5:
            concepts = concepts[:5]  # Trim to 5

        # Validate boundary enforcement
        self._validate_no_hallucination_compliance(concepts)

        return Stage4Output(
            concepts=concepts,
            total_concepts=len(concepts),
            boundary_enforcement_applied=True
        )

    def _get_no_hallucination_rules(self) -> str:
        """Return explicit no-hallucination rules for LLM prompt."""
        return """
## CRITICAL: No-Hallucination Boundaries

You MUST NOT:
- Generate financial projections (TAM, market share, revenue, cost estimates, ROI)
- Invent competitive intelligence ("Brand X does this", "NO company has done this")
- Create market statistics ("Studies show...", "Research indicates...", "X% of consumers...")
- Make unverified claims about feasibility, adoption, or success
- Generate detailed implementation plans or technical specifications

You MUST:
- Synthesize ONLY from provided inputs (trends, insights, techniques, brand context)
- Focus on DIRECTION, not detailed specifications
- Generate creative application of SIT/TRIZ technique to consumer problem
- Keep concepts at "30-second pitch" level
- Include explicit boundary disclosure in EVERY concept

Each concept must include:
1. concept_name: Clear, memorable name
2. concept_statement: 1-sentence what-is-it
3. mechanism: How it works (mechanism only, not implementation)
4. why_it_works: Why it addresses the insight (using provided data)
5. boundary_disclosure: Standard disclosure statement
"""

    def _parse_llm_response(self, llm_content: str) -> List[DirectionalConcept]:
        """Parse LLM response into DirectionalConcept objects.

        Expected JSON structure:
        {
          "concepts": [
            {
              "insight_id": "...",
              "technique_id": "...",
              "concept_name": "...",
              "concept_statement": "...",
              "mechanism": "...",
              "why_it_works": "..."
            }
          ]
        }
        """
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in llm_content:
                json_start = llm_content.find("```json") + 7
                json_end = llm_content.find("```", json_start)
                json_str = llm_content[json_start:json_end].strip()
            elif "```" in llm_content:
                json_start = llm_content.find("```") + 3
                json_end = llm_content.find("```", json_start)
                json_str = llm_content[json_start:json_end].strip()
            else:
                json_str = llm_content.strip()

            parsed = json.loads(json_str)
            concept_list = parsed.get("concepts", [])

            results = []
            for concept_data in concept_list:
                concept = DirectionalConcept(
                    concept_id=str(uuid.uuid4()),
                    insight_id=concept_data["insight_id"],
                    technique_id=concept_data.get("technique_id", "unknown"),
                    concept_name=concept_data["concept_name"],
                    concept_statement=concept_data["concept_statement"],
                    mechanism=concept_data["mechanism"],
                    why_it_works=concept_data["why_it_works"],
                    boundary_disclosure=concept_data.get(
                        "boundary_disclosure",
                        self.BOUNDARY_DISCLOSURE_TEMPLATE
                    )
                )
                results.append(concept)

            return results

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise ValueError(
                f"Failed to parse Stage 4 LLM response: {str(e)}\n\n"
                f"Response: {llm_content[:500]}"
            )

    def _validate_no_hallucination_compliance(self, concepts: List[DirectionalConcept]):
        """Validate that concepts do not contain hallucinated content.

        Checks for:
        - Financial terms (TAM, revenue, market share, ROI, cost)
        - Unverified competitive claims
        - Market statistics without sources
        """
        forbidden_patterns = [
            # Financial hallucinations
            r"\$\d+[MBK]",  # Dollar amounts with M/B/K
            r"\d+%.*market share",
            r"TAM|total addressable market",
            r"ROI|return on investment",
            r"revenue.*\$",
            r"cost.*\$",
            # Competitive hallucinations
            r"no (?:brand|company|competitor) (?:has|does)",
            r"first to market",
            r"only (?:brand|company) that",
            # Statistical hallucinations
            r"studies show",
            r"research indicates",
            r"\d+% of consumers",
            r"according to (?!provided|trend report)",
        ]

        import re
        for concept in concepts:
            full_text = (
                f"{concept.concept_name} {concept.concept_statement} "
                f"{concept.mechanism} {concept.why_it_works}"
            ).lower()

            for pattern in forbidden_patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    raise ValueError(
                        f"Stage 4 boundary violation detected in concept '{concept.concept_name}': "
                        f"Pattern '{pattern}' found. This suggests hallucinated content."
                    )

        # Validate boundary disclosure is present
        for concept in concepts:
            if not concept.boundary_disclosure or len(concept.boundary_disclosure) < 50:
                raise ValueError(
                    f"Concept '{concept.concept_name}' missing proper boundary disclosure"
                )
