"""
CrewAI + EchoRift Swarm Example

A crew of agents that coordinate using EchoRift infrastructure:
- Scout: Monitors blockchain for opportunities
- Analyst: Evaluates opportunities from the task queue
- Executor: Takes action on approved opportunities
"""

import os
from crewai import Agent, Crew, Task, Process
from crewai_echorift import EchoRiftToolkit

# Initialize toolkit
toolkit = EchoRiftToolkit(
    private_key=os.environ.get("ECHORIFT_PRIVATE_KEY"),
    swarm_id=os.environ.get("ECHORIFT_SWARM_ID", "crewai-example"),
)

# ============================================================================
# Define Agents
# ============================================================================

scout = Agent(
    role="Blockchain Scout",
    goal="Monitor Base L2 for new opportunities and report them to the swarm",
    backstory="""You are a vigilant scout agent that watches the Base blockchain 
    for interesting events. You look for new contract deployments, significant 
    liquidity changes, and price movements. When you find something promising, 
    you create a task in the swarm queue for analysis.""",
    tools=[
        toolkit.blockwire_feed(),
        toolkit.switchboard_create_task(),
        toolkit.switchboard_broadcast(),
    ],
    verbose=True,
)

analyst = Agent(
    role="Opportunity Analyst",
    goal="Analyze opportunities from the task queue and determine their viability",
    backstory="""You are a careful analyst who evaluates opportunities discovered 
    by scout agents. You claim tasks from the queue, perform thorough analysis, 
    and broadcast your findings. You're skeptical by nature and only approve 
    opportunities with strong fundamentals.""",
    tools=[
        toolkit.switchboard_list_tasks(),
        toolkit.switchboard_claim_task(),
        toolkit.switchboard_complete_task(),
        toolkit.switchboard_broadcast(),
        toolkit.switchboard_get_state(),
        toolkit.switchboard_set_state(),
    ],
    verbose=True,
)

executor = Agent(
    role="Swarm Executor",
    goal="Execute approved opportunities with proper coordination",
    backstory="""You are the execution specialist. You listen for analysis results 
    from the swarm and take action on approved opportunities. You always acquire 
    locks before executing to prevent conflicts, and you update shared state 
    with your results.""",
    tools=[
        toolkit.switchboard_get_messages(),
        toolkit.arbiter_acquire_lock(),
        toolkit.arbiter_release_lock(),
        toolkit.switchboard_set_state(),
        toolkit.switchboard_broadcast(),
    ],
    verbose=True,
)

coordinator = Agent(
    role="Swarm Coordinator",
    goal="Maintain swarm health and coordinate agent activities",
    backstory="""You are the coordinator who ensures the swarm operates smoothly. 
    You monitor shared state, check leadership status, and help resolve conflicts. 
    You can trigger elections if needed and create proposals for swarm-wide decisions.""",
    tools=[
        toolkit.switchboard_get_state(),
        toolkit.arbiter_get_leader(),
        toolkit.arbiter_trigger_election(),
        toolkit.arbiter_create_proposal(),
    ],
    verbose=True,
)

# ============================================================================
# Define Tasks
# ============================================================================

scouting_task = Task(
    description="""Monitor the blockchain for new opportunities:
    
    1. Use blockwire_feed to get recent events (new_contract, liquidity_added, price_movement)
    2. For each interesting event, create a task in the swarm queue with type "analyze_opportunity"
    3. Include relevant data: contract address, event type, block number, etc.
    4. Broadcast a summary of what you found to the swarm
    
    Focus on events that could represent trading or investment opportunities.
    Create separate tasks for each distinct opportunity.""",
    expected_output="Summary of opportunities found and tasks created",
    agent=scout,
)

analysis_task = Task(
    description="""Analyze opportunities from the task queue:
    
    1. List queued tasks of type "analyze_opportunity"
    2. Claim an available task
    3. Analyze the opportunity based on the task data
    4. Consider: liquidity depth, contract verification, price trends, risk factors
    5. Complete the task with your analysis result (verdict: approve/reject, reasoning)
    6. Broadcast your analysis to the swarm
    7. If approved, update shared state with the opportunity details
    
    Be thorough but efficient. Only approve opportunities with clear potential.""",
    expected_output="Analysis results for claimed opportunities",
    agent=analyst,
)

execution_task = Task(
    description="""Execute approved opportunities:
    
    1. Get recent messages to find analysis results with "approve" verdicts
    2. For approved opportunities, acquire a lock on the relevant resource
    3. Simulate execution (in real scenario, this would interact with contracts)
    4. Update shared state with execution results
    5. Release the lock
    6. Broadcast execution status to the swarm
    
    Always use locks to prevent double-execution. Be cautious and verify before acting.""",
    expected_output="Execution status for approved opportunities",
    agent=executor,
)

coordination_task = Task(
    description="""Coordinate swarm activities:
    
    1. Check current shared state for active opportunities and results
    2. Verify there is a leader (trigger election if needed)
    3. Review swarm health metrics
    4. If any decisions need swarm consensus, create a proposal
    5. Summarize the current swarm status
    
    Ensure smooth coordination between all swarm members.""",
    expected_output="Swarm coordination status report",
    agent=coordinator,
)

# ============================================================================
# Create and Run Crew
# ============================================================================

def run_crew():
    """Run the coordinated agent crew."""
    crew = Crew(
        agents=[scout, analyst, executor, coordinator],
        tasks=[scouting_task, analysis_task, execution_task, coordination_task],
        process=Process.sequential,  # Run in order for this demo
        verbose=True,
    )
    
    print("=" * 60)
    print("Starting EchoRift-Coordinated CrewAI Swarm")
    print("=" * 60)
    print(f"Swarm ID: {os.environ.get('ECHORIFT_SWARM_ID', 'crewai-example')}")
    print()
    
    result = crew.kickoff()
    
    print()
    print("=" * 60)
    print("Crew Execution Complete")
    print("=" * 60)
    print(result)
    
    return result


if __name__ == "__main__":
    run_crew()
