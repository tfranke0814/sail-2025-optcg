# sail-2025-optcg

This is our repo for the N+1 SAIL Program through UW-Madison

An AI assistant for the One Piece Trading Card Game that helps players with rules, strategies, and (eventually) deck building.

## Components

- [Backend API and Agents](backend/README.md)
- [Frontend UI](frontend/README.md)

## Quick Setup

### Option 1: Docker Setup for OPTCG Project

#### Prerequisites

- Docker Desktop installed and running
- Docker Compose (usually included with Docker Desktop)

#### Environment Setup and Runtime

1. **Copy the environment template:**
   ```bash
   # Copy environment template
   cp backend/example.env backend/.env
   ```
2. **Edit the `.env` in the `backend/` directory with your API keys.**
3. **Start runtime:**
   ```bash
   # Run in production mode
   docker-compose up --build
   ```

Access at http://localhost:5173

### Option 2: Manual Setup

#### Backend Setup

1. **Activate a virtual environment in the root directory:**

   ```bash
   # Create a .venv
   python -m venv .venv
   ```

2. **Activate the virtual environment:**

   ```bash
   # On Windows:
   .venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source .venv/bin/activate.bat
   ```

3. **Install the Python package dependencies in the `backend/` directory:**

   ```bash
   cd backend
   pip install -r requirements.txt
   pip install -r backend/requirements-dev.txt  # Development tools
   ```

4. **Copy the environment template:**
   ```bash
   cp example.env .env
   ```
5. **Edit the `.env` in the `backend/` directory with your API keys.**
6. **Run the backend API from the `backend/` directory:**

   ```bash
   # Run the API with auto-reload
   uvicorn src.optcg.api:app --reload --host 127.0.0.1 --port 8000

   # Or run directly
   cd backend && python src.optcg/api.py
   ```

### Frontend Setup

```bash
cd frontend # from root directory
npm install

# Run development server
npm run dev
```

Access at http://localhost:5173

## More Information

For more detailed Docker information see [DOCKER_README.md](DOCKER_README.md). For API documentation see [backend/README.md](backend/README.md) or the [FastAPI](http://localhost:8000/docs) (when running)

## Project Structure

```
sail-2025-optcg/
├── backend/           # Python FastAPI backend
│   └── src/           # Python source code
├── frontend/          # React frontend
└── DOCKER_README.md   # Docker setup instructions
```

For detailed file structure, see [DOCKER_README.md](DOCKER_README.md).
