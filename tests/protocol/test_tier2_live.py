"""Tier 2: Live smoke tests against 402.ethys.dev (opt-in, requires ETHYS_MODE=live)."""

import os
import re
from typing import Dict, List, Set
from urllib.parse import urljoin, urlparse

import pytest
import requests
from pydantic import ValidationError

from tests.schemas import (
    validate_protocol_info,
    validate_x402_json,
    X402Protocol,
    ProtocolInfo,
)


# Live tests only run when explicitly enabled
pytestmark = pytest.mark.skipif(
    os.environ.get("ETHYS_MODE") != "live" and os.environ.get("ETHYS_LIVE_TESTS") != "1",
    reason="Live tests require ETHYS_MODE=live or ETHYS_LIVE_TESTS=1",
)

BASE_URL = "https://402.ethys.dev"
API_BASE = f"{BASE_URL}/api/v1/402"
MAX_CRAWL_URLS = 25


def get_diagnostic_info(url: str, response: requests.Response) -> str:
    """Generate diagnostic information for failed requests."""
    body_preview = ""
    if response.text:
        body_preview = response.text[:500]
        # Redact potential secrets
        body_preview = re.sub(r'("(?:api[_-]?key|token|secret|private[_-]?key)":\s*)"[^"]+"', r'\1"REDACTED"', body_preview, flags=re.IGNORECASE)
    
    return f"""
URL: {url}
Status Code: {response.status_code}
Headers: {dict(response.headers)}
Response Body (first 500 chars):
{body_preview}
"""


class TestProtocolDiscovery:
    """Test protocol discovery endpoints."""

    def test_x402_json_is_reachable(self):
        """Test that /.well-known/x402.json is 200 and parseable."""
        url = f"{BASE_URL}/.well-known/x402.json"
        response = requests.get(url, timeout=10)

        assert response.status_code == 200, get_diagnostic_info(url, response)
        assert response.headers.get("content-type", "").startswith("application/json")

        data = response.json()
        assert isinstance(data, dict)
        assert data.get("protocol") == "x402"

        # Validate schema
        try:
            protocol = validate_x402_json(data)
            assert protocol.version is not None
            assert protocol.endpoints is not None
        except ValidationError as e:
            pytest.fail(f"x402.json schema validation failed: {e}\n{get_diagnostic_info(url, response)}")

    def test_x402_json_structure(self):
        """Test that x402.json has required structure."""
        url = f"{BASE_URL}/.well-known/x402.json"
        response = requests.get(url, timeout=10)
        data = response.json()

        # Check required top-level fields
        assert "protocol" in data
        assert "version" in data
        assert "endpoints" in data
        assert "contracts" in data

        # Check endpoints exist
        endpoints = data.get("endpoints", {})
        required_endpoints = ["connect", "verifyPayment", "telemetry", "trustScore", "trustAttest", "discoverySearch"]
        for endpoint in required_endpoints:
            assert endpoint in endpoints, f"Missing endpoint: {endpoint} in x402.json"

    def test_llms_txt_is_reachable(self):
        """Test that /llms.txt is 200 and non-empty."""
        url = f"{BASE_URL}/llms.txt"
        response = requests.get(url, timeout=10)

        assert response.status_code == 200, get_diagnostic_info(url, response)
        assert len(response.text) > 0, "llms.txt is empty"

        # Should contain key sections
        content = response.text.lower()
        assert "[project]" in content or "project" in content
        assert "[purpose]" in content or "purpose" in content

    def test_info_endpoint_is_reachable(self):
        """Test that /api/v1/402/info is 200 and parseable."""
        url = f"{API_BASE}/info"
        response = requests.get(url, timeout=10)

        assert response.status_code == 200, get_diagnostic_info(url, response)
        assert response.headers.get("content-type", "").startswith("application/json")

        data = response.json()
        assert isinstance(data, dict)

        # Validate key schema fields
        try:
            info = validate_protocol_info(data)
            assert info.protocol == "x402"
            assert info.onboarding is not None
            assert info.pricing is not None
        except ValidationError as e:
            pytest.fail(f"Info endpoint schema validation failed: {e}\n{get_diagnostic_info(url, response)}")

    def test_info_endpoint_structure(self):
        """Test that info endpoint has required structure."""
        url = f"{API_BASE}/info"
        response = requests.get(url, timeout=10)
        data = response.json()

        # Check required fields
        assert "protocol" in data
        assert "onboarding" in data
        assert "pricing" in data
        assert "network" in data

        # Check onboarding steps
        onboarding = data.get("onboarding", {})
        steps = onboarding.get("steps", [])
        assert len(steps) > 0, "Onboarding steps missing"

        # Check pricing
        pricing = data.get("pricing", {})
        assert "activationFee" in pricing or "token" in pricing


