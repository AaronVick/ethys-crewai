"""Basic usage example for ETHYS x402 CrewAI integration."""

import os
from crewai import Agent, Crew, Task
from ethys402_crewai import Ethys402Toolkit

# Load environment variables if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def main():
    """Run basic ETHYS x402 agent example."""
    
    # Initialize toolkit from environment
    toolkit = Ethys402Toolkit.from_env()
    
    # Create agent with ETHYS tools
    agent = Agent(
        role="ETHYS Protocol Agent",
        goal="Interact with ETHYS x402 protocol to check status and search for other agents",
        backstory="""You are an autonomous agent using the ETHYS x402 protocol.
        You can connect to the network, check your trust score, and search for other agents.""",
        tools=toolkit.get_tools(),
        verbose=True,
    )
    
    # Create task
    task = Task(
        description="""Perform the following ETHYS operations:
        
        1. Connect to ETHYS x402 protocol (if not already connected)
        2. Check your current trust score
        3. Search the discovery directory for agents with tags related to 'ml' or 'data'
        4. Provide a summary of available agents
        
        Note: If connection fails due to missing payment, provide clear instructions
        on what needs to be done.""",
        expected_output="Connection status, trust score, and list of discovered agents",
        agent=agent,
    )
    
    # Create and run crew
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )
    
    print("=" * 60)
    print("ETHYS x402 CrewAI Basic Usage Example")
    print("=" * 60)
    print()
    
    result = crew.kickoff()
    
    print()
    print("=" * 60)
    print("Execution Complete")
    print("=" * 60)
    print(result)
    
    return result


if __name__ == "__main__":
    main()

