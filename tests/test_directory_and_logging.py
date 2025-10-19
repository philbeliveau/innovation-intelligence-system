#!/usr/bin/env python3
"""
Integration tests for output directory creation and logging infrastructure.
Tests Story 3.2 acceptance criteria AC5 and AC7.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.run_pipeline import run_from_uploaded_file


def test_output_directory_created_with_permissions():
    """Test 3.2-INT-006: Verify output directory created with correct permissions."""

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf_path = tmp_pdf.name

    run_id = 'test-dir-permissions-001'

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

            # Mock PDF reader
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test PDF content"
            mock_reader = Mock()
            mock_reader.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader

            # Setup mocks
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

            # Verify directory was created
            output_dir = Path(f"data/test-outputs/{run_id}")
            assert output_dir.exists(), f"Output directory should exist at {output_dir}"
            assert output_dir.is_dir(), "Output path should be a directory"

            # Verify permissions (should be readable and writable)
            import os
            assert os.access(output_dir, os.R_OK), "Directory should be readable"
            assert os.access(output_dir, os.W_OK), "Directory should be writable"

            # Cleanup
            shutil.rmtree(output_dir, ignore_errors=True)

    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

    print("✓ test_output_directory_created_with_permissions passed")


def test_log_file_created():
    """Test 3.2-INT-007: Verify log file created at {run_id}/logs/pipeline.log."""

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf_path = tmp_pdf.name

    run_id = 'test-log-creation-001'

    try:
        with patch('scripts.run_pipeline.create_stage1_chain') as mock_stage1, \
             patch('scripts.run_pipeline.create_stage2_chain') as mock_stage2, \
             patch('scripts.run_pipeline.create_stage3_chain') as mock_stage3, \
             patch('scripts.run_pipeline.create_stage4_chain') as mock_stage4, \
             patch('scripts.run_pipeline.create_stage5_chain') as mock_stage5, \
             patch('scripts.run_pipeline.load_brand_profile') as mock_brand, \
             patch('scripts.run_pipeline.load_research_data') as mock_research, \
             patch('scripts.run_pipeline.PdfReader') as mock_pdf_reader, \
             patch('scripts.run_pipeline.validate_brand_id', return_value=True):

            # Mock PDF reader
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test PDF content"
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

            # Execute (without mocking setup_pipeline_logging so it actually runs)
            exit_code = run_from_uploaded_file(
                tmp_pdf_path,
                'test-brand',
                run_id,
                selected_track=1
            )

            # Verify log file was created
            output_dir = Path(f"data/test-outputs/{run_id}")
            log_file = output_dir / "logs" / "pipeline.log"
            assert log_file.exists(), f"Log file should exist at {log_file}"
            assert log_file.is_file(), "Log path should be a file"

            # Verify log file has content
            assert log_file.stat().st_size > 0, "Log file should have content"

            # Cleanup
            shutil.rmtree(output_dir, ignore_errors=True)

    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

    print("✓ test_log_file_created passed")


def test_all_log_messages_present():
    """Test 3.2-INT-011: Verify all 10 log messages appear in pipeline.log (5 starts + 5 completions)."""

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf_path = tmp_pdf.name

    run_id = 'test-log-messages-001'

    try:
        with patch('scripts.run_pipeline.create_stage1_chain') as mock_stage1, \
             patch('scripts.run_pipeline.create_stage2_chain') as mock_stage2, \
             patch('scripts.run_pipeline.create_stage3_chain') as mock_stage3, \
             patch('scripts.run_pipeline.create_stage4_chain') as mock_stage4, \
             patch('scripts.run_pipeline.create_stage5_chain') as mock_stage5, \
             patch('scripts.run_pipeline.load_brand_profile') as mock_brand, \
             patch('scripts.run_pipeline.load_research_data') as mock_research, \
             patch('scripts.run_pipeline.PdfReader') as mock_pdf_reader, \
             patch('scripts.run_pipeline.validate_brand_id', return_value=True):

            # Mock PDF reader
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test PDF content"
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

            # Read log file
            output_dir = Path(f"data/test-outputs/{run_id}")
            log_file = output_dir / "logs" / "pipeline.log"
            log_content = log_file.read_text()

            # Verify all 5 "Starting Stage" messages
            for stage_num in range(1, 6):
                assert f"Starting Stage {stage_num}" in log_content, f"Should have 'Starting Stage {stage_num}' message"

            # Verify all 5 "Stage N execution completed" messages
            for stage_num in range(1, 6):
                assert f"Stage {stage_num} execution completed" in log_content, f"Should have 'Stage {stage_num} execution completed' message"

            # Count total log messages (should be at least 10)
            start_count = log_content.count("Starting Stage")
            stage_completion_count = sum(1 for stage_num in range(1, 6) if f"Stage {stage_num} execution completed" in log_content)
            assert start_count == 5, f"Should have 5 'Starting Stage' messages, got {start_count}"
            assert stage_completion_count == 5, f"Should have 5 stage completion messages, got {stage_completion_count}"

            # Cleanup
            shutil.rmtree(output_dir, ignore_errors=True)

    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

    print("✓ test_all_log_messages_present passed")


if __name__ == "__main__":
    print("Running Directory and Logging Integration Tests\n")

    test_output_directory_created_with_permissions()
    test_log_file_created()
    test_all_log_messages_present()

    print("\n✅ All directory and logging tests passed!")
