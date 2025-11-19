# 9. Backend Architecture

## Python Serverless Functions (Vercel)

**Directory Structure**:

```
api/python/
├── stage1.py                     # Vercel entry point for Stage 1
├── stage2.py                     # Vercel entry point for Stage 2
├── stage3.py                     # Vercel entry point for Stage 3
├── stage4.py                     # Vercel entry point for Stage 4
├── stage5.py                     # Vercel entry point for Stage 5
├── pipeline/
│   ├── stages/
│   │   ├── stage1_input_processing.py
│   │   ├── stage2_signal_amplification.py
│   │   ├── stage3_general_translation.py
│   │   ├── stage4_brand_contextualization.py
│   │   └── stage5_opportunity_generation.py
│   ├── llm_client.py             # OpenRouter ChatOpenAI wrapper
│   ├── blob_client.py            # Vercel Blob SDK wrapper
│   ├── research_loader.py        # Load & parse brand research
│   ├── logger.py                 # Structured logging
│   └── utils.py                  # Retry logic, error handling
├── templates/
│   └── opportunity-card.md.j2    # Jinja2 template
├── requirements.txt
└── tests/
    ├── test_research_loader.py
    ├── test_stage4_brand_contextualization.py
    └── ...
```

## Stage 4: Brand Contextualization (Critical Stage)

**File**: `api/python/pipeline/stages/stage4_brand_contextualization.py`

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pipeline.llm_client import create_llm_client
from pipeline.blob_client import BlobClient
from pipeline.research_loader import ResearchDataLoader
from pipeline.logger import logger
import json

def execute_stage4(
    run_id: str,
    brand_id: str,
    stage3_output_path: str,
    prompt: str,
    llm_config: dict
) -> dict:
    """
    Stage 4: Brand Contextualization

    Injects comprehensive brand research (8 sections, 120+ data points)
    into the prompt to generate brand-specific opportunities.
    """
    logger.stage_start(run_id, stage=4, model=llm_config['model'])

    # Load Stage 3 output (general concepts)
    blob_client = BlobClient()
    stage3_content = blob_client.read(stage3_output_path)
    stage3_data = json.loads(stage3_content)

    # Load comprehensive brand research
    research_loader = ResearchDataLoader()
    research = research_loader.get_brand_research(brand_id)

    # Build research context for prompt injection
    research_context = f"""
# BRAND RESEARCH DATA FOR {research.brand_profile.display_name}

## 1. Brand Overview & Positioning
{research.sections['brand_overview'].content}

## 2. Product Portfolio & Innovation
{research.sections['product_portfolio'].content}

## 3. Recent Innovations (Last 18 Months) ⭐ CRITICAL
{research.sections['recent_innovations'].content}

## 4. Strategic Priorities & Business Strategy
{research.sections['strategic_priorities'].content}

## 5. Target Customers & Market Positioning
{research.sections['target_customers'].content}

## 6. Sustainability & Social Responsibility
{research.sections['sustainability'].content}

## 7. Competitive Context & Market Trends
{research.sections['competitive_context'].content}

## 8. Recent News & Market Signals (Last 6 Months)
{research.sections['recent_news'].content}

---

# KEY INSIGHTS SUMMARY

## Innovation DNA
{research.key_insights.innovation_dna}

## Strategic North Star
{research.key_insights.strategic_north_star}

## Opportunity Whitespace
{research.key_insights.opportunity_whitespace}

---

**Total Research Data Points**: {research.total_data_points}
**Research Date**: {research.research_date.strftime('%Y-%m-%d')}
"""

    # Inject research into prompt template
    prompt_template = PromptTemplate.from_template(prompt)
    formatted_prompt = prompt_template.format(
        brand_name=research.brand_profile.display_name,
        brand_research=research_context,
        general_concepts=json.dumps(stage3_data['general_concepts'], indent=2)
    )

    # Execute LLM
    llm = create_llm_client(llm_config)
    response = llm.invoke(formatted_prompt)

    # Parse response
    contextualized_opportunities = json.loads(response.content)

    # Save output to Blob
    output_path = f"runs/{run_id}/stage4_output.json"
    blob_client.write(
        output_path,
        json.dumps(contextualized_opportunities, indent=2)
    )

    # Log completion and cost
    logger.stage_complete(
        run_id,
        stage=4,
        duration_ms=(time.time() - start_time) * 1000,
        tokens_used=response.usage.total_tokens
    )

    cost_usd = calculate_cost(
        response.usage.prompt_tokens,
        response.usage.completion_tokens,
        llm_config['model']
    )
    logger.cost_incurred(run_id, stage=4, cost_usd=cost_usd, model=llm_config['model'])

    return {
        'output_path': output_path,
        'tokens_used': response.usage.total_tokens,
        'cost_usd': cost_usd,
    }
