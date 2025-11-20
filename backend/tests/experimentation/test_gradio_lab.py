"""
Tests for Gradio Experimentation Lab
Story 11.1: Gradio Experimentation UI

Tests cover:
- PDF upload and extraction
- Brand profile loading (YAML dropdown, file upload, manual entry)
- Pipeline execution workflow
- Quality tagging and database save
- Error handling scenarios
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import json
import yaml

# Import Gradio lab
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "experimentation"))
from gradio_lab import GradioLab


@pytest.fixture
def lab():
    """Create GradioLab instance for testing"""
    return GradioLab()


@pytest.fixture
def mock_pdf_file():
    """Mock PDF file object"""
    mock_file = Mock()
    mock_file.name = "/tmp/test_report.pdf"
    return mock_file


@pytest.fixture
def mock_yaml_file():
    """Mock YAML file object"""
    mock_file = Mock()
    mock_file.name = "/tmp/test_brand.yaml"
    return mock_file


@pytest.fixture
def sample_brand_profile():
    """Sample brand profile data"""
    return {
        "brand_name": "Test Brand",
        "country": "USA",
        "industry": "Food & Beverage",
        "product_portfolio": ["Product A", "Product B", "Product C"]
    }


class TestPDFExtraction:
    """Test PDF upload and text extraction"""

    def test_extract_valid_pdf(self, lab, mock_pdf_file, tmp_path):
        """Test successful PDF text extraction"""
        # Create temporary PDF with text
        pdf_path = tmp_path / "test.pdf"
        # Simplified: In real test, create actual PDF with PyPDF2
        pdf_path.write_text("Sample PDF content for testing" * 10)
        mock_pdf_file.name = str(pdf_path)

        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Sample trend report text" * 20
            mock_reader.return_value.pages = [mock_page] * 3

            text, status = lab.extract_pdf_text(mock_pdf_file)

            assert "Sample trend report text" in text
            assert "✅" in status
            assert "characters" in status

    def test_extract_pdf_file_too_large(self, lab, mock_pdf_file, tmp_path):
        """Test rejection of oversized PDF"""
        # Create file larger than 50MB
        large_file = tmp_path / "large.pdf"
        large_file.write_bytes(b"x" * (51 * 1024 * 1024))
        mock_pdf_file.name = str(large_file)

        text, status = lab.extract_pdf_text(mock_pdf_file)

        assert text == ""
        assert "❌" in status
        assert "too large" in status.lower()

    def test_extract_pdf_no_file(self, lab):
        """Test error when no file uploaded"""
        text, status = lab.extract_pdf_text(None)

        assert text == ""
        assert "⚠️" in status
        assert "No file" in status

    def test_extract_pdf_empty_content(self, lab, mock_pdf_file, tmp_path):
        """Test warning for PDF with minimal text"""
        pdf_path = tmp_path / "empty.pdf"
        pdf_path.write_bytes(b"x" * 1000)
        mock_pdf_file.name = str(pdf_path)

        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "   "  # Empty text
            mock_reader.return_value.pages = [mock_page]

            text, status = lab.extract_pdf_text(mock_pdf_file)

            assert "⚠️" in status
            assert "too short" in status.lower()


class TestBrandProfileLoading:
    """Test brand profile selection mechanisms"""

    def test_load_available_brands(self, lab):
        """Test loading list of available brand profiles"""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'glob') as mock_glob:
                # Mock YAML files
                mock_file = Mock()
                mock_file.stem = "test-brand"
                mock_glob.return_value = [mock_file]

                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = yaml.dump({
                        "brand_name": "Test Brand"
                    })

                    brands = lab.load_available_brands()

                    assert "Custom (Manual Entry)" in brands

    def test_load_brand_from_yaml(self, lab, sample_brand_profile):
        """Test loading brand profile from YAML dropdown"""
        with patch.object(Path, 'glob') as mock_glob:
            mock_file = Mock()
            mock_file.stem = "test-brand"
            mock_glob.return_value = [mock_file]

            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value = MagicMock()
                with patch('yaml.safe_load', return_value=sample_brand_profile):
                    name, industry, geo, portfolio = lab.load_brand_profile_from_yaml("Test Brand")

                    assert name == "Test Brand"
                    assert industry == "Food & Beverage"
                    assert geo == "USA"
                    assert "Product A" in portfolio

    def test_load_custom_brand_selection(self, lab):
        """Test selecting Custom manual entry option"""
        name, industry, geo, portfolio = lab.load_brand_profile_from_yaml("Custom (Manual Entry)")

        assert name == ""
        assert industry == ""
        assert geo == ""
        assert portfolio == ""

    def test_load_brand_from_uploaded_yaml(self, lab, mock_yaml_file, sample_brand_profile, tmp_path):
        """Test loading brand from uploaded YAML file"""
        yaml_path = tmp_path / "brand.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(sample_brand_profile, f)

        mock_yaml_file.name = str(yaml_path)

        name, industry, geo, portfolio, status = lab.load_brand_profile_from_file(mock_yaml_file)

        assert name == "Test Brand"
        assert "✅" in status

    def test_load_brand_yaml_missing_fields(self, lab, mock_yaml_file, tmp_path):
        """Test validation of uploaded YAML with missing required fields"""
        incomplete_profile = {"brand_name": "Test"}  # Missing country, industry, product_portfolio

        yaml_path = tmp_path / "incomplete.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(incomplete_profile, f)

        mock_yaml_file.name = str(yaml_path)

        name, industry, geo, portfolio, status = lab.load_brand_profile_from_file(mock_yaml_file)

        assert "⚠️" in status
        assert "Missing required fields" in status

    def test_load_brand_yaml_invalid_format(self, lab, mock_yaml_file, tmp_path):
        """Test error handling for malformed YAML"""
        yaml_path = tmp_path / "invalid.yaml"
        yaml_path.write_text("invalid: yaml: content:\n  - bad formatting")

        mock_yaml_file.name = str(yaml_path)

        name, industry, geo, portfolio, status = lab.load_brand_profile_from_file(mock_yaml_file)

        assert "❌" in status
        assert "Invalid YAML" in status or "Failed to load" in status


class TestPipelineExecution:
    """Test pipeline execution workflow"""

    @pytest.mark.asyncio
    async def test_run_pipeline_success(self, lab):
        """Test successful pipeline execution through all stages"""
        pdf_text = "Sample trend report text" * 100
        brand_name = "Test Brand"
        industry = "Food & Beverage"
        geography = "USA"
        portfolio = "Product A\nProduct B"

        # Mock backend API calls
        with patch.object(lab, '_call_backend_stage', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {"mock": "output"}

            results = await lab.run_pipeline(
                pdf_text, brand_name, industry, geography, portfolio
            )

            # Should return 8 values (7 stages + status)
            assert len(results) == 8
            assert "✅" in results[7]  # Status message
            assert "Pipeline complete" in results[7]

            # Verify all stages called
            assert mock_call.call_count == 7  # Stages 0-6

    @pytest.mark.asyncio
    async def test_run_pipeline_missing_pdf(self, lab):
        """Test pipeline failure when PDF not provided"""
        results = await lab.run_pipeline(
            "", "Brand", "Industry", "USA", "Products"
        )

        status = results[7]
        assert "❌" in status
        assert "valid PDF" in status

    @pytest.mark.asyncio
    async def test_run_pipeline_missing_brand_fields(self, lab):
        """Test pipeline failure when brand fields incomplete"""
        pdf_text = "Valid PDF text" * 50

        results = await lab.run_pipeline(
            pdf_text, "", "", "", ""
        )

        status = results[7]
        assert "❌" in status
        assert "required brand fields" in status

    @pytest.mark.asyncio
    async def test_run_pipeline_backend_failure(self, lab):
        """Test error handling when backend API fails"""
        pdf_text = "Sample text" * 100

        with patch.object(lab, '_call_backend_stage', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = Exception("API connection failed")

            results = await lab.run_pipeline(
                pdf_text, "Brand", "Industry", "USA", "Products"
            )

            status = results[7]
            assert "❌" in status
            assert "failed" in status.lower()

    @pytest.mark.asyncio
    async def test_call_backend_stage(self, lab):
        """Test backend API stage call"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"stage_output": "test"}

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            result = await lab._call_backend_stage(1, {"test": "data"})

            assert result == {"stage_output": "test"}

    @pytest.mark.asyncio
    async def test_call_backend_stage_error(self, lab):
        """Test backend stage call failure"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            with pytest.raises(Exception) as exc_info:
                await lab._call_backend_stage(1, {"test": "data"})

            assert "Stage 1 failed" in str(exc_info.value)


class TestQualityTagging:
    """Test quality tagging and experiment save"""

    @pytest.mark.asyncio
    async def test_save_experiment_success(self, lab):
        """Test successful experiment save"""
        run_id = "test-run-123"
        pdf_text = "Sample text"
        brand_profile = {"brand_name": "Test"}
        stage_outputs = {"stage_0": {}, "stage_1": {}}
        quality_tag = "Good"
        notes = "Test notes"

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            with patch.object(lab, '_export_few_shot_examples', new_callable=AsyncMock) as mock_export:
                status = await lab.save_experiment(
                    run_id, pdf_text, brand_profile, stage_outputs, quality_tag, notes
                )

                assert "✅" in status
                assert "few-shot" in status.lower()
                mock_export.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_experiment_needs_work(self, lab):
        """Test save without few-shot export for Needs Work tag"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            status = await lab.save_experiment(
                "run-123", "text", {}, {}, "Needs Work", "notes"
            )

            assert "✅" in status
            assert "few-shot" not in status.lower()

    @pytest.mark.asyncio
    async def test_save_experiment_failure(self, lab):
        """Test error handling when save fails"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Database error"

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            status = await lab.save_experiment(
                "run-123", "text", {}, {}, "Good", "notes"
            )

            assert "❌" in status

    @pytest.mark.asyncio
    async def test_export_few_shot_examples(self, lab, tmp_path):
        """Test few-shot example export"""
        run_id = "test-run-456"
        stage_outputs = {
            "stage_0": {"test": "data0"},
            "stage_1": {"test": "data1"},
            "stage_2": {"test": "data2"}
        }

        # Temporarily override examples directory
        examples_dir = tmp_path / "successful_examples"
        with patch.object(Path, '__truediv__', return_value=examples_dir):
            await lab._export_few_shot_examples(run_id, stage_outputs)

            # Verify files created
            assert (examples_dir / "stage_0" / f"{run_id}.json").exists()
            assert (examples_dir / "stage_1" / f"{run_id}.json").exists()


class TestErrorHandling:
    """Test error handling across all scenarios"""

    def test_pdf_extraction_corrupt_file(self, lab, mock_pdf_file, tmp_path):
        """Test handling of corrupt PDF file"""
        corrupt_file = tmp_path / "corrupt.pdf"
        corrupt_file.write_bytes(b"Not a valid PDF")
        mock_pdf_file.name = str(corrupt_file)

        with patch('PyPDF2.PdfReader', side_effect=Exception("Invalid PDF")):
            text, status = lab.extract_pdf_text(mock_pdf_file)

            assert text == ""
            assert "❌" in status

    def test_brand_profile_file_not_found(self, lab):
        """Test handling when brand profile YAML not found"""
        with patch.object(Path, 'glob', return_value=[]):
            name, industry, geo, portfolio = lab.load_brand_profile_from_yaml("Nonexistent Brand")

            # Should return empty fields
            assert name == ""

    @pytest.mark.asyncio
    async def test_pipeline_network_timeout(self, lab):
        """Test handling of network timeout during pipeline execution"""
        with patch.object(lab, '_call_backend_stage', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = asyncio.TimeoutError("Request timeout")

            results = await lab.run_pipeline(
                "text" * 100, "Brand", "Industry", "USA", "Products"
            )

            status = results[7]
            assert "❌" in status


class TestIntegration:
    """Integration tests for full workflows"""

    @pytest.mark.asyncio
    async def test_full_workflow_pdf_to_save(self, lab, tmp_path):
        """Test complete workflow: PDF upload → pipeline → save"""
        # 1. Extract PDF
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("Test content" * 100)
        mock_pdf = Mock()
        mock_pdf.name = str(pdf_path)

        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Trend report text" * 50
            mock_reader.return_value.pages = [mock_page]

            text, status = lab.extract_pdf_text(mock_pdf)
            assert "✅" in status

        # 2. Load brand profile
        brand_profile = {
            "brand_name": "Test Brand",
            "country": "USA",
            "industry": "CPG",
            "product_portfolio": ["Product A"]
        }

        yaml_path = tmp_path / "brand.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(brand_profile, f)

        mock_yaml = Mock()
        mock_yaml.name = str(yaml_path)

        name, industry, geo, portfolio, status = lab.load_brand_profile_from_file(mock_yaml)
        assert "✅" in status

        # 3. Run pipeline (mocked)
        with patch.object(lab, '_call_backend_stage', new_callable=AsyncMock) as mock_stage:
            mock_stage.return_value = {"mock": "output"}

            results = await lab.run_pipeline(text, name, industry, geo, portfolio)
            assert "✅" in results[7]

        # 4. Save experiment (mocked)
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            with patch.object(lab, '_export_few_shot_examples', new_callable=AsyncMock):
                save_status = await lab.save_experiment(
                    "run-123", text, brand_profile, {}, "Good", "Test"
                )
                assert "✅" in save_status


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
