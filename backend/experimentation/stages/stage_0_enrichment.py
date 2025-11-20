"""Stage 0: Brand Profile Enrichment

Transforms basic brand YAML into comprehensive context for downstream stages.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from backend.experimentation.schemas import Stage0Output, BrandEnrichment
from backend.experimentation.prompt_template_library import load_prompt_template


logger = logging.getLogger(__name__)


class Stage0Enrichment:
    """Brand profile enrichment stage.

    Supports two modes:
    - basic: Use only provided brand YAML
    - perplexity_enriched: Add external search data via Perplexity API
    """

    def __init__(self, enrichment_mode: str = "basic"):
        """Initialize Stage 0.

        Args:
            enrichment_mode: Either 'basic' or 'perplexity_enriched'
        """
        self.enrichment_mode = enrichment_mode
        self.prompt_template = load_prompt_template("stage_0_enrichment")

    async def run_basic(self, brand_profile: Dict[str, Any]) -> Stage0Output:
        """Basic enrichment without external search.

        Args:
            brand_profile: Brand profile data from YAML

        Returns:
            Stage0Output with brand context
        """
        logger.info(f"Running Stage 0 (basic) for brand: {brand_profile.get('brand_name', 'Unknown')}")

        # Extract required fields with defaults
        brand_enrichment = BrandEnrichment(
            brand_name=brand_profile.get("brand_name", brand_profile.get("company_name", "Unknown")),
            industry=brand_profile.get("industry", "Unknown"),
            country=brand_profile.get("country", "Unknown"),
            product_portfolio=brand_profile.get("portfolio", brand_profile.get("product_portfolio", [])),
            positioning=brand_profile.get("positioning"),
            confidence_score=1.0  # High confidence - using only provided data
        )

        return Stage0Output(
            brand_context=brand_enrichment,
            enrichment_method="basic"
        )

    async def run_perplexity_enriched(
        self,
        brand_profile: Dict[str, Any],
        perplexity_api_key: Optional[str] = None
    ) -> Stage0Output:
        """Enrichment with Perplexity API search.

        Args:
            brand_profile: Brand profile data from YAML
            perplexity_api_key: Optional API key (falls back to env var)

        Returns:
            Stage0Output with enriched brand context
        """
        logger.info(f"Running Stage 0 (perplexity_enriched) for brand: {brand_profile.get('brand_name', 'Unknown')}")

        # Get API key
        api_key = perplexity_api_key or os.getenv("PERPLEXITY_API_KEY")

        if not api_key:
            logger.warning("PERPLEXITY_API_KEY not found, falling back to basic enrichment")
            return await self.run_basic(brand_profile)

        try:
            import httpx

            brand_name = brand_profile.get("brand_name", brand_profile.get("company_name"))

            # Search for recent news and competitive context
            search_query = f"{brand_name} {brand_profile.get('industry', '')} recent developments 2024"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a market research analyst. Provide factual information with citations."
                            },
                            {
                                "role": "user",
                                "content": f"What are the recent developments (past 12 months) and competitive landscape for {brand_name} in the {brand_profile.get('industry')} industry? Keep response to 3-4 bullet points."
                            }
                        ]
                    },
                    timeout=30.0
                )

            if response.status_code == 200:
                result = response.json()
                enrichment_text = result["choices"][0]["message"]["content"]

                # Parse enrichment text into structured fields
                recent_news = [line.strip() for line in enrichment_text.split('\n') if line.strip().startswith('-')][:3]

                brand_enrichment = BrandEnrichment(
                    brand_name=brand_name,
                    industry=brand_profile.get("industry", "Unknown"),
                    country=brand_profile.get("country", "Unknown"),
                    product_portfolio=brand_profile.get("portfolio", brand_profile.get("product_portfolio", [])),
                    positioning=brand_profile.get("positioning"),
                    recent_news=recent_news if recent_news else None,
                    competitive_landscape=enrichment_text[:200] if enrichment_text else None,
                    confidence_score=0.85  # Lower confidence - using external search
                )

                logger.info(f"Successfully enriched brand profile with Perplexity search")

                return Stage0Output(
                    brand_context=brand_enrichment,
                    enrichment_method="perplexity_enriched"
                )
            else:
                logger.warning(f"Perplexity API returned {response.status_code}, falling back to basic")
                return await self.run_basic(brand_profile)

        except Exception as e:
            logger.error(f"Perplexity enrichment failed: {e}, falling back to basic")
            return await self.run_basic(brand_profile)

    async def run(self, brand_profile: Dict[str, Any]) -> Stage0Output:
        """Run enrichment based on configured mode.

        Args:
            brand_profile: Brand profile data from YAML

        Returns:
            Stage0Output with brand context
        """
        if self.enrichment_mode == "perplexity_enriched":
            return await self.run_perplexity_enriched(brand_profile)
        else:
            return await self.run_basic(brand_profile)
