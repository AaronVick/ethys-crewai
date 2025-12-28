"""EchoRift toolkit for CrewAI."""

import os
from typing import List, Optional

from crewai.tools import BaseTool

from echorift import EchoRift, Arbiter, BlockWire, CronSynth, Switchboard
from crewai_echorift.tools import (
    BlockWireFeedTool,
    BlockWireSubscribeTool,
    CronSynthScheduleTool,
    CronSynthListTool,
    CronSynthDeleteTool,
    SwitchboardCreateTaskTool,
    SwitchboardListTasksTool,
    SwitchboardClaimTaskTool,
    SwitchboardCompleteTaskTool,
    SwitchboardFailTaskTool,
    SwitchboardBroadcastTool,
    SwitchboardGetMessagesTool,
    SwitchboardGetStateTool,
    SwitchboardSetStateTool,
    ArbiterAcquireLockTool,
    ArbiterReleaseLockTool,
    ArbiterGetLeaderTool,
    ArbiterTriggerElectionTool,
    ArbiterVoteElectionTool,
    ArbiterCreateProposalTool,
    ArbiterVoteProposalTool,
)


class EchoRiftToolkit:
    """
    Toolkit providing all EchoRift tools for CrewAI agents.
    
    Example:
        toolkit = EchoRiftToolkit(
            private_key="0x...",
            swarm_id="my-swarm"
        )
        
        agent = Agent(
            role="Coordinator",
            tools=toolkit.get_tools()
        )
    """
    
    def __init__(
        self,
        private_key: Optional[str] = None,
        swarm_id: Optional[str] = None,
        blockwire_url: Optional[str] = None,
        cronsynth_url: Optional[str] = None,
        switchboard_url: Optional[str] = None,
        arbiter_url: Optional[str] = None,
        x402_session: Optional[str] = None,
    ):
        """
        Initialize the toolkit.
        
        Args:
            private_key: Agent's Ethereum private key
            swarm_id: Default swarm ID for Switchboard/Arbiter operations
            blockwire_url: BlockWire API URL
            cronsynth_url: CronSynth API URL
            switchboard_url: Switchboard API URL
            arbiter_url: Arbiter API URL
            x402_session: x402 payment session
        """
        self._swarm_id = swarm_id
        
        # Initialize service clients
        self._blockwire = BlockWire(base_url=blockwire_url, x402_session=x402_session)
        self._cronsynth = CronSynth(base_url=cronsynth_url, x402_session=x402_session)
        self._switchboard = Switchboard(private_key=private_key, base_url=switchboard_url) if private_key else None
        self._arbiter = Arbiter(private_key=private_key, base_url=arbiter_url) if private_key else None
    
    @classmethod
    def from_env(cls) -> "EchoRiftToolkit":
        """
        Create toolkit from environment variables.
        
        Environment variables:
            ECHORIFT_PRIVATE_KEY: Agent's private key
            ECHORIFT_SWARM_ID: Default swarm ID
            ECHORIFT_BLOCKWIRE_URL: BlockWire API URL
            ECHORIFT_CRONSYNTH_URL: CronSynth API URL
            ECHORIFT_SWITCHBOARD_URL: Switchboard API URL
            ECHORIFT_ARBITER_URL: Arbiter API URL
            ECHORIFT_X402_SESSION: x402 payment session
        """
        return cls(
            private_key=os.environ.get("ECHORIFT_PRIVATE_KEY"),
            swarm_id=os.environ.get("ECHORIFT_SWARM_ID"),
            blockwire_url=os.environ.get("ECHORIFT_BLOCKWIRE_URL"),
            cronsynth_url=os.environ.get("ECHORIFT_CRONSYNTH_URL"),
            switchboard_url=os.environ.get("ECHORIFT_SWITCHBOARD_URL"),
            arbiter_url=os.environ.get("ECHORIFT_ARBITER_URL"),
            x402_session=os.environ.get("ECHORIFT_X402_SESSION"),
        )
    
    def get_tools(self) -> List[BaseTool]:
        """
        Get all available tools.
        
        Returns:
            List of all EchoRift tools configured for this toolkit
        """
        tools = []
        
        # BlockWire tools (always available)
        tools.extend([
            self.blockwire_feed(),
            self.blockwire_subscribe(),
        ])
        
        # CronSynth tools (always available)
        tools.extend([
            self.cronsynth_schedule(),
            self.cronsynth_list(),
            self.cronsynth_delete(),
        ])
        
        # Switchboard tools (require swarm_id and private_key)
        if self._switchboard and self._swarm_id:
            tools.extend([
                self.switchboard_create_task(),
                self.switchboard_list_tasks(),
                self.switchboard_claim_task(),
                self.switchboard_complete_task(),
                self.switchboard_fail_task(),
                self.switchboard_broadcast(),
                self.switchboard_get_messages(),
                self.switchboard_get_state(),
                self.switchboard_set_state(),
            ])
        
        # Arbiter tools (require swarm_id and private_key)
        if self._arbiter and self._swarm_id:
            tools.extend([
                self.arbiter_acquire_lock(),
                self.arbiter_release_lock(),
                self.arbiter_get_leader(),
                self.arbiter_trigger_election(),
                self.arbiter_vote_election(),
                self.arbiter_create_proposal(),
                self.arbiter_vote_proposal(),
            ])
        
        return tools
    
    # ========================================================================
    # BlockWire Tools
    # ========================================================================
    
    def blockwire_feed(self) -> BlockWireFeedTool:
        """Get BlockWire feed tool."""
        return BlockWireFeedTool(client=self._blockwire)
    
    def blockwire_subscribe(self) -> BlockWireSubscribeTool:
        """Get BlockWire subscribe tool."""
        return BlockWireSubscribeTool(client=self._blockwire)
    
    # ========================================================================
    # CronSynth Tools
    # ========================================================================
    
    def cronsynth_schedule(self) -> CronSynthScheduleTool:
        """Get CronSynth schedule tool."""
        return CronSynthScheduleTool(client=self._cronsynth)
    
    def cronsynth_list(self) -> CronSynthListTool:
        """Get CronSynth list tool."""
        return CronSynthListTool(client=self._cronsynth)
    
    def cronsynth_delete(self) -> CronSynthDeleteTool:
        """Get CronSynth delete tool."""
        return CronSynthDeleteTool(client=self._cronsynth)
    
    # ========================================================================
    # Switchboard Tools
    # ========================================================================
    
    def switchboard_create_task(self, swarm_id: Optional[str] = None) -> SwitchboardCreateTaskTool:
        """Get Switchboard create task tool."""
        return SwitchboardCreateTaskTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._switchboard,
        )
    
    def switchboard_list_tasks(self, swarm_id: Optional[str] = None) -> SwitchboardListTasksTool:
        """Get Switchboard list tasks tool."""
        return SwitchboardListTasksTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._switchboard,
        )
    
    def switchboard_claim_task(self, swarm_id: Optional[str] = None) -> SwitchboardClaimTaskTool:
        """Get Switchboard claim task tool."""
        return SwitchboardClaimTaskTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._switchboard,
        )
    
    def switchboard_complete_task(self, swarm_id: Optional[str] = None) -> SwitchboardCompleteTaskTool:
        """Get Switchboard complete task tool."""
        return SwitchboardCompleteTaskTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._switchboard,
        )
    
    def switchboard_fail_task(self, swarm_id: Optional[str] = None) -> SwitchboardFailTaskTool:
        """Get Switchboard fail task tool."""
        return SwitchboardFailTaskTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._switchboard,
        )
    
    def switchboard_broadcast(self, swarm_id: Optional[str] = None) -> SwitchboardBroadcastTool:
        """Get Switchboard broadcast tool."""
        return SwitchboardBroadcastTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._switchboard,
        )
    
    def switchboard_get_messages(self, swarm_id: Optional[str] = None) -> SwitchboardGetMessagesTool:
        """Get Switchboard get messages tool."""
        return SwitchboardGetMessagesTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._switchboard,
        )
    
    def switchboard_get_state(self, swarm_id: Optional[str] = None) -> SwitchboardGetStateTool:
        """Get Switchboard get state tool."""
        return SwitchboardGetStateTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._switchboard,
        )
    
    def switchboard_set_state(self, swarm_id: Optional[str] = None) -> SwitchboardSetStateTool:
        """Get Switchboard set state tool."""
        return SwitchboardSetStateTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._switchboard,
        )
    
    # ========================================================================
    # Arbiter Tools
    # ========================================================================
    
    def arbiter_acquire_lock(self, swarm_id: Optional[str] = None) -> ArbiterAcquireLockTool:
        """Get Arbiter acquire lock tool."""
        return ArbiterAcquireLockTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._arbiter,
        )
    
    def arbiter_release_lock(self) -> ArbiterReleaseLockTool:
        """Get Arbiter release lock tool."""
        return ArbiterReleaseLockTool(client=self._arbiter)
    
    def arbiter_get_leader(self, swarm_id: Optional[str] = None) -> ArbiterGetLeaderTool:
        """Get Arbiter get leader tool."""
        return ArbiterGetLeaderTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._arbiter,
        )
    
    def arbiter_trigger_election(self, swarm_id: Optional[str] = None) -> ArbiterTriggerElectionTool:
        """Get Arbiter trigger election tool."""
        return ArbiterTriggerElectionTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._arbiter,
        )
    
    def arbiter_vote_election(self) -> ArbiterVoteElectionTool:
        """Get Arbiter vote election tool."""
        return ArbiterVoteElectionTool(client=self._arbiter)
    
    def arbiter_create_proposal(self, swarm_id: Optional[str] = None) -> ArbiterCreateProposalTool:
        """Get Arbiter create proposal tool."""
        return ArbiterCreateProposalTool(
            swarm_id=swarm_id or self._swarm_id,
            client=self._arbiter,
        )
    
    def arbiter_vote_proposal(self) -> ArbiterVoteProposalTool:
        """Get Arbiter vote proposal tool."""
        return ArbiterVoteProposalTool(client=self._arbiter)
