# Brand Research Data Structure

## Overview

Pre-existing brand research data is stored in comprehensive markdown files that provide strategic context for Stage 4 (Brand Contextualization). Each brand has a single research file containing 8 strategic sections with ~550-720 lines and 35-48 KB of content.

## File Location and Naming Convention

### Directory Structure
```
docs/web-search-setup/
├── lactalis-canada-research.md      (546 lines, 35.8 KB)
├── mccormick-usa-research.md        (721 lines, 47.0 KB)
├── columbia-sportswear-research.md  (575 lines, 42.1 KB)
└── decathlon-research.md            (604 lines, 43.8 KB)
```

### File Naming Pattern
**Format:** `{brand-id}-research.md`

Where `{brand-id}` matches the brand identifier used in:
- Brand profile YAML files (`data/brand-profiles/{brand-id}.yaml`)
- Pipeline execution parameters
- Output directory naming

**Examples:**
- `lactalis-canada-research.md` → Brand ID: `lactalis-canada`
- `mccormick-usa-research.md` → Brand ID: `mccormick-usa`
- `columbia-sportswear-research.md` → Brand ID: `columbia-sportswear`
- `decathlon-research.md` → Brand ID: `decathlon`

## 8-Section Research Structure

Each research file contains comprehensive brand intelligence organized into 8 strategic sections:

### 1. Brand Overview & Positioning
- Company background and history
- Brand identity and core values
- Market positioning and competitive stance
- Geographic presence and scale

### 2. Product Portfolio & Innovation
- Current product lines and categories
- Innovation track record and approach
- R&D capabilities and investments
- Product development philosophy

### 3. Recent Innovations (Last 18 Months)
- New product launches
- Feature enhancements and reformulations
- Packaging innovations
- Technology integrations

### 4. Strategic Priorities & Business Strategy
- Corporate strategic goals
- Growth initiatives and expansion plans
- Digital transformation efforts
- Partnership and acquisition strategy

### 5. Target Customers & Market Positioning
- Primary customer segments
- Demographics and psychographics
- Customer needs and pain points
- Brand-customer relationship dynamics

### 6. Sustainability & Social Responsibility
- Environmental commitments and initiatives
- Social impact programs
- ESG (Environmental, Social, Governance) priorities
- Sustainability innovation and practices

### 7. Competitive Context & Market Trends
- Key competitors and competitive dynamics
- Market trends affecting the category
- Industry challenges and opportunities
- Emerging disruptions and innovations

### 8. Recent News & Market Signals (Last 6 Months)
- Recent announcements and press releases
- Market performance and business results
- Strategic moves and organizational changes
- Consumer sentiment and brand perception

## Stage 4 Integration Pattern

### Loading Research Data

Use the `load_research_data()` function from `pipeline/utils.py`:

```python
from pathlib import Path
from pipeline.utils import load_research_data

# Load research data for a specific brand
brand_id = "lactalis-canada"
research_content = load_research_data(brand_id)

# Research content is returned as complete markdown string
# Ready for injection into Stage 4 prompt
```

### Function Signature

```python
def load_research_data(
    brand_id: str,
    research_directory: Path = Path("docs/web-search-setup")
) -> str:
    """Load pre-generated brand research from markdown file.

    Returns:
        Complete research content as string for Stage 4 prompt injection.
        Returns empty string if file missing or unreadable (non-fatal error).
    """
```

### Integration in Stage 4 Prompt

The research data is injected into the Stage 4 prompt template to provide brand-specific context:

```python
from pipeline.utils import load_research_data
from pipeline.prompts.stage4_prompt import get_prompt_template

# Load brand research
brand_id = "lactalis-canada"
research_data = load_research_data(brand_id)

# Get Stage 4 prompt template
prompt_template = get_prompt_template()

# Inject research data into prompt
stage4_input = {
    "stage3_output": stage3_output,  # Universal lessons from Stage 3
    "brand_research": research_data,  # Complete brand research
    "brand_profile": brand_profile    # Brand YAML data
}

# Execute Stage 4 chain
stage4_output = stage4_chain.invoke(stage4_input)
```

