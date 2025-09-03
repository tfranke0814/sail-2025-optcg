import logging
import uuid
from typing import Literal
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain.chat_models import init_chat_model
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# Custom Imports
from .analysis_schemas import AnalysisExtractorSchema, AnalysisStateInput, AnalysisState, AnalysisRouterSchema
from optcg.tools import create_rulebook_retriever_tool, get_board_tool, get_board_tool_http
from .analysis_prompts import ANALYSIS_EXTRACTION_SYSTEM_PROMPT, ANALYSIS_EXTRACTION_USER_PROMPT, ANALYSIS_ADVISOR_SYSTEM_PROMPT, ANALYSIS_ADVISOR_USER_PROMPT, ANALYSIS_ROUTER_SYSTEM_PROMPT, ANALYSIS_ROUTER_USER_PROMPT, ANALYSIS_STATE_SUMMARY_SYSTEM_PROMPT, ANALYSIS_STATE_SUMMARY_USER_PROMPT

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

llm_router = init_chat_model(model="openai:gpt-5-nano")
llm_router = llm_router.with_structured_output(AnalysisRouterSchema)

llm_state_summarizer = init_chat_model(model="openai:gpt-5-nano")

llm_extractor = init_chat_model(model="gpt-4.1", temperature=0)
llm_extractor = llm_extractor.with_structured_output(AnalysisExtractorSchema)

retriever = create_rulebook_retriever_tool()

llm_advisor = init_chat_model(model="openai:gpt-5-mini")

def boardstate_retrieval(state: AnalysisStateInput) -> Command[Literal["router", "__end__"]]:
    board = get_board_tool_http.invoke("") # Replace tool later

    no_board_msg = {
        "role": "assistant",
        "content": "No board state was found. Please update the board state.",
    }

    if board.get("error"):
        goto = "__end__"
        update = {
            "board": None,
            "messages": state["messages"] + [no_board_msg]
        }
    else:
        goto = "router"
        update = {
            "board": board
            }
    return Command(goto=goto, update=update)

def boardstate_router(state: AnalysisState) -> Command[Literal["extract_board", "summarize_board"]]:
    # Format user prompt with board and question
    user_prompt = ANALYSIS_ROUTER_USER_PROMPT.format(
        question=state["user_message"]
    )

    # System prompt
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
    logging.info(f"Summarizing board state for user question")
    board = state["board"]
    if not board:
        return Command(goto="__end__", update={"messages": state["messages"] + [{"role": "assistant", "content": "No board state available."}]})

    user_prompt = ANALYSIS_STATE_SUMMARY_USER_PROMPT.format(
        board=board, 
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
    # Format user prompt with board and question
    logging.info(f"Extracting board state for user question")
    user_prompt = ANALYSIS_EXTRACTION_USER_PROMPT.format(
        board=state["board"], question=state["user_message"]
    )

    # System prompt
    system_prompt = ANALYSIS_EXTRACTION_SYSTEM_PROMPT

    extraction = llm_extractor.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    logging.info(f"Extracted queries: {extraction.queries}") # type: ignore
    return Command(goto="rule_retriever", update={"extraction": extraction.queries}) # type: ignore

def rulebook_retriever(state: AnalysisState) -> Command[Literal["advisor"]]:
    """Uses the rulebook retriever to get relevant information based on extracted queries."""
    queries = state["extraction"]
    results = []
    for query in queries: # type: ignore
        result = retriever.invoke(query)
        results.append(result)

    combined_results = "\n\n".join(results)

    return Command(goto="advisor", update={"retrieval": combined_results})

def advisor(state: AnalysisState) -> Command[Literal["__end__"]]:
    """Interprets the user's message using the rulebook information and board state."""
    # Create the prompt for the LLM
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


# Define the agent builder for extraction
agent_builder = StateGraph(AnalysisState, input_schema=AnalysisStateInput)
agent_builder.add_node("router", boardstate_router)
agent_builder.add_node("retrieve_board", boardstate_retrieval)
agent_builder.add_node("summarize_board", summarize_board_state)
agent_builder.add_node("extract_board", extract_board_state)
agent_builder.add_node("rule_retriever", rulebook_retriever)
agent_builder.add_node("advisor", advisor)

agent_builder.add_edge(START, "retrieve_board")

analysis_agent = agent_builder.compile(checkpointer=InMemorySaver())
