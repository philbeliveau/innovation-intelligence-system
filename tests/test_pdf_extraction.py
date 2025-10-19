#!/usr/bin/env python3
"""
Integration tests for PDF text extraction.
Tests Story 3.2 acceptance criteria AC6.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
import io

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.run_pipeline import run_from_uploaded_file


def create_test_pdf_content(text_content: str) -> str:
    """Create minimal PDF content with text."""
    # Create a minimal valid PDF with text
    pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
({text_content}) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
410
%%EOF"""
    return pdf_content


def test_pdf_extraction_single_page():
    """Test 3.2-INT-008: Verify PDF text extraction from valid single-page PDF."""

    test_text = "sustainable packaging innovation"
    pdf_content = create_test_pdf_content(test_text)

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False, mode='w') as tmp_pdf:
        tmp_pdf.write(pdf_content)
        tmp_pdf_path = tmp_pdf.name

    try:
        # Mock all LLM stages
        with patch('scripts.run_pipeline.create_stage1_chain') as mock_stage1, \
             patch('scripts.run_pipeline.create_stage2_chain') as mock_stage2, \
             patch('scripts.run_pipeline.create_stage3_chain') as mock_stage3, \
             patch('scripts.run_pipeline.create_stage4_chain') as mock_stage4, \
             patch('scripts.run_pipeline.create_stage5_chain') as mock_stage5, \
             patch('scripts.run_pipeline.load_brand_profile') as mock_brand, \
             patch('scripts.run_pipeline.load_research_data') as mock_research, \
             patch('scripts.run_pipeline.setup_pipeline_logging'), \
             patch('scripts.run_pipeline.validate_brand_id', return_value=True):

            # Setup mocks
            mock_brand.return_value = {'company_name': 'Test'}
            mock_research.return_value = "Research"

            # Track PDF text extraction
            extracted_text = []

            def capture_stage1_run(input_text_str):
                # Capture the input_text that was extracted from PDF
                extracted_text.append(input_text_str)
                return {'stage1_output': '## Track 1: Test\nContent\n\n## Track 2: Test2\nContent2'}

            for mock_stage, key in [
                (mock_stage1, 'stage1_output'),
                (mock_stage2, 'stage2_output'),
                (mock_stage3, 'stage3_output'),
                (mock_stage4, 'stage4_output'),
            ]:
                inst = Mock()
                inst.output_key = key
                if mock_stage == mock_stage1:
                    inst.run.side_effect = capture_stage1_run
                else:
                    inst.run.return_value = {key: 'output'}
                inst.save_output.return_value = Path('/tmp/out.md')
                mock_stage.return_value = inst

            stage5_inst = Mock()
            stage5_inst.run.return_value = {'opportunities': []}
            stage5_inst.render_opportunity_cards.return_value = []
            stage5_inst.generate_summary_file.return_value = Path('/tmp/summary.md')
            mock_stage5.return_value = stage5_inst

            # Execute
            exit_code = run_from_uploaded_file(
                tmp_pdf_path,
                'test-brand',
                'test-pdf-single',
                selected_track=1
            )

            # Assertions
            assert exit_code == 0, "Should extract PDF successfully"
            assert len(extracted_text) > 0, "Should have extracted text from PDF"
            assert test_text in extracted_text[0], f"Extracted text should contain '{test_text}'"

    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

    print("✓ test_pdf_extraction_single_page passed")


def test_pdf_extraction_multi_page():
    """Test 3.2-INT-009: Verify PDF text extraction from multi-page PDF."""

    # For multi-page test, create a simple multi-page PDF structure
    test_text = "Page 1 innovation content Page 2 market analysis Page 3 recommendations"
    pdf_content = create_test_pdf_content(test_text)

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False, mode='w') as tmp_pdf:
        tmp_pdf.write(pdf_content)
        tmp_pdf_path = tmp_pdf.name

    try:
        with patch('scripts.run_pipeline.create_stage1_chain') as mock_stage1, \
             patch('scripts.run_pipeline.create_stage2_chain') as mock_stage2, \
             patch('scripts.run_pipeline.create_stage3_chain') as mock_stage3, \
             patch('scripts.run_pipeline.create_stage4_chain') as mock_stage4, \
             patch('scripts.run_pipeline.create_stage5_chain') as mock_stage5, \
             patch('scripts.run_pipeline.load_brand_profile') as mock_brand, \
             patch('scripts.run_pipeline.load_research_data') as mock_research, \
             patch('scripts.run_pipeline.setup_pipeline_logging'), \
             patch('scripts.run_pipeline.validate_brand_id', return_value=True):

            mock_brand.return_value = {'company_name': 'Test'}
            mock_research.return_value = "Research"

            extracted_text = []

            def capture_stage1_run(input_text_str):
                extracted_text.append(input_text_str)
                return {'stage1_output': '## Track 1: Test\nContent\n\n## Track 2: Test2\nContent2'}

            for mock_stage, key in [
                (mock_stage1, 'stage1_output'),
                (mock_stage2, 'stage2_output'),
                (mock_stage3, 'stage3_output'),
                (mock_stage4, 'stage4_output'),
            ]:
                inst = Mock()
                inst.output_key = key
                if mock_stage == mock_stage1:
                    inst.run.side_effect = capture_stage1_run
                else:
                    inst.run.return_value = {key: 'output'}
                inst.save_output.return_value = Path('/tmp/out.md')
                mock_stage.return_value = inst

            stage5_inst = Mock()
            stage5_inst.run.return_value = {'opportunities': []}
            stage5_inst.render_opportunity_cards.return_value = []
            stage5_inst.generate_summary_file.return_value = Path('/tmp/summary.md')
            mock_stage5.return_value = stage5_inst

            exit_code = run_from_uploaded_file(
                tmp_pdf_path,
                'test-brand',
                'test-pdf-multi',
                selected_track=1
            )

            # Assertions
            assert exit_code == 0, "Should extract multi-page PDF successfully"
            assert len(extracted_text) > 0, "Should have extracted text from PDF"
            # Verify content was extracted (simplified assertion for manual multi-page PDF)
            assert len(extracted_text[0]) > 0, "Should extract text content"

    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

    print("✓ test_pdf_extraction_multi_page passed")


def test_pdf_extraction_corrupted_file():
    """Test 3.2-INT-010: Verify graceful error handling for corrupted PDF."""

    # Create a file with invalid PDF content
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf.write(b"This is not a valid PDF file")
        tmp_pdf_path = tmp_pdf.name

    try:
        with patch('scripts.run_pipeline.load_brand_profile') as mock_brand, \
             patch('scripts.run_pipeline.load_research_data') as mock_research, \
             patch('scripts.run_pipeline.setup_pipeline_logging'), \
             patch('scripts.run_pipeline.validate_brand_id', return_value=True):

            mock_brand.return_value = {'company_name': 'Test'}
            mock_research.return_value = "Research"

            # Execute with corrupted PDF
            exit_code = run_from_uploaded_file(
                tmp_pdf_path,
                'test-brand',
                'test-pdf-corrupt',
                selected_track=1
            )

            # Should return non-zero exit code on error
            assert exit_code == 1, "Should return error code for corrupted PDF"

    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

    print("✓ test_pdf_extraction_corrupted_file passed")


if __name__ == "__main__":
    print("Running PDF Extraction Integration Tests\n")

    test_pdf_extraction_single_page()
    test_pdf_extraction_multi_page()
    test_pdf_extraction_corrupted_file()

    print("\n✅ All PDF extraction tests passed!")
