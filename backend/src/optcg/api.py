from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import os
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

# Import Agents
from optcg.agents import RulebookAgent

# Load environment variables from .env file if it exists
load_dotenv()  

# Environment validation and logging setup on startup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event to validate environment on startup"""
    try:
        required_env_vars = ["OPENAI_API_KEY", "BRAVE_SEARCH_API_KEY", "TAVILY_API_KEY"]
        for var in required_env_vars:
            if not os.getenv(var):
                raise ValueError(f"{var} environment variable is required")
        logger.info("✅ Environment validated")
        yield
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise

app = FastAPI(title="OPTCG Agent API", version="1.0.0", lifespan=lifespan)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    agent_type: str

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    agent_type: str

# Store active agents - Won't persist across server restarts
# -- Retains short-term memory threads for each agent
# -- Resets when the server runtime restarts
active_agents = {}
avail_agents = ["rulebook"] # List of available agent types. See /agents endpoint

def get_or_create_agent(agent_type: str):
    """Get or create an agent instance"""
    if agent_type not in active_agents:
        if agent_type == "rulebook":
            active_agents[agent_type] = RulebookAgent()
        else:
            logger.error(f"Unknown agent type requested: {agent_type}")
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
    
    return active_agents[agent_type]

@app.get("/")
async def root():
    """API status endpoint"""
    return {
        "status": "OPTCG Agent API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "GET /agents": "List available agent types",
            "POST /chat": "Chat with agents", 
            "GET /health": "Health check"
        }
    }

@app.get("/agents")
async def list_agents():
    """List available agent types"""
    return {
        "available_agents": avail_agents,
        "descriptions": {
            "rulebook": "Access to information in the One Piece TCG rulebooks"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with an agent"""
    try:
        # We define the thread outside the chat method even though BaseAgent can handle it internally
        # This allows us to return the thread_id in the response
        # The chat method extracts the messasge response in the BaseAgent class, i.e. verbose = False
        agent = get_or_create_agent(request.agent_type)
        actual_thread_id = request.thread_id or str(uuid.uuid4()) # Generate a new thread ID if not provided
        agent_response = agent.chat(request.message, thread_id=actual_thread_id)
        return ChatResponse(
            response=agent_response,
            thread_id=actual_thread_id,
            agent_type=request.agent_type
        )
    except Exception as e:
        logger.error(f"Error in API <chat_with_agent>: {e}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents_loaded": list(active_agents.keys()),
        "environment": {
            "langsmith_api_key": bool(os.getenv("LANGSMITH_API_KEY")),
            "openai_api_key": bool(os.getenv("OPENAI_API_KEY")), 
            "brave_search_api_key": bool(os.getenv("BRAVE_SEARCH_API_KEY")),
            "tavily_api_key": bool(os.getenv("TAVILY_API_KEY"))
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
