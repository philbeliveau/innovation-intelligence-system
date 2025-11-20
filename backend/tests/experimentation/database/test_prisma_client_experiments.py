"""Tests for PrismaAPIClient experiment operations

Story 11.4a - Database Schema + Core Operations
Tests save_experiment() and get_experiments() methods
"""
import pytest
from unittest.mock import Mock, patch
from app.prisma_client import PrismaAPIClient


@pytest.fixture
def prisma_client():
    """Create PrismaAPIClient instance for testing"""
    with patch.dict('os.environ', {
        'FRONTEND_WEBHOOK_URL': 'https://test-frontend.com',
        'WEBHOOK_SECRET': 'test-secret'
    }):
        client = PrismaAPIClient()
        return client


@pytest.fixture
def sample_experiment_data():
    """Sample experiment data for testing"""
    return {
        "run_id": "test-run-123",
        "brand_profile": {
            "brand_name": "Test Brand",
            "industry": "Food & Beverage",
            "country": "USA"
        },
        "stage_outputs": {
            "stage_0": {"output": "test"},
            "stage_1": {"trends": []},
            "stage_2": {"insights": []},
            "stage_3": {"techniques": []},
            "stage_4": {"concepts": []},
            "stage_5": {"competitive": []},
            "stage_6": {"cards": "markdown"}
        },
        "report_text": "Sample report text",
        "report_name": "test-report.pdf",
        "quality_tag": "good",
        "notes": "Test notes",
        "execution_time": 120,
        "token_usage": {
            "total_input_tokens": 1000,
            "total_output_tokens": 500
        },
        "cost_usd": 0.50,
        "pipeline_version": "1.0"
    }


class TestSaveExperiment:
    """Test save_experiment() method"""

    def test_save_experiment_success(self, prisma_client, sample_experiment_data):
        """Test successful experiment save"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "success": True,
            "experimentId": "exp-123",
            "runId": "test-run-123"
        }

        with patch.object(prisma_client.session, 'post', return_value=mock_response) as mock_post:
            result = prisma_client.save_experiment(**sample_experiment_data)

        assert result is True
        mock_post.assert_called_once()

        # Verify API endpoint
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://test-frontend.com/api/experiments"

        # Verify payload structure
        payload = call_args[1]['json']
        assert payload['runId'] == "test-run-123"
        assert payload['brandProfile'] == sample_experiment_data['brand_profile']
        assert payload['stageOutputs'] == sample_experiment_data['stage_outputs']
        assert payload['qualityTag'] == "good"

    def test_save_experiment_minimal_data(self, prisma_client):
        """Test save with only required fields"""
        mock_response = Mock()
        mock_response.ok = True

        with patch.object(prisma_client.session, 'post', return_value=mock_response) as mock_post:
            result = prisma_client.save_experiment(
                run_id="test-run-456",
                brand_profile={"brand_name": "Test"},
                stage_outputs={"stage_0": {}}
            )

        assert result is True

        # Verify optional fields are None
        payload = mock_post.call_args[1]['json']
        assert payload['reportText'] is None
        assert payload['qualityTag'] is None
        assert payload['experimentNotes'] is None

    def test_save_experiment_api_error(self, prisma_client, sample_experiment_data):
        """Test handling of API error responses"""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch.object(prisma_client.session, 'post', return_value=mock_response):
            result = prisma_client.save_experiment(**sample_experiment_data)

        assert result is False

    def test_save_experiment_network_error(self, prisma_client, sample_experiment_data):
        """Test handling of network errors"""
        with patch.object(prisma_client.session, 'post', side_effect=Exception("Network error")):
            result = prisma_client.save_experiment(**sample_experiment_data)

        assert result is False


class TestGetExperiments:
    """Test get_experiments() method"""

    def test_get_experiments_no_filters(self, prisma_client):
        """Test retrieve experiments without filters"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "experiments": [
                {
                    "id": "exp-1",
                    "runId": "run-1",
                    "qualityTag": "good"
                }
            ],
            "pagination": {
                "page": 1,
                "pageSize": 20,
                "total": 1,
                "totalPages": 1
            }
        }

        with patch.object(prisma_client.session, 'get', return_value=mock_response):
            result = prisma_client.get_experiments()

        assert result is not None
        assert len(result['experiments']) == 1
        assert result['pagination']['page'] == 1

    def test_get_experiments_with_filters(self, prisma_client):
        """Test retrieve experiments with all filters"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "experiments": [],
            "pagination": {"page": 1, "pageSize": 10, "total": 0, "totalPages": 0}
        }

        with patch.object(prisma_client.session, 'get', return_value=mock_response) as mock_get:
            result = prisma_client.get_experiments(
                quality_tag="good",
                brand_name="Test Brand",
                start_date="2025-01-01T00:00:00Z",
                end_date="2025-12-31T23:59:59Z",
                pipeline_version="1.0",
                page=2,
                page_size=10,
                order_by="cost_desc"
            )

        assert result is not None

        # Verify query parameters
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['qualityTag'] == "good"
        assert params['brandName'] == "Test Brand"
        assert params['startDate'] == "2025-01-01T00:00:00Z"
        assert params['endDate'] == "2025-12-31T23:59:59Z"
        assert params['pipelineVersion'] == "1.0"
        assert params['page'] == 2
        assert params['pageSize'] == 10
        assert params['orderBy'] == "cost_desc"

    def test_get_experiments_pagination(self, prisma_client):
        """Test pagination parameters"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "experiments": [],
            "pagination": {"page": 3, "pageSize": 50, "total": 150, "totalPages": 3}
        }

        with patch.object(prisma_client.session, 'get', return_value=mock_response):
            result = prisma_client.get_experiments(page=3, page_size=50)

        assert result is not None
        assert result['pagination']['page'] == 3
        assert result['pagination']['pageSize'] == 50
        assert result['pagination']['total'] == 150

    def test_get_experiments_api_error(self, prisma_client):
        """Test handling of API error"""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Server Error"

        with patch.object(prisma_client.session, 'get', return_value=mock_response):
            result = prisma_client.get_experiments()

        assert result is None

    def test_get_experiments_network_error(self, prisma_client):
        """Test handling of network error"""
        with patch.object(prisma_client.session, 'get', side_effect=Exception("Connection timeout")):
            result = prisma_client.get_experiments()

        assert result is None


class TestIntegration:
    """Integration tests for experiment operations"""

    def test_save_and_retrieve_workflow(self, prisma_client, sample_experiment_data):
        """Test complete save and retrieve workflow"""
        # Mock save response
        save_response = Mock()
        save_response.ok = True
        save_response.json.return_value = {
            "success": True,
            "experimentId": "exp-123",
            "runId": "test-run-123"
        }

        # Mock retrieve response
        get_response = Mock()
        get_response.ok = True
        get_response.json.return_value = {
            "experiments": [
                {
                    "id": "exp-123",
                    "runId": "test-run-123",
                    "qualityTag": "good",
                    "brandProfile": sample_experiment_data['brand_profile']
                }
            ],
            "pagination": {"page": 1, "pageSize": 20, "total": 1, "totalPages": 1}
        }

        with patch.object(prisma_client.session, 'post', return_value=save_response):
            save_result = prisma_client.save_experiment(**sample_experiment_data)

        assert save_result is True

        with patch.object(prisma_client.session, 'get', return_value=get_response):
            get_result = prisma_client.get_experiments(
                quality_tag="good",
                brand_name="Test Brand"
            )

        assert get_result is not None
        assert len(get_result['experiments']) == 1
        assert get_result['experiments'][0]['runId'] == "test-run-123"
