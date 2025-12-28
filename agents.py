"""Reference CrewAI agent templates for ETHYS x402."""

from typing import Optional

from crewai import Agent, Task
from crewai.tools import BaseTool

from ethys402_crewai.toolkit import Ethys402Toolkit


def create_onboard_agent(
    toolkit: Ethys402Toolkit,
    agent_name: str = "OnboardAgent",
    verbose: bool = True,
) -> Agent:
    """
    Create an OnboardAgent that handles agent onboarding flow.
    
    This agent connects, checks balance, guides payment, verifies, and registers discovery.
    
    Args:
        toolkit: ETHYS x402 toolkit instance
        agent_name: Name for the agent
        verbose: Enable verbose output
        
    Returns:
        Configured CrewAI Agent
    """
    tools = [
        toolkit.connect(),
        toolkit.verify_payment(),
        toolkit.search_discovery(),
    ]
    
    return Agent(
        role="ETHYS Onboarding Specialist",
        goal="Guide agents through the ETHYS x402 onboarding process: connect, verify payment, and register for discovery",
        backstory="""You are an expert at helping autonomous agents onboard to the ETHYS x402 protocol.
        You understand the payment workflow, contract interactions, and registration requirements.
        You provide clear step-by-step guidance and verify each step completes successfully.""",
        tools=tools,
        verbose=verbose,
    )


def create_reputation_reporter(
    toolkit: Ethys402Toolkit,
    agent_name: str = "ReputationReporter",
    verbose: bool = True,
) -> Agent:
    """
    Create a ReputationReporter agent that submits telemetry and checks scores.
    
    Args:
        toolkit: ETHYS x402 toolkit instance
        agent_name: Name for the agent
        verbose: Enable verbose output
        
    Returns:
        Configured CrewAI Agent
    """
    tools = [
        toolkit.submit_telemetry(),
        toolkit.get_trust_score(),
        toolkit.attest_trust(),
    ]
    
    return Agent(
        role="Reputation & Trust Manager",
        goal="Monitor and report agent reputation by submitting telemetry and tracking trust scores",
        backstory="""You are responsible for maintaining the agent's reputation on ETHYS.
        You regularly submit telemetry data about agent performance, check trust scores,
        and provide attestations for other agents when appropriate.""",
        tools=tools,
        verbose=verbose,
    )


def create_network_scout(
    toolkit: Ethys402Toolkit,
    agent_name: str = "NetworkScout",
    verbose: bool = True,
) -> Agent:
    """
    Create a NetworkScout agent that searches discovery and evaluates candidates.
    
    Args:
        toolkit: ETHYS x402 toolkit instance
        agent_name: Name for the agent
        verbose: Enable verbose output
        
    Returns:
        Configured CrewAI Agent
    """
    tools = [
        toolkit.search_discovery(),
        toolkit.get_trust_score(),
        toolkit.attest_trust(),
    ]
    
    return Agent(
        role="Network Discovery Specialist",
        goal="Search the ETHYS network for potential partners, collaborators, and service providers",
        backstory="""You are an expert at finding and evaluating agents in the ETHYS network.
        You search the discovery directory by tags and trust scores, evaluate potential partners,
        and help build strategic connections.""",
        tools=tools,
        verbose=verbose,
    )


def create_onboarding_task(agent: Agent) -> Task:
    """
    Create an onboarding task for the OnboardAgent.
    
    Args:
        agent: The onboarding agent
        
    Returns:
        Configured Task
    """
    return Task(
        description="""Complete the ETHYS x402 onboarding process:
        
        1. Connect to the ETHYS x402 protocol using your wallet signature
        2. Check the payment requirements and instructions
        3. Guide the user through acquiring ETHYS tokens if needed
        4. Verify payment once the transaction is complete
        5. Search the discovery directory to see what agents are available
        
        Provide clear status updates at each step.""",
        expected_output="Onboarding complete status with agent ID and payment verification confirmation",
        agent=agent,
    )


def create_reputation_task(agent: Agent) -> Task:
    """
    Create a reputation reporting task for the ReputationReporter.
    
    Args:
        agent: The reputation reporter agent
        
    Returns:
        Configured Task
    """
    return Task(
        description="""Monitor and report agent reputation:
        
        1. Check current trust score (reliability and coherence index)
        2. Submit telemetry events about recent agent activity
        3. Provide a summary of reputation status
        
        Include specific metrics and any recommendations for improvement.""",
        expected_output="Reputation report with trust score, telemetry submission status, and recommendations",
        agent=agent,
    )


def create_scouting_task(agent: Agent, search_tags: Optional[list] = None) -> Task:
    """
    Create a network scouting task for the NetworkScout.
    
    Args:
        agent: The network scout agent
        search_tags: Optional list of tags to search for
        
    Returns:
        Configured Task
    """
    tags_str = f" with tags: {', '.join(search_tags)}" if search_tags else ""
    
    return Task(
        description=f"""Search the ETHYS network for potential partners{tags_str}:
        
        1. Search the discovery directory for agents matching the criteria
        2. Evaluate the trust scores and capabilities of found agents
        3. Provide recommendations on potential collaborators
        
        Focus on agents with strong trust scores and relevant capabilities.""",
        expected_output="List of discovered agents with trust scores and evaluation recommendations",
        agent=agent,
    )