```

## Research Data Loader

**File**: `api/python/pipeline/research_loader.py`

```python
import re
from dataclasses import dataclass
from typing import Dict
from datetime import datetime
from pipeline.blob_client import BlobClient

@dataclass
class ResearchSection:
    title: str
    content: str
    data_points: int

@dataclass
class BrandResearch:
    brand_id: str
    brand_profile: any  # BrandProfile from DB
    sections: Dict[str, ResearchSection]
    key_insights: Dict[str, str]
    total_data_points: int
    research_date: datetime

class ResearchDataLoader:
    """Loads and parses comprehensive brand research files from Blob storage."""

    SECTION_MAP = {
        "1. Brand Overview & Positioning": "brand_overview",
        "2. Product Portfolio & Innovation": "product_portfolio",
        "3. Recent Innovations (Last 18 Months)": "recent_innovations",
        "4. Strategic Priorities & Business Strategy": "strategic_priorities",
        "5. Target Customers & Market Positioning": "target_customers",
        "6. Sustainability & Social Responsibility": "sustainability",
        "7. Competitive Context & Market Trends": "competitive_context",
        "8. Recent News & Market Signals (Last 6 Months)": "recent_news",
    }

    def __init__(self):
        self.blob_client = BlobClient()
        self._cache = {}  # Cache loaded research

    def get_brand_research(self, brand_id: str) -> BrandResearch:
        """Load brand research from Blob storage with caching."""
        if brand_id in self._cache:
            return self._cache[brand_id]

        # Load brand profile from DB
        brand_profile = get_brand_profile(brand_id)  # From DB

        # Load research file from Blob
        research_content = self.blob_client.read(brand_profile.research_file_path)

        # Parse markdown
        research = self._parse_research_file(research_content, brand_id)
        research.brand_profile = brand_profile

        # Cache
        self._cache[brand_id] = research

        return research

    def _parse_research_file(self, content: str, brand_id: str) -> BrandResearch:
        """Parse research markdown into structured data."""
        sections = {}
        key_insights = {}

        # Extract metadata
        research_date_match = re.search(r'\*\*Research Date:\*\* (\d{4}-\d{2}-\d{2})', content)
        research_date = datetime.strptime(research_date_match.group(1), '%Y-%m-%d') if research_date_match else datetime.now()

        # Extract sections
        for section_title, section_key in self.SECTION_MAP.items():
            pattern = rf'## {re.escape(section_title)}(.*?)(?=##|\Z)'
            match = re.search(pattern, content, re.DOTALL)

            if match:
                section_content = match.group(1).strip()
                data_points = self._count_data_points(section_content)

                sections[section_key] = ResearchSection(
                    title=section_title,
                    content=section_content,
                    data_points=data_points
                )

        # Extract key insights
        insights_pattern = r'## Key Insights Summary.*?### Innovation DNA\n(.*?)\n\n### Strategic North Star\n(.*?)\n\n### Opportunity Whitespace\n(.*?)\n'
        insights_match = re.search(insights_pattern, content, re.DOTALL)

        if insights_match:
            key_insights = {
                'innovation_dna': insights_match.group(1).strip(),
                'strategic_north_star': insights_match.group(2).strip(),
                'opportunity_whitespace': insights_match.group(3).strip(),
            }

        total_data_points = sum(s.data_points for s in sections.values())

        return BrandResearch(
            brand_id=brand_id,
            brand_profile=None,  # Will be set by caller
            sections=sections,
            key_insights=key_insights,
            total_data_points=total_data_points,
            research_date=research_date
        )

    def _count_data_points(self, content: str) -> int:
        """Estimate data points by counting bullet points and sub-items."""
        bullets = len(re.findall(r'^[\-\*]\s', content, re.MULTILINE))
        numbered = len(re.findall(r'^\d+\.\s', content, re.MULTILINE))
        return bullets + numbered
```

## LLM Client Wrapper

**File**: `api/python/pipeline/llm_client.py`

```python
from langchain_openai import ChatOpenAI
import os

def create_llm_client(llm_config: dict) -> ChatOpenAI:
    """
    Create LangChain ChatOpenAI client configured for OpenRouter.

    Args:
        llm_config: {
            'model': 'anthropic/claude-sonnet-4-20250514',
            'temperature': 0.5
        }
    """
    return ChatOpenAI(
        model=llm_config['model'],
        temperature=llm_config.get('temperature', 0.5),
        openai_api_key=os.getenv('OPENROUTER_API_KEY'),
        openai_api_base='https://openrouter.ai/api/v1',
        default_headers={
            'HTTP-Referer': os.getenv('APP_URL', 'https://pipeline.yourdomain.com'),
            'X-Title': 'Innovation Intelligence Pipeline'
        }
    )
```

---
