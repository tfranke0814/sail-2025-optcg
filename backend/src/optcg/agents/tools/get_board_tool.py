"""Board state retrieval tool. The HTTP request version is the current implementation. Future versions may (will) use a different approach."""

from asyncio.log import logger
import os
from langchain_core.tools import tool
import logging
import requests

# Custom Imports
from optcg import state

api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")


# Primary tool to get the current board state
# Depends on the process memory or state management to store the current board state
@tool
def get_board_tool() -> dict:
    """Retrieves the game board state set up by the user for the One Piece TCG.

    Returns:
      The current board state as a JSON object or an error message if no board state is set."""
    if state.current_board_state is None:
        logger.debug("No board state found. Returning 404.")
        return {"error": "No board state found. Please tell user to update the board state first."}
    return state.current_board_state

# Old version that uses HTTP to get the board state from the API
# For testing purposes, can be removed later
@tool 
def get_board_tool_http() -> dict:
    """Retrieves the game board state set up by the user for the One Piece TCG.

    Returns:
      The current board state as a JSON object or an error message if no board state is set."""
    response = None
    print("Getting board state via HTTP...")
    try:
        url = f"{api_base_url}/board/"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.exception(f"Exception in get_board_tool: {str(e)}")
        if response is not None and response.status_code == 404:
            return {"error": "No board state found. Please tell user to update the board state first."}
        return {"error": str(e)}
    return response.json()