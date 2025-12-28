"""ETHYS x402 toolkit for CrewAI agents."""

from typing import List, Optional

from crewai.tools import BaseTool

from ethys402_crewai.client import Ethys402Client
from ethys402_crewai.tools import (
    AttestTool,
    ConnectTool,
    DiscoverySearchTool,
    TelemetryTool,
    TrustScoreTool,
    VerifyPaymentTool,
)


class Ethys402Toolkit:
    """
    Toolkit providing all ETHYS x402 tools for CrewAI agents.
    
    Example:
        toolkit = Ethys402Toolkit(
            private_key="0x...",
            base_url="https://402.ethys.dev/api/v1/402"
        )
        
        agent = Agent(
            role="ETHYS Agent",
            tools=toolkit.get_tools()
        )
    """
    
    def __init__(
        self,
        private_key: Optional[str] = None,
        base_url: str = "https://402.ethys.dev/api/v1/402",
        api_key: Optional[str] = None,
    ):
        """
        Initialize the toolkit.
        
        Args:
            private_key: Agent's Ethereum private key for wallet signing
            base_url: Base URL for the ETHYS x402 API
            api_key: Optional API key for legacy authentication
        """
        self.client = Ethys402Client(
            private_key=private_key,
            base_url=base_url,
            api_key=api_key,
        )
    
    @classmethod
    def from_env(cls) -> "Ethys402Toolkit":
        """
        Create toolkit from environment variables.
        
        Environment variables:
            ETHYS402_PRIVATE_KEY: Agent's private key
            ETHYS402_BASE_URL: Base URL (defaults to production)
            ETHYS402_API_KEY: Optional API key
        
        Returns:
            Configured Ethys402Toolkit
        """
        import os
        return cls(
            private_key=os.environ.get("ETHYS402_PRIVATE_KEY"),
            base_url=os.environ.get(
                "ETHYS402_BASE_URL",
                "https://402.ethys.dev/api/v1/402"
            ),
            api_key=os.environ.get("ETHYS402_API_KEY"),
        )
    
    def get_tools(self) -> List[BaseTool]:
        """
        Get all available ETHYS x402 tools.
        
        Returns:
            List of all ETHYS x402 tools configured for this toolkit
        """
        return [
            self.connect(),
            self.verify_payment(),
            self.submit_telemetry(),
            self.get_trust_score(),
            self.attest_trust(),
            self.search_discovery(),
        ]
    
    # ========================================================================
    # Core Tools
    # ========================================================================
    
    def connect(self) -> ConnectTool:
        """Get Connect tool for agent onboarding."""
        return ConnectTool(client=self.client)
    
    def verify_payment(self) -> VerifyPaymentTool:
        """Get Verify Payment tool."""
        return VerifyPaymentTool(client=self.client)
    
    def submit_telemetry(self) -> TelemetryTool:
        """Get Telemetry submission tool."""
        return TelemetryTool(client=self.client)
    
    def get_trust_score(self) -> TrustScoreTool:
        """Get Trust Score query tool."""
        return TrustScoreTool(client=self.client)
    
    def attest_trust(self) -> AttestTool:
        """Get Trust Attestation tool."""
        return AttestTool(client=self.client)
    
    def search_discovery(self) -> DiscoverySearchTool:
        """Get Discovery Search tool."""
        return DiscoverySearchTool(client=self.client)

