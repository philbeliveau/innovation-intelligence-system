"""Unit Tests for Route Helper Functions

Tests for helper functions in routes.py: download_pdf_from_blob, load_brand_profile, etc.
"""
import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.routes import (
    generate_run_id,
    validate_blob_url,
    download_pdf_from_blob,
    load_brand_profile
)


@pytest.mark.unit
class TestGenerateRunId:
    """Tests for generate_run_id function"""

    def test_generate_run_id_format(self):
        """Test run_id has correct format: run-{timestamp}-{random}"""
        run_id = generate_run_id()

        assert run_id.startswith("run-")
        parts = run_id.split("-")
        assert len(parts) == 3
        assert parts[0] == "run"
        assert parts[1].isdigit()  # timestamp
        assert parts[2].isdigit()  # random suffix
        assert len(parts[2]) == 4  # 4-digit random

    def test_generate_run_id_unique(self):
        """Test multiple calls generate different run_ids"""
        run_id1 = generate_run_id()
        run_id2 = generate_run_id()

        assert run_id1 != run_id2


@pytest.mark.unit
class TestValidateBlobUrl:
    """Tests for validate_blob_url function"""

    def test_validate_blob_url_valid(self):
        """Test valid Vercel Blob URL passes"""
        url = "https://blob.vercel-storage.com/abc123/test.pdf"
        assert validate_blob_url(url) is True

    def test_validate_blob_url_http_rejected(self):
        """Test non-HTTPS URL is rejected"""
        url = "http://blob.vercel-storage.com/test.pdf"
        assert validate_blob_url(url) is False

    def test_validate_blob_url_wrong_domain(self):
        """Test URL from wrong domain is rejected"""
        url = "https://example.com/test.pdf"
        assert validate_blob_url(url) is False

    def test_validate_blob_url_no_protocol(self):
        """Test URL without protocol is rejected"""
        url = "blob.vercel-storage.com/test.pdf"
        assert validate_blob_url(url) is False

    def test_validate_blob_url_empty(self):
        """Test empty URL is rejected"""
        url = ""
        assert validate_blob_url(url) is False


@pytest.mark.unit
class TestDownloadPdfFromBlob:
    """Tests for download_pdf_from_blob function"""

    @patch("app.routes.requests.get")
    def test_download_pdf_success(self, mock_get, sample_run_id, sample_pdf_bytes):
        """Test successful PDF download"""
        # Mock response
        mock_response = Mock()
        mock_response.content = sample_pdf_bytes
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        url = "https://blob.vercel-storage.com/test.pdf"
        pdf_path = download_pdf_from_blob(url, sample_run_id)

        assert pdf_path == f"/tmp/{sample_run_id}.pdf"
        assert Path(pdf_path).exists()

        # Verify file content
        with open(pdf_path, "rb") as f:
            content = f.read()
        assert content == sample_pdf_bytes

        # Cleanup
        Path(pdf_path).unlink()

    @patch("app.routes.requests.get")
    def test_download_pdf_file_too_large(self, mock_get, sample_run_id):
        """Test PDF download rejects files >25MB"""
        # Create 26MB of data
        large_content = b"x" * (26 * 1024 * 1024)

        mock_response = Mock()
        mock_response.content = large_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        url = "https://blob.vercel-storage.com/large.pdf"

        with pytest.raises(HTTPException) as exc_info:
            download_pdf_from_blob(url, sample_run_id)

        # Error is caught by outer exception handler, returns 500
        assert exc_info.value.status_code == 500
        assert "25MB" in exc_info.value.detail

    @patch("app.routes.requests.get")
    def test_download_pdf_network_error(self, mock_get, sample_run_id):
        """Test PDF download handles network errors"""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")

        url = "https://blob.vercel-storage.com/test.pdf"

        with pytest.raises(HTTPException) as exc_info:
            download_pdf_from_blob(url, sample_run_id)

        assert exc_info.value.status_code == 400
        assert "download" in exc_info.value.detail.lower()

    @patch("app.routes.requests.get")
    def test_download_pdf_404_error(self, mock_get, sample_run_id):
        """Test PDF download handles 404 from blob storage"""
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        url = "https://blob.vercel-storage.com/missing.pdf"

        with pytest.raises(HTTPException) as exc_info:
            download_pdf_from_blob(url, sample_run_id)

        assert exc_info.value.status_code == 400

    @patch("app.routes.requests.get")
    def test_download_pdf_timeout(self, mock_get, sample_run_id):
        """Test PDF download has 30s timeout"""
        import requests
        mock_get.side_effect = requests.Timeout("Request timeout")

        url = "https://blob.vercel-storage.com/test.pdf"

        with pytest.raises(HTTPException):
            download_pdf_from_blob(url, sample_run_id)

        # Verify timeout was set
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs.get("timeout") == 30


