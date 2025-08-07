# sail-2025-optcg

This is our repo for the N+1 SAIL Program through UW-Madison

An AI assistant for the One Piece Trading Card Game that helps players with rules, strategies, and (eventually) deck building.

## Components

- [Backend API](backend/README.md)
- [Frontend UI](frontend/README.md)

## Quick Setup

<details>
<summary>Option 1: (Not Configured) Docker Setup</summary>

#### Prerequisites

- Docker Desktop installed and running
- Docker Compose (usually included with Docker Desktop)

#### Environment Setup and Runtime

1. **Copy the environment template:**
   ```bash
   # Copy environment template
   cp backend/.env.example backend/.env
   ```
2. **Edit the `.env` in the `backend/` directory with your API keys.**
3. **Start runtime:**
   ```bash
   # Run in production mode
   docker-compose up --build
   ```

Access at http://localhost:5173
</details>

### Option 2: Manual Setup

#### Backend Setup

1. **Change to the `backend/` directory and set up environment:**

   ```shell
   cd backend # from root directory
   cp example.env .env  # Add your API_KEYS
   ```

2. **UV installation and runtime**

    ```shell
    # Install uv if you haven't already
    pip install uv

    # Runtime with reload for development
    uv run uvicorn optcg.api:app --reload --host 0.0.0.0 --port 8000
    ```

#### Frontend Setup
1. **Open another terminal instance with the backend still running in the first one.**
2. **Change to the `frontend/` directory, install the package requirements, and run the server:**
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
