# Coding Standards

## Overview

This document defines coding standards for the Innovation Intelligence System. These standards ensure code consistency, maintainability, and readability for both human developers and AI agents.

## Python Style Guide

### Base Standards

Follow **PEP 8** - Python's official style guide:
- **Line Length:** 88 characters (Black formatter default)
- **Indentation:** 4 spaces (no tabs)
- **Encoding:** UTF-8
- **Imports:** Grouped and ordered (standard library, third-party, local)

### Naming Conventions

```python
# Modules: lowercase_with_underscores
# pipeline/stages/stage1_input_processing.py

# Classes: PascalCase
class BrandContextualizer:
    pass

# Functions/Methods: lowercase_with_underscores
def load_brand_profile(brand_id: str) -> dict:
    pass

# Constants: UPPERCASE_WITH_UNDERSCORES
MAX_OPPORTUNITIES = 5
DEFAULT_TEMPERATURE = 0.7

# Private: Leading underscore
def _internal_helper():
    pass
```

### Type Hints

**Required** for all function signatures:

```python
from typing import Optional, Dict, List
from pathlib import Path

def load_brand_research(
    brand_id: str,
    research_base_path: str = "docs/web-search-setup"
) -> str:
    """Load comprehensive brand research from markdown file."""
    pass

def get_prompt_template() -> str:
    """Return the Stage 4 prompt template."""
    pass
```

## LangChain Conventions

### Chain Construction

Use explicit chain construction with named inputs/outputs:

```python
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

# ✅ Good: Explicit configuration
def create_stage1_chain():
    llm = ChatOpenAI(
        model="anthropic/claude-sonnet-4.5-20250514",
        temperature=0.3,
        max_tokens=2000
    )

    prompt = get_prompt_template()

    return LLMChain(
        llm=llm,
        prompt=prompt,
        output_key="stage1_output"
    )

# ❌ Bad: Implicit configuration
chain = LLMChain(llm, prompt)
```

### Prompt Templates

Store prompts in dedicated files under `pipeline/prompts/`:

```python
# pipeline/prompts/stage1_prompt.py

from langchain.prompts import PromptTemplate

def get_prompt_template() -> PromptTemplate:
    """Stage 1: Input Processing prompt template."""

    template = """You are an innovation analyst extracting insights from inspiration sources.

INPUT DOCUMENT:
{input_text}

TASK:
1. Identify the core innovation or success story
2. Extract key mechanisms that drove success
3. Analyze what made this approach effective

OUTPUT FORMAT:
# Innovation Analysis
[Your analysis here]
"""

    return PromptTemplate(
        input_variables=["input_text"],
        template=template
    )
```

## Project Structure Standards

### Stage Implementation

Each stage follows this structure:

```python
# pipeline/stages/stageN_name.py

import logging
from pathlib import Path
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from ..prompts.stageN_prompt import get_prompt_template

def create_chain():
    """Create the Stage N chain."""
    llm = ChatOpenAI(
        model="anthropic/claude-sonnet-4.5-20250514",
        temperature=0.5,
        max_tokens=2500
    )

    prompt = get_prompt_template()

    return LLMChain(
        llm=llm,
        prompt=prompt,
        output_key="stageN_output"
    )

def save_output(output: str, run_dir: Path) -> None:
    """Save stage output to file."""
    output_dir = run_dir / "stageN"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "output.md"
    output_file.write_text(output, encoding='utf-8')

    logging.info(f"Stage N output saved: {output_file}")
```

### Error Handling

Use explicit error handling with informative messages:

```python
# ✅ Good: Specific error handling
def load_brand_profile(brand_id: str) -> dict:
    """Load brand profile from YAML file."""
    profile_path = Path(f"data/brand-profiles/{brand_id}.yaml")

    if not profile_path.exists():
        logging.error(f"Brand profile not found: {profile_path}")
        raise FileNotFoundError(
            f"Brand profile '{brand_id}' not found. "
            f"Expected: {profile_path}"
        )

    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        logging.error(f"Invalid YAML in {profile_path}: {e}")
        raise ValueError(f"Invalid brand profile YAML: {e}")

# ❌ Bad: Silent failures
def load_brand_profile(brand_id: str) -> dict:
    try:
        return yaml.safe_load(open(f"data/brand-profiles/{brand_id}.yaml"))
    except:
        return {}
```

### Logging Standards

Use structured logging throughout:

```python
import logging

# Configure at module level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Usage in functions
def run_pipeline(input_id: str, brand_id: str):
    """Run the complete pipeline."""
    logging.info(f"Starting pipeline: input={input_id}, brand={brand_id}")

    try:
        # Process stages
        logging.info("Stage 1: Input Processing")
        stage1_output = run_stage1(input_id)

        logging.info("Stage 2: Signal Amplification")
        stage2_output = run_stage2(stage1_output)

    except Exception as e:
        logging.error(f"Pipeline failed: {e}", exc_info=True)
        raise

    logging.info("Pipeline completed successfully")
```

## File Organization

### Module Structure

