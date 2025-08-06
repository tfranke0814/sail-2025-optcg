from fastapi import APIRouter, HTTPException
import logging
import uuid

# Custom Imports
from optcg import state
from optcg.schemas import ChatRequest, ChatResponse
from optcg.agents.react import RulebookAgent, ChatAgent

router = APIRouter()
logger = logging.getLogger(__name__)

AVAILABLE_AGENTS = ["rulebook", "userChat"]

def get_or_create_agent(agent_type: str):
    """Get or create an agent instance"""
    logger.debug(f"Requesting agent of type: {agent_type}")
    if agent_type not in state.active_agents:
        if agent_type == "rulebook":
            state.active_agents[agent_type] = RulebookAgent()
            logger.debug(f"Created new agent of type: {agent_type}")
        elif agent_type == "userChat":
            state.active_agents[agent_type] = ChatAgent()
            logger.debug(f"Created new agent of type: {agent_type}")
        else:
            logger.error(f"Unknown agent type requested: {agent_type}")
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
    logger.debug(f"Current active agents: {state.active_agents.keys()}")

    return state.active_agents[agent_type]

@router.get("/")
async def list_agents():
    """List available agent types"""
    return {
        "available_agents": AVAILABLE_AGENTS,
        "descriptions": {
            "rulebook": "Access to information in the One Piece TCG rulebooks",
            "userChat": "General chat agent for board state discussions and questions"
        }
    }

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with an agent"""
    logger.debug(f"Chat request received for agent: {request.agent_type}")  # Optional
    try:
        agent = get_or_create_agent(request.agent_type)
        actual_thread_id = request.thread_id or str(uuid.uuid4()) # Generate a new thread ID if not provided
        agent_response = agent.chat(request.message, thread_id=actual_thread_id)
        return ChatResponse(
            response=agent_response,
            thread_id=actual_thread_id,
            agent_type=request.agent_type
        )
    except Exception as e:
        logger.error(f"Error in API <chat_with_agent: {request.agent_type}>: {e}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")