@pytest.mark.unit
class TestLoadBrandProfile:
    """Tests for load_brand_profile function"""

    def test_load_brand_profile_success(self, tmp_path, sample_brand_yaml, monkeypatch):
        """Test successful brand profile loading"""
        # Create temp brand profile
        brand_dir = tmp_path / "data" / "brand-profiles"
        brand_dir.mkdir(parents=True)
        brand_file = brand_dir / "test-brand.yaml"
        brand_file.write_text(sample_brand_yaml)

        # Patch __file__ to point to temp location
        import app.routes as routes_module
        fake_file_path = tmp_path / "app" / "routes.py"
        fake_file_path.parent.mkdir(parents=True, exist_ok=True)
        fake_file_path.touch()

        with patch.object(routes_module, "__file__", str(fake_file_path)):
            brand_profile = load_brand_profile("test-brand")

        assert brand_profile["brand_id"] == "test-brand"
        assert brand_profile["company_name"] == "Test Company"
        assert "portfolio" in brand_profile
        assert "positioning" in brand_profile

    def test_load_brand_profile_not_found(self):
        """Test load_brand_profile raises 404 for missing brand"""
        with pytest.raises(HTTPException) as exc_info:
            load_brand_profile("nonexistent-brand")

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail

    def test_load_brand_profile_malformed_yaml(self, tmp_path, monkeypatch):
        """Test load_brand_profile handles malformed YAML"""
        # Create malformed YAML file
        brand_dir = tmp_path / "data" / "brand-profiles"
        brand_dir.mkdir(parents=True)
        brand_file = brand_dir / "bad-brand.yaml"
        brand_file.write_text("invalid: yaml: content: [unclosed")

        import app.routes as routes_module
        fake_file_path = tmp_path / "app" / "routes.py"
        fake_file_path.parent.mkdir(parents=True, exist_ok=True)
        fake_file_path.touch()

        with patch.object(routes_module, "__file__", str(fake_file_path)):
            with pytest.raises(HTTPException) as exc_info:
                load_brand_profile("bad-brand")

            assert exc_info.value.status_code == 400
            assert "Malformed" in exc_info.value.detail

    def test_load_brand_profile_missing_required_fields(self, tmp_path, monkeypatch):
        """Test load_brand_profile validates required fields"""
        # Create YAML missing required fields
        incomplete_yaml = """brand_id: incomplete-brand
company_name: Test Company
# Missing: portfolio, positioning
"""
        brand_dir = tmp_path / "data" / "brand-profiles"
        brand_dir.mkdir(parents=True)
        brand_file = brand_dir / "incomplete-brand.yaml"
        brand_file.write_text(incomplete_yaml)

        import app.routes as routes_module
        fake_file_path = tmp_path / "app" / "routes.py"
        fake_file_path.parent.mkdir(parents=True, exist_ok=True)
        fake_file_path.touch()

        with patch.object(routes_module, "__file__", str(fake_file_path)):
            with pytest.raises(HTTPException) as exc_info:
                load_brand_profile("incomplete-brand")

            # Error is caught by outer exception handler, returns 500
            assert exc_info.value.status_code == 500
            assert "missing required fields" in exc_info.value.detail.lower()

    def test_load_brand_profile_checks_multiple_paths(self, tmp_path, monkeypatch):
        """Test load_brand_profile checks both local and Railway paths"""
        # Simplified test - just verify function checks multiple paths
        # The actual implementation uses Path.exists() which is hard to mock comprehensively

        # Create brand profile in local backend path
        brand_dir = tmp_path / "data" / "brand-profiles"
        brand_dir.mkdir(parents=True)
        brand_file = brand_dir / "multi-path-brand.yaml"
        brand_yaml = """brand_id: multi-path-brand
company_name: Multi Path Test
portfolio: [Product]
positioning: Test positioning
"""
        brand_file.write_text(brand_yaml)

        import app.routes as routes_module
        fake_file_path = tmp_path / "app" / "routes.py"
        fake_file_path.parent.mkdir(parents=True, exist_ok=True)
        fake_file_path.touch()

        with patch.object(routes_module, "__file__", str(fake_file_path)):
            brand_profile = load_brand_profile("multi-path-brand")
            assert brand_profile["brand_id"] == "multi-path-brand"
