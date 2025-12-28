"""Core ETHYS x402 client with wallet signature authentication."""

import os
import time
from typing import Any, Dict, Optional

import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3


class Ethys402Client:
    """
    Core client for ETHYS x402 protocol interactions.
    
    Handles wallet signature authentication, identity encoding,
    and API communication with the ETHYS x402 backend.
    
    Example:
        client = Ethys402Client(
            private_key="0x...",
            base_url="https://402.ethys.dev/api/v1/402"
        )
        
        # Connect agent
        result = client.connect(agent_name="MyAgent")
    """
    
    def __init__(
        self,
        private_key: Optional[str] = None,
        base_url: str = "https://402.ethys.dev/api/v1/402",
        api_key: Optional[str] = None,
    ):
        """
        Initialize ETHYS x402 client.
        
        Args:
            private_key: Ethereum private key (hex string with 0x prefix)
            base_url: Base URL for the ETHYS x402 API
            api_key: Optional API key for legacy authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        
        if private_key:
            if not private_key.startswith("0x"):
                private_key = "0x" + private_key
            self.account = Account.from_key(private_key)
            self.address = self.account.address
        else:
            self.account = None
            self.address = None
    
    @classmethod
    def from_env(cls) -> "Ethys402Client":
        """
        Create client from environment variables.
        
        Environment variables:
            ETHYS402_PRIVATE_KEY: Ethereum private key
            ETHYS402_API_KEY: Optional API key
            ETHYS402_BASE_URL: Base URL (defaults to production)
        
        Returns:
            Configured Ethys402Client
        """
        return cls(
            private_key=os.environ.get("ETHYS402_PRIVATE_KEY"),
            base_url=os.environ.get("ETHYS402_BASE_URL", "https://402.ethys.dev/api/v1/402"),
            api_key=os.environ.get("ETHYS402_API_KEY"),
        )
    
    def _sign_message(self, message: str) -> str:
        """
        Sign a message with the wallet's private key.
        
        Args:
            message: Message to sign
            
        Returns:
            Signature as hex string
            
        Raises:
            ValueError: If no private key is configured
        """
        if not self.account:
            raise ValueError("Private key required for wallet signing")
        
        message_hash = encode_defunct(text=message)
        signed_message = self.account.sign_message(message_hash)
        return signed_message.signature.hex()
    
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get request headers with optional authentication."""
        headers = {"Content-Type": "application/json"}
        if include_auth and self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def connect(
        self,
        agent_name: Optional[str] = None,
        token_contract: Optional[str] = None,
        token_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Connect agent with wallet signature authentication.
        
        POST /api/v1/402/connect
        
        Args:
            agent_name: Optional agent name for the connection message
            token_contract: ERC-721 token contract address (for ERC-6551 agents)
            token_id: ERC-721 token ID (for ERC-6551 agents)
            
        Returns:
            Connection response with agentId, payment instructions, etc.
            
        Raises:
            ValueError: If no private key is configured
            requests.RequestException: If API request fails
        """
        if not self.account:
            raise ValueError("Private key required for connect endpoint")
        
        message = agent_name or f"Connect to ETHYS x402 - {int(time.time())}"
        signature = self._sign_message(message)
        
        payload: Dict[str, Any] = {
            "address": self.address,
            "signature": signature,
            "message": message,
        }
        
        if token_contract and token_id:
            payload["tokenContract"] = token_contract
            payload["tokenId"] = token_id
        
        response = requests.post(
            f"{self.base_url}/connect",
            json=payload,
            headers=self._get_headers(include_auth=False),
        )
        response.raise_for_status()
        return response.json()
    
    def verify_payment(
        self,
        agent_id: str,
        tx_hash: str,
    ) -> Dict[str, Any]:
        """
        Verify payment transaction and activate agent.
        
        POST /api/v1/402/verify-payment
        
        Args:
            agent_id: Agent ID from connect response
            tx_hash: Transaction hash of the payment transaction
            
        Returns:
            Verification response with API key and activation status
        """
        payload = {
            "agentId": agent_id,
            "txHash": tx_hash,
        }
        
        response = requests.post(
            f"{self.base_url}/verify-payment",
            json=payload,
            headers=self._get_headers(include_auth=False),
        )
        response.raise_for_status()
        result = response.json()
        
        # Store API key if provided
        if "apiKey" in result:
            self.api_key = result["apiKey"]
        
        return result
    
    def submit_telemetry(
        self,
        events: list,
        signature: Optional[str] = None,
        timestamp: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Submit telemetry events (wallet-signed).
        
        POST /api/v1/402/telemetry
        
        Args:
            events: List of telemetry event dictionaries
            signature: Wallet signature (if not provided, will be generated)
            timestamp: Timestamp for signature (if not provided, current time)
            
        Returns:
            Telemetry submission response
        """
        if not self.account:
            raise ValueError("Private key required for wallet-signed telemetry")
        
        timestamp = timestamp or int(time.time())
        
        # Build telemetry payload
        payload: Dict[str, Any] = {
            "agentId": self._get_agent_id_key(),
            "timestamp": timestamp,
            "events": events,
        }
        
        # Create signature message
        import json
        message_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        
        if signature is None:
            signature = self._sign_message(message_str)
        
        payload["signature"] = signature
        payload["address"] = self.address
        
        response = requests.post(
            f"{self.base_url}/telemetry",
            json=payload,
            headers=self._get_headers(include_auth=False),
        )
        response.raise_for_status()
        return response.json()
    
    def get_trust_score(self) -> Dict[str, Any]:
        """
        Get current trust score for authenticated agent.
        
        GET /api/v1/402/trust/score
        
        Returns:
            Trust score response with reliability score and coherence index
        """
        response = requests.get(
            f"{self.base_url}/trust/score",
            headers=self._get_headers(include_auth=True),
        )
        response.raise_for_status()
        return response.json()
    
    def attest_trust(
        self,
        target_agent_id: str,
        score: int,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Submit trust attestation for another agent.
        
        POST /api/v1/402/trust/attest
        
        Args:
            target_agent_id: Agent ID to attest for
            score: Trust score (typically 1-100)
            reason: Reason for the attestation
            
        Returns:
            Attestation response
        """
        payload = {
            "targetAgentId": target_agent_id,
            "score": score,
            "reason": reason,
        }
        
        response = requests.post(
            f"{self.base_url}/trust/attest",
            json=payload,
            headers=self._get_headers(include_auth=True),
        )
        response.raise_for_status()
        return response.json()
    
    def search_discovery(
        self,
        tags: Optional[list] = None,
        min_trust: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search discovery directory for agents.
        
        GET /api/v1/402/discovery/search
        
        Args:
            tags: List of tags to search for
            min_trust: Minimum trust score filter
            
        Returns:
            Search results with matching agents
        """
        params = {}
        if tags:
            params["tags"] = ",".join(tags) if isinstance(tags, list) else tags
        if min_trust is not None:
            params["minTrust"] = min_trust
        
        response = requests.get(
            f"{self.base_url}/discovery/search",
            params=params,
            headers=self._get_headers(include_auth=False),
        )
        response.raise_for_status()
        return response.json()
    
    def _get_agent_id_key(self) -> str:
        """
        Generate agentIdKey from identity.
        
        For EOA agents, agentIdKey is the address (lowercase, checksummed).
        For ERC-6551 agents, this would be keccak256(abi.encode(AgentIdentity)),
        but that requires Solidity ABI encoding which is not implemented here.
        
        Returns:
            Agent ID key string (address for EOA agents)
        """
        if not self.address:
            raise ValueError("Address required for agent ID key")
        # For EOA agents, agentIdKey is the address
        # Protocol spec indicates this should be the address for EOA identities
        return Web3.to_checksum_address(self.address)

