"""
Test template rendering for opportunity cards.

Tests that the Jinja2 template correctly renders opportunity cards
with all required sections and valid YAML frontmatter.
"""

import pytest
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import yaml
import re
from datetime import datetime


def load_template():
    """Load the opportunity card Jinja2 template."""
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    return env.get_template("opportunity-card.md.j2")


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown content with YAML frontmatter

    Returns:
        Tuple of (frontmatter_dict, body_content)

    Raises:
        ValueError: If frontmatter is missing or invalid
    """
    # Match YAML frontmatter between --- delimiters
    pattern = r'^---\n(.*?)\n---\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        raise ValueError("No valid YAML frontmatter found")

    frontmatter_str = match.group(1)
    body = match.group(2)

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML frontmatter: {e}")

    return frontmatter, body


def get_sample_data():
    """Return sample data for template testing."""
    return {
        "opportunity_id": "test-brand-20251007-001",
        "brand": "Test Brand Inc.",
        "input_source": "test-input-document",
        "timestamp": "2025-10-07T14:30:00Z",
        "tags": '["product-innovation", "sustainability", "premium"]',
        "title": "Transform Packaging Into Customer Experience",
        "description": """Innovative brands are reimagining packaging as more than \
protection—it's becoming a critical touchpoint for storytelling, sustainability \
signaling, and memorable unboxing experiences.

For Test Brand, this represents an opportunity to differentiate in a commoditized \
market by creating packaging that customers want to keep, photograph, and share. \
Premium unboxing experiences can justify higher price points while building \
emotional connections.

This aligns with Test Brand's commitment to sustainability and premium positioning, \
turning necessary packaging spend into brand-building investment.""",
        "actionability_items": [
            "**Product Team:** Conduct packaging audit of top 10 competitors and \
identify differentiation opportunities (2 weeks)",
            "**Sustainability:** Research compostable/recyclable premium materials \
that maintain structural integrity and visual appeal (3 weeks)",
            "**Design:** Create 3-5 packaging prototypes with unboxing experience \
focus, test with 20-30 target customers (6 weeks)",
            "**Finance:** Model incremental packaging costs vs. projected brand lift \
and price premium justification (2 weeks)"
        ],
        "visual_description": "Imagine opening a beautifully designed box with \
magnetic closure, revealing the product nestled in sustainable tissue paper with \
a handwritten-style thank you note. The interior features illustrated brand story \
elements and a QR code linking to product origin stories. The packaging doubles as \
a storage container customers want to keep, with Test Brand's logo subtly debossed \
on natural kraft material.",
        "follow_up_prompts": [
            "**Validation:** How might we test whether premium packaging actually \
influences purchase decisions vs. being perceived as wasteful, and at what price \
point does packaging investment become margin-destructive?",
            "**Expansion:** What other touchpoints beyond packaging could benefit \
from experience design thinking—shipping boxes, retail displays, product inserts—\
and should they follow consistent design language?",
            "**Challenge:** How might we balance sustainability commitments with \
premium packaging aesthetics when many eco-materials lack visual refinement, and \
would customers accept trade-offs if sustainability story is compelling?"
        ]
    }


def test_template_loads():
    """Test that the template file can be loaded."""
    template = load_template()
    assert template is not None
    assert template.name == "opportunity-card.md.j2"


def test_template_renders_with_sample_data():
    """Test that template renders successfully with sample data."""
    template = load_template()
    sample_data = get_sample_data()

    rendered = template.render(**sample_data)

    assert rendered is not None
    assert len(rendered) > 0


def test_rendered_output_has_frontmatter():
    """Test that rendered output includes YAML frontmatter."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    # Should start with ---
    assert rendered.startswith("---\n")

    # Should have closing ---
    assert "\n---\n" in rendered


def test_frontmatter_is_valid_yaml():
    """Test that frontmatter can be parsed as valid YAML."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    frontmatter, body = parse_frontmatter(rendered)

    # Should return a dictionary
    assert isinstance(frontmatter, dict)
    assert len(frontmatter) > 0