class TestLinkIntegrity:
    """Test link integrity from protocol discovery documents."""

    def collect_urls_from_x402_json(self) -> Set[str]:
        """Collect URLs from x402.json."""
        url = f"{BASE_URL}/.well-known/x402.json"
        response = requests.get(url, timeout=10)
        data = response.json()

        urls = set()

        # Extract endpoint paths
        endpoints = data.get("endpoints", {})
        for endpoint_path in endpoints.values():
            if endpoint_path.startswith("/"):
                urls.add(urljoin(BASE_URL, endpoint_path))

        # Extract docs paths
        pathways = data.get("pathways", {})
        for pathway in pathways.values():
            if isinstance(pathway, dict):
                docs = pathway.get("docs")
                if docs and isinstance(docs, str):
                    urls.add(urljoin(BASE_URL, docs))

        return urls

    def collect_urls_from_llms_txt(self) -> Set[str]:
        """Collect URLs from llms.txt."""
        url = f"{BASE_URL}/llms.txt"
        response = requests.get(url, timeout=10)
        content = response.text

        urls = set()
        # Extract HTTP(S) URLs
        url_pattern = re.compile(r'https?://[^\s\)]+')
        for match in url_pattern.finditer(content):
            url_str = match.group(0).rstrip('.,;')
            urls.add(url_str)

        return urls

    def test_x402_json_links_are_reachable(self):
        """Test that URLs in x402.json are reachable (bounded crawl)."""
        urls = self.collect_urls_from_x402_json()
        assert len(urls) > 0, "No URLs found in x402.json"

        # Limit crawl size
        urls_to_test = list(urls)[:MAX_CRAWL_URLS]
        failed_urls = []

        for url in urls_to_test:
            try:
                # Use HEAD first for efficiency
                response = requests.head(url, timeout=10, allow_redirects=True)
                if response.status_code == 405:  # Method not allowed, try GET
                    response = requests.get(url, timeout=10, allow_redirects=True)

                # Allow 200, 3xx redirects, 401/403 (auth required is OK)
                if response.status_code not in [200, 301, 302, 303, 307, 308, 401, 403]:
                    failed_urls.append((url, response.status_code, get_diagnostic_info(url, response)))
            except requests.RequestException as e:
                failed_urls.append((url, None, f"Request failed: {e}"))

        if failed_urls:
            failure_messages = "\n".join([f"{url}: {status}\n{diag}" for url, status, diag in failed_urls])
            pytest.fail(f"Some x402.json links failed:\n{failure_messages}")

    def test_llms_txt_links_are_reachable(self):
        """Test that URLs in llms.txt are reachable (bounded crawl)."""
        urls = self.collect_urls_from_llms_txt()
        assert len(urls) > 0, "No URLs found in llms.txt"

        # Limit crawl size
        urls_to_test = list(urls)[:MAX_CRAWL_URLS]
        failed_urls = []

        for url in urls_to_test:
            try:
                # Skip non-HTTP URLs and external domains beyond 402.ethys.dev
                parsed = urlparse(url)
                if parsed.scheme not in ["http", "https"]:
                    continue
                if parsed.netloc and "402.ethys.dev" not in parsed.netloc:
                    continue  # Skip external links for now

                response = requests.head(url, timeout=10, allow_redirects=True)
                if response.status_code == 405:
                    response = requests.get(url, timeout=10, allow_redirects=True)

                if response.status_code not in [200, 301, 302, 303, 307, 308, 401, 403]:
                    failed_urls.append((url, response.status_code, get_diagnostic_info(url, response)))
            except requests.RequestException as e:
                failed_urls.append((url, None, f"Request failed: {e}"))

        if failed_urls:
            failure_messages = "\n".join([f"{url}: {status}\n{diag}" for url, status, diag in failed_urls])
            pytest.fail(f"Some llms.txt links failed:\n{failure_messages}")


class TestOpenAPISpec:
    """Test OpenAPI specification endpoint."""

    def test_openapi_endpoint_exists(self):
        """Test that OpenAPI endpoint exists and returns valid spec."""
        url = f"{API_BASE}/docs/openapi"
        response = requests.get(url, timeout=10)

        # Accept JSON or YAML
        content_type = response.headers.get("content-type", "")
        is_json = "json" in content_type
        is_yaml = "yaml" in content_type or "yaml" in content_type

        if response.status_code != 200:
            pytest.fail(
                f"OpenAPI endpoint returned {response.status_code}.\n"
                f"Expected 200. Check /api/v1/402/docs/openapi handler or docs link in llms.txt.\n"
                f"{get_diagnostic_info(url, response)}"
            )

        assert is_json or is_yaml, f"OpenAPI endpoint must return JSON or YAML, got {content_type}"

        # Try to parse
        try:
            if is_json:
                spec = response.json()
            else:
                import yaml
                spec = yaml.safe_load(response.text)

            assert isinstance(spec, dict)
            assert "openapi" in spec or "swagger" in spec
            assert "paths" in spec
        except Exception as e:
            pytest.fail(
                f"OpenAPI spec is not parseable: {e}\n"
                f"Check that /api/v1/402/docs/openapi returns valid OpenAPI (JSON/YAML).\n"
                f"{get_diagnostic_info(url, response)}"
            )


