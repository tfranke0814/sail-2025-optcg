# region Imports
from asyncio.log import logger
import os
from langchain_core.tools import tool
from langchain_core.tools.retriever import create_retriever_tool
from langchain_community.tools import BraveSearch, YouTubeSearchTool
from langchain_tavily import TavilyExtract
import json
from typing import List
import logging
import ast
import requests

# Custom Imports
from optcg.vectorstore_logic import create_or_load_vectorstore_optcg_rulebooks
from optcg.schemas import CardSearchRequest
from optcg import state

api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

# endregion Imports



# region rulebook_retriever_tool
def create_rulebook_retriever_tool():
    # Ensure the vectorstore is created or loaded
    vectorstore = create_or_load_vectorstore_optcg_rulebooks()
    # Create the retriever tool
    rulebook_retriever_tool = create_retriever_tool(
    retriever=vectorstore.as_retriever(), # type: ignore
    name="rulebooks_retriever",
    description="""Retrieves relevant information from the One Piece TCG rulebooks. This tool is useful for answering questions about the rules of the game, such as how to play, game setup, keywords, and tournament rules.
    
    Args:
      query (str): The query to search for in the rulebooks.

    Returns:
        A list of relevant document chunks from the rulebooks, or an error message if no relevant information is found.
    """
    )
    return rulebook_retriever_tool
# endregion rulebook_retriever_tool



# region get_board_tool

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
# endregion get_board_tool



# region card_search_tool
@tool
def card_search_tool(input: CardSearchRequest) -> List[dict]:
    """Tool that searches for cards in the One Piece TCG database with API TCG. Returns a list of cards matching the search criteria."""
    try:
        response = requests.post(
            f"{api_base_url}/cards",
            json=input.model_dump(exclude_none=True) 
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logging.exception(f"Exception in card_search_tool: {str(e)}")
        return [{"error": str(e)}]
    return response.json().get("data", [])
# endregion card_search_tool



# region web_search_tool
@tool
def web_search_tool(query: str) -> List[dict]:
    """Tool that performs a web search and return the results from the webpages. This can be used to find information that is not in the rulebooks, such as news, updates, or general information about the One Piece TCG."""
    if not query.strip():
        logging.warning("web_search_tool - Agent queried an empty string. Query cannot be empty.")
        return [{"error": "Query cannot be empty"}]
    try:
        # Initialize BraveSearch and TavilyExtract with the necessary API keys
        search = BraveSearch.from_search_kwargs(search_kwargs={"count": 5})
        extract = TavilyExtract(extract_depth="advanced")

        # Perform the search
        search_results = json.loads(search.invoke(query))
        urls = [result["link"] for result in search_results if "link" in result]
        if not urls:
            logging.warning("web_search_tool - No URLs found in search results.")
            return [{"error": "No URLs found in search results"}]
        
        # Extract content from the URLs
        results = extract.invoke({"urls": urls})
        if isinstance(results, str) or results.get("error"):
            logging.warning(f"web_search_tool - Failed to extract content from URLs: {urls}")
            return [{"error": "Failed to extract content from URLs"}]
        return results.get("results", [])
    except Exception as e:
        logging.exception(f"Exception in web_search_tool: {str(e)}")
        return [{"error": str(e)}]
# endregion web_search_tool



# region youtube_search_tool
@tool
def youtube_search_tool(query: str) -> List[dict]:
    """Tool that performs a youtube search and return the results from the youtube videos."""
    if not query.strip(): # Keeps consistent with web search tool. Faster error handling
        logging.warning("youtube_search_tool - Agent queried an empty string. Query cannot be empty.")
        return [{"error": "Query cannot be empty"}]
    try:
        # Initialize YouTubeSearch (no key) and TavilyExtract with the necessary API keys
        search = YouTubeSearchTool()
        extract = TavilyExtract(extract_depth="advanced")

        # Perform the search
        urls = ast.literal_eval(search.invoke(f"{query},5"))
        if not urls:
            logging.warning("youtube_search_tool - No URLs found in search results.")
            return [{"error": "No URLs found in search results"}]
        
        # Extract content from the URLs
        results = extract.invoke({"urls": urls})
        if isinstance(results, str) or results.get("error"):
            logging.warning(f"youtube_search_tool - Failed to extract content from URLs: {urls}")
            return [{"error": "Failed to extract content from URLs"}]
        return results.get("results", [])
    except Exception as e:
        logging.exception(f"Exception in web_search_tool: {str(e)}")
        return [{"error": str(e)}]
# endregion youtube_search_tool