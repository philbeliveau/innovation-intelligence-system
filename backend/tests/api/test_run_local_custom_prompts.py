"""
Integration tests for /run/local endpoint with custom prompts

Tests custom prompt validation and integration with pipeline execution.
Part of Story 11.6.2: Backend Custom Prompt Integration.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient


# Mock the pipeline execution to avoid import issues and focus on validation
with patch('app.pipeline_runner.execute_pipeline_background'):
    from app.main import app

client = TestClient(app)


class TestRunLocalCustomPrompts:
    """Test suite for /run/local endpoint with custom_prompts parameter"""

    @pytest.fixture
    def valid_request_payload(self):
        """Base request payload with valid PDF text and brand profile"""
        return {
            "pdf_text": "Sample trend report text about Strategic Joy...",
            "brand_profile": {
                "brand_name": "Test Brand",
                "industry": "Food & Beverage",
                "portfolio": ["Product A", "Product B"]
            }
        }

    @pytest.fixture
    def valid_stage_4_custom_prompt(self):
        """Valid custom prompt for Stage 4 with all required placeholders"""
        return """
        Generate innovative concepts using:
        - Consumer Insights: {insights}
        - Matched SIT Techniques: {matched_techniques}
        - Brand Context: {brand_context}
        - No Hallucination Rules: {no_hallucination_rules}
        """

    def test_run_local_without_custom_prompts_success(self, valid_request_payload):
        """Test /run/local endpoint works without custom_prompts (backward compatible)"""
        response = client.post("/run/local", json=valid_request_payload)

        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "running"

    def test_run_local_with_valid_custom_prompt_success(
        self, valid_request_payload, valid_stage_4_custom_prompt
    ):
        """Test /run/local accepts valid custom prompt with all required placeholders"""
        payload = {
            **valid_request_payload,
            "custom_prompts": {
                "stage_4": valid_stage_4_custom_prompt
            }
        }

        response = client.post("/run/local", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "running"

    def test_run_local_invalid_custom_prompt_missing_placeholder(self, valid_request_payload):
        """Test /run/local returns 400 when custom prompt missing required placeholders"""
        invalid_prompt = "Generate concepts using {insights} only"  # Missing 3 placeholders

        payload = {
            **valid_request_payload,
            "custom_prompts": {
                "stage_4": invalid_prompt
            }
        }

        response = client.post("/run/local", json=payload)

        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        detail = error_data["detail"]
        assert "error" in detail
        assert "Invalid custom prompt for Stage 4" in detail["error"]
        assert "details" in detail
        assert "Missing required placeholders" in detail["details"]
        assert detail["stage"] == 4

    def test_run_local_multiple_custom_prompts_valid(self, valid_request_payload):
        """Test /run/local accepts multiple valid custom prompts"""
        payload = {
            **valid_request_payload,
            "custom_prompts": {
                "stage_0": "Enrich {company_name} in {industry} with portfolio: {portfolio}",
                "stage_1": "Extract trends from {report_text}",
                "stage_2": "Synthesize {trend_data} with {brand_context}"
            }
        }

        response = client.post("/run/local", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "running"

    def test_run_local_invalid_stage_key_format(self, valid_request_payload):
        """Test /run/local returns 400 for invalid stage key format"""
        payload = {
            **valid_request_payload,
            "custom_prompts": {
                "invalid_key": "Some prompt content"
            }
        }

        response = client.post("/run/local", json=payload)

        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        assert "Invalid stage key format" in error_data["detail"]

    def test_run_local_invalid_stage_number_out_of_range(self, valid_request_payload):
        """Test /run/local returns 400 for stage number outside 0-6 range"""
        payload = {
            **valid_request_payload,
            "custom_prompts": {
                "stage_10": "Invalid stage number prompt"
            }
        }

        response = client.post("/run/local", json=payload)

        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        assert "Invalid stage number" in error_data["detail"]
        assert "Must be between 0 and 6" in error_data["detail"]

    def test_run_local_custom_prompt_extra_placeholders_allowed(self, valid_request_payload):
        """Test /run/local allows extra (non-required) placeholders in custom prompts"""
        prompt_with_extras = """
        Extract trends from {report_text}
        Additional context: {custom_field}
        Extra instructions: {another_field}
        """

        payload = {
            **valid_request_payload,
            "custom_prompts": {
                "stage_1": prompt_with_extras
            }
        }

        response = client.post("/run/local", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data

    def test_run_local_custom_prompt_stage_0_all_placeholders(self, valid_request_payload):
        """Test Stage 0 validation requires company_name, industry, portfolio"""
        # Valid Stage 0 prompt
        valid_prompt = "Enrich {company_name} operating in {industry} with {portfolio}"
        payload = {
            **valid_request_payload,
            "custom_prompts": {"stage_0": valid_prompt}
        }
        response = client.post("/run/local", json=payload)
        assert response.status_code == 200

        # Invalid Stage 0 prompt (missing portfolio)
        invalid_prompt = "Enrich {company_name} in {industry}"
        payload = {
            **valid_request_payload,
            "custom_prompts": {"stage_0": invalid_prompt}
        }
        response = client.post("/run/local", json=payload)
        assert response.status_code == 400
        assert "portfolio" in response.json()["detail"]["details"]

    def test_run_local_custom_prompt_stage_1_report_text(self, valid_request_payload):
        """Test Stage 1 validation requires report_text placeholder"""
        # Valid Stage 1 prompt
        valid_prompt = "Extract trends from: {report_text}"
        payload = {
            **valid_request_payload,
            "custom_prompts": {"stage_1": valid_prompt}
        }
        response = client.post("/run/local", json=payload)
        assert response.status_code == 200

        # Invalid Stage 1 prompt (missing report_text)
        invalid_prompt = "Extract trends from report"
        payload = {
            **valid_request_payload,
            "custom_prompts": {"stage_1": invalid_prompt}
        }
        response = client.post("/run/local", json=payload)
        assert response.status_code == 400
        assert "report_text" in response.json()["detail"]["details"]

    def test_run_local_custom_prompt_stage_6_all_stage_outputs(self, valid_request_payload):
        """Test Stage 6 validation requires all_stage_outputs placeholder"""
        # Valid Stage 6 prompt
        valid_prompt = "Package results from {all_stage_outputs}"
        payload = {
            **valid_request_payload,
            "custom_prompts": {"stage_6": valid_prompt}
        }
        response = client.post("/run/local", json=payload)
        assert response.status_code == 200

        # Invalid Stage 6 prompt (missing all_stage_outputs)
        invalid_prompt = "Package results"
        payload = {
            **valid_request_payload,
            "custom_prompts": {"stage_6": invalid_prompt}
        }
        response = client.post("/run/local", json=payload)
        assert response.status_code == 400
        assert "all_stage_outputs" in response.json()["detail"]["details"]

    def test_run_local_empty_custom_prompts_dict_allowed(self, valid_request_payload):
        """Test /run/local accepts empty custom_prompts dict (treated as no custom prompts)"""
        payload = {
            **valid_request_payload,
            "custom_prompts": {}
        }

        response = client.post("/run/local", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data

    def test_run_local_validation_error_includes_stage_number(self, valid_request_payload):
        """Test validation error response includes stage number for debugging"""
        payload = {
            **valid_request_payload,
            "custom_prompts": {
                "stage_2": "Missing both placeholders"
            }
        }

        response = client.post("/run/local", json=payload)

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert error_detail["stage"] == 2
        assert "Stage 2" in error_detail["error"]