class TestConnectorAlignment:
    """Test that connector/client aligns with live endpoints."""

    def test_connector_base_url_matches(self):
        """Test that default base URL matches production."""
        from ethys402_crewai.client import Ethys402Client

        client = Ethys402Client()
        assert client.base_url == API_BASE, f"Default base URL should be {API_BASE}, got {client.base_url}"

    def test_endpoints_exist_via_head(self):
        """Test that required endpoints exist (HEAD checks where safe)."""
        # Endpoints that should support HEAD or GET
        safe_endpoints = [
            "/info",
            "/discovery/search",
        ]

        for endpoint in safe_endpoints:
            url = f"{API_BASE}{endpoint}"
            try:
                # Try HEAD first
                response = requests.head(url, timeout=10, allow_redirects=True)
                if response.status_code == 405:
                    response = requests.get(url, timeout=10, allow_redirects=True)

                # 200, 3xx, 400 (bad request is OK - endpoint exists), 401/403 (auth required is OK)
                assert response.status_code in [200, 301, 302, 303, 307, 308, 400, 401, 403], (
                    f"Endpoint {endpoint} returned unexpected status {response.status_code}.\n"
                    f"Endpoint may not exist or may have changed.\n"
                    f"{get_diagnostic_info(url, response)}"
                )
            except requests.RequestException as e:
                pytest.fail(f"Failed to reach endpoint {endpoint}: {e}")

    def test_unauthenticated_behavior(self):
        """Test that unauthenticated requests return expected 401/403."""
        # Endpoints that require auth
        auth_endpoints = [
            ("/connect", "POST"),
            ("/telemetry", "POST"),
            ("/trust/score", "GET"),
        ]

        for endpoint, method in auth_endpoints:
            url = f"{API_BASE}{endpoint}"

            try:
                if method == "POST":
                    response = requests.post(url, json={}, timeout=10)
                else:
                    response = requests.get(url, timeout=10)

                # Should return 401 or 403 for unauthenticated requests
                assert response.status_code in [401, 403, 400], (
                    f"Endpoint {endpoint} should return 401/403 for unauthenticated requests, "
                    f"got {response.status_code}.\n"
                    f"Request construction may be incorrect.\n"
                    f"{get_diagnostic_info(url, response)}"
                )

                # Should return structured error
                if response.headers.get("content-type", "").startswith("application/json"):
                    error_data = response.json()
                    assert "error" in error_data or "message" in error_data

            except requests.RequestException as e:
                pytest.fail(f"Failed to test unauthenticated behavior for {endpoint}: {e}")


class TestSchemaDriftDetection:
    """Test for schema/contract drift detection."""

    def test_info_endpoint_schema_stability(self):
        """Test that info endpoint schema matches expected key fields."""
        url = f"{API_BASE}/info"
        response = requests.get(url, timeout=10)
        data = response.json()

        # Check that key fields exist (contract validation)
        required_fields = ["protocol", "onboarding", "pricing", "network"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            pytest.fail(
                f"Info endpoint schema drift detected. Missing fields: {missing_fields}.\n"
                f"Schema may have changed. Update schemas.py and mock_responses.py.\n"
                f"{get_diagnostic_info(url, response)}"
            )

        # Check pricing structure
        pricing = data.get("pricing", {})
        if "activationFee" not in pricing and "token" not in pricing:
            pytest.fail(
                "Info endpoint pricing structure changed. Expected 'activationFee' or 'token'.\n"
                f"Update schemas.py if this is intentional.\n"
                f"{get_diagnostic_info(url, response)}"
            )

    def test_x402_json_schema_stability(self):
        """Test that x402.json schema matches expected structure."""
        url = f"{BASE_URL}/.well-known/x402.json"
        response = requests.get(url, timeout=10)
        data = response.json()

        # Check required top-level fields
        required_fields = ["protocol", "version", "endpoints"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            pytest.fail(
                f"x402.json schema drift detected. Missing fields: {missing_fields}.\n"
                f"Protocol structure may have changed. Update schemas.py.\n"
                f"{get_diagnostic_info(url, response)}"
            )

        # Check that endpoints exist
        endpoints = data.get("endpoints", {})
        if not endpoints:
            pytest.fail(
                "x402.json endpoints section missing or empty.\n"
                f"Protocol structure may have changed.\n"
                f"{get_diagnostic_info(url, response)}"
            )

