"""Utility functions for the agents"""

from typing import Any, Mapping

def get_latest_user_message(state: Mapping[str, Any]) -> str:
    """Extract the most recent human message from the conversation history."""
    return next(
        (msg.content for msg in reversed(state["messages"]) if msg.type == "human"),
        ""
    )