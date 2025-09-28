"""
The primary graph orchestration between the agents.
The chat agent is the primary agent, which can hand off to other agents as needed.
"""

from langgraph.graph import StateGraph, START, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState

# Custom Imports
from .analysis import analysis_agent
from .react import chat_agent, rulebook_agent

# Define the multi-agent graph
multi_agent_graph = (
    StateGraph(MessagesState)
    .add_node("chat_agent", chat_agent)
    .add_node("rulebook_agent", rulebook_agent)
    .add_node("board_analyst", analysis_agent)
    .add_edge(START, "chat_agent")
    .compile(checkpointer=InMemorySaver())
)