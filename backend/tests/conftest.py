"""Pytest configuration and shared fixtures"""
import os
import json
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up required environment variables for testing"""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    monkeypatch.setenv("LLM_MODEL", "anthropic/claude-sonnet-4.5")
    monkeypatch.setenv("VERCEL_BLOB_READ_WRITE_TOKEN", "test-blob-token")


@pytest.fixture
def client(mock_env_vars) -> TestClient:
    """Create FastAPI test client with mocked environment"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def sample_run_id() -> str:
    """Generate a sample run ID for testing"""
    return "run-1234567890-1234"


@pytest.fixture
def temp_output_dir(sample_run_id) -> Generator[Path, None, None]:
    """Create temporary output directory for run artifacts"""
    output_dir = Path("/tmp/runs") / sample_run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    yield output_dir

    # Cleanup
    import shutil
    if output_dir.exists():
        shutil.rmtree(output_dir.parent)


@pytest.fixture
def sample_status_json(sample_run_id) -> Dict[str, Any]:
    """Sample status.json structure matching API schema"""
    return {
        "run_id": sample_run_id,
        "status": "running",
        "current_stage": 2,
        "stages": {
            "1": {
                "status": "complete",
                "started_at": "2025-01-15T14:20:30Z",
                "completed_at": "2025-01-15T14:24:15Z",
                "output": {
                    "inspiration_1_title": "Experience Theater",
                    "inspiration_1_content": "The Savannah Bananas have transformed...",
                    "inspiration_2_title": "Community Building",
                    "inspiration_2_content": "Creating a sense of belonging..."
                }
            },
            "2": {
                "status": "running",
                "started_at": "2025-01-15T14:24:16Z"
            },
            "3": {"status": "pending"},
            "4": {"status": "pending"},
            "5": {"status": "pending"}
        },
        "error": None
    }


@pytest.fixture
def sample_brand_profile() -> Dict[str, Any]:
    """Sample brand profile for testing"""
    return {
        "brand_id": "test-brand",
        "company_name": "Test Company",
        "portfolio": ["Product A", "Product B"],
        "positioning": "Premium test products",
        "target_audience": "Test consumers",
        "capabilities": ["Manufacturing", "Distribution"]
    }


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Sample PDF file content (minimal valid PDF)"""
    # Minimal valid PDF structure
    return b"""%PDF-1.4
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
(Test PDF Content) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000214 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
308
%%EOF
"""


@pytest.fixture
def sample_brand_yaml() -> str:
    """Sample brand profile YAML content"""
    return """brand_id: test-brand
company_name: Test Company
portfolio:
  - Product A
  - Product B
positioning: Premium test products
target_audience: Test consumers
capabilities:
  - Manufacturing
  - Distribution
"""


@pytest.fixture
def temp_brand_profile_file(tmp_path, sample_brand_yaml) -> Path:
    """Create temporary brand profile YAML file"""
    brand_dir = tmp_path / "data" / "brand-profiles"
    brand_dir.mkdir(parents=True)

    brand_file = brand_dir / "test-brand.yaml"
    brand_file.write_text(sample_brand_yaml)

    return brand_file


@pytest.fixture
def mock_stage1_output() -> Dict[str, Any]:
    """Sample Stage 1 pipeline output"""
    return {
        "inspirations": [
            {
                "title": "Experience Theater",
                "content": "The Savannah Bananas have transformed baseball into entertainment"
            },
            {
                "title": "Community Building",
                "content": "Creating a sense of belonging through shared experiences"
            }
        ],
        "stage1_output": "Detailed analysis of innovation patterns..."
    }


@pytest.fixture
def mock_stage_output() -> Dict[str, Any]:
    """Generic stage output for testing"""
    return {
        "stage2_output": "Amplified signals and trends...",
        "insights": ["Insight 1", "Insight 2"]
    }
