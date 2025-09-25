"""
An agentic workflow to retrieve the current board state from the user.
Depending on the user's question, the agent may extract detailed information from the board state or summarize it.
"""

import logging
from typing import Literal
from langchain.chat_models import init_chat_model
from langgraph.types import Command
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import InMemorySaver

# Custom Imports
from ..tools import create_rulebook_retriever_tool, get_board_tool_http
from .analysis_schemas import (AnalysisStateInput, AnalysisState, 
                               AnalysisRouterSchema, AnalysisExtractorSchema)
from .analysis_prompts import (ANALYSIS_ROUTER_SYSTEM_PROMPT, ANALYSIS_ROUTER_USER_PROMPT, 
                               ANALYSIS_STATE_SUMMARY_SYSTEM_PROMPT, ANALYSIS_STATE_SUMMARY_USER_PROMPT, 
                               ANALYSIS_EXTRACTION_SYSTEM_PROMPT, ANALYSIS_EXTRACTION_USER_PROMPT, 
                               ANALYSIS_ADVISOR_SYSTEM_PROMPT, ANALYSIS_ADVISOR_USER_PROMPT
)

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Initialize LLMs
llm_router = init_chat_model(model="openai:gpt-5-nano")
llm_router = llm_router.with_structured_output(AnalysisRouterSchema)

llm_state_summarizer = init_chat_model(model="openai:gpt-5-nano")

llm_extractor = init_chat_model(model="gpt-4.1", temperature=0)
llm_extractor = llm_extractor.with_structured_output(AnalysisExtractorSchema)

retriever = create_rulebook_retriever_tool()

llm_advisor = init_chat_model(model="openai:gpt-5-mini")

# Define the functions for each node in the state graph
def boardstate_retrieval(state: AnalysisStateInput) -> Command[Literal["router", "__end__"]]:
    """Retrieves the current board state using the get_board_tool."""

    board = get_board_tool_http.invoke("") # TODO: Replace tool later

    if board.get("error"): # No board state found
        goto = "__end__"
        update = {
            "board": None,
            "messages": state["messages"] + [{
                "role": "assistant",
                "content": "No board state was found. Please update the board state.",
            }]
        }
        logging.info("No board state found for user. Was it updated?")
    else:
        goto = "router"
        update = {
            "board": board
            }
    return Command(goto=goto, update=update)

def boardstate_router(state: AnalysisState) -> Command[Literal["extract_board", "summarize_board"]]:
    """Decides whether to extract detailed information from the board state or to summarize it based on the user's question."""

    user_prompt = ANALYSIS_ROUTER_USER_PROMPT.format(
        question=state["user_message"]
    )

    system_prompt = ANALYSIS_ROUTER_SYSTEM_PROMPT

    result = llm_router.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    
    if result.rule_retrieval: # type: ignore
        goto = "extract_board"
        updates = {}
    else:
        goto = "summarize_board"
        updates = {}
    return Command(goto=goto, update=updates)

def summarize_board_state(state: AnalysisState) -> Command[Literal["__end__"]]:
    """Summarizes the board state for the user."""

    logging.debug(f"Summarizing board state for user question...")
    if not state["board"]:
        logging.debug("summarize_board_state node reached with empty board — this should not happen")
        return Command(goto="__end__", update={"messages": state["messages"] + [{"role": "assistant", "content": "(Error) No board state available."}]}) # type: ignore

    user_prompt = ANALYSIS_STATE_SUMMARY_USER_PROMPT.format(
        board=state["board"],
        question=state["user_message"]
    )

    system_prompt = ANALYSIS_STATE_SUMMARY_SYSTEM_PROMPT

    summary = llm_state_summarizer.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return Command(goto="__end__", update={"messages": state["messages"] + [{"role": "assistant", "content": summary.content}]})

def extract_board_state(state: AnalysisState) -> Command[Literal["rule_retriever"]]:
    """Extracts the board state from the input state."""

    logging.debug(f"Extracting board state for user question...")
    if not state["board"]:
        logging.debug("extract_board_state nodereached with empty board — this should not happen")
        return Command(goto="__end__", update={"messages": state["messages"] + [{"role": "assistant", "content": "(Error) No board state available."}]}) # type: ignore

    user_prompt = ANALYSIS_EXTRACTION_USER_PROMPT.format(
        board=state["board"], question=state["user_message"]
    )

    system_prompt = ANALYSIS_EXTRACTION_SYSTEM_PROMPT

    extraction = llm_extractor.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return Command(goto="rule_retriever", update={"extraction": extraction.queries}) # type: ignore

def rulebook_retriever(state: AnalysisState) -> Command[Literal["advisor"]]:
    """Uses the rulebook retriever to get relevant information based on extracted queries."""

    if not state["extraction"]:
        logging.debug("rulebook_retriever node reached with empty extraction — this should not happen")
        return Command(goto="__end__", update={"messages": state["messages"] + [{"role": "assistant", "content": "No extraction queries available."}]}) # type: ignore
    
    results = []
    for query in state["extraction"]:
        result = retriever.invoke(query)
        results.append(result)

    combined_results = "\n\n".join(results)

    return Command(goto="advisor", update={"retrieval": combined_results})

def advisor(state: AnalysisState) -> Command[Literal["__end__"]]:
    """Interprets the user's message using the rulebook information and board state."""

    if not state["board"] or not state["retrieval"]:
        logging.debug("advisor node reached with empty board or rule retrieval — this should not happen")
        return Command(goto="__end__", update={"messages": state["messages"] + [{"role": "assistant", "content": "(Error) Missing board state or rule retrieval information."}]})

    user_prompt = ANALYSIS_ADVISOR_USER_PROMPT.format(
        board=state["board"],
        question=state["user_message"]
    )

    system_prompt = ANALYSIS_ADVISOR_SYSTEM_PROMPT.format(
        retrieval=state["retrieval"]
    )

    messages = [{"role": "system", "content": system_prompt}] + state["messages"] + [{"role": "user", "content": user_prompt}]

    response = llm_advisor.invoke(messages)

    return Command(
        goto="__end__", 
        update={
            "messages": state["messages"] + [{"role": "assistant", "content": response.content}]
        }
    )


# Define the agent builder
agent_builder = StateGraph(AnalysisState, input_schema=AnalysisStateInput)
agent_builder.add_node("router", boardstate_router)
agent_builder.add_node("retrieve_board", boardstate_retrieval)
agent_builder.add_node("summarize_board", summarize_board_state)
agent_builder.add_node("extract_board", extract_board_state)
agent_builder.add_node("rule_retriever", rulebook_retriever)
agent_builder.add_node("advisor", advisor)

agent_builder.add_edge(START, "retrieve_board")

# Compile the agent
analysis_agent = agent_builder.compile(checkpointer=InMemorySaver())
