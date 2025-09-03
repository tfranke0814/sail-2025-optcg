# region Imports
from abc import ABC, abstractmethod

import uuid
from IPython.display import Image

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

# Custom Imports
from optcg.tools import create_rulebook_retriever_tool, get_board_tool
from .react_prompts import CHAT_AGENT_PROMPT, RULEBOOK_AGENT_PROMPT


## This file defines the base agent class for the optcg project.
## It provides a structure for creating agents with tools and prompts,
## and includes methods for chatting with the agent and displaying its graph.

## This file contains agent subclasses that implement specific tools and prompts.

# - BaseAgent class can me imported elsewhere and used to create new agents. However, it is best practice to define the agents in the same file
# - Subclass BaseAgent and implement the _create_prompt and _setup_tools methods.
# - Ensure that the agent's name is set in the subclass constructor.

# --------------------------------------------------------
### Example of how to create a new agent subclass:

# class YourAgent(BaseAgent):
#     # If model and temperature are not specified, defaults will be used, defined in BaseAgent.
#     def __init__(self, model_name="gpt-4.1"):
#         self.name = "<YourAgent>"
#         super().__init__(model_name=model_name, temperature=0)
    
#     def _create_prompt(self):
#         """Create a system prompt for the agent. This should be tailored to the specific agent's purpose."""
#         return "<Your System Prompt>"

#     def _setup_tools(self):
#         """Setup tools for this agent. This can include any tools you want to use, or be an empty list if no tools are needed."""
#         return [
#             tool_1, 
#             tool_2, 
#             tool_3
#         ]

# --------------------------------------------------------
### See below for more examples of agent subclasses.
# --------------------------------------------------------


# endregion Imports


# region BaseAgent Class
class BaseAgent(ABC):
    def __init__(self, model_name="gpt-4o-mini", temperature=0):
        if model_name in ["o4-mini", "o3-mini"]:
            self.model = ChatOpenAI(model=model_name)
        else:
            self.model = ChatOpenAI(model=model_name, temperature=temperature)
        if not hasattr(self, 'name'): # Ensure name is set if not specified in subclasses
            self.name = "NamelessAgent"
        self.memory = InMemorySaver()
        self.tools = self._setup_tools()
        self.prompt = self._create_prompt()
        self.agent = self._build_agent()
    
    @abstractmethod
    def _setup_tools(self) -> list:
        """Define tools for this agent - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def _create_prompt(self) -> str:
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
    
    def chat(self, message, thread_id=None, verbose=False):
        """Chat with the agent"""
        if thread_id is None: # Ensures a unique thread ID if not provided
            thread_id = str(uuid.uuid4())
        
        response = self.agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": thread_id}}
        )
        
        if verbose:
            return response
        else:
            # Return just the last message content
            return response["messages"][-1].content
    
    def display_graph(self):
        """Display the agent's graph structure"""
        try:
            return Image(self.agent.get_graph().draw_mermaid_png())
        except Exception as e:
            print(f"Could not generate graph: {e}")
            return None
# endregion BaseAgent Class



# region ChatAgent Class
class ChatAgent(BaseAgent):
    def __init__(self, model_name="gpt-4.1"):
        self.name = "ChatAgent"
        super().__init__(model_name=model_name, temperature=0)
    
    def _create_prompt(self):
        return CHAT_AGENT_PROMPT

    def _setup_tools(self):
        return [
            create_rulebook_retriever_tool(), 
            get_board_tool
        ]
# endregion ChatAgent Class



# region RulebookAgent Class
class RulebookAgent(BaseAgent):
    def __init__(self, model_name="gpt-4.1"):
        self.name = "RulebookAgent"
        super().__init__(model_name=model_name, temperature=0)
    
    def _create_prompt(self):
        return RULEBOOK_AGENT_PROMPT

    def _setup_tools(self):
        return [
            create_rulebook_retriever_tool(),
        ]
# endregion RulebookAgent Class