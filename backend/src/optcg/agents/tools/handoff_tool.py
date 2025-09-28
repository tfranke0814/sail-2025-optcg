"""Agent tool to hand off tasks to other agents."""

from langgraph_swarm import create_handoff_tool

transfer_to_board_analyst = create_handoff_tool(
    agent_name="board_analyst", 
    description="Transfer the task to the board state analysis agent."
)

transfer_to_rulebook_agent = create_handoff_tool(
    agent_name="rulebook_agent", 
    description="Transfer the task to the rulebook agent."
)