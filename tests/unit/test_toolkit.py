"""Unit tests for Ethys402Toolkit."""

import pytest
from unittest.mock import MagicMock, patch

from ethys402_crewai.toolkit import Ethys402Toolkit


def test_toolkit_initialization():
    """Test toolkit initialization."""
    toolkit = Ethys402Toolkit(
        private_key="0x" + "0" * 64,
        base_url="https://test.ethys.dev/api/v1/402",
    )
    
    assert toolkit.client is not None
    assert toolkit.client.base_url == "https://test.ethys.dev/api/v1/402"


def test_toolkit_get_tools():
    """Test toolkit returns all tools."""
    toolkit = Ethys402Toolkit(private_key="0x" + "0" * 64)
    
    tools = toolkit.get_tools()
    
    assert len(tools) == 6
    tool_names = [tool.name for tool in tools]
    assert "ethys402_connect" in tool_names
    assert "ethys402_verify_payment" in tool_names
    assert "ethys402_submit_telemetry" in tool_names
    assert "ethys402_get_trust_score" in tool_names
    assert "ethys402_attest_trust" in tool_names
    assert "ethys402_search_discovery" in tool_names


def test_toolkit_individual_tools():
    """Test individual tool methods."""
    toolkit = Ethys402Toolkit(private_key="0x" + "0" * 64)
    
    assert toolkit.connect() is not None
    assert toolkit.verify_payment() is not None
    assert toolkit.submit_telemetry() is not None
    assert toolkit.get_trust_score() is not None
    assert toolkit.attest_trust() is not None
    assert toolkit.search_discovery() is not None


@patch("ethys402_crewai.toolkit.Ethys402Client")
def test_toolkit_from_env(mock_client_class, monkeypatch):
    """Test toolkit creation from environment variables."""
    test_key = "0x" + "0" * 64
    monkeypatch.setenv("ETHYS402_PRIVATE_KEY", test_key)
    monkeypatch.setenv("ETHYS402_BASE_URL", "https://test.ethys.dev/api/v1/402")
    monkeypatch.setenv("ETHYS402_API_KEY", "test_api_key")
    
    toolkit = Ethys402Toolkit.from_env()
    
    assert toolkit.client is not None
    mock_client_class.assert_called_once_with(
        private_key=test_key,
        base_url="https://test.ethys.dev/api/v1/402",
        api_key="test_api_key",
    )

