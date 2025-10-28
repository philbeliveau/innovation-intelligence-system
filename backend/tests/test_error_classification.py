"""Error Classification and Standardization Tests

Tests for pipeline error handling, classification, and standardized error payloads.

References Story 8.0: Backend API Endpoints Prerequisites
- AC#7: Error State Payloads Standardized
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from app.pipeline_errors import (
    PipelineErrorCode,
    classify_error,
    create_error_payload,
    is_retryable_error,
)


@pytest.mark.unit
class TestErrorClassification:
    """Tests for error classification logic"""

    def test_classify_pdf_parse_error(self):
        """Test classification of PDF parsing errors"""
        error = Exception("Failed to extract text from PDF")
        code = classify_error(error, stage=1)
        assert code == PipelineErrorCode.PDF_PARSE_ERROR

        error = Exception("PDF file appears to be corrupted")
        code = classify_error(error, stage=1)
        assert code == PipelineErrorCode.PDF_PARSE_ERROR

        error = Exception("Unable to read PDF structure")
        code = classify_error(error, stage=1)
        assert code == PipelineErrorCode.PDF_PARSE_ERROR

    def test_classify_llm_rate_limit_error(self):
        """Test classification of LLM rate limit errors"""
        error = Exception("Rate limit exceeded for model")
        code = classify_error(error, stage=2)
        assert code == PipelineErrorCode.LLM_RATE_LIMIT

        error = Exception("429 Too Many Requests")
        code = classify_error(error, stage=3)
        assert code == PipelineErrorCode.LLM_RATE_LIMIT

        error = Exception("rate_limit_error: You have exceeded your quota")
        code = classify_error(error, stage=4)
        assert code == PipelineErrorCode.LLM_RATE_LIMIT

    def test_classify_llm_api_error(self):
        """Test classification of LLM API errors"""
        error = Exception("OpenRouter API returned 500 error")
        code = classify_error(error, stage=2)
        assert code == PipelineErrorCode.LLM_ERROR

        error = Exception("Failed to connect to LLM service")
        code = classify_error(error, stage=3)
        assert code == PipelineErrorCode.LLM_ERROR

        error = Exception("LLM returned invalid JSON response")
        code = classify_error(error, stage=4)
        assert code == PipelineErrorCode.LLM_ERROR

    def test_classify_webhook_failure(self):
        """Test classification of webhook delivery failures"""
        error = Exception("Failed to deliver webhook")
        code = classify_error(error, stage=5)
        assert code == PipelineErrorCode.WEBHOOK_FAILURE

        error = Exception("Webhook endpoint returned 500")
        code = classify_error(error, stage=3)
        assert code == PipelineErrorCode.WEBHOOK_FAILURE

        error = Exception("Connection refused to webhook URL")
        code = classify_error(error, stage=2)
        assert code == PipelineErrorCode.WEBHOOK_FAILURE

    def test_classify_database_error(self):
        """Test classification of database errors"""
        error = Exception("Database connection timeout")
        code = classify_error(error, stage=5)
        assert code == PipelineErrorCode.DATABASE_ERROR

        error = Exception("Prisma query failed")
        code = classify_error(error, stage=4)
        assert code == PipelineErrorCode.DATABASE_ERROR

        error = Exception("Failed to save opportunity to database")
        code = classify_error(error, stage=5)
        assert code == PipelineErrorCode.DATABASE_ERROR

    def test_classify_timeout_error(self):
        """Test classification of timeout errors"""
        error = Exception("Operation timed out after 300 seconds")
        code = classify_error(error, stage=3)
        assert code == PipelineErrorCode.TIMEOUT_ERROR

        error = Exception("Request timeout: exceeded 120s limit")
        code = classify_error(error, stage=2)
        assert code == PipelineErrorCode.TIMEOUT_ERROR

    def test_classify_unknown_error(self):
        """Test classification of unknown/unhandled errors"""
        error = Exception("Something completely unexpected happened")
        code = classify_error(error, stage=3)
        assert code == PipelineErrorCode.UNKNOWN

        error = Exception("NoneType object has no attribute 'get'")
        code = classify_error(error, stage=4)
        assert code == PipelineErrorCode.UNKNOWN


@pytest.mark.unit
class TestErrorPayloadCreation:
    """Tests for standardized error payload creation"""

    def test_create_error_payload_structure(self):
        """Test error payload has all required fields"""
        error = Exception("Test error")
        payload = create_error_payload(
            error=error,
            stage=3,
            run_id="run-123"
        )

        # Verify required fields
        assert "runId" in payload
        assert "status" in payload
        assert "error" in payload

        # Verify error object structure
        error_obj = payload["error"]
        assert "stage" in error_obj
        assert "code" in error_obj
        assert "message" in error_obj
        assert "timestamp" in error_obj
        assert "canRetry" in error_obj

        # Verify values
        assert payload["runId"] == "run-123"
        assert payload["status"] == "FAILED"
        assert error_obj["stage"] == 3

    def test_create_error_payload_pdf_parse_error(self):
        """Test error payload for PDF parse errors"""
        error = Exception("Failed to extract text from PDF")
        payload = create_error_payload(
            error=error,
            stage=1,
            run_id="run-pdf-error"
        )

        error_obj = payload["error"]
        assert error_obj["code"] == "PDF_PARSE_ERROR"
        assert error_obj["stage"] == 1
        assert "PDF" in error_obj["message"] or "parse" in error_obj["message"].lower()
        assert error_obj["canRetry"] is False  # PDF errors usually not retryable

    def test_create_error_payload_rate_limit(self):
        """Test error payload for rate limit errors"""
        error = Exception("Rate limit exceeded")
        payload = create_error_payload(
            error=error,
            stage=3,
            run_id="run-rate-limit"
        )

        error_obj = payload["error"]
        assert error_obj["code"] == "LLM_RATE_LIMIT"
        assert error_obj["stage"] == 3
        assert "rate limit" in error_obj["message"].lower()
        assert error_obj["canRetry"] is True  # Rate limits are retryable

    def test_create_error_payload_llm_error(self):
        """Test error payload for LLM API errors"""
        error = Exception("LLM API returned 500 error")
        payload = create_error_payload(
            error=error,
            stage=4,
            run_id="run-llm-error"
        )

        error_obj = payload["error"]
        assert error_obj["code"] == "LLM_ERROR"
        assert error_obj["stage"] == 4
        assert "LLM" in error_obj["message"] or "API" in error_obj["message"]
        assert error_obj["canRetry"] is True  # Transient API errors can be retried

    def test_create_error_payload_webhook_failure(self):
        """Test error payload for webhook failures"""
        error = Exception("Failed to deliver webhook")
        payload = create_error_payload(
            error=error,
            stage=5,
            run_id="run-webhook-fail"
        )

        error_obj = payload["error"]
        assert error_obj["code"] == "WEBHOOK_FAILURE"
        assert error_obj["stage"] == 5
        assert "webhook" in error_obj["message"].lower()
        assert error_obj["canRetry"] is True  # Webhook failures are retryable

    def test_create_error_payload_timestamp_format(self):
        """Test error payload timestamp is ISO 8601 format"""
        error = Exception("Test error")
        payload = create_error_payload(
            error=error,
            stage=2,
            run_id="run-timestamp"
        )

        timestamp = payload["error"]["timestamp"]

        # Verify it's a valid ISO 8601 timestamp
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            valid_timestamp = True
        except ValueError:
            valid_timestamp = False

        assert valid_timestamp is True
        assert timestamp.endswith('Z')  # Should be UTC

    def test_create_error_payload_database_error(self):
        """Test error payload for database errors"""
        error = Exception("Database connection failed")
        payload = create_error_payload(
            error=error,
            stage=5,
            run_id="run-db-error"
        )

        error_obj = payload["error"]
        assert error_obj["code"] == "DATABASE_ERROR"
        assert error_obj["stage"] == 5
        assert "database" in error_obj["message"].lower()
        assert error_obj["canRetry"] is True

    def test_create_error_payload_timeout_error(self):
        """Test error payload for timeout errors"""
        error = Exception("Operation timed out")
        payload = create_error_payload(
            error=error,
            stage=3,
            run_id="run-timeout"
        )

        error_obj = payload["error"]
        assert error_obj["code"] == "TIMEOUT_ERROR"
        assert error_obj["stage"] == 3
        assert "timeout" in error_obj["message"].lower() or "timed out" in error_obj["message"].lower()
        assert error_obj["canRetry"] is True


@pytest.mark.unit
class TestRetryableErrors:
    """Tests for retry eligibility logic"""

    def test_rate_limit_is_retryable(self):
        """Test rate limit errors are retryable"""
        assert is_retryable_error(PipelineErrorCode.LLM_RATE_LIMIT) is True

    def test_llm_error_is_retryable(self):
        """Test LLM errors are retryable"""
        assert is_retryable_error(PipelineErrorCode.LLM_ERROR) is True

    def test_webhook_failure_is_retryable(self):
        """Test webhook failures are retryable"""
        assert is_retryable_error(PipelineErrorCode.WEBHOOK_FAILURE) is True

    def test_database_error_is_retryable(self):
        """Test database errors are retryable"""
        assert is_retryable_error(PipelineErrorCode.DATABASE_ERROR) is True

    def test_timeout_error_is_retryable(self):
        """Test timeout errors are retryable"""
        assert is_retryable_error(PipelineErrorCode.TIMEOUT_ERROR) is True

    def test_pdf_parse_error_not_retryable(self):
        """Test PDF parse errors are not retryable"""
        assert is_retryable_error(PipelineErrorCode.PDF_PARSE_ERROR) is False

    def test_unknown_error_not_retryable(self):
        """Test unknown errors are not retryable by default"""
        assert is_retryable_error(PipelineErrorCode.UNKNOWN) is False


@pytest.mark.integration
class TestErrorPayloadIntegration:
    """Integration tests for error payloads in pipeline"""

    def test_error_payload_matches_status_endpoint_schema(self):
        """Test error payload matches expected schema from status endpoint"""
        error = Exception("Test error")
        payload = create_error_payload(
            error=error,
            stage=3,
            run_id="run-123"
        )

        # Verify top-level structure matches status endpoint
        assert payload["runId"] == "run-123"
        assert payload["status"] == "FAILED"
        assert isinstance(payload["error"], dict)

        # Verify nested error structure
        error_obj = payload["error"]
        required_fields = ["stage", "code", "message", "timestamp", "canRetry"]
        for field in required_fields:
            assert field in error_obj, f"Missing required field: {field}"

    def test_multiple_error_scenarios_end_to_end(self):
        """Test creating error payloads for all error types"""
        test_cases = [
            (Exception("PDF parse failed"), 1, "PDF_PARSE_ERROR", False),
            (Exception("Rate limit exceeded"), 2, "LLM_RATE_LIMIT", True),
            (Exception("LLM API error"), 3, "LLM_ERROR", True),
            (Exception("Webhook failed"), 4, "WEBHOOK_FAILURE", True),
            (Exception("Database error"), 5, "DATABASE_ERROR", True),
            (Exception("Timeout"), 3, "TIMEOUT_ERROR", True),
            (Exception("Unknown error"), 2, "UNKNOWN", False),
        ]

        for error, stage, expected_code, expected_retry in test_cases:
            payload = create_error_payload(
                error=error,
                stage=stage,
                run_id=f"run-{expected_code}"
            )

            error_obj = payload["error"]
            assert error_obj["code"] == expected_code
            assert error_obj["canRetry"] == expected_retry
            assert error_obj["stage"] == stage
            assert len(error_obj["message"]) > 0
            assert error_obj["timestamp"].endswith('Z')


@pytest.mark.unit
class TestErrorCodeEnum:
    """Tests for PipelineErrorCode enum"""

    def test_all_error_codes_defined(self):
        """Test all expected error codes are defined"""
        expected_codes = [
            "PDF_PARSE_ERROR",
            "LLM_RATE_LIMIT",
            "LLM_ERROR",
            "WEBHOOK_FAILURE",
            "DATABASE_ERROR",
            "TIMEOUT_ERROR",
            "UNKNOWN",
        ]

        for code in expected_codes:
            assert hasattr(PipelineErrorCode, code)
            assert getattr(PipelineErrorCode, code) == code

    def test_error_code_values_are_strings(self):
        """Test all error code values are strings"""
        for attr_name in dir(PipelineErrorCode):
            if not attr_name.startswith('_'):
                attr_value = getattr(PipelineErrorCode, attr_name)
                if not callable(attr_value):
                    assert isinstance(attr_value, str)


@pytest.mark.unit
class TestErrorMessageGeneration:
    """Tests for user-friendly error message generation"""

    def test_error_messages_are_user_friendly(self):
        """Test error messages don't leak technical details"""
        test_errors = [
            (Exception("NoneType object has no attribute 'get'"), "An unexpected error occurred"),
            (Exception("list index out of range"), "An unexpected error occurred"),
            (Exception("KeyError: 'missing_key'"), "An unexpected error occurred"),
        ]

        for error, expected_message_hint in test_errors:
            payload = create_error_payload(
                error=error,
                stage=3,
                run_id="run-test"
            )

            message = payload["error"]["message"]

            # Should not expose raw Python errors
            assert "NoneType" not in message
            assert "KeyError" not in message
            assert "list index" not in message

    def test_rate_limit_message_includes_guidance(self):
        """Test rate limit messages provide user guidance"""
        error = Exception("Rate limit exceeded")
        payload = create_error_payload(
            error=error,
            stage=2,
            run_id="run-rate"
        )

        message = payload["error"]["message"].lower()

        # Should include helpful guidance
        assert "rate limit" in message or "try again" in message or "later" in message

    def test_pdf_error_message_actionable(self):
        """Test PDF error messages are actionable"""
        error = Exception("Failed to parse PDF")
        payload = create_error_payload(
            error=error,
            stage=1,
            run_id="run-pdf"
        )

        message = payload["error"]["message"].lower()

        # Should suggest what to do
        assert "pdf" in message or "document" in message or "file" in message


