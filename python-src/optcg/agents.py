# region Imports
from abc import ABC, abstractmethod

import uuid
from IPython.display import Image

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools.retriever import create_retriever_tool
from langgraph.checkpoint.memory import InMemorySaver

from langsmith import traceable

# Custom Imports
from optcg.vectorstore_logic import create_or_load_vectorstore_optcg_rulebooks


## This file defines the base agent class for the optcg project.
## It provides a structure for creating agents with tools and prompts,
## and includes methods for chatting with the agent and displaying its graph.

## It contains agent subclasses that implement specific tools and prompts,
## allowing for flexible and extensible agent behavior.

# Classes:
# - BaseAgent: An abstract base class for agents, defining the structure and methods for creating agents.
# - RulebookAgent: A concrete implementation of BaseAgent that retrieves information from the One Piece TCG rulebooks.

# endregion Imports


# region BaseAgent Class
class BaseAgent(ABC):
    def __init__(self, model_name="gpt-4o-mini", temperature=0):
        self.model = ChatOpenAI(model=model_name, temperature=temperature)
        self.name = "BaseAgent"
        self.memory = InMemorySaver()
        self.tools = self._setup_tools()
        self.prompt = self._create_prompt()
        self.agent = self._build_agent()
    
    @abstractmethod
    def _setup_tools(self):
        """Define tools for this agent - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def _create_prompt(self):
        """Create system prompt - must be implemented by subclasses"""
        pass
    
    def _build_agent(self):
        """Build the agent with tools and prompt"""
        return create_react_agent(
            model=self.model,
            name=self.name,
            tools=self.tools, # type: ignore
            prompt=self.prompt,
            checkpointer=self.memory
        )
    
    def chat(self, message, thread_id=None):
        """Chat with the agent"""
        if thread_id is None: # Ensures a unique thread ID if not provided
            thread_id = str(uuid.uuid4())
        
        return self.agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": thread_id}}
        )
    
    def display_graph(self):
        """Display the agent's graph structure"""
        try:
            return Image(self.agent.get_graph().draw_mermaid_png())
        except Exception as e:
            print(f"Could not generate graph: {e}")
            return None
# endregion BaseAgent Class



# region RulebookAgent Class
class RulebookAgent(BaseAgent):
    def __init__(self, model_name="gpt-4.1"):
        super().__init__(model_name=model_name, temperature=0)
        self.name = "RulebookAgent"
    
    def _create_prompt(self):
        return "You are a helpful assistant that helps people find information in the Rulebook for One Piece TCG, otherwise abbreviated as optcg. You have access to the following tools: {tools}. Use them to find the information the user is looking for. If you don't know the answer, just say you don't know. Do not try to make up an answer. If you cannot find the answer in the rulebooks, tell the user that you cannot find the answer in the rulebooks."
    
    def _setup_tools(self):
        return [
            self._create_rulebook_retriever_tool()
        ]
    
    def _create_rulebook_retriever_tool(self):
        # Ensure the vectorstore is created or loaded
        vectorstore = create_or_load_vectorstore_optcg_rulebooks()
        # Create the retriever tool
        rulebook_retriever_tool = create_retriever_tool(
        retriever=vectorstore.as_retriever(), # type: ignore
        name="rulebooks_retriever",
        description="""Retrieves relevant information from the One Piece TCG rulebooks. This tool is useful for answering questions about the rules of the game, such as how to play, what cards do, and how to resolve specific situations. This is a retrieval tool that will return relevant document chunks from the vectorstore, which contains the rulebooks of the One Piece TCG."""
        )
        return rulebook_retriever_tool
# endregion RulebookAgent Class