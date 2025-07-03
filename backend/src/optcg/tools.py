# region Imports
from dotenv import load_dotenv
from langchain_community.tools import BraveSearch
from langchain_tavily import TavilyExtract
import json
from langchain_core.tools import tool
from typing import List
import logging


# endregion Imports



# region web_search_tool
@tool
def web_search_tool(query: str) -> List[dict]:
    """Tool that performs a web search and return the results from the webpages."""
    if not query.strip():
        return [{"error": "Query cannot be empty"}]
    try:
        # Initialize BraveSearch and TavilyExtract with the necessary API keys
        search = BraveSearch.from_search_kwargs(search_kwargs={"count": 5})
        extract = TavilyExtract(extract_depth="advanced")

        # Perform the search
        search_results = json.loads(search.invoke(query))
        urls = [result["link"] for result in search_results if "link" in result]
        if not urls:
            logging.warning("No URLs found in search results.")
            return [{"error": "No URLs found in search results"}]
        
        # Extract content from the URLs
        results = extract.invoke({"urls": urls})
        if isinstance(results, str) or results.get("error"):
            logging.warning(f"Failed to extract content from URLs: {urls}")
            return [{"error": "Failed to extract content from URLs"}]
        return results.get("results", [])
    except Exception as e:
        logging.exception(f"Exception in web_search_tool: {str(e)}")
        return [{"error": str(e)}]
# endregion web_search_tool
