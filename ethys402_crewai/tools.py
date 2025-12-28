"""CrewAI tools for ETHYS x402 protocol."""

from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ConnectToolInput(BaseModel):
    """Input for ConnectTool."""
    
    agent_name: Optional[str] = Field(
        default=None,
        description="Optional name for the agent connection"
    )
    token_contract: Optional[str] = Field(
        default=None,
        description="ERC-721 token contract address (for ERC-6551 agents)"
    )
    token_id: Optional[str] = Field(
        default=None,
        description="ERC-721 token ID (for ERC-6551 agents)"
    )


class ConnectTool(BaseTool):
    """
    Tool for connecting an agent to ETHYS x402 protocol.
    
    Wraps POST /api/v1/402/connect with wallet signature authentication.
    Returns agent ID and payment instructions.
    """
    
    name: str = "ethys402_connect"
    description: str = (
        "Connect agent to ETHYS x402 protocol with wallet signature. "
        "Returns agent ID and payment instructions. "
        "Use this first before any other ETHYS operations."
    )
    args_schema: Type[BaseModel] = ConnectToolInput
    
    def __init__(self, client):
        super().__init__()
        self.client = client
    
    def _run(
        self,
        agent_name: Optional[str] = None,
        token_contract: Optional[str] = None,
        token_id: Optional[str] = None,
    ) -> str:
        """Execute the connect operation."""
        try:
            result = self.client.connect(
                agent_name=agent_name,
                token_contract=token_contract,
                token_id=token_id,
            )
            return f"Connected successfully. Agent ID: {result.get('agentId')}. Payment required: {result.get('payment', {}).get('amount', 'N/A')} ETHYS tokens."
        except Exception as e:
            return f"Connection failed: {str(e)}"


class VerifyPaymentToolInput(BaseModel):
    """Input for VerifyPaymentTool."""
    
    agent_id: str = Field(description="Agent ID from connect response")
    tx_hash: str = Field(description="Transaction hash of the payment transaction")


class VerifyPaymentTool(BaseTool):
    """
    Tool for verifying payment transaction.
    
    Wraps POST /api/v1/402/verify-payment.
    Activates agent access after payment confirmation.
    """
    
    name: str = "ethys402_verify_payment"
    description: str = (
        "Verify payment transaction and activate agent access. "
        "Submit the transaction hash from the buyTierAuto() contract call. "
        "Returns API key upon successful verification."
    )
    args_schema: Type[BaseModel] = VerifyPaymentToolInput
    
    def __init__(self, client):
        super().__init__()
        self.client = client
    
    def _run(self, agent_id: str, tx_hash: str) -> str:
        """Execute the payment verification."""
        try:
            result = self.client.verify_payment(agent_id=agent_id, tx_hash=tx_hash)
            return f"Payment verified successfully. Agent activated. API key: {result.get('apiKey', 'N/A')}"
        except Exception as e:
            return f"Payment verification failed: {str(e)}"


class TelemetryToolInput(BaseModel):
    """Input for TelemetryTool."""
    
    events: list = Field(
        description="List of telemetry event dictionaries. Each event should have 'type' and 'data' fields."
    )


class TelemetryTool(BaseTool):
    """
    Tool for submitting telemetry events.
    
    Wraps POST /api/v1/402/telemetry with wallet-signed payload.
    """
    
    name: str = "ethys402_submit_telemetry"
    description: str = (
        "Submit telemetry/metrics events for agent monitoring. "
        "Events are wallet-signed for authentication. "
        "Each event should have 'type' and 'data' fields."
    )
    args_schema: Type[BaseModel] = TelemetryToolInput
    
    def __init__(self, client):
        super().__init__()
        self.client = client
    
    def _run(self, events: list) -> str:
        """Execute the telemetry submission."""
        try:
            result = self.client.submit_telemetry(events=events)
            return f"Telemetry submitted successfully. Recorded {len(events)} events."
        except Exception as e:
            return f"Telemetry submission failed: {str(e)}"


class TrustScoreToolInput(BaseModel):
    """Input for TrustScoreTool."""
    
    pass


class TrustScoreTool(BaseTool):
    """
    Tool for reading current trust score.
    
    Wraps GET /api/v1/402/trust/score.
    """
    
    name: str = "ethys402_get_trust_score"
    description: str = (
        "Get the current trust score and components for the authenticated agent. "
        "Returns reliability score (rs) and coherence index (ci)."
    )
    args_schema: Type[BaseModel] = TrustScoreToolInput
    
    def __init__(self, client):
        super().__init__()
        self.client = client
    
    def _run(self) -> str:
        """Execute the trust score query."""
        try:
            result = self.client.get_trust_score()
            trust_score = result.get("trustScore", {})
            return f"Trust Score - Reliability: {trust_score.get('rs', 'N/A')}, Coherence Index: {trust_score.get('ci', 'N/A')}"
        except Exception as e:
            return f"Failed to get trust score: {str(e)}"


class AttestToolInput(BaseModel):
    """Input for AttestTool."""
    
    target_agent_id: str = Field(description="Agent ID to attest for")
    score: int = Field(description="Trust score (typically 1-100)", ge=1, le=100)
    reason: str = Field(description="Reason for the attestation")


class AttestTool(BaseTool):
    """
    Tool for submitting trust attestations.
    
    Wraps POST /api/v1/402/trust/attest.
    """
    
    name: str = "ethys402_attest_trust"
    description: str = (
        "Submit a trust attestation for another agent. "
        "Score should be between 1-100. Include a reason for the attestation."
    )
    args_schema: Type[BaseModel] = AttestToolInput
    
    def __init__(self, client):
        super().__init__()
        self.client = client
    
    def _run(self, target_agent_id: str, score: int, reason: str) -> str:
        """Execute the trust attestation."""
        try:
            result = self.client.attest_trust(
                target_agent_id=target_agent_id,
                score=score,
                reason=reason,
            )
            return f"Trust attestation submitted successfully for agent {target_agent_id} with score {score}."
        except Exception as e:
            return f"Trust attestation failed: {str(e)}"


class DiscoverySearchToolInput(BaseModel):
    """Input for DiscoverySearchTool."""
    
    tags: Optional[list] = Field(
        default=None,
        description="List of tags to search for (comma-separated string also accepted)"
    )
    min_trust: Optional[int] = Field(
        default=None,
        description="Minimum trust score filter"
    )


class DiscoverySearchTool(BaseTool):
    """
    Tool for searching the discovery directory.
    
    Wraps GET /api/v1/402/discovery/search.
    """
    
    name: str = "ethys402_search_discovery"
    description: str = (
        "Search for agents in the discovery directory by tags and minimum trust score. "
        "Returns matching agents with their profiles and capabilities."
    )
    args_schema: Type[BaseModel] = DiscoverySearchToolInput
    
    def __init__(self, client):
        super().__init__()
        self.client = client
    
    def _run(
        self,
        tags: Optional[list] = None,
        min_trust: Optional[int] = None,
    ) -> str:
        """Execute the discovery search."""
        try:
            result = self.client.search_discovery(tags=tags, min_trust=min_trust)
            agents = result.get("agents", [])
            if not agents:
                return "No agents found matching the search criteria."
            
            summary = f"Found {len(agents)} agent(s):\n"
            for agent in agents[:10]:  # Limit to first 10
                agent_id = agent.get("agentId", "Unknown")
                tags_str = ", ".join(agent.get("tags", []))
                summary += f"- {agent_id}: {tags_str}\n"
            
            if len(agents) > 10:
                summary += f"... and {len(agents) - 10} more"
            
            return summary
        except Exception as e:
            return f"Discovery search failed: {str(e)}"

