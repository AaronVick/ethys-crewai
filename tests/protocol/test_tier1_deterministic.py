"""Tier 1: Deterministic protocol alignment tests (no network required)."""

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from ethys402_crewai.client import Ethys402Client
from ethys402_crewai.tools import (
    AttestTool,
    ConnectTool,
    DiscoverySearchTool,
    TelemetryTool,
    TrustScoreTool,
    VerifyPaymentTool,
)
from ethys402_crewai.toolkit import Ethys402Toolkit
from tests.fixtures.mock_responses import (
    MOCK_CONNECT_RESPONSE,
    MOCK_DISCOVERY_SEARCH_RESPONSE,
    MOCK_ERROR_RESPONSE_400,
    MOCK_ERROR_RESPONSE_401,
    MOCK_ERROR_RESPONSE_402,
    MOCK_ERROR_RESPONSE_404,
    MOCK_ERROR_RESPONSE_500,
    MOCK_TELEMETRY_RESPONSE,
    MOCK_TRUST_ATTEST_RESPONSE,
    MOCK_TRUST_SCORE_RESPONSE,
    MOCK_VERIFY_PAYMENT_RESPONSE,
)
from tests.schemas import (
    validate_connect_response,
    validate_discovery_response,
    validate_error_response,
    validate_telemetry_response,
    validate_trust_score_response,
    validate_verify_payment_response,
)


@pytest.fixture
def private_key():
    """Generate a test private key."""
    from eth_account import Account
    return Account.create().key.hex()


@pytest.fixture
def mock_client(private_key):
    """Create a client with mocked HTTP."""
    return Ethys402Client(
        private_key=private_key,
        base_url="https://402.ethys.dev/api/v1/402",
    )


@pytest.fixture
def mock_toolkit(private_key):
    """Create a toolkit with mocked HTTP."""
    return Ethys402Toolkit(
        private_key=private_key,
        base_url="https://402.ethys.dev/api/v1/402",
    )


