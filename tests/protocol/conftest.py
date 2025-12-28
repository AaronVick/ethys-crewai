"""Pytest configuration for protocol alignment tests."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "live: marks tests as live smoke tests (requires ETHYS_MODE=live)")


@pytest.fixture(scope="session", autouse=True)
def check_live_test_requirements():
    """Check that live tests are explicitly enabled."""
    import os

    live_enabled = os.environ.get("ETHYS_MODE") == "live" or os.environ.get("ETHYS_LIVE_TESTS") == "1"

    if not live_enabled:
        pytest.skip("Live tests require ETHYS_MODE=live or ETHYS_LIVE_TESTS=1")

