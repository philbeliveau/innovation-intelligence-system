"""Stage 5: Competitive Intelligence Search

Searches for similar concepts with strict honesty constraints using Perplexity API.

HONESTY CONSTRAINTS (CRITICAL):
- ❌ Do NOT invent competitors or products
- ✅ Separate "What we know" vs "What we infer"
- ✅ Cite search queries and sources with URLs
- ✅ If no results found, explicitly state "No similar concepts found"
- ✅ Include search evidence (URLs, snippets)

Process:
1. For each concept, generate 3 search queries:
   - Direct: Exact concept search
   - Analogous: Similar solutions in different industries
   - Competitive: Brand's competitors with similar initiatives
2. Execute searches via Perplexity API
3. Classify findings:
   - Direct Match: Exact same concept exists
   - Analogous: Similar concept in different domain
   - Novel: No matches found
4. Structure output with explicit "What we know" vs "What we infer" sections

Performance Target: < 60 seconds (3-5 concepts × 3 queries each)
"""
import json
import os
import httpx
from typing import Dict, Any, List, Optional
from ..schemas import Stage4Output, DirectionalConcept
from ..prompt_template_library import load_prompt_template
from ..few_shot_integration import inject_examples_into_stage_prompt


class CompetitiveFinding(Dict[str, Any]):
    """Competitive intelligence finding with honesty constraints."""
    pass