class TestConnectEndpoint:
    """Test connect endpoint request construction and response parsing."""

    @patch("ethys402_crewai.client.requests.post")
    def test_connect_builds_correct_payload(self, mock_post, mock_client):
        """Test that connect builds correct signed payload."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_CONNECT_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = mock_client.connect(agent_name="TestAgent")

        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "/connect" in call_args[0][0]

        payload = call_args[1]["json"]
        assert "address" in payload
        assert "signature" in payload
        assert "message" in payload
        assert payload["address"] == mock_client.address
        assert payload["signature"].startswith("0x")
        assert len(payload["signature"]) > 100

        # Validate response schema
        validated = validate_connect_response(result)
        assert validated.agentId == "agent_abc123def456"
        assert validated.payment.amount == "150.000000"

    @patch("ethys402_crewai.client.requests.post")
    def test_connect_handles_auth_errors(self, mock_post, mock_client):
        """Test that connect handles authentication errors correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_ERROR_RESPONSE_401
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            mock_client.connect()

        # Verify error response is parseable
        error_data = MOCK_ERROR_RESPONSE_401
        validated = validate_error_response(error_data)
        assert validated.error == "Unauthorized"
        assert validated.code == "AUTH_ERROR"

    @patch("ethys402_crewai.client.requests.post")
    def test_connect_with_erc6551(self, mock_post, mock_client):
        """Test connect with ERC-6551 identity."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_CONNECT_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        mock_client.connect(
            agent_name="ERC6551Agent",
            token_contract="0x1234567890123456789012345678901234567890",
            token_id="1",
        )

        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["tokenContract"] == "0x1234567890123456789012345678901234567890"
        assert payload["tokenId"] == "1"


class TestVerifyPaymentEndpoint:
    """Test verify payment endpoint."""

    @patch("ethys402_crewai.client.requests.post")
    def test_verify_payment_success(self, mock_post, mock_client):
        """Test successful payment verification."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_VERIFY_PAYMENT_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = mock_client.verify_payment(
            agent_id="agent_abc123def456",
            tx_hash="0x1234567890abcdef",
        )

        validated = validate_verify_payment_response(result)
        assert validated.success is True
        assert validated.activated is True
        assert validated.apiKey == "api_key_xyz789"

        # Verify API key is stored
        assert mock_client.api_key == "api_key_xyz789"

    @patch("ethys402_crewai.client.requests.post")
    def test_verify_payment_handles_failure(self, mock_post, mock_client):
        """Test payment verification handles failures."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_ERROR_RESPONSE_404
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            mock_client.verify_payment(
                agent_id="agent_invalid",
                tx_hash="0xinvalid",
            )


class TestTelemetryEndpoint:
    """Test telemetry submission endpoint."""

    @patch("ethys402_crewai.client.requests.post")
    def test_telemetry_validates_payload_schema(self, mock_post, mock_client):
        """Test telemetry validates payload schema."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_TELEMETRY_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        events = [
            {"type": "performance", "data": {"latency": 100}},
            {"type": "error", "data": {"count": 0}},
        ]

        result = mock_client.submit_telemetry(events=events)

        # Verify request payload structure
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "events" in payload
        assert "signature" in payload
        assert "address" in payload
        assert "timestamp" in payload
        assert len(payload["events"]) == 2

        # Validate response
        validated = validate_telemetry_response(result)
        assert validated.success is True
        assert validated.recorded == 2

    @patch("ethys402_crewai.client.requests.post")
    def test_telemetry_handles_validation_errors(self, mock_post, mock_client):
        """Test telemetry handles server validation errors."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_ERROR_RESPONSE_400
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            mock_client.submit_telemetry(events=[])


class TestDiscoverySearchEndpoint:
    """Test discovery search endpoint."""

    @patch("ethys402_crewai.client.requests.get")
    def test_discovery_builds_query_correctly(self, mock_get, mock_client):
        """Test discovery search builds query parameters correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_DISCOVERY_SEARCH_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = mock_client.search_discovery(tags=["ml", "data"], min_trust=80)

        # Verify query parameters
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["tags"] == "ml,data"
        assert params["minTrust"] == 80

        # Validate response
        validated = validate_discovery_response(result)
        assert validated.success is True
        assert len(validated.agents) == 2

    @patch("ethys402_crewai.client.requests.get")
    def test_discovery_parses_results(self, mock_get, mock_client):
        """Test discovery search parses results correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_DISCOVERY_SEARCH_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = mock_client.search_discovery()

        validated = validate_discovery_response(result)
        agent = validated.agents[0]
        assert agent.agentId == "agent_xyz789"
        assert "ml" in agent.tags
        assert agent.trustScore is not None
        assert agent.trustScore.rs == 88.5


class TestTrustScoreEndpoint:
    """Test trust score endpoint."""

    @patch("ethys402_crewai.client.requests.get")
    def test_trust_score_parses_response(self, mock_get, mock_client):
        """Test trust score parses response correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_TRUST_SCORE_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Set API key for authenticated request
        mock_client.api_key = "test_key"

        result = mock_client.get_trust_score()

        validated = validate_trust_score_response(result)
        assert validated.trustScore.rs == 85.5
        assert validated.trustScore.ci == 0.92


