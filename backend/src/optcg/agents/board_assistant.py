import logging
import uuid
from typing import Literal
from langchain_core.messages import HumanMessage, ToolMessage
from langchain.chat_models import init_chat_model
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# Custom Imports
from optcg.schemas import ExtractorSchema, StateInput, State
from optcg.tools import create_rulebook_retriever_tool, get_board_tool, get_board_tool_http
from optcg.agents.react import ChatAgent
from optcg.prompts import extraction_system_prompt, extraction_user_prompt, interpreter_system_prompt, interpreter_user_prompt

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

llm_extractor = init_chat_model(model="gpt-4.1", temperature=0)
llm_extractor = llm_extractor.with_structured_output(ExtractorSchema)

retriever = create_rulebook_retriever_tool()

llm_interpreter = init_chat_model(model="gpt-4.1", temperature=0)

def boardstate_retrieval(state: State) -> Command[Literal["chat_agent", "extract_board"]]:
    board = get_board_tool_http.invoke("") # Replace tool later
    if "messages" in state and state["messages"]:
        messages = state["messages"]
    else:
        messages = []

    print(f"Board State Retrieved: {board}")
    if board.get("error"):
        logging.info(f"No Board State Found: {board['error']}")
        goto = "chat_agent"
        update = {
            "board": board,
            "messages": messages.append({"role": "assistant", "content": "No board state found. Please update the board state first."})
        }
    else:
        goto = "extract_board"
        update = {
            "board": board,
            "messages": messages.append({"role": "assistant", "content": "Board state retrieved successfully."})
        }
    return Command(goto=goto, update=update)

def extract_board_state(state: State) -> Command[Literal["rule_retriever"]]:
    """Extracts the board state from the input state."""
    if "board" not in state:
        raise ValueError("Board state not found in input.")
    board = state["board"]

    # Format user prompt with board and question
    user_prompt = extraction_user_prompt.format(
        board=board, question=state["user_message"]
    )

    # System prompt
    system_prompt = extraction_system_prompt

    extraction = llm_extractor.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    return Command(goto="rule_retriever", update={"extraction": extraction.queries})

def rulebook_retriever(state: State) -> Command[Literal["llm_interpreter"]]:
    """Uses the rulebook retriever to get relevant information based on extracted queries."""
    if "extraction" not in state:
        raise ValueError("No extraction queries found in state.")
    queries = state["extraction"]

    results = []
    for query in queries:
        result = retriever.invoke(query)
        results.append(result)

    combined_results = "\n\n".join(results)

    return Command(goto="llm_interpreter", update={"retrieval": combined_results})

def llm_interpretation(state: State) -> Command[Literal["__end__"]]:
    """Interprets the user's message using the rulebook information and board state."""
    if "retrieval" not in state:
        raise ValueError("No retrieval information found in state.")
    if "board" not in state:
        raise ValueError("No board state found in state.")

    # Create the prompt for the LLM
    user_prompt = interpreter_user_prompt.format(
        board=state["board"],
        retrieval=state["retrieval"],
        question=state["user_message"]
    )

    system_prompt = interpreter_system_prompt

    if not state.get("thread_id"):
        state["thread_id"] = str(uuid.uuid4())
    config = {"configurable": {"thread_id": state["thread_id"]}}

    messages = [{"role": "system", "content": system_prompt}]

    if "messages" in state and state["messages"]:
        messages.extend(state["messages"])


    messages.append({"role": "user", "content": user_prompt})

    response = llm_interpreter.invoke(messages, config=config)

    output = [{"role": "user", "content": state["user_message"]}, {"role": "assistant", "content": response.content}]

    return Command(
        goto="__end__", 
        update={
            "messages": output
        }
    )

chat = ChatAgent()
# Define the agent builder for extraction
agent_builder = StateGraph(State, input_type=StateInput)

agent_builder.add_node("retrieve_board", boardstate_retrieval)
agent_builder.add_node("extract_board", extract_board_state)
agent_builder.add_node("rule_retriever", rulebook_retriever)
agent_builder.add_node("llm_interpreter", llm_interpretation)
agent_builder.add_node("chat_agent", chat.agent)

agent_builder.add_edge(START, "retrieve_board")
## agent_builder.add_edge("retrieve_board", "extract_board")
# # agent_builder.add_edge("retrieve_board", "chat_agent")
# # agent_builder.add_edge("extract_board", "chat_agent")
# agent_builder.add_edge("chat_agent", END)

agent = agent_builder.compile()
