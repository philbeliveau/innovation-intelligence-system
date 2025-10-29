"""
Tests for webhook delivery functionality with retry logic.

Tests the webhook utility functions in pipeline/utils.py to ensure
reliable delivery with exponential backoff and proper error handling.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
import httpx

from pipeline.utils import (
    send_webhook_with_retry,
    send_webhook_sync,
    WebhookDeliveryError
)


class TestWebhookDeliveryAsync:
    """Test async webhook delivery with retry logic."""

    @pytest.mark.asyncio
    async def test_webhook_success_first_attempt(self):
        """Test successful webhook delivery on first attempt."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        with patch.dict('os.environ', {
            'FRONTEND_URL': 'https://example.com',
            'WEBHOOK_SECRET': 'test-secret'
        }):
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )

                # Should not raise exception
                await send_webhook_with_retry(
                    run_id="test-123",
                    endpoint="stage-update",
                    payload={"stageNumber": 1, "status": "COMPLETE"}
                )

    @pytest.mark.asyncio
    async def test_webhook_retry_logic(self):
        """Test webhook retries with exponential backoff."""
        call_count = 0

        async def mock_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.HTTPError("Connection failed")
            # Success on third attempt
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status = Mock()
            return mock_response

        with patch.dict('os.environ', {
            'FRONTEND_URL': 'https://example.com',
            'WEBHOOK_SECRET': 'test-secret'
        }):
            with patch('httpx.AsyncClient') as mock_client:
                with patch('pipeline.utils.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                    mock_client.return_value.__aenter__.return_value.post = mock_post

                    # Should succeed after retries
                    await send_webhook_with_retry(
                        run_id="test-123",
                        endpoint="stage-update",
                        payload={"stageNumber": 1}
                    )

                    # Verify exponential backoff was applied (2 sleeps: 1s, 2s)
                    assert mock_sleep.call_count == 2
                    mock_sleep.assert_any_call(1)  # First retry wait
                    mock_sleep.assert_any_call(2)  # Second retry wait

    @pytest.mark.asyncio
    async def test_webhook_timeout(self):
        """Test webhook delivery with timeout."""
        with patch.dict('os.environ', {
            'FRONTEND_URL': 'https://example.com',
            'WEBHOOK_SECRET': 'test-secret'
        }):
            with patch('httpx.AsyncClient') as mock_client:
                with patch('asyncio.sleep'):  # Don't actually sleep
                    mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                        side_effect=httpx.TimeoutException("Request timeout")
                    )

                    # Should raise WebhookDeliveryError after max retries
                    with pytest.raises(WebhookDeliveryError):
                        await send_webhook_with_retry(
                            run_id="test-123",
                            endpoint="stage-update",
                            payload={"stageNumber": 1},
                            max_retries=3,
                            timeout=10
                        )

    @pytest.mark.asyncio
    async def test_webhook_max_retries_exceeded(self):
        """Test webhook fails after max retries."""
        with patch.dict('os.environ', {
            'FRONTEND_URL': 'https://example.com',
            'WEBHOOK_SECRET': 'test-secret'
        }):
            with patch('httpx.AsyncClient') as mock_client:
                with patch('asyncio.sleep'):  # Don't actually sleep
                    mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                        side_effect=httpx.HTTPError("Connection failed")
                    )

                    # Should raise WebhookDeliveryError after 3 attempts
                    with pytest.raises(WebhookDeliveryError) as exc_info:
                        await send_webhook_with_retry(
                            run_id="test-123",
                            endpoint="stage-update",
                            payload={"stageNumber": 1},
                            max_retries=3
                        )

                    assert "Failed after 3 attempts" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_webhook_missing_frontend_url(self):
        """Test webhook gracefully handles missing FRONTEND_URL."""
        with patch.dict('os.environ', {}, clear=True):
            # Should not raise exception, just log and return
            await send_webhook_with_retry(
                run_id="test-123",
                endpoint="stage-update",
                payload={"stageNumber": 1}
            )

    @pytest.mark.asyncio
    async def test_webhook_missing_secret(self, caplog):
        """Test webhook warns when WEBHOOK_SECRET missing."""
        with patch.dict('os.environ', {
            'FRONTEND_URL': 'https://example.com'
        }, clear=True):
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raise_for_status = Mock()
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )

                await send_webhook_with_retry(
                    run_id="test-123",
                    endpoint="stage-update",
                    payload={"stageNumber": 1}
                )

                # Should log warning about missing secret
                assert any("WEBHOOK_SECRET not configured" in record.message
                          for record in caplog.records)