```python
# pipeline/__init__.py
"""Innovation Intelligence Pipeline package."""

from .chains import create_sequential_chain
from .utils import load_brand_profile, load_input_document

__all__ = [
    'create_sequential_chain',
    'load_brand_profile',
    'load_input_document'
]
```

### Import Order

```python
# 1. Standard library
import logging
from pathlib import Path
from typing import Dict, List, Optional

# 2. Third-party packages
import yaml
from langchain.chains import LLMChain, SequentialChain
from langchain_openai import ChatOpenAI

# 3. Local imports
from pipeline.utils import load_brand_profile
from pipeline.prompts.stage1_prompt import get_prompt_template
```

## Documentation Standards

### Docstrings

Use Google-style docstrings:

```python
def create_opportunity_card(
    opportunity: Dict,
    brand_profile: Dict,
    template_path: Path
) -> str:
    """Generate opportunity card from template.

    Args:
        opportunity: Opportunity data dictionary with keys: title, description, etc.
        brand_profile: Brand profile dictionary from YAML
        template_path: Path to Jinja2 template file

    Returns:
        Rendered opportunity card as markdown string

    Raises:
        FileNotFoundError: If template file doesn't exist
        jinja2.TemplateError: If template rendering fails

    Example:
        >>> opportunity = {"title": "Product Innovation"}
        >>> brand = load_brand_profile("lactalis-canada")
        >>> card = create_opportunity_card(opportunity, brand, Path("templates/card.j2"))
    """
    pass
```

### Inline Comments

```python
# ✅ Good: Explain WHY, not WHAT
# Research files are 35-48KB - ensure context window can accommodate
research_content = load_research_data(brand_id)

# Handle degraded mode if research data missing
if not research_content:
    logging.warning("Proceeding without research data")

# ❌ Bad: States the obvious
# Load the research data
research_content = load_research_data(brand_id)
```

## Testing Standards

### Test Structure

```python
# tests/test_stage1.py

import pytest
from pathlib import Path
from pipeline.stages.stage1_input_processing import create_chain

def test_stage1_chain_creation():
    """Test Stage 1 chain can be created."""
    chain = create_chain()
    assert chain is not None
    assert chain.output_key == "stage1_output"

def test_stage1_with_sample_input():
    """Test Stage 1 processes sample input correctly."""
    chain = create_chain()

    sample_input = "The Savannah Bananas reimagined baseball..."
    result = chain.invoke({"input_text": sample_input})

    assert "stage1_output" in result
    assert len(result["stage1_output"]) > 100

@pytest.fixture
def sample_brand_profile():
    """Load sample brand profile for testing."""
    return {
        "brand_id": "test-brand",
        "company_name": "Test Company",
        "industry": "Food & Beverage"
    }
```

## Configuration Management

### Environment Variables

```python
# ✅ Good: Use python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set in environment")

# ❌ Bad: Hardcoded values
OPENROUTER_API_KEY = "sk-or-v1-..."  # Never commit API keys
```

## AI Agent Considerations

### Self-Documenting Code

Write code that AI agents can easily understand:

```python
# ✅ Good: Clear structure and naming
def load_brand_research_data(
    brand_id: str,
    research_directory: Path = Path("docs/web-search-setup")
) -> str:
    """Load pre-generated brand research from markdown file.

    Each brand has comprehensive research (~550-720 lines) with 8 sections:
    1. Brand Overview & Positioning
    2. Product Portfolio & Innovation
    3. Recent Innovations (Last 18 Months)
    4. Strategic Priorities & Business Strategy
    5. Target Customers & Market Positioning
    6. Sustainability & Social Responsibility
    7. Competitive Context & Market Trends
    8. Recent News & Market Signals (Last 6 Months)
    """
    research_file = research_directory / f"{brand_id}-research.md"

    if not research_file.exists():
        logging.warning(f"Research file not found: {research_file}")
        return ""

    return research_file.read_text(encoding='utf-8')
```

### Code References

Include file paths and line numbers in logs:

```python
# ✅ Good: Traceable references
logging.info(f"Loaded brand profile: data/brand-profiles/{brand_id}.yaml")
logging.info(f"Using prompt template: pipeline/prompts/stage4_prompt.py:42")

# ❌ Bad: Vague references
logging.info(f"Loaded profile for {brand_id}")
```

## Code Review Checklist

Before committing code, verify:

- [ ] Type hints on all function signatures
- [ ] Docstrings for all public functions/classes
- [ ] Error handling with informative messages
- [ ] Logging at appropriate levels
- [ ] Tests cover core functionality
- [ ] No hardcoded paths or API keys
- [ ] Imports properly organized
- [ ] Line length ≤ 88 characters
- [ ] PEP 8 compliant (run `flake8` or `black`)

## References

- **PEP 8:** https://peps.python.org/pep-0008/
- **Type Hints:** https://docs.python.org/3/library/typing.html
- **LangChain Docs:** https://python.langchain.com/docs/
- **Google Python Style Guide:** https://google.github.io/styleguide/pyguide.html

---
