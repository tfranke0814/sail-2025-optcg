from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
import uuid
import logging
from fastapi import HTTPException
from optcg.models import ChatRequest, ChatResponse
# Make sure get_or_create_agent is imported or defined
from optcg.routes.agent_routes import get_or_create_agent

# Custom Imports
import optcg.state as state
from optcg.routes import agent_routes, card_routes, board_routes

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
        required_env_vars = ["OPENAI_API_KEY", "APITCG_API_KEY", "BRAVE_SEARCH_API_KEY", "TAVILY_API_KEY"]
        # LangSmith is optional, not required for basic functionality
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

# App Routes
app.include_router(agent_routes.router, prefix="/agents", tags=["agents"])
app.include_router(card_routes.router, prefix="/cards", tags=["cards"])
app.include_router(board_routes.router, prefix="/board", tags=["board"])

@app.get("/")
async def root():
    """API status endpoint"""
    return {
        "status": f"{app.title} is running",
        "version": app.version,
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents_loaded": list(state.active_agents.keys()),
        "environment": {
            "langsmith_api_key": bool(os.getenv("LANGSMITH_API_KEY")),
            "openai_api_key": bool(os.getenv("OPENAI_API_KEY")), 
            "apitcg_api_key": bool(os.getenv("APITCG_API_KEY")),
            "brave_search_api_key": bool(os.getenv("BRAVE_SEARCH_API_KEY")),
            "tavily_api_key": bool(os.getenv("TAVILY_API_KEY"))
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
