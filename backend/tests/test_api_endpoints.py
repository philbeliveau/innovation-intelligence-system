"""API Endpoint Tests for /run and /status

Tests for POST /run and GET /status/{run_id} endpoints.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException


@pytest.mark.api
class TestHealthEndpoint:
    """Tests for GET /health endpoint"""

    def test_health_check_ok(self, client, mock_env_vars):
        """Test health check returns ok when all env vars present"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"

    def test_health_check_degraded(self, client, monkeypatch):
        """Test health check returns degraded when env vars missing"""
        # Remove one required env var
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"


@pytest.mark.api
class TestRunEndpoint:
    """Tests for POST /run endpoint"""

    @patch("app.routes.Thread")
    @patch("app.routes.download_pdf_from_blob")
    @patch("app.routes.load_brand_profile")
    def test_run_pipeline_success(
        self,
        mock_load_brand,
        mock_download,
        mock_thread,
        client,
        sample_brand_profile
    ):
        """Test POST /run with valid inputs returns run_id and status"""
        # Setup mocks
        mock_download.return_value = "/tmp/test.pdf"
        mock_load_brand.return_value = sample_brand_profile

        # Make request
        response = client.post("/run", json={
            "blob_url": "https://blob.vercel-storage.com/test.pdf",
            "brand_id": "test-brand"
        })

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert data["run_id"].startswith("run-")
        assert data["status"] == "running"

        # Verify thread started
        mock_thread.assert_called_once()
        thread_instance = mock_thread.return_value
        thread_instance.start.assert_called_once()

    def test_run_pipeline_invalid_blob_url(self, client):
        """Test POST /run with invalid blob URL returns 400"""
        response = client.post("/run", json={
            "blob_url": "http://example.com/test.pdf",
            "brand_id": "test-brand"
        })

        assert response.status_code == 400
        assert "Invalid blob URL" in response.json()["detail"]

    def test_run_pipeline_non_https(self, client):
        """Test POST /run with non-HTTPS URL returns 400"""
        response = client.post("/run", json={
            "blob_url": "http://blob.vercel-storage.com/test.pdf",
            "brand_id": "test-brand"
        })

        assert response.status_code == 400

    @patch("app.routes.download_pdf_from_blob")
    @patch("app.routes.load_brand_profile")
    def test_run_pipeline_missing_brand(
        self,
        mock_load_brand,
        mock_download,
        client
    ):
        """Test POST /run with missing brand profile returns 404"""
        mock_download.return_value = "/tmp/test.pdf"
        mock_load_brand.side_effect = HTTPException(
            status_code=404,
            detail="Brand 'missing-brand' not found"
        )

        response = client.post("/run", json={
            "blob_url": "https://blob.vercel-storage.com/test.pdf",
            "brand_id": "missing-brand"
        })

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch("app.routes.download_pdf_from_blob")
    def test_run_pipeline_download_failure(self, mock_download, client):
        """Test POST /run with blob download failure returns 400"""
        mock_download.side_effect = HTTPException(
            status_code=400,
            detail="Failed to download PDF from Vercel Blob"
        )

        response = client.post("/run", json={
            "blob_url": "https://blob.vercel-storage.com/test.pdf",
            "brand_id": "test-brand"
        })

        assert response.status_code == 400
        assert "download" in response.json()["detail"].lower()

    def test_run_pipeline_missing_fields(self, client):
        """Test POST /run with missing required fields returns 422"""
        # Missing brand_id
        response = client.post("/run", json={
            "blob_url": "https://blob.vercel-storage.com/test.pdf"
        })

        assert response.status_code == 422


