# region Imports
from dotenv import load_dotenv
from langchain_community.tools import BraveSearch
from langchain_tavily import TavilyExtract
import json
from langchain_core.tools import tool
from typing import List
import logging
import ast
from langchain_community.tools import YouTubeSearchTool


# endregion Imports



# region web_search_tool
@tool
def web_search_tool(query: str) -> List[dict]:
    """Tool that performs a web search and return the results from the webpages."""
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