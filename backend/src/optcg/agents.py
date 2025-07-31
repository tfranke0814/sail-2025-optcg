# region Imports
from abc import ABC, abstractmethod

import uuid
from IPython.display import Image

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

from langsmith import traceable

# Custom Imports
from optcg.tools import create_rulebook_retriever_tool, web_search_tool, youtube_search_tool, card_search_tool, get_board_tool


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
        return """You are a helpful assistant that helps people answer information about the One Piece TCG based on their current board state. You have access to the following tools: {tools}. To get the current board state, use the get board state tool and take into account the opponent's hand size. Use the rulebook retriever tool to find the information related to the rules of the game. If you give advice or turn recommendations, you MUST ensure it is correct by consulting the rulebooks. If you don't know the answer, just say you don't know. Do not try to make up an answer.

        General Rule Guidelines to keep in mind:
        - Leaders can always use their main ability, unless stated otherwise.
        - Leaders can always attack, unless stated otherwise.
        - Cards in your opponent's hand may have "counter" effects that can be played in response to your actions to stop your attacks.

        Here is the general game overview for One Piece TCG from the comprehensive rules:
        1. Game Overview
1-1. Number of Players
1-1-1. Fundamentally, this game is intended to be played by two players, head-to-head.
These rules do not currently support play by three or more players.
1-2. Ending the Game
1-2-1. The game ends when either player loses the game. When a player’s opponent loses
the game, the player who has not lost wins the game.
1-2-1-1. The two defeat conditions are as follows:
1-2-1-1-1. When you have 0 Life cards and your Leader takes damage.
1-2-1-1-2. When you have 0 cards in your deck.
1-2-2. When either player meets a defeat condition, they will lose the game according to
the rule processing at the next time of rule processing. (See 9. Rule Processing)
1-2-2-1. If either player’s Leader takes damage when that player has 0 Life cards
remaining during the game, that player has met a defeat condition.
1-2-2-2. If either player has 0 cards in their deck during the game, that player has met
a defeat condition.
1-2-3. Either player may concede at any point during a game. When a player concedes,
they lose immediately and the game ends.
1-2-4. A concession is not affected by any card. Furthermore, concession cannot be
forced by any card effect, and defeat by concession cannot be replaced by any
replacement effect.
1-2-5. The effects of some cards may cause a player to win or lose the game. In such a
case, the player wins or loses during the processing of that effect, and the game
ends.
1-3. Fundamental Principles
1-3-1. When card text contradicts the Comprehensive Rules, the card text takes
precedence over the Comprehensive Rules.
1-3-2. If a player is required to perform an impossible action for any reason, that action
is not carried out. Likewise, if an effect requires the player to carry out multiple
actions, some of which are impossible, the player performs as many of the actions
as possible.
1-3-2-1. If an object is required to change to a given state, and the object is already in
that state, the object’s state remains the same, and the action is not performed.
1-3-2-2. If a player is required to perform an action 0 or a negative number of times
for any reason, that action is not carried out. A request to perform a certain
action negative times does not imply performing its opposite action.
1-3-3. If a card’s effect requires a player to carry out an action while a currently active
effect prohibits that action, the prohibiting effect always takes precedence.
1-3-4. If both players are required to make choices simultaneously for any reason, the
player whose turn it is makes the choices first. After that player has made their
choices, the other player makes their choices.
1-3-5. If a card or rule requires a player to choose a number, unless otherwise specified,
the player must choose a whole number of 0 or greater. Players cannot choose
numbers containing fractions less than 1, or negative numbers.
1-3-5-1. If a card or rule specifies a maximum value for a number, such as “up to ...”,
as long as no minimum number is specified, the player can choose 0.
1-3-6. If a card effect changes information on a card, unless otherwise specified or defined
by the rules, numbers on a card cannot contain fractions less than 1. If non-power
numbers would become negative, they are treated as 0, except in cases where the
information is added to or subtracted from.
1-3-7. Power can become a negative value.
1-3-7-1. Even if a card’s power becomes a negative value, unless otherwise specified, that card will not be trashed or otherwise moved to an area.
1-3-8. Unless otherwise specified, card effects are carried out in the order described on
the card.
1-3-9. If card effects require a player to rest a card and set it as active simultaneously, the
effect requiring the player to rest the card always takes precedence.
1-3-10. Cost and Activation Cost
1-3-10-1. Cost refers to a payment that must be made to play a card. A card’s cost is
the number written in its upper left corner. (See 6-5-3-1.)
1-3-10-2. Activation cost refers to a payment required to activate a card’s effect. (See
8-3.)
1-3-11. If both players are instructed to perform some action at the same time according
to a card’s effect, the turn player is to perform the action first, followed by the
non-turn player.
        """

    # def _create_prompt(self):
    #     return "You are a helpful assistant that helps people answer information about the One Piece TCG based on their current board state. You have access to the following tools: {tools}. To get the current board state, use the get board state tool. Use the rulebook retriever tool to find the information related to the rules of the game. If you give advice or turn recommendations, you MUST ensure it is correct by consulting the rulebooks. If you don't know the answer, just say you don't know. Do not try to make up an answer."

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
        return "You are a helpful assistant that helps people find information in the Rulebook for One Piece TCG, otherwise abbreviated as optcg. You have access to the following tools: {tools}. Use the Rulebook to find the information the user is looking for related to rules. If the user ask for the current board state, use the get board state tool. If you don't know the answer, just say you don't know. Do not try to make up an answer."
    
    def _setup_tools(self):
        return [
            create_rulebook_retriever_tool(), 
            get_board_tool
        ]
