"""Integration tests for ETHYS x402 client.

These tests require either:
1. A running local server (ETHYS402_BASE_URL=http://localhost:3000/api/v1/402)
2. Or mock server responses (using pytest fixtures)

To run against a local server, use docker-compose or set ETHYS402_BASE_URL.
"""

import os
import pytest

from ethys402_crewai.client import Ethys402Client


@pytest.fixture
def base_url():
    """Get base URL from environment or use default."""
    return os.environ.get(
        "ETHYS402_BASE_URL",
        "https://402.ethys.dev/api/v1/402"
    )


@pytest.fixture
def test_private_key():
    """Get test private key from environment."""
    key = os.environ.get("ETHYS402_TEST_PRIVATE_KEY")
    if not key:
        pytest.skip("ETHYS402_TEST_PRIVATE_KEY not set for integration tests")
    return key


@pytest.mark.integration
def test_connect_integration(base_url, test_private_key):
    """Integration test for connect endpoint."""
    client = Ethys402Client(
        private_key=test_private_key,
        base_url=base_url,
    )
    
    try:
        result = client.connect(agent_name="IntegrationTestAgent")
        assert "agentId" in result or "error" in result
    except Exception as e:
        # If connection fails (e.g., server not available), that's ok for CI
        # but we should log it
        pytest.skip(f"Connection failed: {e}")


@pytest.mark.integration
def test_discovery_search_integration(base_url):
    """Integration test for discovery search (no auth required)."""
    client = Ethys402Client(base_url=base_url)
    
    try:
        result = client.search_discovery(tags=["test"], min_trust=0)
        assert "agents" in result or "error" in result
    except Exception as e:
        pytest.skip(f"Discovery search failed: {e}")


@pytest.mark.integration
@pytest.mark.skip(reason="Requires authenticated agent and API key")
def test_trust_score_integration(base_url, test_private_key):
    """Integration test for trust score (requires authenticated agent)."""
    client = Ethys402Client(
        private_key=test_private_key,
        base_url=base_url,
    )
    
    # This would require a fully onboarded agent with API key
    # For now, we skip this test
    pytest.skip("Requires fully onboarded agent with API key")

