"""Rulebook Retrieval Tool from the vector store. Must be called as a function to initiate vectorstore loading/creation on first use."""

from langchain_core.tools.retriever import create_retriever_tool

# Custom Imports
from optcg.vectorstore_logic import create_or_load_vectorstore_optcg_rulebooks


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