class Stage5CompetitiveIntelligence:
    """Stage 5: Search for similar concepts with honesty constraints."""

    PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

    async def execute(
        self,
        stage4_output: Stage4Output,
        brand_context: Dict[str, Any],
        openrouter_client: Any,
        run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute Stage 5: Competitive Intelligence Search.

        Args:
            stage4_output: Directional concepts from Stage 4
            brand_context: Enriched brand profile from Stage 0
            openrouter_client: OpenRouter API client (for query generation)
            run_id: Optional pipeline run ID (for usage tracking)

        Returns:
            Dict with competitive_intel array containing search findings
        """
        perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        if not perplexity_api_key:
            # Graceful degradation: Skip Stage 5 if Perplexity not configured
            return {
                "competitive_intel": [
                    {
                        "concept_id": concept.concept_id,
                        "search_queries": [],
                        "findings": [],
                        "novelty_assessment": "Competitive search skipped (PERPLEXITY_API_KEY not configured)"
                    }
                    for concept in stage4_output.concepts
                ],
                "search_enabled": False,
                "total_queries_executed": 0
            }

        competitive_intel = []
        total_queries = 0

        for concept in stage4_output.concepts:
            # Step 1: Generate 3 search queries using LLM
            queries = await self._generate_search_queries(
                concept=concept,
                brand_context=brand_context,
                openrouter_client=openrouter_client,
                run_id=run_id
            )

            # Step 2: Execute searches via Perplexity API
            findings = []
            for query in queries:
                finding = await self._execute_perplexity_search(
                    query=query,
                    perplexity_api_key=perplexity_api_key
                )
                if finding:
                    findings.append(finding)
                total_queries += 1

            # Step 3: Assess novelty based on findings
            novelty_assessment = self._assess_novelty(findings)

            competitive_intel.append({
                "concept_id": concept.concept_id,
                "search_queries": queries,
                "findings": findings,
                "novelty_assessment": novelty_assessment
            })

        return {
            "competitive_intel": competitive_intel,
            "search_enabled": True,
            "total_queries_executed": total_queries
        }

    async def _generate_search_queries(
        self,
        concept: DirectionalConcept,
        brand_context: Dict[str, Any],
        openrouter_client: Any,
        run_id: Optional[str] = None
    ) -> List[str]:
        """Generate 3 search queries: Direct, Analogous, Competitive.

        Args:
            concept: Directional concept to search for
            brand_context: Brand profile for competitive query
            openrouter_client: OpenRouter API client
            run_id: Optional pipeline run ID (for usage tracking)

        Returns:
            List of 3 search queries
        """
        prompt_template = load_prompt_template("stage_5_competitive_search")

        # Inject few-shot examples
        enhanced_template = inject_examples_into_stage_prompt(
            prompt_template=prompt_template,
            stage=5,
            brand_context=brand_context,
            run_id=run_id
        )

        prompt = enhanced_template.format(
            concept_name=concept.concept_name,
            concept_statement=concept.concept_statement,
            mechanism=concept.mechanism,
            brand_name=brand_context.get("brand_name", ""),
            industry=brand_context.get("industry", "")
        )

        response = await openrouter_client.call_llm(
            prompt=prompt,
            model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-5-sonnet-20240620"),
            max_tokens=1000,
            temperature=0.3  # Lower temp for more focused query generation
        )

        # Parse queries from LLM response
        queries = self._parse_queries_from_response(response["content"])

        # Ensure we have exactly 3 queries
        if len(queries) < 3:
            # Fallback: Generate basic queries if LLM fails
            queries = [
                f"{concept.concept_name} product innovation",
                f"{concept.mechanism.split()[0]} similar solutions",
                f"{brand_context.get('industry', '')} innovation trends"
            ][:3]

        return queries[:3]  # Limit to 3 queries

    def _parse_queries_from_response(self, llm_content: str) -> List[str]:
        """Parse search queries from LLM response.

        Expected format:
        1. Direct: "..."
        2. Analogous: "..."
        3. Competitive: "..."

        OR JSON format:
        {"queries": ["...", "...", "..."]}
        """
        queries = []

        # Try JSON parsing first
        try:
            if "```json" in llm_content:
                json_start = llm_content.find("```json") + 7
                json_end = llm_content.find("```", json_start)
                json_str = llm_content[json_start:json_end].strip()
                parsed = json.loads(json_str)
                queries = parsed.get("queries", [])
                if queries:
                    return queries
        except (json.JSONDecodeError, KeyError):
            pass

        # Fallback: Parse numbered list format
        lines = llm_content.split("\n")
        for line in lines:
            line = line.strip()
            # Match patterns like: "1. Direct: query" or "1. query" or "- query"
            if any(line.startswith(prefix) for prefix in ["1.", "2.", "3.", "-", "*"]):
                # Extract query after colon if present
                if ":" in line:
                    query = line.split(":", 1)[1].strip().strip('"')
                else:
                    # Remove prefix
                    query = line.lstrip("123.-*").strip().strip('"')

                if query and len(query) > 5:  # Minimum query length
                    queries.append(query)

        return queries

    async def _execute_perplexity_search(
        self,
        query: str,
        perplexity_api_key: str
    ) -> Optional[CompetitiveFinding]:
        """Execute search query via Perplexity API.

        Args:
            query: Search query string
            perplexity_api_key: Perplexity API key

        Returns:
            CompetitiveFinding with search results or None if no results
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.PERPLEXITY_API_URL,
                    headers={
                        "Authorization": f"Bearer {perplexity_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a competitive intelligence researcher. "
                                    "Search for real products, services, or initiatives that match "
                                    "the user's query. Provide ONLY factual information with sources. "
                                    "If no matches found, explicitly state 'No similar concepts found.'"
                                )
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ],
                        "max_tokens": 500,
                        "temperature": 0.2,
                        "return_citations": True,
                        "return_images": False
                    }
                )

                if response.status_code != 200:
                    print(f"Perplexity API error: {response.status_code} - {response.text}")
                    return None

                result = response.json()
                content = result["choices"][0]["message"]["content"]
                citations = result.get("citations", [])

                # Classify match type based on content
                match_type = self._classify_match_type(content, query)

                # Separate "What we know" vs "What we infer"
                what_we_know, what_we_infer = self._separate_knowledge_inference(
                    content=content,
                    citations=citations
                )

                return CompetitiveFinding({
                    "match_type": match_type,
                    "query": query,
                    "description": content,
                    "source_urls": citations,
                    "what_we_know": what_we_know,
                    "what_we_infer": what_we_infer
                })

        except Exception as e:
            print(f"Perplexity search failed for query '{query}': {str(e)}")
            return None

    def _classify_match_type(self, content: str, query: str) -> str:
        """Classify search result as Direct, Analogous, or Novel.

        Args:
            content: Search result content
            query: Original search query

        Returns:
            "Direct Match", "Analogous", or "Novel"
        """
        content_lower = content.lower()

        # Novel: Explicit "no match" signals
        if any(phrase in content_lower for phrase in [
            "no similar",
            "not found",
            "no matches",
            "no results",
            "no existing",
            "does not exist"
        ]):
            return "Novel"

        # Direct Match: Strong similarity signals
        if any(phrase in content_lower for phrase in [
            "similar product",
            "existing solution",
            "already exists",
            "same concept",
            "identical"
        ]):
            return "Direct Match"

        # Analogous: Default if results found but not direct match
        return "Analogous"

    def _separate_knowledge_inference(
        self,
        content: str,
        citations: List[str]
    ) -> tuple[str, str]:
        """Separate factual knowledge (with sources) from inferences.

        Args:
            content: Search result content
            citations: List of source URLs

        Returns:
            Tuple of (what_we_know, what_we_infer)
        """
        # WHAT WE KNOW: Factual statements with citations
        what_we_know_parts = []
        if citations:
            what_we_know_parts.append(f"Sources: {', '.join(citations)}")

        # Extract factual statements (heuristic: sentences with proper nouns, dates, or specific details)
        sentences = content.split(". ")
        for sentence in sentences:
            # Heuristic: Factual sentences often contain years, proper nouns (capital letters), or brand names
            if any(word[0].isupper() for word in sentence.split() if len(word) > 1) or \
               any(char.isdigit() for char in sentence):
                what_we_know_parts.append(sentence.strip())

        what_we_know = ". ".join(what_we_know_parts) if what_we_know_parts else "No specific factual information found."

        # WHAT WE INFER: Interpretive or comparative statements
        what_we_infer_signals = [
            "could", "might", "may", "similar to", "like", "appears to",
            "suggests", "indicates", "implies", "potentially"
        ]
        what_we_infer_parts = []
        for sentence in sentences:
            if any(signal in sentence.lower() for signal in what_we_infer_signals):
                what_we_infer_parts.append(sentence.strip())

        what_we_infer = ". ".join(what_we_infer_parts) if what_we_infer_parts else "No inferences drawn beyond documented facts."

        return what_we_know, what_we_infer

    def _assess_novelty(self, findings: List[CompetitiveFinding]) -> str:
        """Assess overall novelty based on all search findings.

        Args:
            findings: List of competitive findings

        Returns:
            Novelty assessment string
        """
        if not findings:
            return "No search results available for novelty assessment"

        # Count match types
        direct_matches = sum(1 for f in findings if f.get("match_type") == "Direct Match")
        analogous_matches = sum(1 for f in findings if f.get("match_type") == "Analogous")
        novel_matches = sum(1 for f in findings if f.get("match_type") == "Novel")

        if direct_matches > 0:
            return f"Direct matches found ({direct_matches}/{len(findings)} queries). Concept has existing implementations."
        elif analogous_matches > 0:
            return f"Analogous solutions exist in other domains ({analogous_matches}/{len(findings)} queries). Concept has transferable precedents."
        else:
            return f"Novel concept ({novel_matches}/{len(findings)} queries found no direct or analogous matches)."