class TestWebhookDeliverySync:
    """Test synchronous webhook wrapper."""

    def test_webhook_sync_success(self):
        """Test synchronous webhook wrapper succeeds."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        with patch.dict('os.environ', {
            'FRONTEND_URL': 'https://example.com',
            'WEBHOOK_SECRET': 'test-secret'
        }):
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )

                # Should not raise exception
                send_webhook_sync(
                    run_id="test-123",
                    endpoint="stage-update",
                    payload={"stageNumber": 1, "status": "COMPLETE"}
                )

    def test_webhook_sync_failure_no_exception(self):
        """Test synchronous wrapper logs error but doesn't raise."""
        with patch.dict('os.environ', {
            'FRONTEND_URL': 'https://example.com',
            'WEBHOOK_SECRET': 'test-secret'
        }):
            with patch('httpx.AsyncClient') as mock_client:
                with patch('asyncio.sleep'):  # Don't actually sleep
                    mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                        side_effect=httpx.HTTPError("Connection failed")
                    )

                    # Should NOT raise exception (failures are logged, not raised)
                    send_webhook_sync(
                        run_id="test-123",
                        endpoint="stage-update",
                        payload={"stageNumber": 1},
                        max_retries=3
                    )


class TestWebhookPayloadStructure:
    """Test webhook payload structures match story requirements."""

    @pytest.mark.asyncio
    async def test_stage1_payload_structure(self):
        """Test Stage 1 payload has extractedText and mechanisms."""
        expected_payload = {
            "stageNumber": 1,
            "stageName": "Extraction",
            "status": "COMPLETE",
            "output": {
                "extractedText": "Sample text...",
                "mechanisms": [
                    {
                        "title": "Mechanism 1",
                        "description": "How it works",
                        "context": "Where it appears"
                    }
                ]
            }
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        with patch.dict('os.environ', {
            'FRONTEND_URL': 'https://example.com',
            'WEBHOOK_SECRET': 'test-secret'
        }):
            with patch('httpx.AsyncClient') as mock_client:
                mock_post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value.post = mock_post

                await send_webhook_with_retry(
                    run_id="test-123",
                    endpoint="stage-update",
                    payload=expected_payload
                )

                # Verify payload was sent correctly
                mock_post.assert_called_once()
                call_kwargs = mock_post.call_args[1]
                assert call_kwargs['json'] == expected_payload

    @pytest.mark.asyncio
    async def test_stage2_payload_structure(self):
        """Test Stage 2 payload has signals."""
        expected_payload = {
            "stageNumber": 2,
            "stageName": "Signals",
            "status": "COMPLETE",
            "output": {
                "signals": [
                    {
                        "id": "signal-1",
                        "category": "Technology",
                        "description": "Signal description",
                        "relevance": "Why this matters"
                    }
                ]
            }
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        with patch.dict('os.environ', {
            'FRONTEND_URL': 'https://example.com',
            'WEBHOOK_SECRET': 'test-secret'
        }):
            with patch('httpx.AsyncClient') as mock_client:
                mock_post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value.post = mock_post

                await send_webhook_with_retry(
                    run_id="test-123",
                    endpoint="stage-update",
                    payload=expected_payload
                )

                call_kwargs = mock_post.call_args[1]
                assert call_kwargs['json'] == expected_payload