class TestTrustAttestEndpoint:
    """Test trust attestation endpoint."""

    @patch("ethys402_crewai.client.requests.post")
    def test_trust_attest_submits_correctly(self, mock_post, mock_client):
        """Test trust attestation submits correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_TRUST_ATTEST_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        mock_client.api_key = "test_key"

        result = mock_client.attest_trust(
            target_agent_id="agent_target456",
            score=90,
            reason="Excellent performance",
        )

        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["targetAgentId"] == "agent_target456"
        assert payload["score"] == 90
        assert payload["reason"] == "Excellent performance"


class TestErrorMapping:
    """Test error response mapping and handling."""

    @patch("ethys402_crewai.client.requests.post")
    def test_error_mapping_4xx(self, mock_post, mock_client):
        """Test 4xx errors are properly handled."""
        for status_code, error_data in [
            (400, MOCK_ERROR_RESPONSE_400),
            (401, MOCK_ERROR_RESPONSE_401),
            (402, MOCK_ERROR_RESPONSE_402),
            (404, MOCK_ERROR_RESPONSE_404),
        ]:
            mock_response = MagicMock()
            mock_response.json.return_value = error_data
            mock_response.status_code = status_code
            mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
            mock_post.return_value = mock_response

            with pytest.raises(requests.HTTPError) as exc_info:
                mock_client.connect()

            assert exc_info.value.response.status_code == status_code
            validated = validate_error_response(error_data)
            assert validated.error is not None

    @patch("ethys402_crewai.client.requests.post")
    def test_error_mapping_5xx(self, mock_post, mock_client):
        """Test 5xx errors are properly handled."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_ERROR_RESPONSE_500
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        with pytest.raises(requests.HTTPError) as exc_info:
            mock_client.connect()

        assert exc_info.value.response.status_code == 500


class TestCrewAITools:
    """Test CrewAI tool implementations."""

    def test_connect_tool_instantiation(self, mock_toolkit):
        """Test ConnectTool can be instantiated and executed."""
        tool = mock_toolkit.connect()
        assert isinstance(tool, ConnectTool)
        assert tool.name == "ethys402_connect"

    def test_verify_payment_tool_instantiation(self, mock_toolkit):
        """Test VerifyPaymentTool can be instantiated."""
        tool = mock_toolkit.verify_payment()
        assert isinstance(tool, VerifyPaymentTool)

    def test_telemetry_tool_instantiation(self, mock_toolkit):
        """Test TelemetryTool can be instantiated."""
        tool = mock_toolkit.submit_telemetry()
        assert isinstance(tool, TelemetryTool)

    def test_trust_score_tool_instantiation(self, mock_toolkit):
        """Test TrustScoreTool can be instantiated."""
        tool = mock_toolkit.get_trust_score()
        assert isinstance(tool, TrustScoreTool)

    def test_attest_tool_instantiation(self, mock_toolkit):
        """Test AttestTool can be instantiated."""
        tool = mock_toolkit.attest_trust()
        assert isinstance(tool, AttestTool)

    def test_discovery_tool_instantiation(self, mock_toolkit):
        """Test DiscoverySearchTool can be instantiated."""
        tool = mock_toolkit.search_discovery()
        assert isinstance(tool, DiscoverySearchTool)

    @patch("ethys402_crewai.client.requests.post")
    def test_connect_tool_execution(self, mock_post, mock_toolkit):
        """Test ConnectTool executes correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_CONNECT_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        tool = mock_toolkit.connect()
        result = tool._run(agent_name="TestAgent")

        assert "Connected successfully" in result
        assert "agent_abc123def456" in result

    @patch("ethys402_crewai.client.requests.get")
    def test_discovery_tool_execution(self, mock_get, mock_toolkit):
        """Test DiscoverySearchTool executes correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_DISCOVERY_SEARCH_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        tool = mock_toolkit.search_discovery()
        result = tool._run(tags=["ml"], min_trust=80)

        assert "Found" in result
        assert "agent" in result.lower()


class TestToolkitIntegration:
    """Test toolkit integration."""

    def test_toolkit_get_tools(self, mock_toolkit):
        """Test toolkit returns all tools."""
        tools = mock_toolkit.get_tools()
        assert len(tools) == 6
        tool_names = [tool.name for tool in tools]
        assert "ethys402_connect" in tool_names
        assert "ethys402_verify_payment" in tool_names
        assert "ethys402_submit_telemetry" in tool_names
        assert "ethys402_get_trust_score" in tool_names
        assert "ethys402_attest_trust" in tool_names
        assert "ethys402_search_discovery" in tool_names

