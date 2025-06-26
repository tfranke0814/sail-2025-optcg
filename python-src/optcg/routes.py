from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import os
from contextlib import asynccontextmanager
import logging

# Import Agents
from optcg.agents import RulebookAgent

# Environment validation and logging setup on startup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event to validate environment on startup"""
    try:
        required_env_vars = ["OPENAI_API_KEY"]
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
    allow_origins=["http://localhost:3000"],  # React Server; adjust as needed
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

def get_or_create_agent(agent_type: str):
    """Get or create an agent instance"""
    if agent_type not in active_agents:
        if agent_type == "rulebook":
            active_agents[agent_type] = RulebookAgent()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
    
    return active_agents[agent_type]

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "OPTCG Agent API is running"}

@app.get("/agents")
async def list_agents():
    """List available agent types"""
    return {
        "available_agents": ,
        "description": {
            "rulebook": "Expert in One Piece TCG rules and gameplay"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with an agent"""
    try:
        # Get or create agent
        agent = get_or_create_agent(request.agent_type)
        
        # Generate thread_id if not provided
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # Get response from agent
        response = agent.chat(request.message, thread_id=thread_id)
        
        # Extract the message content from the response
        if hasattr(response, 'messages') and response.messages:
            # Get the last message from the agent
            last_message = response.messages[-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            else:
                agent_response = str(last_message)
        else:
            agent_response = str(response)
        
        return ChatResponse(
            response=agent_response,
            thread_id=thread_id,
            agent_type=request.agent_type
        )
        
    except Exception as e:
        if "API key" in str(e):
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.post("/chat/new")
async def start_new_conversation(agent_type: str = "rulebook"):
    """Start a new conversation with a fresh thread"""
    thread_id = str(uuid.uuid4())
    return {
        "thread_id": thread_id,
        "agent_type": agent_type,
        "message": f"New conversation started with {agent_type} agent"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents_loaded": list(active_agents.keys()),
        "environment": {
            "langchain_api_key": bool(os.getenv("LANGCHAIN_API_KEY")),
            "openai_api_key": bool(os.getenv("OPENAI_API_KEY"))
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
