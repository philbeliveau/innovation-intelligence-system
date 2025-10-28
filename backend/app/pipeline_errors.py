"""Pipeline Error Codes and Standardized Error Handling

Defines standard error codes and error payload structure for pipeline failures.
"""

from enum import Enum
from typing import Dict, Any
from datetime import datetime


class PipelineErrorCode(str, Enum):
    """Standard pipeline error codes."""

    PDF_PARSE_ERROR = "PDF_PARSE_ERROR"
    LLM_RATE_LIMIT = "LLM_RATE_LIMIT"
    LLM_ERROR = "LLM_ERROR"
    WEBHOOK_FAILURE = "WEBHOOK_FAILURE"
    STAGE_EXECUTION_ERROR = "STAGE_EXECUTION_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    UNKNOWN = "UNKNOWN"


# User-friendly error messages
ERROR_MESSAGES: Dict[PipelineErrorCode, str] = {
    PipelineErrorCode.PDF_PARSE_ERROR: "Failed to extract text from the uploaded PDF. The file may be corrupted or password-protected.",
    PipelineErrorCode.LLM_RATE_LIMIT: "AI service rate limit reached. Please try again in a few minutes.",
    PipelineErrorCode.LLM_ERROR: "AI service encountered an error while processing your request.",
    PipelineErrorCode.WEBHOOK_FAILURE: "Failed to update pipeline status. Your results may have been saved but the interface may not reflect the latest state.",
    PipelineErrorCode.STAGE_EXECUTION_ERROR: "An error occurred while processing this pipeline stage.",
    PipelineErrorCode.DATABASE_ERROR: "Failed to save pipeline results to database.",
    PipelineErrorCode.UNKNOWN: "An unexpected error occurred during pipeline execution."
}


# Retry eligibility for each error type
CAN_RETRY: Dict[PipelineErrorCode, bool] = {
    PipelineErrorCode.PDF_PARSE_ERROR: False,  # Bad file, retrying won't help
    PipelineErrorCode.LLM_RATE_LIMIT: True,   # Temporary, can retry later
    PipelineErrorCode.LLM_ERROR: True,        # May be temporary
    PipelineErrorCode.WEBHOOK_FAILURE: True,  # Network issue, can retry
    PipelineErrorCode.STAGE_EXECUTION_ERROR: False,  # Logic error, won't fix itself
    PipelineErrorCode.DATABASE_ERROR: True,   # May be temporary connection issue
    PipelineErrorCode.UNKNOWN: False          # Don't know what went wrong
}


def create_error_payload(
    run_id: str,
    stage: int,
    error_code: PipelineErrorCode,
    error_message: str,
    exception: Exception | None = None
) -> Dict[str, Any]:
    """Create standardized error payload for pipeline failures.

    Args:
        run_id: Pipeline run identifier
        stage: Stage number where error occurred (1-5)
        error_code: Standardized error code
        error_message: Detailed error message
        exception: Original exception if available

    Returns:
        Standardized error dictionary
    """
    return {
        "runId": run_id,
        "status": "FAILED",
        "error": {
            "stage": stage,
            "code": error_code.value,
            "message": ERROR_MESSAGES.get(error_code, "An error occurred"),
            "details": error_message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "canRetry": CAN_RETRY.get(error_code, False),
            "exceptionType": type(exception).__name__ if exception else None
        }
    }


def classify_error(exception: Exception, stage: int = 0) -> PipelineErrorCode:
    """Classify an exception into a standard error code.

    Args:
        exception: The exception to classify
        stage: Stage number where error occurred (for context)

    Returns:
        Appropriate PipelineErrorCode
    """
    exception_str = str(exception).lower()
    exception_type = type(exception).__name__

    # PDF parsing errors
    if "pdf" in exception_str or exception_type in ["PdfReadError", "PyPdfError"]:
        return PipelineErrorCode.PDF_PARSE_ERROR

    # Rate limit errors
    if "rate limit" in exception_str or "429" in exception_str or "quota" in exception_str:
        return PipelineErrorCode.LLM_RATE_LIMIT

    # LLM/API errors
    if any(keyword in exception_str for keyword in ["openai", "anthropic", "llm", "api key", "openrouter"]):
        return PipelineErrorCode.LLM_ERROR

    # Webhook errors
    if "webhook" in exception_str or exception_type in ["ConnectionError", "Timeout"]:
        return PipelineErrorCode.WEBHOOK_FAILURE

    # Database errors
    if "prisma" in exception_str or "database" in exception_str or exception_type == "DatabaseError":
        return PipelineErrorCode.DATABASE_ERROR

    # Default to unknown
    return PipelineErrorCode.UNKNOWN
