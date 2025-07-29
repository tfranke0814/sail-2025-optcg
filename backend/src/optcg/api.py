from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

# Custom Imports
from optcg import state
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
        if os.getenv("API_BASE_URL") == "http://localhost:8000":
            logger.warning("⚠️ Running in local development mode. Ensure this is intended.")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
