"""Mock ETHYS x402 API responses for deterministic testing."""

# Mock responses based on actual ETHYS x402 protocol structure
# Derived from https://402.ethys.dev/.well-known/x402.json and API documentation

MOCK_X402_JSON = {
    "protocol": "x402",
    "version": "2.0.0",
    "pathways": {
        "api": {
            "description": "API pathway - backend prepares transactions",
            "recommended": True,
            "docs": "/docs/agent-quick-start.md"
        }
    },
    "identity": {
        "version": "1",
        "supportedTypes": ["EOA", "ERC6551"],
        "encoding": "AgentIdentity struct with versioned abi.encode",
        "keying": "agentIdKey = keccak256(abi.encode(AgentIdentity))"
    },
    "contracts": {
        "v2": {
            "network": "base-mainnet",
            "chainId": 8453,
            "addresses": {
                "ETHYSAgentRegistryV2": "0x91f2d727d20a2CB739C0a1366c1c991120F91EF9",
                "ETHYSTierPurchasesV2": "0x1AB4434AF31AF4b8564c4bB12B6aD417B97923b8",
                "ETHYS": "0x1Dd996287dB5a95D6C9236EfB10C7f90145e5B07"
            }
        }
    },
    "endpoints": {
        "connect": "/api/v1/402/connect",
        "verifyPayment": "/api/v1/402/verify-payment",
        "telemetry": "/api/v1/402/telemetry",
        "trustScore": "/api/v1/402/trust/score",
        "trustAttest": "/api/v1/402/trust/attest",
        "discoverySearch": "/api/v1/402/discovery/search"
    }
}

MOCK_INFO_RESPONSE = {
    "protocol": "x402",
    "name": "ETHYS x402 Protocol",
    "version": "1.0.0",
    "onboarding": {
        "steps": [
            {
                "step": 1,
                "title": "Connect with Wallet",
                "endpoint": "POST /api/v1/402/connect"
            },
            {
                "step": 3,
                "title": "Approve & Pay via Contract",
                "details": {
                    "payment": {
                        "contract": "0x5BA13d7183603cB42240a80Fe76A73D7750287Ec",
                        "function": "buyTierAuto(tuple identity, uint256 tierId, uint256 tokenAmount, bytes32 backendRef)"
                    }
                }
            },
            {
                "step": 5,
                "title": "Verify Payment",
                "endpoint": "POST /api/v1/402/verify-payment"
            }
        ]
    },
    "pricing": {
        "activationFee": {
            "usd": 150,
            "tokenAmount": "150.000000"
        },
        "token": {
            "address": "0x1Dd996287dB5a95D6C9236EfB10C7f90145e5B07",
            "symbol": "ETHYS",
            "decimals": 18
        }
    },
    "network": {
        "name": "Base",
        "chainId": 8453
    }
}

MOCK_CONNECT_RESPONSE = {
    "success": True,
    "agentId": "agent_abc123def456",
    "payment": {
        "amount": "150.000000",
        "token": {
            "address": "0x1Dd996287dB5a95D6C9236EfB10C7f90145e5B07",
            "symbol": "ETHYS"
        },
        "contract": {
            "address": "0x1AB4434AF31AF4b8564c4bB12B6aD417B97923b8",
            "function": "buyTierAuto"
        }
    },
    "instructions": "Approve ETHYS tokens and call buyTierAuto() on the purchase contract"
}

MOCK_VERIFY_PAYMENT_RESPONSE = {
    "success": True,
    "agentId": "agent_abc123def456",
    "apiKey": "api_key_xyz789",
    "activated": True,
    "message": "Payment verified, agent activated"
}

MOCK_TELEMETRY_RESPONSE = {
    "success": True,
    "recorded": 2,
    "timestamp": 1703847600,
    "message": "Telemetry events recorded successfully"
}

MOCK_TRUST_SCORE_RESPONSE = {
    "success": True,
    "agentId": "agent_abc123def456",
    "trustScore": {
        "rs": 85.5,
        "ci": 0.92
    },
    "updatedAt": 1703847600
}

MOCK_TRUST_ATTEST_RESPONSE = {
    "success": True,
    "attestationId": "attest_123",
    "targetAgentId": "agent_target456",
    "score": 90,
    "message": "Trust attestation submitted successfully"
}

MOCK_DISCOVERY_SEARCH_RESPONSE = {
    "success": True,
    "agents": [
        {
            "agentId": "agent_xyz789",
            "tags": ["ml", "data", "ai"],
            "minTrust": 80,
            "profile": {
                "name": "ML Research Agent",
                "uri": "https://example.com/agent-profile"
            },
            "trustScore": {
                "rs": 88.5,
                "ci": 0.95
            }
        },
        {
            "agentId": "agent_def456",
            "tags": ["ml", "research"],
            "minTrust": 75,
            "trustScore": {
                "rs": 82.3,
                "ci": 0.89
            }
        }
    ],
    "total": 2
}

MOCK_ERROR_RESPONSE_401 = {
    "error": "Unauthorized",
    "message": "Invalid signature or missing authentication",
    "code": "AUTH_ERROR"
}

MOCK_ERROR_RESPONSE_400 = {
    "error": "Bad Request",
    "message": "Invalid request format",
    "code": "VALIDATION_ERROR",
    "details": {
        "field": "events",
        "issue": "Must be a non-empty array"
    }
}

MOCK_ERROR_RESPONSE_402 = {
    "error": "Payment Required",
    "message": "Agent payment not verified",
    "code": "PAYMENT_REQUIRED"
}

MOCK_ERROR_RESPONSE_404 = {
    "error": "Not Found",
    "message": "Agent not found",
    "code": "NOT_FOUND"
}

MOCK_ERROR_RESPONSE_500 = {
    "error": "Internal Server Error",
    "message": "An unexpected error occurred",
    "code": "INTERNAL_ERROR"
}

