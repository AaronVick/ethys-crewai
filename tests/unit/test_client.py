"""Unit tests for Ethys402Client."""

import time
from unittest.mock import MagicMock, patch

import pytest
import requests
from eth_account import Account

from ethys402_crewai.client import Ethys402Client


@pytest.fixture
def private_key():
    """Generate a test private key."""
    return Account.create().key.hex()


@pytest.fixture
def client(private_key):
    """Create a test client."""
    return Ethys402Client(
        private_key=private_key,
        base_url="https://402.ethys.dev/api/v1/402",
    )


def test_client_initialization(private_key):
    """Test client initialization."""
    client = Ethys402Client(private_key=private_key)
    assert client.account is not None
    assert client.address is not None
    assert client.base_url == "https://402.ethys.dev/api/v1/402"


def test_client_initialization_with_0x_prefix():
    """Test client initialization handles private key with 0x prefix."""
    account = Account.create()
    private_key = account.key.hex()
    
    # Test with 0x prefix
    client1 = Ethys402Client(private_key=f"0x{private_key}")
    assert client1.address == account.address
    
    # Test without 0x prefix
    client2 = Ethys402Client(private_key=private_key)
    assert client2.address == account.address


def test_client_initialization_no_private_key():
    """Test client initialization without private key."""
    client = Ethys402Client()
    assert client.account is None
    assert client.address is None


def test_sign_message(client):
    """Test message signing."""
    message = "Test message"
    signature = client._sign_message(message)
    
    assert signature is not None
    assert signature.startswith("0x")
    assert len(signature) > 100  # Signature should be long hex string


def test_sign_message_no_private_key():
    """Test message signing fails without private key."""
    client = Ethys402Client()
    with pytest.raises(ValueError, match="Private key required"):
        client._sign_message("test")


def test_get_headers_with_api_key():
    """Test headers generation with API key."""
    client = Ethys402Client(api_key="test_key")
    headers = client._get_headers(include_auth=True)
    
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_key"
    assert headers["Content-Type"] == "application/json"


def test_get_headers_without_api_key():
    """Test headers generation without API key."""
    client = Ethys402Client()
    headers = client._get_headers(include_auth=True)
    
    assert "Authorization" not in headers
    assert headers["Content-Type"] == "application/json"


@patch("ethys402_crewai.client.requests.post")
def test_connect_success(mock_post, client):
    """Test successful connection."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "agentId": "agent_123",
        "payment": {"amount": "150.0"},
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    result = client.connect(agent_name="TestAgent")
    
    assert result["agentId"] == "agent_123"
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "/connect" in call_args[0][0]
    payload = call_args[1]["json"]
    assert "address" in payload
    assert "signature" in payload
    assert "message" in payload


@patch("ethys402_crewai.client.requests.post")
def test_connect_with_erc6551(mock_post, client):
    """Test connection with ERC-6551 identity."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"agentId": "agent_123"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    client.connect(
        agent_name="TestAgent",
        token_contract="0x1234567890123456789012345678901234567890",
        token_id="1",
    )
    
    call_args = mock_post.call_args
    payload = call_args[1]["json"]
    assert payload["tokenContract"] == "0x1234567890123456789012345678901234567890"
    assert payload["tokenId"] == "1"


def test_connect_no_private_key():
    """Test connect fails without private key."""
    client = Ethys402Client()
    with pytest.raises(ValueError, match="Private key required"):
        client.connect()


@patch("ethys402_crewai.client.requests.post")
def test_verify_payment_success(mock_post, client):
    """Test successful payment verification."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "apiKey": "test_api_key",
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    result = client.verify_payment(
        agent_id="agent_123",
        tx_hash="0x1234567890abcdef",
    )
    
    assert result["success"] is True
    assert client.api_key == "test_api_key"
    mock_post.assert_called_once()


@patch("ethys402_crewai.client.requests.post")
def test_submit_telemetry_success(mock_post, client):
    """Test successful telemetry submission."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    events = [
        {"type": "performance", "data": {"latency": 100}},
        {"type": "error", "data": {"count": 0}},
    ]
    
    result = client.submit_telemetry(events=events)
    
    assert result["success"] is True
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    payload = call_args[1]["json"]
    assert "events" in payload
    assert "signature" in payload
    assert "address" in payload


def test_submit_telemetry_no_private_key():
    """Test telemetry submission fails without private key."""
    client = Ethys402Client()
    with pytest.raises(ValueError, match="Private key required"):
        client.submit_telemetry(events=[])


@patch("ethys402_crewai.client.requests.get")
def test_get_trust_score_success(mock_get, client):
    """Test successful trust score retrieval."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "trustScore": {"rs": 85.5, "ci": 0.92},
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    # Set API key for authenticated request
    client.api_key = "test_key"
    
    result = client.get_trust_score()
    
    assert result["trustScore"]["rs"] == 85.5
    assert result["trustScore"]["ci"] == 0.92
    mock_get.assert_called_once()


@patch("ethys402_crewai.client.requests.post")
def test_attest_trust_success(mock_post, client):
    """Test successful trust attestation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    # Set API key for authenticated request
    client.api_key = "test_key"
    
    result = client.attest_trust(
        target_agent_id="agent_456",
        score=90,
        reason="Excellent performance",
    )
    
    assert result["success"] is True
    mock_post.assert_called_once()


@patch("ethys402_crewai.client.requests.get")
def test_search_discovery_success(mock_get, client):
    """Test successful discovery search."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "agents": [
            {"agentId": "agent_1", "tags": ["ml", "data"]},
            {"agentId": "agent_2", "tags": ["ai"]},
        ],
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    result = client.search_discovery(tags=["ml"], min_trust=80)
    
    assert len(result["agents"]) == 2
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert "tags" in call_args[1]["params"]
    assert "minTrust" in call_args[1]["params"]


def test_get_agent_id_key(client):
    """Test agent ID key generation."""
    agent_id_key = client._get_agent_id_key()
    assert agent_id_key == client.address


def test_get_agent_id_key_no_address():
    """Test agent ID key generation fails without address."""
    client = Ethys402Client()
    with pytest.raises(ValueError, match="Address required"):
        client._get_agent_id_key()


def test_from_env(monkeypatch):
    """Test client creation from environment variables."""
    test_key = Account.create().key.hex()
    monkeypatch.setenv("ETHYS402_PRIVATE_KEY", test_key)
    monkeypatch.setenv("ETHYS402_API_KEY", "test_api_key")
    monkeypatch.setenv("ETHYS402_BASE_URL", "https://test.ethys.dev/api/v1/402")
    
    client = Ethys402Client.from_env()
    
    assert client.address == Account.from_key(test_key).address
    assert client.api_key == "test_api_key"
    assert client.base_url == "https://test.ethys.dev/api/v1/402"

