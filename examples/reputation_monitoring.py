"""Reputation monitoring example with telemetry submission."""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Crew
from ethys402_crewai import Ethys402Toolkit
from agents import create_reputation_reporter, create_reputation_task


def main():
    """Run reputation monitoring example."""
    
    # Initialize toolkit
    toolkit = Ethys402Toolkit.from_env()
    
    # Create reputation reporter agent
    agent = create_reputation_reporter(toolkit, agent_name="ReputationReporter")
    
    # Create reputation task
    task = create_reputation_task(agent)
    
    # Create and run crew
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )
    
    print("=" * 60)
    print("ETHYS x402 Reputation Monitoring Example")
    print("=" * 60)
    print()
    
    result = crew.kickoff()
    
    print()
    print("=" * 60)
    print("Reputation Report Complete")
    print("=" * 60)
    print(result)
    
    return result


if __name__ == "__main__":
    main()