def test_frontmatter_contains_required_fields():
    """Test that frontmatter includes all required metadata fields."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    frontmatter, body = parse_frontmatter(rendered)

    required_fields = [
        "opportunity_id",
        "brand",
        "input_source",
        "timestamp",
        "tags"
    ]

    for field in required_fields:
        assert field in frontmatter, f"Missing required field: {field}"


def test_frontmatter_values_match_input():
    """Test that frontmatter values match input data."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    frontmatter, body = parse_frontmatter(rendered)

    assert frontmatter["opportunity_id"] == sample_data["opportunity_id"]
    assert frontmatter["brand"] == sample_data["brand"]
    assert frontmatter["input_source"] == sample_data["input_source"]
    # YAML parses timestamp as datetime object, verify it matches input
    # Convert datetime back to ISO format with Z suffix
    timestamp_str = frontmatter["timestamp"].isoformat().replace('+00:00', 'Z')
    assert timestamp_str == sample_data["timestamp"]


def test_body_contains_title():
    """Test that body includes the title as H1."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    frontmatter, body = parse_frontmatter(rendered)

    # Should have H1 with title
    assert f"# {sample_data['title']}" in body


def test_body_contains_description():
    """Test that body includes the description section."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    frontmatter, body = parse_frontmatter(rendered)

    # Should have Description heading
    assert "## Description" in body

    # Should include description content
    assert "Innovative brands are reimagining packaging" in body


def test_body_contains_actionability():
    """Test that body includes actionability section with all items."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    frontmatter, body = parse_frontmatter(rendered)

    # Should have Actionability heading
    assert "## Actionability" in body

    # Should include all action items
    for item in sample_data["actionability_items"]:
        # Check for key phrases from each action item
        assert "Product Team:" in body
        assert "Sustainability:" in body
        assert "Design:" in body
        assert "Finance:" in body


def test_body_contains_visual():
    """Test that body includes visual placeholder section."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    frontmatter, body = parse_frontmatter(rendered)

    # Should have Visual heading
    assert "## Visual" in body

    # Should include visual description in italics
    assert sample_data["visual_description"] in body


def test_body_contains_follow_up_prompts():
    """Test that body includes follow-up prompts section."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    frontmatter, body = parse_frontmatter(rendered)

    # Should have Follow-up Prompts heading
    assert "## Follow-up Prompts" in body

    # Should include all prompts with numbering
    assert "1." in body
    assert "2." in body
    assert "3." in body

    # Check for key phrases from prompts
    assert "Validation:" in body
    assert "Expansion:" in body
    assert "Challenge:" in body


def test_all_sections_present_in_order():
    """Test that all sections appear in the correct order."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    frontmatter, body = parse_frontmatter(rendered)

    # Find positions of each section
    sections = [
        "# ",  # Title (H1)
        "## Description",
        "## Actionability",
        "## Visual",
        "## Follow-up Prompts"
    ]

    positions = []
    for section in sections:
        pos = body.find(section)
        assert pos != -1, f"Section not found: {section}"
        positions.append(pos)

    # Verify sections appear in order
    assert positions == sorted(positions), \
        "Sections are not in the correct order"


def test_template_handles_empty_lists():
    """Test template behavior with empty lists."""
    template = load_template()
    sample_data = get_sample_data()

    # Test with empty actionability items
    sample_data["actionability_items"] = []
    rendered = template.render(**sample_data)

    # Should still render without errors
    assert rendered is not None
    assert "## Actionability" in rendered


def test_template_handles_special_characters():
    """Test template handles special characters in content."""
    template = load_template()
    sample_data = get_sample_data()

    # Add special characters to description
    sample_data["description"] = "Test & special <chars> \"quotes\" 'apostrophes'"

    rendered = template.render(**sample_data)

    # Should render without errors
    assert rendered is not None
    assert sample_data["description"] in rendered


def test_output_is_valid_markdown():
    """Test that output is structurally valid markdown."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    # Basic markdown validation checks
    assert rendered.startswith("---\n")  # Valid frontmatter start
    assert "\n---\n" in rendered  # Valid frontmatter end
    assert "# " in rendered  # Has H1 heading
    assert "## " in rendered  # Has H2 headings
    assert not rendered.endswith("\n\n\n")  # No excessive trailing newlines


def test_save_rendered_output():
    """Test saving rendered output to file for manual inspection."""
    template = load_template()
    sample_data = get_sample_data()
    rendered = template.render(**sample_data)

    output_path = Path(__file__).parent / "data" / "test-outputs" / \
        "test-template-output.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(rendered, encoding='utf-8')

    assert output_path.exists()
    assert output_path.stat().st_size > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
