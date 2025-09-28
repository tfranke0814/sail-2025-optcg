"""The ReAct style agents used within the project and workflows."""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Custom Imports
from ..tools import transfer_to_board_analyst, transfer_to_rulebook_agent, create_rulebook_retriever_tool
from .react_prompts import CHAT_AGENT_PROMPT, RULEBOOK_AGENT_PROMPT

chat_agent = create_react_agent(
            model=ChatOpenAI(model="gpt-4.1", temperature=0),
            name="chat_agent",
            prompt=CHAT_AGENT_PROMPT,
            tools=[transfer_to_board_analyst, transfer_to_rulebook_agent]
        )

rulebook_agent = create_react_agent(
            model=ChatOpenAI(model="gpt-4.1", temperature=0),
            name="rulebook_agent",
            prompt=RULEBOOK_AGENT_PROMPT,
            tools=[create_rulebook_retriever_tool()]
        )