# endregion RulebookAgent Class



# region Toolless Agent Class
class ToollessAgent_4_1(BaseAgent):
    def __init__(self, model_name="gpt-4.1"):
        self.name = "ToollessAgent_4_1"
        super().__init__(model_name=model_name, temperature=0)

    def _create_prompt(self):
        return "You are a helpful assistant that helps people answer information about the One Piece TCG. If you don't know the answer, just say you don't know. Do not try to make up an answer."

    def _setup_tools(self):
        return []

class ToollessAgent_o4_mini(BaseAgent):
    def __init__(self, model_name="gpt-o4-mini"):
        self.name = "ToollessAgent_o4"
        super().__init__(model_name=model_name, temperature=0)

    def _create_prompt(self):
        return "You are a helpful assistant that helps people answer information about the One Piece TCG. If you don't know the answer, just say you don't know. Do not try to make up an answer."

    def _setup_tools(self):
        return []
# endregion Toolless Agent Class



# region SearchAgent Class
class SearchAgent_web_youtube(BaseAgent):
    def __init__(self, model_name="gpt-4.1"):
        self.name = "SearchAgent_web_youtube"
        super().__init__(model_name=model_name, temperature=0)

    def _create_prompt(self):
        return "You are a helpful assistant that helps people find information about the One Piece TCG. Use the following tools to assist you: {tools}. If you don't know the answer, just say you don't know. Do not try to make up an answer."

    def _setup_tools(self):
        return [
            web_search_tool,
            youtube_search_tool,
        ]

class SearchAgent_web(BaseAgent):
    def __init__(self, model_name="gpt-4.1"):
        self.name = "SearchAgent_web"
        super().__init__(model_name=model_name, temperature=0)

    def _create_prompt(self):
        return "You are a helpful assistant that helps people find information about the One Piece TCG. Use the following tools to assist you: {tools}. If you don't know the answer, just say you don't know. Do not try to make up an answer."

    def _setup_tools(self):
        return [
            web_search_tool,
        ]

class SearchAgent_youtube(BaseAgent):
    def __init__(self, model_name="gpt-4.1"):
        self.name = "SearchAgent_web_youtube"
        super().__init__(model_name=model_name, temperature=0)

    def _create_prompt(self):
        return "You are a helpful assistant that helps people find information about the One Piece TCG. Use the following tools to assist you: {tools}. If you don't know the answer, just say you don't know. Do not try to make up an answer."

    def _setup_tools(self):
        return [
            youtube_search_tool
        ]

class SearchAgent_web_youtube_rulebook(BaseAgent):
    def __init__(self, model_name="gpt-4.1"):
        self.name = "SearchAgent_web_youtube_rulebook"
        super().__init__(model_name=model_name, temperature=0)

    def _create_prompt(self):
        return "You are a helpful assistant that helps people find information about the One Piece TCG. Use the following tools to assist you: {tools}. If you don't know the answer, just say you don't know. Do not try to make up an answer."

    def _setup_tools(self):
        return [
            web_search_tool,
            youtube_search_tool,
            create_rulebook_retriever_tool()
        ]

class SearchAgent_web_rulebook(BaseAgent):
    def __init__(self, model_name="gpt-4.1"):
        self.name = "SearchAgent_web_youtube_rulebook"
        super().__init__(model_name=model_name, temperature=0)

    def _create_prompt(self):
        return "You are a helpful assistant that helps people find information about the One Piece TCG. Use the following tools to assist you: {tools}. If you don't know the answer, just say you don't know. Do not try to make up an answer."

    def _setup_tools(self):
        return [
            web_search_tool,
            create_rulebook_retriever_tool()
        ]

class SearchAgent_youtube_rulebook(BaseAgent):
    def __init__(self, model_name="gpt-4.1"):
        self.name = "SearchAgent_web_youtube_rulebook"
        super().__init__(model_name=model_name, temperature=0)

    def _create_prompt(self):
        return "You are a helpful assistant that helps people find information about the One Piece TCG. Use the following tools to assist you: {tools}. If you don't know the answer, just say you don't know. Do not try to make up an answer."

    def _setup_tools(self):
        return [
            youtube_search_tool,
            create_rulebook_retriever_tool()
        ]
# endregion SearchAgent Class



# region CardSearchAgent Class
class CardDBToolAgent(BaseAgent):
    # If model and temperature are not specified, defaults will be used, defined in BaseAgent.
    def __init__(self, model_name="gpt-4.1"):
        self.name = "CardDBToolAgent"
        super().__init__(model_name=model_name, temperature=0)
    
    def _create_prompt(self):
        """Create a system prompt for the agent. This should be tailored to the specific agent's purpose."""
        return "You are a helpful assistant that helps people answer information about the One Piece TCG. If you don't know the answer, just say you don't know. Do not try to make up an answer."

    def _setup_tools(self):
        """Setup tools for this agent. This can include any tools you want to use, or be an empty list if no tools are needed."""
        return [
            card_search_tool
        ]
# endregion CardSearchAgent Class