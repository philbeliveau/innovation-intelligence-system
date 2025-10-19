#!/usr/bin/env python3
"""
Integration tests for full pipeline execution via run_from_uploaded_file().
Tests Story 3.2 acceptance criteria AC4.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.run_pipeline import run_from_uploaded_file


def test_run_from_uploaded_file_executes_all_stages():
    """Test 3.2-INT-003: Verify pipeline executes all 5 stages sequentially."""

    # Create a mock PDF file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf_path = tmp_pdf.name

    try:
        # Mock all stage chains to avoid actual LLM calls
        with patch('scripts.run_pipeline.create_stage1_chain') as mock_stage1, \
             patch('scripts.run_pipeline.create_stage2_chain') as mock_stage2, \
             patch('scripts.run_pipeline.create_stage3_chain') as mock_stage3, \
             patch('scripts.run_pipeline.create_stage4_chain') as mock_stage4, \
             patch('scripts.run_pipeline.create_stage5_chain') as mock_stage5, \
             patch('scripts.run_pipeline.load_brand_profile') as mock_brand, \
             patch('scripts.run_pipeline.load_research_data') as mock_research, \
             patch('scripts.run_pipeline.PdfReader') as mock_pdf_reader, \
             patch('scripts.run_pipeline.setup_pipeline_logging'), \
             patch('scripts.run_pipeline.validate_brand_id', return_value=True):

            # Setup PDF reader mock
            mock_page = Mock()
            mock_page.extract_text.return_value = "Sample PDF content for testing"
            mock_reader_instance = Mock()
            mock_reader_instance.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader_instance

            # Setup brand profile mock
            mock_brand.return_value = {
                'company_name': 'Test Company',
                'industry': 'Technology'
            }
            mock_research.return_value = "Test research data"

            # Setup stage chain mocks
            stage1_instance = Mock()
            stage1_instance.output_key = 'stage1_output'
            stage1_instance.run.return_value = {'stage1_output': '## Track 1: Test\nContent\n\n## Track 2: Test2\nContent2'}
            stage1_instance.save_output.return_value = Path('/tmp/stage1.md')
            mock_stage1.return_value = stage1_instance

            stage2_instance = Mock()
            stage2_instance.output_key = 'stage2_output'
            stage2_instance.run.return_value = {'stage2_output': 'Stage 2 output'}
            stage2_instance.save_output.return_value = Path('/tmp/stage2.md')
            mock_stage2.return_value = stage2_instance

            stage3_instance = Mock()
            stage3_instance.output_key = 'stage3_output'
            stage3_instance.run.return_value = {'stage3_output': 'Stage 3 output'}
            stage3_instance.save_output.return_value = Path('/tmp/stage3.md')
            mock_stage3.return_value = stage3_instance

            stage4_instance = Mock()
            stage4_instance.output_key = 'stage4_output'
            stage4_instance.run.return_value = {'stage4_output': 'Stage 4 output'}
            stage4_instance.save_output.return_value = Path('/tmp/stage4.md')
            mock_stage4.return_value = stage4_instance

            stage5_instance = Mock()
            stage5_instance.run.return_value = {'opportunities': [
                {'title': 'Opportunity 1', 'description': 'Test opportunity'}
            ]}
            stage5_instance.render_opportunity_cards.return_value = [Path('/tmp/opp1.md')]
            stage5_instance.generate_summary_file.return_value = Path('/tmp/summary.md')
            mock_stage5.return_value = stage5_instance

            # Execute pipeline
            exit_code = run_from_uploaded_file(
                input_file_path=tmp_pdf_path,
                brand_id='test-brand',
                run_id='test-run-001',
                selected_track=1
            )

            # Assertions
            assert exit_code == 0, "Pipeline should complete successfully with exit code 0"

            # Verify all stages were called
            assert mock_stage1.called, "Stage 1 should be created"
            assert mock_stage2.called, "Stage 2 should be created"
            assert mock_stage3.called, "Stage 3 should be created"
            assert mock_stage4.called, "Stage 4 should be created"
            assert mock_stage5.called, "Stage 5 should be created"

            # Verify stages were run
            assert stage1_instance.run.called, "Stage 1 should be run"
            assert stage2_instance.run.called, "Stage 2 should be run"
            assert stage3_instance.run.called, "Stage 3 should be run"
            assert stage4_instance.run.called, "Stage 4 should be run"
            assert stage5_instance.run.called, "Stage 5 should be run"

            # Verify outputs were saved
            assert stage1_instance.save_output.called, "Stage 1 output should be saved"
            assert stage2_instance.save_output.called, "Stage 2 output should be saved"
            assert stage3_instance.save_output.called, "Stage 3 output should be saved"
            assert stage4_instance.save_output.called, "Stage 4 output should be saved"

            # Verify selected_track was passed to Stage 1 save_output
            # save_output is called as: save_output(stage1_output, output_dir, selected_track)
            stage1_save_call_args = stage1_instance.save_output.call_args[0]
            assert len(stage1_save_call_args) == 3, "save_output should be called with 3 positional args"
            assert stage1_save_call_args[2] == 1, "selected_track (3rd arg) should be 1"

    finally:
        # Cleanup temp file
        Path(tmp_pdf_path).unlink(missing_ok=True)

    print("✓ test_run_from_uploaded_file_executes_all_stages passed")


def test_run_from_uploaded_file_returns_zero_on_success():
    """Test 3.2-INT-004: Verify function returns exit code 0 on success."""

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf_path = tmp_pdf.name

    try:
        # Mock successful execution
        with patch('scripts.run_pipeline.create_stage1_chain') as mock_stage1, \
             patch('scripts.run_pipeline.create_stage2_chain') as mock_stage2, \
             patch('scripts.run_pipeline.create_stage3_chain') as mock_stage3, \
             patch('scripts.run_pipeline.create_stage4_chain') as mock_stage4, \
             patch('scripts.run_pipeline.create_stage5_chain') as mock_stage5, \
             patch('scripts.run_pipeline.load_brand_profile') as mock_brand, \
             patch('scripts.run_pipeline.load_research_data') as mock_research, \
             patch('scripts.run_pipeline.PdfReader') as mock_pdf_reader, \
             patch('scripts.run_pipeline.setup_pipeline_logging'), \
             patch('scripts.run_pipeline.validate_brand_id', return_value=True):

            # Setup mocks (simplified)
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test content"
            mock_reader = Mock()
            mock_reader.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader

            mock_brand.return_value = {'company_name': 'Test'}
            mock_research.return_value = "Research"

            # Setup all stage mocks to return successfully
            for mock_stage, output_key in [
                (mock_stage1, 'stage1_output'),
                (mock_stage2, 'stage2_output'),
                (mock_stage3, 'stage3_output'),
                (mock_stage4, 'stage4_output'),
            ]:
                instance = Mock()
                instance.output_key = output_key
                instance.run.return_value = {output_key: 'output'}
                instance.save_output.return_value = Path('/tmp/out.md')
                mock_stage.return_value = instance

            stage5_instance = Mock()
            stage5_instance.run.return_value = {'opportunities': [{'title': 'Test'}]}
            stage5_instance.render_opportunity_cards.return_value = [Path('/tmp/opp.md')]
            stage5_instance.generate_summary_file.return_value = Path('/tmp/summary.md')
            mock_stage5.return_value = stage5_instance

            # Execute
            exit_code = run_from_uploaded_file(
                tmp_pdf_path,
                'test-brand',
                'test-run-002',
                selected_track=2
            )

            # Assert success
            assert exit_code == 0, "Should return 0 on successful execution"

    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

    print("✓ test_run_from_uploaded_file_returns_zero_on_success passed")


def test_run_from_uploaded_file_returns_nonzero_on_failure():
    """Test 3.2-INT-005: Verify function returns non-zero on stage failure."""

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf_path = tmp_pdf.name

    try:
        # Mock Stage 1 to raise an exception
        with patch('scripts.run_pipeline.create_stage1_chain') as mock_stage1, \
             patch('scripts.run_pipeline.load_brand_profile') as mock_brand, \
             patch('scripts.run_pipeline.load_research_data') as mock_research, \
             patch('scripts.run_pipeline.PdfReader') as mock_pdf_reader, \
             patch('scripts.run_pipeline.setup_pipeline_logging'), \
             patch('scripts.run_pipeline.validate_brand_id', return_value=True):

            mock_page = Mock()
            mock_page.extract_text.return_value = "Test"
            mock_reader = Mock()
            mock_reader.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader

            mock_brand.return_value = {'company_name': 'Test'}
            mock_research.return_value = "Research"

            # Make Stage 1 fail
            stage1_instance = Mock()
            stage1_instance.output_key = 'stage1_output'
            stage1_instance.run.side_effect = Exception("Stage 1 LLM call failed")
            mock_stage1.return_value = stage1_instance

            # Execute
            exit_code = run_from_uploaded_file(
                tmp_pdf_path,
                'test-brand',
                'test-run-fail',
                selected_track=1
            )

            # Assert failure
            assert exit_code == 1, "Should return 1 on pipeline failure"

    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

    print("✓ test_run_from_uploaded_file_returns_nonzero_on_failure passed")


def test_output_directory_creation():
    """Test that output directory is created at data/test-outputs/{run_id}/."""

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf_path = tmp_pdf.name

    run_id = 'test-dir-creation-001'

    try:
        with patch('scripts.run_pipeline.create_stage1_chain') as mock_stage1, \
             patch('scripts.run_pipeline.create_stage2_chain') as mock_stage2, \
             patch('scripts.run_pipeline.create_stage3_chain') as mock_stage3, \
             patch('scripts.run_pipeline.create_stage4_chain') as mock_stage4, \
             patch('scripts.run_pipeline.create_stage5_chain') as mock_stage5, \
             patch('scripts.run_pipeline.load_brand_profile') as mock_brand, \
             patch('scripts.run_pipeline.load_research_data') as mock_research, \
             patch('scripts.run_pipeline.PdfReader') as mock_pdf_reader, \
             patch('scripts.run_pipeline.setup_pipeline_logging'), \
             patch('scripts.run_pipeline.validate_brand_id', return_value=True):

            # Setup mocks
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test"
            mock_reader = Mock()
            mock_reader.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader

            mock_brand.return_value = {'company_name': 'Test'}
            mock_research.return_value = "Research"

            for mock_stage, key in [
                (mock_stage1, 'stage1_output'),
                (mock_stage2, 'stage2_output'),
                (mock_stage3, 'stage3_output'),
                (mock_stage4, 'stage4_output'),
            ]:
                inst = Mock()
                inst.output_key = key
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
                run_id,
                selected_track=1
            )

            # Verify output directory was created
            output_dir = Path(f"data/test-outputs/{run_id}")
            assert output_dir.exists(), f"Output directory should exist at {output_dir}"

            # Cleanup
            import shutil
            shutil.rmtree(output_dir, ignore_errors=True)

    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

    print("✓ test_output_directory_creation passed")


if __name__ == "__main__":
    print("Running Pipeline Execution Integration Tests\n")

    test_run_from_uploaded_file_executes_all_stages()
    test_run_from_uploaded_file_returns_zero_on_success()
    test_run_from_uploaded_file_returns_nonzero_on_failure()
    test_output_directory_creation()

    print("\n✅ All pipeline execution tests passed!")
