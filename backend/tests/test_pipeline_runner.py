"""Unit Tests for Pipeline Runner

Tests for background pipeline execution logic.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime

from app.pipeline_runner import (
    extract_text_from_pdf,
    get_output_dir,
    initialize_status,
    update_stage_status,
    save_stage_output,
    transform_stage1_output,
    execute_pipeline_background
)


@pytest.mark.unit
class TestExtractTextFromPDF:
    """Tests for extract_text_from_pdf function"""

    @patch("app.pipeline_runner.PdfReader")
    def test_extract_text_success(self, mock_pdf_reader, tmp_path):
        """Test successful PDF text extraction"""
        # Setup mock
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test PDF content"
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        # Create temp PDF
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"fake pdf content")

        # Execute
        result = extract_text_from_pdf(str(pdf_path))

        # Verify
        assert result == "Test PDF content"
        mock_pdf_reader.assert_called_once_with(str(pdf_path))

    @patch("app.pipeline_runner.PdfReader")
    def test_extract_text_multiple_pages(self, mock_pdf_reader, tmp_path):
        """Test PDF extraction with multiple pages"""
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"

        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"fake pdf")

        result = extract_text_from_pdf(str(pdf_path))

        assert result == "Page 1 contentPage 2 content"

    @patch("app.pipeline_runner.PdfReader")
    def test_extract_text_pdf_error(self, mock_pdf_reader, tmp_path):
        """Test PDF extraction handles errors"""
        mock_pdf_reader.side_effect = Exception("Corrupted PDF")

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"fake pdf")

        with pytest.raises(Exception, match="Corrupted PDF"):
            extract_text_from_pdf(str(pdf_path))


@pytest.mark.unit
class TestGetOutputDir:
    """Tests for get_output_dir function"""

    def test_get_output_dir_creates_directory(self, sample_run_id):
        """Test output directory creation"""
        output_dir = get_output_dir(sample_run_id)

        assert output_dir.exists()
        assert output_dir.is_dir()
        assert str(output_dir) == f"/tmp/runs/{sample_run_id}"

        # Cleanup
        import shutil
        shutil.rmtree(output_dir.parent)

    def test_get_output_dir_idempotent(self, sample_run_id):
        """Test calling get_output_dir multiple times is safe"""
        output_dir1 = get_output_dir(sample_run_id)
        output_dir2 = get_output_dir(sample_run_id)

        assert output_dir1 == output_dir2
        assert output_dir1.exists()

        # Cleanup
        import shutil
        shutil.rmtree(output_dir1.parent)


@pytest.mark.unit
class TestInitializeStatus:
    """Tests for initialize_status function"""

    def test_initialize_status_creates_file(self, sample_run_id):
        """Test status.json file creation"""
        initialize_status(sample_run_id)

        status_file = Path("/tmp/runs") / sample_run_id / "status.json"
        assert status_file.exists()

        # Cleanup
        import shutil
        shutil.rmtree(status_file.parent.parent)

    def test_initialize_status_correct_structure(self, sample_run_id):
        """Test status.json has correct initial structure"""
        initialize_status(sample_run_id)

        status_file = Path("/tmp/runs") / sample_run_id / "status.json"
        with open(status_file, "r") as f:
            status = json.load(f)

        assert status["run_id"] == sample_run_id
        assert status["status"] == "running"
        assert status["current_stage"] == 1
        assert status["error"] is None

        # Check stages object
        assert isinstance(status["stages"], dict)
        for stage_num in ["1", "2", "3", "4", "5"]:
            assert stage_num in status["stages"]
            assert status["stages"][stage_num]["status"] == "pending"

        # Cleanup
        import shutil
        shutil.rmtree(status_file.parent.parent)


@pytest.mark.unit
class TestUpdateStageStatus:
    """Tests for update_stage_status function"""

    def test_update_stage_to_running(self, sample_run_id, temp_output_dir):
        """Test updating stage status to running"""
        initialize_status(sample_run_id)

        update_stage_status(sample_run_id, 1, "running")

        status_file = temp_output_dir / "status.json"
        with open(status_file, "r") as f:
            status = json.load(f)

        assert status["stages"]["1"]["status"] == "running"
        assert "started_at" in status["stages"]["1"]
        assert status["stages"]["1"]["started_at"].endswith("Z")

    def test_update_stage_to_complete(self, sample_run_id, temp_output_dir):
        """Test updating stage status to complete"""
        initialize_status(sample_run_id)

        output_data = {"result": "test output"}
        update_stage_status(sample_run_id, 1, "complete", output=output_data)

        status_file = temp_output_dir / "status.json"
        with open(status_file, "r") as f:
            status = json.load(f)

        assert status["stages"]["1"]["status"] == "complete"
        assert "completed_at" in status["stages"]["1"]
        assert status["stages"]["1"]["output"] == output_data

    def test_update_stage_to_failed(self, sample_run_id, temp_output_dir):
        """Test updating stage status to failed with error"""
        initialize_status(sample_run_id)

        error_msg = "LLM API timeout"
        update_stage_status(sample_run_id, 2, "failed", error=error_msg)

        status_file = temp_output_dir / "status.json"
        with open(status_file, "r") as f:
            status = json.load(f)

        assert status["stages"]["2"]["status"] == "failed"
        assert status["status"] == "failed"
        assert status["error"] == error_msg

    def test_update_final_stage_complete(self, sample_run_id, temp_output_dir):
        """Test completing final stage updates overall status"""
        initialize_status(sample_run_id)

        update_stage_status(sample_run_id, 5, "complete")

        status_file = temp_output_dir / "status.json"
        with open(status_file, "r") as f:
            status = json.load(f)

        assert status["stages"]["5"]["status"] == "complete"
        assert status["status"] == "complete"

    def test_update_current_stage_number(self, sample_run_id, temp_output_dir):
        """Test current_stage field updates correctly"""
        initialize_status(sample_run_id)

        update_stage_status(sample_run_id, 3, "running")

        status_file = temp_output_dir / "status.json"
        with open(status_file, "r") as f:
            status = json.load(f)

        assert status["current_stage"] == 3


@pytest.mark.unit
class TestSaveStageOutput:
    """Tests for save_stage_output function"""

    def test_save_stage_output_creates_file(self, sample_run_id, temp_output_dir):
        """Test stage output file creation"""
        output_data = {"key": "value", "result": [1, 2, 3]}

        save_stage_output(sample_run_id, 1, output_data)

        output_file = temp_output_dir / "stage_1_output.json"
        assert output_file.exists()

        with open(output_file, "r") as f:
            saved_data = json.load(f)

        assert saved_data == output_data

    def test_save_stage_output_all_stages(self, sample_run_id, temp_output_dir):
        """Test saving outputs for all 5 stages"""
        for stage_num in range(1, 6):
            output_data = {f"stage{stage_num}": "output"}
            save_stage_output(sample_run_id, stage_num, output_data)

            output_file = temp_output_dir / f"stage_{stage_num}_output.json"
            assert output_file.exists()


@pytest.mark.unit
class TestTransformStage1Output:
    """Tests for transform_stage1_output function"""

    def test_transform_with_two_inspirations(self, mock_stage1_output):
        """Test transformation with 2 inspirations"""
        result = transform_stage1_output(mock_stage1_output)

        assert "inspiration_1_title" in result
        assert "inspiration_1_content" in result
        assert "inspiration_2_title" in result
        assert "inspiration_2_content" in result

        assert result["inspiration_1_title"] == "Experience Theater"
        assert result["inspiration_2_title"] == "Community Building"

    def test_transform_with_one_inspiration(self):
        """Test transformation with only 1 inspiration"""
        stage1_output = {
            "inspirations": [
                {"title": "Single Inspiration", "content": "Content here"}
            ]
        }

        result = transform_stage1_output(stage1_output)

        assert "inspiration_1_title" in result
        assert "inspiration_1_content" in result
        assert "inspiration_2_title" not in result
        assert "inspiration_2_content" not in result

    def test_transform_with_no_inspirations(self):
        """Test transformation with no inspirations"""
        stage1_output = {"inspirations": []}

        result = transform_stage1_output(stage1_output)

        assert result == {}

    def test_transform_missing_inspirations_key(self):
        """Test transformation when inspirations key missing"""
        stage1_output = {"other_key": "value"}

        result = transform_stage1_output(stage1_output)

        assert result == {}


@pytest.mark.unit
class TestExecutePipelineBackground:
    """Tests for execute_pipeline_background function"""

    @patch("app.pipeline_runner.Stage5Chain")
    @patch("app.pipeline_runner.Stage4Chain")
    @patch("app.pipeline_runner.Stage3Chain")
    @patch("app.pipeline_runner.Stage2Chain")
    @patch("app.pipeline_runner.Stage1Chain")
    @patch("app.pipeline_runner.extract_text_from_pdf")
    @patch("app.pipeline_runner.load_research_data")
    def test_execute_pipeline_success(
        self,
        mock_load_research,
        mock_extract_text,
        mock_stage1_class,
        mock_stage2_class,
        mock_stage3_class,
        mock_stage4_class,
        mock_stage5_class,
        sample_run_id,
        sample_brand_profile,
        temp_output_dir,
        tmp_path
    ):
        """Test successful pipeline execution through all 5 stages"""
        # Setup mocks
        mock_extract_text.return_value = "Extracted PDF text"
        mock_load_research.return_value = "Research data"

        # Mock stage chains
        mock_stage1 = Mock()
        mock_stage1.run.return_value = {
            "inspirations": [
                {"title": "T1", "content": "C1"},
                {"title": "T2", "content": "C2"}
            ],
            "stage1_output": "Stage 1 output text"
        }
        mock_stage1_class.return_value = mock_stage1

        mock_stage2 = Mock()
        mock_stage2.run.return_value = {"stage2_output": "Stage 2 output text"}
        mock_stage2_class.return_value = mock_stage2

        mock_stage3 = Mock()
        mock_stage3.run.return_value = {"stage3_output": "Stage 3 output text"}
        mock_stage3_class.return_value = mock_stage3

        mock_stage4 = Mock()
        mock_stage4.run.return_value = {"stage4_output": "Stage 4 output text"}
        mock_stage4_class.return_value = mock_stage4

        mock_stage5 = Mock()
        mock_stage5.run.return_value = {"stage5_output": "Stage 5 output text"}
        mock_stage5_class.return_value = mock_stage5

        # Create temp PDF
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"fake pdf")

        # Execute
        execute_pipeline_background(sample_run_id, str(pdf_path), sample_brand_profile)

        # Verify all stages called
        mock_stage1.run.assert_called_once()
        mock_stage2.run.assert_called_once()
        mock_stage3.run.assert_called_once()
        mock_stage4.run.assert_called_once()
        mock_stage5.run.assert_called_once()

        # Verify status file shows complete
        status_file = temp_output_dir / "status.json"
        with open(status_file, "r") as f:
            status = json.load(f)

        assert status["status"] == "complete"
        assert status["current_stage"] == 5
        assert all(status["stages"][str(i)]["status"] == "complete" for i in range(1, 6))

    @patch("app.pipeline_runner.Stage1Chain")
    @patch("app.pipeline_runner.extract_text_from_pdf")
    def test_execute_pipeline_stage1_failure(
        self,
        mock_extract_text,
        mock_stage1_class,
        sample_run_id,
        sample_brand_profile,
        temp_output_dir,
        tmp_path
    ):
        """Test pipeline handles Stage 1 failure"""
        mock_extract_text.return_value = "Extracted text"

        # Mock Stage 1 to raise exception
        mock_stage1 = Mock()
        mock_stage1.run.side_effect = Exception("LLM API timeout")
        mock_stage1_class.return_value = mock_stage1

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"fake pdf")

        # Execute (should not raise)
        execute_pipeline_background(sample_run_id, str(pdf_path), sample_brand_profile)

        # Verify status shows failed
        status_file = temp_output_dir / "status.json"
        with open(status_file, "r") as f:
            status = json.load(f)

        assert status["status"] == "failed"
        assert "LLM API timeout" in status["error"]

    @patch("app.pipeline_runner.Stage3Chain")
    @patch("app.pipeline_runner.Stage2Chain")
    @patch("app.pipeline_runner.Stage1Chain")
    @patch("app.pipeline_runner.extract_text_from_pdf")
    def test_execute_pipeline_mid_stage_failure(
        self,
        mock_extract_text,
        mock_stage1_class,
        mock_stage2_class,
        mock_stage3_class,
        sample_run_id,
        sample_brand_profile,
        temp_output_dir,
        tmp_path
    ):
        """Test pipeline handles failure in middle stage"""
        mock_extract_text.return_value = "Extracted text"

        # Stages 1-2 succeed
        mock_stage1 = Mock()
        mock_stage1.run.return_value = {
            "inspirations": [{"title": "T", "content": "C"}],
            "stage1_output": "Output"
        }
        mock_stage1_class.return_value = mock_stage1

        mock_stage2 = Mock()
        mock_stage2.run.return_value = {"stage2_output": "Output"}
        mock_stage2_class.return_value = mock_stage2

        # Stage 3 fails
        mock_stage3 = Mock()
        mock_stage3.run.side_effect = Exception("Stage 3 error")
        mock_stage3_class.return_value = mock_stage3

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"fake pdf")

        execute_pipeline_background(sample_run_id, str(pdf_path), sample_brand_profile)

        # Verify stages 1-2 complete, stage 3 failed
        status_file = temp_output_dir / "status.json"
        with open(status_file, "r") as f:
            status = json.load(f)

        assert status["status"] == "failed"
        assert status["stages"]["1"]["status"] == "complete"
        assert status["stages"]["2"]["status"] == "complete"
        assert "Stage 3 error" in status["error"]

    @patch("app.pipeline_runner.Stage1Chain")
    @patch("app.pipeline_runner.extract_text_from_pdf")
    def test_execute_pipeline_pdf_cleanup(
        self,
        mock_extract_text,
        mock_stage1_class,
        sample_run_id,
        sample_brand_profile,
        temp_output_dir,
        tmp_path
    ):
        """Test PDF file is cleaned up after pipeline execution"""
        mock_extract_text.return_value = "Text"

        mock_stage1 = Mock()
        mock_stage1.run.return_value = {
            "inspirations": [],
            "stage1_output": "Output"
        }
        mock_stage1_class.return_value = mock_stage1

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"fake pdf")

        assert pdf_path.exists()

        execute_pipeline_background(sample_run_id, str(pdf_path), sample_brand_profile)

        # PDF should be deleted
        assert not pdf_path.exists()

    @patch("app.pipeline_runner.Stage1Chain")
    @patch("app.pipeline_runner.extract_text_from_pdf")
    def test_execute_pipeline_stage_output_files_created(
        self,
        mock_extract_text,
        mock_stage1_class,
        sample_run_id,
        sample_brand_profile,
        temp_output_dir,
        tmp_path
    ):
        """Test stage output files are created"""
        mock_extract_text.return_value = "Text"

        mock_stage1 = Mock()
        mock_stage1.run.return_value = {
            "inspirations": [{"title": "T", "content": "C"}],
            "stage1_output": "Output"
        }
        mock_stage1_class.return_value = mock_stage1

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"fake pdf")

        execute_pipeline_background(sample_run_id, str(pdf_path), sample_brand_profile)

        # Verify output file exists
        output_file = temp_output_dir / "stage_1_output.json"
        assert output_file.exists()
