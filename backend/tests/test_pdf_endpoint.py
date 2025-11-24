"""Test PDF Download Endpoint

Verifies that the backend PDF generation endpoint works correctly.
"""
import pytest
from pathlib import Path


def test_pdf_export_module_imports():
    """Test that pdf_export module can be imported"""
    from app.pdf_export import generate_all_stages_pdf, generate_stage_pdf
    assert callable(generate_all_stages_pdf)
    assert callable(generate_stage_pdf)


def test_pdf_generation_with_markdown():
    """Test PDF generation with sample markdown content"""
    from app.pdf_export import generate_all_stages_pdf
    import tempfile

    # Sample markdown for testing
    sample_markdowns = {
        0: "# Brand Context\n\nThis is a test brand profile.",
        1: "# Stage 1: Extraction\n\nTest trend data.",
        2: "# Stage 2: Signals\n\nTest consumer signals."
    }

    # Generate PDF
    pdf_path = generate_all_stages_pdf(
        stage_markdowns=sample_markdowns,
        brand_name="Test Brand"
    )

    # Verify PDF was created
    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
    assert pdf_path.stat().st_size > 0  # Non-empty file

    print(f"✅ PDF generated successfully: {pdf_path}")


def test_format_stage_output():
    """Test that format_stage_output works for all stages"""
    from pipeline.output_formatters import format_stage_output

    # Test Stage 0 (Brand Context)
    stage0_output = {
        "brand_name": "Test Brand",
        "industry": "Food & Beverage",
        "country": "Canada"
    }
    md0 = format_stage_output(0, stage0_output)
    assert isinstance(md0, str)
    assert len(md0) > 0
    print(f"✅ Stage 0 markdown: {len(md0)} chars")

    # Test Stage 1 (Extraction)
    stage1_output = {
        "trend_name": "Test Trend",
        "lifecycle_stage": "EMERGING",
        "evidence": ["Evidence 1", "Evidence 2"]
    }
    md1 = format_stage_output(1, stage1_output)
    assert isinstance(md1, str)
    assert len(md1) > 0
    print(f"✅ Stage 1 markdown: {len(md1)} chars")


if __name__ == "__main__":
    print("\n=== Testing PDF Export Module ===\n")

    print("Test 1: Module imports...")
    test_pdf_export_module_imports()

    print("\nTest 2: PDF generation with markdown...")
    test_pdf_generation_with_markdown()

    print("\nTest 3: Format stage output...")
    test_format_stage_output()

    print("\n✅ All tests passed!")
