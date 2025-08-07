import logging
from typing import Literal
from langchain.chat_models import init_chat_model
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# Custom Imports
from optcg.schemas import ExtractorSchema, StateInput, State
from optcg.tools import create_rulebook_retriever_tool, get_board_tool, get_board_tool_http
from optcg.agents.react import ChatAgent
from optcg.prompts import extraction_system_prompt, extraction_user_prompt

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

llm_extractor = init_chat_model(model="gpt-4.1", temperature=0)
llm_extractor = llm_extractor.with_structured_output(ExtractorSchema)

llm_retriever = init_chat_model(model="gpt-4.1", temperature=0)
llm_retriever = llm_retriever.bind_tools([create_rulebook_retriever_tool()], tool_choice="required")

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
    board = state["board"]

    # Format user prompt with board and question
    user_prompt = extraction_user_prompt.format(
        board=board, question=state["message"]
    )

    # Format system prompt with background and triage instructions
    system_prompt = extraction_system_prompt

    extraction = llm_extractor.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    print(f"Extraction Result: {extraction}")
    return extraction #Command(goto="chat_agent")


chat = ChatAgent()
# Define the agent builder for extraction
agent_builder = StateGraph(State, input_type=StateInput)
agent_builder.add_node("retrieve_board", boardstate_retrieval)
agent_builder.add_node("extract_board", extract_board_state)
agent_builder.add_node("chat_agent", chat.agent)

agent_builder.add_edge(START, "retrieve_board")
agent_builder.add_edge("retrieve_board", "extract_board")
agent_builder.add_edge("retrieve_board", "chat_agent")
agent_builder.add_edge("extract_board", "chat_agent")
agent_builder.add_edge("chat_agent", END)

agent = agent_builder.compile()
