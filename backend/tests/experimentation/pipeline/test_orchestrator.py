"""Tests for Pipeline Orchestrator"""
import pytest
import json
from unittest.mock import AsyncMock, Mock
from backend.experimentation.pipeline_orchestrator import PipelineOrchestrator
from backend.experimentation.schemas import (
    Stage0Output,
    Stage1Output,
    Stage2Output,
    BrandEnrichment,
    Trend,
    AbstractionLadder,
    EmotionalDrivers
)


@pytest.fixture
def mock_prisma_client(mocker):
    """Mock Prisma API client."""
    mock_client = mocker.Mock()
    mock_client.initialize_pipeline_stages = mocker.Mock()
    mock_client.mark_stage_processing = mocker.Mock()
    mock_client.mark_stage_complete = mocker.Mock()
    mock_client.mark_stage_failed = mocker.Mock()
    return mock_client


@pytest.fixture
def sample_brand_profile():
    """Sample brand profile for testing."""
    return {
        "brand_name": "Test Brand",
        "industry": "Food & Beverage",
        "country": "Canada",
        "portfolio": ["Product A", "Product B"]
    }


@pytest.fixture
def sample_pdf_text():
    """Sample PDF text for testing."""
    return "Sample trend report with emotional trends and consumer insights."


@pytest.mark.asyncio
async def test_orchestrator_execute_stage_with_retry_success(mock_prisma_client):
    """Test successful stage execution with retry logic."""
    orchestrator = PipelineOrchestrator("test-run-123", prisma_client=mock_prisma_client)

    async def mock_stage_func():
        return {"result": "success"}

    result = await orchestrator.execute_stage_with_retry(
        stage_num=0,
        stage_name="Test Stage",
        stage_func=mock_stage_func
    )

    assert result == {"result": "success"}
    mock_prisma_client.mark_stage_processing.assert_called_once_with("test-run-123", 1)


@pytest.mark.asyncio
async def test_orchestrator_execute_stage_with_retry_failure(mock_prisma_client):
    """Test stage execution with retry and eventual failure."""
    orchestrator = PipelineOrchestrator("test-run-123", prisma_client=mock_prisma_client)
    orchestrator.max_retries = 2
    orchestrator.retry_delay = 0  # No delay for testing

    async def mock_failing_stage():
        raise ValueError("Stage failed")

    with pytest.raises(ValueError, match="Stage failed"):
        await orchestrator.execute_stage_with_retry(
            stage_num=0,
            stage_name="Failing Stage",
            stage_func=mock_failing_stage
        )


@pytest.mark.asyncio
async def test_orchestrator_full_pipeline_stages_0_2(mocker, mock_prisma_client, sample_brand_profile, sample_pdf_text):
    """Test full pipeline execution for stages 0-2."""
    orchestrator = PipelineOrchestrator("test-run-456", prisma_client=mock_prisma_client)

    # Mock Stage 0 output
    mock_stage0_output = Stage0Output(
        brand_context=BrandEnrichment(
            brand_name="Test Brand",
            industry="Food & Beverage",
            country="Canada",
            product_portfolio=["Product A"],
            confidence_score=1.0
        ),
        enrichment_method="basic"
    )

    # Mock Stage 1 output
    mock_stage1_output = Stage1Output(
        trends=[
            Trend(
                trend_id="test-trend",
                name="Test Trend",
                lifecycle_stage="EMERGING",
                evidence=["Evidence"],
                weak_signals=["Signal"],
                emotional_drivers=EmotionalDrivers(
                    current_negative=["Neg"],
                    aspirational_positive=["Pos"]
                ),
                abstraction_ladder=AbstractionLadder(
                    L1_domain_specific="L1",
                    L2_category="L2",
                    L3_cross_category="L3",
                    L4_universal="L4"
                )
            )
        ],
        total_trends_extracted=1
    )

    # Mock Stage 2 output
    mock_stage2_output = Stage2Output(
        insights=[],
        convergence_count=0
    )

    # Mock stage classes
    mocker.patch(
        "backend.experimentation.pipeline_orchestrator.Stage0Enrichment.run",
        new_callable=AsyncMock,
        return_value=mock_stage0_output
    )
    mocker.patch(
        "backend.experimentation.pipeline_orchestrator.Stage1Decomposition.run",
        new_callable=AsyncMock,
        return_value=mock_stage1_output
    )
    mocker.patch(
        "backend.experimentation.pipeline_orchestrator.Stage2Insights.run",
        new_callable=AsyncMock,
        return_value=mock_stage2_output
    )

    # Mock webhook sending
    mocker.patch("backend.experimentation.pipeline_orchestrator.send_webhook_sync")

    # Execute pipeline
    result = await orchestrator.run_pipeline(
        pdf_text=sample_pdf_text,
        brand_profile=sample_brand_profile,
        enrichment_mode="basic"
    )

    # Validate results
    assert result["run_id"] == "test-run-456"
    assert result["status"] == "PARTIAL_COMPLETE"
    assert result["completed_stages"] == [0, 1, 2]
    assert "stage_0" in result["stage_outputs"]
    assert "stage_1" in result["stage_outputs"]
    assert "stage_2" in result["stage_outputs"]

    # Verify database calls
    mock_prisma_client.initialize_pipeline_stages.assert_called_once()
    assert mock_prisma_client.mark_stage_complete.call_count == 3  # Stages 0, 1, 2


@pytest.mark.asyncio
async def test_orchestrator_handles_stage_failure(mocker, mock_prisma_client, sample_brand_profile, sample_pdf_text):
    """Test that orchestrator handles stage failures gracefully."""
    orchestrator = PipelineOrchestrator("test-run-789", prisma_client=mock_prisma_client)
    orchestrator.max_retries = 1
    orchestrator.retry_delay = 0

    # Mock Stage 0 to fail
    mocker.patch(
        "backend.experimentation.pipeline_orchestrator.Stage0Enrichment.run",
        new_callable=AsyncMock,
        side_effect=ValueError("Stage 0 failed")
    )

    mocker.patch("backend.experimentation.pipeline_orchestrator.send_webhook_sync")

    # Should raise exception after retries
    with pytest.raises(ValueError, match="Stage 0 failed"):
        await orchestrator.run_pipeline(
            pdf_text=sample_pdf_text,
            brand_profile=sample_brand_profile
        )

    # Verify error was recorded
    mock_prisma_client.mark_stage_failed.assert_called_once()


def test_orchestrator_initialization():
    """Test orchestrator initialization."""
    orchestrator = PipelineOrchestrator("test-run-abc")

    assert orchestrator.run_id == "test-run-abc"
    assert orchestrator.prisma_client is not None
    assert orchestrator.stage_outputs == {}
    assert orchestrator.max_retries >= 1
    assert orchestrator.retry_delay >= 1


@pytest.mark.asyncio
async def test_orchestrator_resume_from_checkpoint_not_implemented(mock_prisma_client):
    """Test that resume from checkpoint raises NotImplementedError."""
    orchestrator = PipelineOrchestrator("test-run-def", prisma_client=mock_prisma_client)

    with pytest.raises(NotImplementedError, match="Resume from checkpoint not yet implemented"):
        await orchestrator.resume_from_checkpoint(last_completed_stage=1)
