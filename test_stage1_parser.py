#!/usr/bin/env python3
"""Test script for Stage 1 markdown parser."""

import sys
import re
from typing import Dict, Any

# Inline the parser method to test without dependencies
def parse_markdown_output(markdown_text: str, input_text: str) -> Dict[str, Any]:
    """Parse structured fields from markdown-formatted Stage 1 output."""

    # Initialize with defaults
    extracted = {
        "extractedText": input_text[:500],
        "trendTitle": None,
        "trendImage": None,
        "coreMechanism": "",
        "businessImpact": "",
        "patternTransfersTo": [],
        "mechanisms": [],
        "abstractionTest": "",
        "evidenceStrength": "MEDIUM",
        "cpgRelevance": "",
        "stage1_output": markdown_text
    }

    # Extract trend title from document
    title_lines = []
    for line in input_text.split('\n')[:5]:
        line = line.strip()
        if line and line.isupper() and len(line.split()) <= 4:
            title_lines.append(line)
        elif title_lines:
            break

    if title_lines:
        extracted["trendTitle"] = ' '.join(title_lines)

    # Extract core mechanism from markdown
    mechanism_match = re.search(
        r'\*\*The Underlying Mechanism:\*\*\s*(.+?)(?=\n\n|\*\*|$)',
        markdown_text,
        re.DOTALL
    )
    if mechanism_match:
        extracted["coreMechanism"] = mechanism_match.group(1).strip()
    else:
        mech_fallback = re.search(
            r'## Mechanism \d+:.*?\n\n(.+?)(?=\n\n|\*\*)',
            markdown_text,
            re.DOTALL
        )
        if mech_fallback:
            extracted["coreMechanism"] = mech_fallback.group(1).strip()[:500]

    # Extract business impact
    impact_match = re.search(
        r'\*\*Why It Works:\*\*\s*(.+?)(?=\n\n|\*\*|$)',
        markdown_text,
        re.DOTALL
    )
    if impact_match:
        extracted["businessImpact"] = impact_match.group(1).strip()

    # Extract CPG relevance
    cpg_match = re.search(
        r'\*\*CPG Relevance:\*\*\s*(.+?)(?=\n\n|$)',
        markdown_text,
        re.DOTALL
    )
    if cpg_match:
        extracted["cpgRelevance"] = cpg_match.group(1).strip()

    # Extract evidence strength
    evidence_match = re.search(
        r'\*\*Evidence Strength:\*\*\s*(HIGH|MEDIUM|LOW)',
        markdown_text
    )
    if evidence_match:
        extracted["evidenceStrength"] = evidence_match.group(1)

    # Extract pattern transfers to
    if extracted["cpgRelevance"]:
        app_items = re.findall(
            r'(?:apply|applies|applying|relevant)\s+to\s+([a-z\s,]+?)(?:\.|,\s*while|\s+or\s+)',
            extracted["cpgRelevance"],
            re.IGNORECASE
        )
        if app_items:
            all_items = []
            for item in app_items:
                all_items.extend([x.strip() for x in item.split(',') if x.strip()])
            extracted["patternTransfersTo"] = all_items[:6]
        else:
            product_items = re.findall(
                r'\b(apps?|kits?|brands?|products?|lines?|launches?|wellness\s+\w+|fitness\s+\w+|food\s+\w+)\b',
                extracted["cpgRelevance"],
                re.IGNORECASE
            )
            extracted["patternTransfersTo"] = list(set(product_items))[:6] if product_items else []

    if not extracted["patternTransfersTo"]:
        transfers_section = re.search(
            r'(?:could\s+)?(?:apply|transfer|relevant)\s+to[:\s]+(.+?)(?=\n\n|##|$)',
            markdown_text,
            re.DOTALL | re.IGNORECASE
        )
        if transfers_section:
            items = re.findall(r'(?:[-•]\s*)?([a-z\s]+)(?:,|\n|$)', transfers_section.group(1), re.IGNORECASE)
            extracted["patternTransfersTo"] = [item.strip() for item in items if item.strip() and len(item.strip()) > 3][:6]

    return extracted

# Sample markdown output from LLM
markdown_output = """## Mechanism 1: **Modular Ritualization**

**Concrete Example:** Sol, a wellness app, curates personalized self-discovery paths by combining ancient practices (tai chi, prayer, breathwork) with modern psychology, astrology, and numerology, allowing users to mix and match components into daily rituals.

**The Underlying Mechanism:** By breaking down complex spiritual or wellness systems into modular, customizable components, brands enable users to create personalized practices that resonate with their individual needs and values, rather than prescribing rigid, one-size-fits-all solutions.

**Mechanism Type:** COMBINED

**Constraint Eliminated:** Reduced the need for users to adopt entire spiritual systems or practices, which often require significant time, effort, and alignment with specific beliefs.

**Why It Works:** People increasingly seek meaning and connection in ways that align with their personal identities and lifestyles. Modularization allows for flexibility and personalization, making spiritual practices more accessible and sustainable.

**Structural Pattern:** When [users seek personalized meaning], eliminating [the need for rigid, universal systems] by [offering modular, mix-and-match components] creates [accessible, sustainable rituals].

---

## Extraction Quality Check

**Abstraction Test:** Yes. Both mechanisms can be explained to someone in a completely different industry.

**Evidence Strength:** HIGH. The document provides multiple concrete examples and measurable impacts.

**CPG Relevance:** Both mechanisms are highly relevant to CPG. Modular ritualization could apply to product lines offering customizable wellness kits, while cultural recontextualization could inspire seasonal product launches tied to cultural or natural cycles."""

input_text = """SACRED
SYNC
Ritual is redesigned for
restless times
EXPERIENCE DEFICT #3"""

# Test parser directly
result = parse_markdown_output(markdown_output, input_text)

print("=== EXTRACTED FIELDS ===\n")
print(f"Trend Title: {result['trendTitle']}")
print(f"\nCore Mechanism ({len(result['coreMechanism'])} chars):")
print(result['coreMechanism'])
print(f"\nBusiness Impact ({len(result['businessImpact'])} chars):")
print(result['businessImpact'])
print(f"\nCPG Relevance ({len(result['cpgRelevance'])} chars):")
print(result['cpgRelevance'])
print(f"\nPattern Transfers To: {result['patternTransfersTo']}")
print(f"\nEvidence Strength: {result['evidenceStrength']}")
