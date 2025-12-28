"""Unit tests for CrewAI tools."""

import pytest
from unittest.mock import MagicMock, patch

from ethys402_crewai.tools import (
    AttestTool,
    ConnectTool,
    DiscoverySearchTool,
    TelemetryTool,
    TrustScoreTool,
    VerifyPaymentTool,
)


@pytest.fixture
def mock_client():
    """Create a mock client."""
    client = MagicMock()
    client.address = "0x1234567890123456789012345678901234567890"
    return client


def test_connect_tool(mock_client):
    """Test ConnectTool."""
    tool = ConnectTool(client=mock_client)
    
    mock_client.connect.return_value = {
        "agentId": "agent_123",
        "payment": {"amount": "150.0"},
    }
    
    result = tool._run(agent_name="TestAgent")
    
    assert "Connected successfully" in result
    assert "agent_123" in result
    mock_client.connect.assert_called_once_with(
        agent_name="TestAgent",
        token_contract=None,
        token_id=None,
    )


def test_connect_tool_failure(mock_client):
    """Test ConnectTool handles errors."""
    tool = ConnectTool(client=mock_client)
    
    mock_client.connect.side_effect = Exception("Connection failed")
    
    result = tool._run()
    
    assert "Connection failed" in result


def test_verify_payment_tool(mock_client):
    """Test VerifyPaymentTool."""
    tool = VerifyPaymentTool(client=mock_client)
    
    mock_client.verify_payment.return_value = {
        "success": True,
        "apiKey": "test_key",
    }
    
    result = tool._run(agent_id="agent_123", tx_hash="0xabc")
    
    assert "Payment verified" in result
    assert "test_key" in result
    mock_client.verify_payment.assert_called_once_with(
        agent_id="agent_123",
        tx_hash="0xabc",
    )


def test_telemetry_tool(mock_client):
    """Test TelemetryTool."""
    tool = TelemetryTool(client=mock_client)
    
    mock_client.submit_telemetry.return_value = {"success": True}
    
    events = [{"type": "performance", "data": {"latency": 100}}]
    result = tool._run(events=events)
    
    assert "Telemetry submitted" in result
    mock_client.submit_telemetry.assert_called_once()


def test_trust_score_tool(mock_client):
    """Test TrustScoreTool."""
    tool = TrustScoreTool(client=mock_client)
    
    mock_client.get_trust_score.return_value = {
        "trustScore": {"rs": 85.5, "ci": 0.92},
    }
    
    result = tool._run()
    
    assert "Trust Score" in result
    assert "85.5" in result
    assert "0.92" in result
    mock_client.get_trust_score.assert_called_once()


def test_attest_tool(mock_client):
    """Test AttestTool."""
    tool = AttestTool(client=mock_client)
    
    mock_client.attest_trust.return_value = {"success": True}
    
    result = tool._run(
        target_agent_id="agent_456",
        score=90,
        reason="Excellent performance",
    )
    
    assert "Trust attestation submitted" in result
    assert "agent_456" in result
    mock_client.attest_trust.assert_called_once_with(
        target_agent_id="agent_456",
        score=90,
        reason="Excellent performance",
    )


def test_discovery_search_tool(mock_client):
    """Test DiscoverySearchTool."""
    tool = DiscoverySearchTool(client=mock_client)
    
    mock_client.search_discovery.return_value = {
        "agents": [
            {"agentId": "agent_1", "tags": ["ml", "data"]},
            {"agentId": "agent_2", "tags": ["ai"]},
        ],
    }
    
    result = tool._run(tags=["ml"], min_trust=80)
    
    assert "Found 2 agent(s)" in result
    assert "agent_1" in result
    mock_client.search_discovery.assert_called_once_with(tags=["ml"], min_trust=80)


def test_discovery_search_tool_no_results(mock_client):
    """Test DiscoverySearchTool with no results."""
    tool = DiscoverySearchTool(client=mock_client)
    
    mock_client.search_discovery.return_value = {"agents": []}
    
    result = tool._run()
    
    assert "No agents found" in result