## Error Handling

### Non-Fatal Errors

The `load_research_data()` function handles missing or unreadable files gracefully:

```python
research_content = load_research_data("missing-brand")
# Returns: ""  (empty string)
# Logs: WARNING - Research file not found, proceeding without research data
```

**Behavior:**
- Missing files → Returns empty string, logs warning, continues pipeline
- Read errors → Returns empty string, logs warning, continues pipeline
- **Pipeline does NOT fail** if research data is unavailable

### Logging Output

Successful load:
```
INFO - Loaded research data: docs/web-search-setup/lactalis-canada-research.md (546 lines, 35.9 KB)
```

Missing file:
```
WARNING - Research file not found: docs/web-search-setup/missing-brand-research.md. Proceeding without research data.
```

Read error:
```
WARNING - Failed to read research file docs/web-search-setup/corrupted-research.md: [error details]. Proceeding without research data.
```

## Usage Examples

### Basic Usage

```python
from pipeline.utils import load_research_data

# Load research for a single brand
research = load_research_data("mccormick-usa")
print(f"Loaded {len(research)} characters of research")
# Output: Loaded 48085 characters of research
```

### Pipeline Integration

```python
from pipeline.utils import load_research_data, load_brand_profile

def run_stage4(brand_id: str, stage3_output: str):
    """Execute Stage 4 with brand research integration."""

    # Load brand data
    brand_profile = load_brand_profile(brand_id)
    brand_research = load_research_data(brand_id)

    # Prepare Stage 4 inputs
    stage4_inputs = {
        "universal_lessons": stage3_output,
        "brand_research": brand_research,
        "brand_name": brand_profile["company_name"],
        "brand_industry": brand_profile["industry"]
    }

    # Execute Stage 4 chain
    return stage4_chain.invoke(stage4_inputs)
```

### Error Handling Example

```python
from pipeline.utils import load_research_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Attempt to load research
research = load_research_data("new-brand")

if not research:
    logging.warning("Proceeding with Stage 4 in degraded mode (no research data)")
    # Stage 4 will rely solely on brand profile YAML
else:
    logging.info(f"Stage 4 enriched with {len(research)} characters of research")
```

## Data Quality Characteristics

### File Size Range
- **Minimum:** ~35 KB (smallest: lactalis-canada at 35.8 KB)
- **Maximum:** ~48 KB (largest: mccormick-usa at 47.0 KB)
- **Average:** ~42 KB

### Line Count Range
- **Minimum:** ~545 lines (lactalis-canada: 546 lines)
- **Maximum:** ~720 lines (mccormick-usa: 721 lines)
- **Average:** ~610 lines

### Encoding
- **Required:** UTF-8
- **Handled by:** `load_research_data()` function automatically

## Testing

Test the research loader with all available brands:

```bash
python test_research_loader.py
```

**Test Coverage:**
- ✓ All 4 brand research files load successfully
- ✓ UTF-8 encoding handled correctly
- ✓ File statistics validated (line count, size)
- ✓ Missing file handling (non-fatal error)
- ✓ Logging output verified

## Future Extensibility

### Adding New Brand Research

1. Create new research file following naming convention:
   ```
   docs/web-search-setup/{brand-id}-research.md
   ```

2. Include all 8 strategic sections

3. Maintain UTF-8 encoding

4. Verify with test script:
   ```bash
   python test_research_loader.py
   ```

### Research Data Updates

Research files can be updated independently without code changes:
- Update content in markdown files
- No pipeline code modifications required
- Next pipeline execution automatically uses updated research

## References

- **Implementation:** `pipeline/utils.py:231` (`load_research_data()` function)
- **Test Script:** `test_research_loader.py`
- **Research Files:** `docs/web-search-setup/{brand-id}-research.md`
- **Epic 3 Documentation:** Story 3.1 - Pre-Existing Research Data Integration

---

**Last Updated:** Story 3.1 Implementation
**Related Stories:** Epic 3 - Brand Contextualization with Research Data (Stage 4)
