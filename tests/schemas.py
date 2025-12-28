"""Pydantic schemas for validating ETHYS x402 API responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class TokenInfo(BaseModel):
    """Token information schema."""

    address: str = Field(pattern=r"^0x[a-fA-F0-9]{40}$")
    symbol: str
    decimals: int = Field(ge=0, le=18)


class PaymentInfo(BaseModel):
    """Payment information schema."""

    amount: str
    token: TokenInfo
    contract: Optional[Dict[str, Any]] = None


class ConnectResponse(BaseModel):
    """Connect endpoint response schema."""

    success: bool
    agentId: str = Field(min_length=1)
    payment: PaymentInfo
    instructions: Optional[str] = None


class VerifyPaymentResponse(BaseModel):
    """Verify payment endpoint response schema."""

    success: bool
    agentId: str
    apiKey: Optional[str] = None
    activated: bool
    message: str


class TrustScore(BaseModel):
    """Trust score component schema."""

    rs: float = Field(ge=0, le=100, description="Reliability score")
    ci: float = Field(ge=0, le=1, description="Coherence index")


class TrustScoreResponse(BaseModel):
    """Trust score endpoint response schema."""

    success: bool
    agentId: str
    trustScore: TrustScore
    updatedAt: int = Field(ge=0)


class TrustAttestResponse(BaseModel):
    """Trust attestation response schema."""

    success: bool
    attestationId: str
    targetAgentId: str
    score: int = Field(ge=1, le=100)
    message: str


class TelemetryResponse(BaseModel):
    """Telemetry submission response schema."""

    success: bool
    recorded: int = Field(ge=0)
    timestamp: int = Field(ge=0)
    message: str


class AgentProfile(BaseModel):
    """Agent profile in discovery results."""

    name: Optional[str] = None
    uri: Optional[str] = None


class DiscoveryAgent(BaseModel):
    """Agent in discovery search results."""

    agentId: str
    tags: List[str] = Field(default_factory=list)
    minTrust: Optional[int] = None
    profile: Optional[AgentProfile] = None
    trustScore: Optional[TrustScore] = None


class DiscoverySearchResponse(BaseModel):
    """Discovery search endpoint response schema."""

    success: bool
    agents: List[DiscoveryAgent]
    total: Optional[int] = None


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    message: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ProtocolInfo(BaseModel):
    """Protocol info endpoint schema (key fields only)."""

    protocol: str = Field(default="x402")
    version: str
    onboarding: Dict[str, Any]
    pricing: Dict[str, Any]
    network: Dict[str, Any]


class X402Protocol(BaseModel):
    """x402.json protocol discovery schema (key fields)."""

    protocol: str = Field(default="x402")
    version: str
    pathways: Dict[str, Any]
    identity: Dict[str, Any]
    contracts: Dict[str, Any]
    endpoints: Dict[str, str]


def validate_connect_response(data: Dict[str, Any]) -> ConnectResponse:
    """Validate and parse connect response."""
    return ConnectResponse(**data)


def validate_verify_payment_response(data: Dict[str, Any]) -> VerifyPaymentResponse:
    """Validate and parse verify payment response."""
    return VerifyPaymentResponse(**data)


def validate_trust_score_response(data: Dict[str, Any]) -> TrustScoreResponse:
    """Validate and parse trust score response."""
    return TrustScoreResponse(**data)


def validate_telemetry_response(data: Dict[str, Any]) -> TelemetryResponse:
    """Validate and parse telemetry response."""
    return TelemetryResponse(**data)


def validate_discovery_response(data: Dict[str, Any]) -> DiscoverySearchResponse:
    """Validate and parse discovery search response."""
    return DiscoverySearchResponse(**data)


def validate_error_response(data: Dict[str, Any]) -> ErrorResponse:
    """Validate and parse error response."""
    return ErrorResponse(**data)


def validate_protocol_info(data: Dict[str, Any]) -> ProtocolInfo:
    """Validate protocol info endpoint response (key fields only)."""
    return ProtocolInfo(**data)


def validate_x402_json(data: Dict[str, Any]) -> X402Protocol:
    """Validate x402.json protocol discovery document."""
    return X402Protocol(**data)

