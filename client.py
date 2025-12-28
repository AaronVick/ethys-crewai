"""Main EchoRift client combining all services."""

import os
from typing import Optional

from echorift.arbiter import Arbiter
from echorift.blockwire import BlockWire
from echorift.cronsynth import CronSynth
from echorift.switchboard import Switchboard


class EchoRift:
    """
    Main client for EchoRift infrastructure services.
    
    Provides unified access to all EchoRift services:
    - BlockWire: Blockchain event perception
    - CronSynth: Scheduled triggers
    - Switchboard: Swarm coordination
    - Arbiter: Consensus and locks
    
    Example:
        client = EchoRift(private_key="0x...")
        
        # Access individual services
        client.blockwire.subscribe(...)
        client.cronsynth.create_schedule(...)
        client.switchboard.create_task(...)
        client.arbiter.lock(...)
    """
    
    def __init__(
        self,
        private_key: Optional[str] = None,
        blockwire_url: Optional[str] = None,
        cronsynth_url: Optional[str] = None,
        switchboard_url: Optional[str] = None,
        arbiter_url: Optional[str] = None,
        x402_session: Optional[str] = None,
    ):
        """
        Initialize EchoRift client.
        
        Args:
            private_key: Agent's Ethereum private key for authenticated requests
            blockwire_url: BlockWire API URL
            cronsynth_url: CronSynth API URL
            switchboard_url: Switchboard API URL
            arbiter_url: Arbiter API URL
            x402_session: x402 payment session for paid endpoints
        """
        self._private_key = private_key
        self._x402_session = x402_session
        
        # Initialize service clients
        self._blockwire = BlockWire(
            base_url=blockwire_url,
            x402_session=x402_session,
        )
        
        self._cronsynth = CronSynth(
            base_url=cronsynth_url,
            x402_session=x402_session,
        )
        
        self._switchboard = Switchboard(
            private_key=private_key,
            base_url=switchboard_url,
        )
        
        self._arbiter = Arbiter(
            private_key=private_key,
            base_url=arbiter_url,
        )
    
    @classmethod
    def from_env(cls) -> "EchoRift":
        """
        Create client from environment variables.
        
        Environment variables:
            ECHORIFT_PRIVATE_KEY: Agent's private key
            ECHORIFT_BLOCKWIRE_URL: BlockWire API URL
            ECHORIFT_CRONSYNTH_URL: CronSynth API URL
            ECHORIFT_SWITCHBOARD_URL: Switchboard API URL
            ECHORIFT_ARBITER_URL: Arbiter API URL
            ECHORIFT_X402_SESSION: x402 payment session
        
        Returns:
            Configured EchoRift client
        """
        return cls(
            private_key=os.environ.get("ECHORIFT_PRIVATE_KEY"),
            blockwire_url=os.environ.get("ECHORIFT_BLOCKWIRE_URL"),
            cronsynth_url=os.environ.get("ECHORIFT_CRONSYNTH_URL"),
            switchboard_url=os.environ.get("ECHORIFT_SWITCHBOARD_URL"),
            arbiter_url=os.environ.get("ECHORIFT_ARBITER_URL"),
            x402_session=os.environ.get("ECHORIFT_X402_SESSION"),
        )
    
    @property
    def agent_id(self) -> Optional[str]:
        """Get the agent ID (Ethereum address) for this client."""
        return self._switchboard.agent_id
    
    @property
    def blockwire(self) -> BlockWire:
        """BlockWire client for blockchain event perception."""
        return self._blockwire
    
    @property
    def cronsynth(self) -> CronSynth:
        """CronSynth client for scheduled triggers."""
        return self._cronsynth
    
    @property
    def switchboard(self) -> Switchboard:
        """Switchboard client for swarm coordination."""
        return self._switchboard
    
    @property
    def arbiter(self) -> Arbiter:
        """Arbiter client for consensus and locks."""
        return self._arbiter
    
    def close(self) -> None:
        """Close all service clients."""
        self._blockwire.close()
        self._cronsynth.close()
        self._switchboard.close()
        self._arbiter.close()
    
    def __enter__(self) -> "EchoRift":
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
