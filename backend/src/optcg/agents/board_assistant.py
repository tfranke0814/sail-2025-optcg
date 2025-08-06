import logging
from typing import Literal
from langchain.chat_models import init_chat_model
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# Custom Imports
from optcg.schemas import StateInput, State
from optcg.tools import create_rulebook_retriever_tool, get_board_tool, get_board_tool_http
from optcg.agents.react import ChatAgent

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

llm = init_chat_model(model="gpt-4.1", temperature=0)
llm.bind_tools([create_rulebook_retriever_tool()], tool_choice="required")

def boardstate_retrieval(state: State) -> Command[Literal["chat_agent", "extract_board"]]:
    board = get_board_tool_http.invoke("") # Replace tool later
    print(f"Board State Retrieved: {board}")
    if board.get("error"):
        logging.info(f"No Board State Found: {board['error']}")
        goto = "chat_agent"
        update = {
            "board": board
        }
    else:
        goto = "extract_board"
        update = {
            "board": board
        }
    return Command(goto=goto, update=update)

def extract_board_state(state: State) -> Command[Literal["chat_agent"]]:
    """Extracts the board state from the input state."""
    if "board" not in state:
        raise ValueError("Board state not found in input.")
    
    return Command(goto="chat_agent")

chat = ChatAgent()
# Define the agent builder for extraction
agent_builder = StateGraph(State)
agent_builder.add_node("retrieve_board", boardstate_retrieval)
agent_builder.add_node("extract_board", extract_board_state)
agent_builder.add_node("chat_agent", chat.agent)

agent_builder.add_edge(START, "retrieve_board")
agent_builder.add_edge("retrieve_board", "extract_board")
agent_builder.add_edge("retrieve_board", "chat_agent")
agent_builder.add_edge("extract_board", "chat_agent")
agent_builder.add_edge("chat_agent", END)

agent = agent_builder.compile()