@pytest.mark.unit
class TestErrorClassificationEdgeCases:
    """Tests for edge cases in error classification"""

    def test_classify_error_with_no_stage(self):
        """Test classification works without stage number"""
        error = Exception("Some error")
        code = classify_error(error, stage=None)
        assert code == PipelineErrorCode.UNKNOWN

    def test_classify_error_with_nested_exception(self):
        """Test classification with exception chaining"""
        try:
            raise ValueError("Inner error")
        except ValueError as inner:
            outer = Exception(f"Outer error: {inner}")
            code = classify_error(outer, stage=2)
            # Should still classify based on message content
            assert code in [
                PipelineErrorCode.UNKNOWN,
                PipelineErrorCode.LLM_ERROR,
            ]

    def test_classify_error_case_insensitive(self):
        """Test classification is case-insensitive"""
        test_cases = [
            "RATE LIMIT EXCEEDED",
            "rate limit exceeded",
            "Rate Limit Exceeded",
        ]

        for error_msg in test_cases:
            error = Exception(error_msg)
            code = classify_error(error, stage=2)
            assert code == PipelineErrorCode.LLM_RATE_LIMIT

    def test_classify_error_with_multiple_keywords(self):
        """Test classification when multiple error types match"""
        # "webhook" + "rate limit" - should prioritize more specific
        error = Exception("Webhook delivery failed due to rate limit")
        code = classify_error(error, stage=5)
        # Should match webhook failure (more specific to stage 5)
        assert code == PipelineErrorCode.WEBHOOK_FAILURE
