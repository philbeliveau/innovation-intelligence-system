"""Stage 3: Innovation Technique Matching

Matches consumer insights to SIT/TRIZ/Doblin innovation techniques.

Process:
1. Load technique libraries (SIT, TRIZ, Doblin)
2. Match each insight to 1-2 SIT techniques (primary framework)
3. Assess defensibility (can competitors easily copy?)
4. If SIT insufficient, conditionally apply TRIZ
5. Map to Doblin type for strategic classification
6. Generate transferability mapping (L1 → L4)

Performance Target: < 90 seconds
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..schemas import (
    Stage2Output,
    Stage3Output,
    MatchedTechnique,
    InnovationTechnique,
    TechniqueTransferability
)
from ..prompt_template_library import load_prompt_template
from ..few_shot_integration import inject_examples_into_stage_prompt


class Stage3TechniqueMatching:
    """Stage 3: Match consumer insights to innovation techniques."""

    def __init__(self):
        self.technique_libraries = self._load_technique_libraries()

    def _load_technique_libraries(self) -> Dict[str, Any]:
        """Load SIT, TRIZ, and Doblin technique libraries."""
        base_path = Path(__file__).parent.parent / "technique_libraries"

        libraries = {}
        for filename in ["sit_techniques.json", "triz_principles.json", "doblin_types.json"]:
            file_path = base_path / filename
            with open(file_path, 'r') as f:
                framework_name = filename.replace("_", " ").replace(".json", "").upper()
                libraries[framework_name] = json.load(f)

        return libraries

    async def execute(
        self,
        stage2_output: Stage2Output,
        brand_context: Dict[str, Any],
        openrouter_client: Any,
        run_id: Optional[str] = None,
        custom_prompt_content: Optional[str] = None
    ) -> Stage3Output:
        """Execute Stage 3: Technique Matching.

        Args:
            stage2_output: Consumer insights from Stage 2
            brand_context: Enriched brand profile from Stage 0
            openrouter_client: OpenRouter API client
            run_id: Optional pipeline run ID (for usage tracking)
            custom_prompt_content: Optional custom prompt template (Story 11.6.2)

        Returns:
            Stage3Output with matched techniques
        """
        # Use custom prompt if provided, otherwise load default template
        if custom_prompt_content:
            # Custom prompt provided - use directly without few-shot injection
            enhanced_template = custom_prompt_content
        else:
            # Load default prompt template
            prompt_template = load_prompt_template("stage_3_technique_matching")

            # Inject few-shot examples (only for default templates)
            enhanced_template = inject_examples_into_stage_prompt(
                prompt_template=prompt_template,
                stage=3,
                brand_context=brand_context,
                run_id=run_id
            )

        # Prepare technique library summaries for LLM
        sit_summary = self._format_sit_library()
        triz_summary = self._format_triz_library()
        doblin_summary = self._format_doblin_library()

        # Build prompt
        prompt = enhanced_template.format(
            insights=json.dumps([insight.model_dump() for insight in stage2_output.insights], indent=2),
            brand_context=json.dumps(brand_context, indent=2),
            sit_techniques=sit_summary,
            triz_principles=triz_summary,
            doblin_types=doblin_summary
        )

        # Call LLM
        response = await openrouter_client.call_llm(
            prompt=prompt,
            model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-5-sonnet-20240620"),
            max_tokens=6000,
            temperature=0.7
        )

        # Parse response
        matched_techniques = self._parse_llm_response(response["content"], stage2_output.insights)

        # Calculate statistics
        sit_count = sum(1 for m in matched_techniques if m.primary_technique.framework == "SIT")
        triz_count = sum(
            1 for m in matched_techniques
            if m.secondary_technique and m.secondary_technique.framework == "TRIZ"
        )

        return Stage3Output(
            matched_techniques=matched_techniques,
            sit_matches=sit_count,
            triz_matches=triz_count
        )

    def _format_sit_library(self) -> str:
        """Format SIT techniques for LLM prompt."""
        sit = self.technique_libraries["SIT TECHNIQUES"]
        techniques = sit["techniques"]

        formatted = "## SIT (Systematic Inventive Thinking) - 5 Core Techniques\n\n"
        for t in techniques:
            formatted += f"### {t['name']}\n"
            formatted += f"**Description:** {t['description']}\n"
            formatted += f"**Prompt Hint:** {t['prompt_hint']}\n"
            formatted += f"**When to Use:** {t['when_to_use']}\n"
            formatted += f"**Examples:** {', '.join(t['examples'][:2])}\n\n"

        return formatted

    def _format_triz_library(self) -> str:
        """Format TRIZ principles for LLM prompt (abbreviated)."""
        triz = self.technique_libraries["TRIZ PRINCIPLES"]
        principles = triz["principles"][:10]  # Only show first 10 for token efficiency

        formatted = "## TRIZ - Selected Principles (Apply ONLY if SIT insufficient)\n\n"
        formatted += f"**Usage Note:** {triz['usage_note']}\n\n"
        for p in principles:
            formatted += f"- **{p['name']}**: {p['description']}\n"
        formatted += "\n(... 30 more principles available if needed)\n\n"

        return formatted

    def _format_doblin_library(self) -> str:
        """Format Doblin types for LLM prompt."""
        doblin = self.technique_libraries["DOBLIN TYPES"]
        types = doblin["types"]

        formatted = "## Doblin Ten Types of Innovation\n\n"
        formatted += f"**Usage Note:** {doblin['usage_note']}\n\n"

        for category in ["Configuration", "Offering", "Experience"]:
            category_types = [t for t in types if t["category"] == category]
            formatted += f"### {category}\n"
            for t in category_types:
                formatted += f"- **{t['name']}**: {t['description']}\n"
            formatted += "\n"

        return formatted

    def _parse_llm_response(
        self,
        llm_content: str,
        insights: List[Any]
    ) -> List[MatchedTechnique]:
        """Parse LLM response into MatchedTechnique objects.

        Expected JSON structure:
        {
          "matched_techniques": [
            {
              "insight_id": "...",
              "primary_technique": {...},
              "secondary_technique": {...},
              "doblin_type": "...",
              "transferability": {...}
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
            matched_list = parsed.get("matched_techniques", [])

            results = []
            for match_data in matched_list:
                # Build primary technique
                primary_tech = InnovationTechnique(
                    framework=match_data["primary_technique"]["framework"],
                    technique=match_data["primary_technique"]["technique"],
                    rationale=match_data["primary_technique"]["rationale"],
                    defensibility_score=match_data["primary_technique"].get("defensibility_score")
                )

                # Build secondary technique (optional)
                secondary_tech = None
                if match_data.get("secondary_technique"):
                    secondary_tech = InnovationTechnique(
                        framework=match_data["secondary_technique"]["framework"],
                        technique=match_data["secondary_technique"]["technique"],
                        rationale=match_data["secondary_technique"]["rationale"],
                        defensibility_score=match_data["secondary_technique"].get("defensibility_score")
                    )

                # Build transferability
                transferability = TechniqueTransferability(
                    L1_domain=match_data["transferability"]["L1_domain"],
                    L4_universal=match_data["transferability"]["L4_universal"]
                )

                matched = MatchedTechnique(
                    insight_id=match_data["insight_id"],
                    primary_technique=primary_tech,
                    secondary_technique=secondary_tech,
                    doblin_type=match_data["doblin_type"],
                    transferability=transferability
                )
                results.append(matched)

            return results

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise ValueError(f"Failed to parse Stage 3 LLM response: {str(e)}\n\nResponse: {llm_content[:500]}")
