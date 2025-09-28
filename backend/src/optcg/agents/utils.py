"""Utility functions for the agents"""

from typing import Any, Mapping
from IPython.display import Image
import uuid

def get_latest_user_message(state: Mapping[str, Any]) -> str:
    """Extract the most recent human message from the conversation history."""
    return next(
        (msg.content for msg in reversed(state["messages"]) if msg.type == "human"),
        ""
    )

def display_graph(agent, xray=0):
    """Display the agent's graph structure"""
    try:
        return Image(agent.get_graph(xray=xray).draw_mermaid_png())
    except Exception as e:
        print(f"Could not generate graph: {e}")
        return None

def chat(agent, message, thread_id=None, verbose=False):
        """Chat with the agent workflow. Handles thread id if checkpointing is enabled."""
        if thread_id is None: # Ensures a unique thread ID if not provided
            thread_id = str(uuid.uuid4())
        
        response = agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": thread_id}}
        )
        
        if verbose:
            return response
        else:
            # Return just the last message content
            return response["messages"][-1].content