@pytest.mark.api
class TestStatusEndpoint:
    """Tests for GET /status/{run_id} endpoint"""

    def test_get_status_success(
        self,
        client,
        sample_run_id,
        temp_output_dir,
        sample_status_json
    ):
        """Test GET /status with valid run_id returns status"""
        # Create status file
        status_file = temp_output_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(sample_status_json, f)

        response = client.get(f"/status/{sample_run_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["run_id"] == sample_run_id
        assert data["status"] == "running"
        assert data["current_stage"] == 2
        assert "stages" in data
        assert isinstance(data["stages"], dict)

    def test_get_status_with_stage1_output(
        self,
        client,
        sample_run_id,
        temp_output_dir,
        sample_status_json
    ):
        """Test GET /status includes Stage 1 track data in output"""
        status_file = temp_output_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(sample_status_json, f)

        response = client.get(f"/status/{sample_run_id}")

        assert response.status_code == 200
        data = response.json()

        # Verify Stage 1 output format
        stage1 = data["stages"]["1"]
        assert stage1["status"] == "complete"
        assert "output" in stage1
        assert "inspiration_1_title" in stage1["output"]
        assert "inspiration_1_content" in stage1["output"]
        assert stage1["output"]["inspiration_1_title"] == "Experience Theater"

    def test_get_status_run_not_found(self, client):
        """Test GET /status with non-existent run_id returns 404"""
        response = client.get("/status/run-nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_status_corrupted_file(
        self,
        client,
        sample_run_id,
        temp_output_dir
    ):
        """Test GET /status with corrupted status.json returns 500"""
        # Create corrupted JSON file
        status_file = temp_output_dir / "status.json"
        with open(status_file, "w") as f:
            f.write("{invalid json content")

        response = client.get(f"/status/{sample_run_id}")

        assert response.status_code == 500
        assert "corrupted" in response.json()["detail"].lower()

    def test_get_status_complete_pipeline(
        self,
        client,
        sample_run_id,
        temp_output_dir
    ):
        """Test GET /status with completed pipeline"""
        status_data = {
            "run_id": sample_run_id,
            "status": "complete",
            "current_stage": 5,
            "stages": {
                "1": {"status": "complete", "output": {}},
                "2": {"status": "complete"},
                "3": {"status": "complete"},
                "4": {"status": "complete"},
                "5": {"status": "complete"}
            },
            "error": None
        }

        status_file = temp_output_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(status_data, f)

        response = client.get(f"/status/{sample_run_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"
        assert data["current_stage"] == 5

    def test_get_status_failed_pipeline(
        self,
        client,
        sample_run_id,
        temp_output_dir
    ):
        """Test GET /status with failed pipeline includes error"""
        status_data = {
            "run_id": sample_run_id,
            "status": "failed",
            "current_stage": 3,
            "stages": {
                "1": {"status": "complete"},
                "2": {"status": "complete"},
                "3": {"status": "failed"},
                "4": {"status": "pending"},
                "5": {"status": "pending"}
            },
            "error": "LLM API timeout"
        }

        status_file = temp_output_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(status_data, f)

        response = client.get(f"/status/{sample_run_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error"] == "LLM API timeout"


@pytest.mark.api
class TestStatusSchemaCompliance:
    """Tests verifying status response matches 6-api-design.md schema"""

    def test_stages_is_object_not_array(
        self,
        client,
        sample_run_id,
        temp_output_dir,
        sample_status_json
    ):
        """Verify stages field is object keyed by stage number, not array"""
        status_file = temp_output_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(sample_status_json, f)

        response = client.get(f"/status/{sample_run_id}")
        data = response.json()

        # Must be dict, not list
        assert isinstance(data["stages"], dict)
        assert "1" in data["stages"]
        assert "2" in data["stages"]
        assert not isinstance(data["stages"], list)

    def test_status_values_correct(
        self,
        client,
        sample_run_id,
        temp_output_dir,
        sample_status_json
    ):
        """Verify status values use correct enum: pending/running/complete/failed"""
        status_file = temp_output_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(sample_status_json, f)

        response = client.get(f"/status/{sample_run_id}")
        data = response.json()

        # Check overall status
        assert data["status"] in ["running", "complete", "failed"]

        # Check stage statuses
        for stage_key, stage_info in data["stages"].items():
            assert stage_info["status"] in ["pending", "running", "complete", "failed"]

    def test_stage1_output_format(
        self,
        client,
        sample_run_id,
        temp_output_dir,
        sample_status_json
    ):
        """Verify Stage 1 output uses inspiration_N_title/content format"""
        status_file = temp_output_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(sample_status_json, f)

        response = client.get(f"/status/{sample_run_id}")
        data = response.json()

        stage1_output = data["stages"]["1"]["output"]

        # Must have inspiration_1_title and inspiration_1_content
        assert "inspiration_1_title" in stage1_output
        assert "inspiration_1_content" in stage1_output

        # Should NOT have track_id or description
        assert "track_id" not in stage1_output
        assert "description" not in stage1_output
