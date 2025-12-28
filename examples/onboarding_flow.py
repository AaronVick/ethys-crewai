"""Complete onboarding flow example."""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Crew
from ethys402_crewai import Ethys402Toolkit
from agents import create_onboard_agent, create_onboarding_task


def main():
    """Run complete onboarding flow example."""
    
    # Initialize toolkit
    toolkit = Ethys402Toolkit.from_env()
    
    # Create onboarding agent
    agent = create_onboard_agent(toolkit, agent_name="OnboardAgent")
    
    # Create onboarding task
    task = create_onboarding_task(agent)
    
    # Create and run crew
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )
    
    print("=" * 60)
    print("ETHYS x402 Onboarding Flow Example")
    print("=" * 60)
    print()
    
    result = crew.kickoff()
    
    print()
    print("=" * 60)
    print("Onboarding Complete")
    print("=" * 60)
    print(result)
    
    return result


if __name__ == "__main__":
    main()

