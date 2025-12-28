"""Pytest configuration and shared fixtures."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "live: marks tests as live smoke tests (requires ETHYS_MODE=live)")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    # Ensure test isolation by not using real environment variables
    # unless explicitly set
    pass

