"""Network scouting example - search and evaluate agents."""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Crew
from ethys402_crewai import Ethys402Toolkit
from agents import create_network_scout, create_scouting_task


def main():
    """Run network scouting example."""
    
    # Initialize toolkit
    toolkit = Ethys402Toolkit.from_env()
    
    # Create network scout agent
    agent = create_network_scout(toolkit, agent_name="NetworkScout")
    
    # Create scouting task with search tags
    task = create_scouting_task(
        agent,
        search_tags=["ml", "data", "ai"]  # Search for ML/data/AI agents
    )
    
    # Create and run crew
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )
    
    print("=" * 60)
    print("ETHYS x402 Network Scouting Example")
    print("=" * 60)
    print()
    
    result = crew.kickoff()
    
    print()
    print("=" * 60)
    print("Network Scouting Complete")
    print("=" * 60)
    print(result)
    
    return result


if __name__ == "__main__":
    main()

