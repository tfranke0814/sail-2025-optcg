# Docker Setup for OPTCG Project

This document explains how to set up and run the OPTCG project using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (usually included with Docker Desktop)

## Environment Setup

1. **Copy the environment template:**
   ```bash
   cp backend/example.env backend/.env
   ```

2. **Edit the `backend/.env` file** and add your API keys:
   ```bash
   OPENAI_API_KEY="your-openai-api-key"
   BRAVE_SEARCH_API_KEY="your-brave-search-api-key"
   TAVILY_API_KEY="your-tavily-api-key"
   LANGSMITH_API_KEY="your-langsmith-api-key"
   ```

## Running the Application

### Production Mode

To run the application in production mode:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

**Access points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development Mode

To run the application in development mode with hot reloading:

```bash
# Build and start development services
docker-compose -f docker-compose.dev.yml up --build

# Or run in detached mode
docker-compose -f docker-compose.dev.yml up --build -d
```

**Development features:**
- Hot reloading for both frontend and backend
- Source code mounted as volumes for live editing
- Development dependencies included

## Useful Commands

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop services
```bash
# Production
docker-compose down

# Development
docker-compose -f docker-compose.dev.yml down
```

### Rebuild services
```bash
# Production
docker-compose up --build --force-recreate

# Development
docker-compose -f docker-compose.dev.yml up --build --force-recreate
```

### Access container shell
```bash
# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend sh
```

### Clean up
```bash
# Remove containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all
```

## Service Architecture

### Backend Service
- **Image:** Python 3.11 slim
- **Port:** 8000
- **Health Check:** `/health` endpoint
- **Features:** FastAPI with auto-reload in development

### Frontend Service
- **Image:** Node.js 18 (dev) / Nginx (prod)
- **Port:** 3000
- **Health Check:** HTTP 200 response
- **Features:** React with Vite, hot reloading in development

### Network
- **Name:** `optcg-network` (prod) / `optcg-network-dev` (dev)
- **Communication:** Frontend proxies API calls to backend

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :8000
   netstat -ano | findstr :3000
   ```

2. **Environment variables not loading:**
   - Ensure `backend/.env` file exists and has correct format
   - Check for typos in variable names

3. **Build failures:**
   ```bash
   # Clean build cache
   docker-compose build --no-cache
   ```

4. **Permission issues (Linux/Mac):**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Health Checks

Monitor service health:
```bash
# Check service status
docker-compose ps

# View health check logs
docker inspect optcg-backend | grep -A 10 Health
```

## Development Workflow

1. **Start development environment:**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

2. **Make code changes** in your local files
   - Frontend changes will auto-reload
   - Backend changes will auto-reload

3. **Test API endpoints:**
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What are the One Piece TCG rules?", "agent_type": "rulebook"}'
   ```

4. **Stop development:**
   ```bash
   docker-compose -f docker-compose.dev.yml down
   ```

## Production Deployment

For production deployment:

1. **Remove development volumes** from `docker-compose.yml`
2. **Set appropriate environment variables**
3. **Use production Dockerfiles**
4. **Configure reverse proxy** (nginx, traefik, etc.)
5. **Set up SSL certificates**
6. **Configure logging and monitoring**

## File Structure

```
sail-2025-optcg/
├── backend/
│   ├── Dockerfile.backend           # Backend production Dockerfile
│   ├── requirements.txt             # Python dependencies
│   ├── requirements-dev.txt         # Development dependencies
│   ├── example.env                  # Environment template
│   └── src/                         # Python source code
│       └── optcg/                   # Main package
│           ├── api.py               # FastAPI application
│           ├── agents.py            # LLM agents implementation
│           ├── vectorstore_logic.py # Vector database handling
│           └── tools.py/            # Agent tools directory
├── frontend/
│   ├── Dockerfile.frontend          # Frontend production Dockerfile
│   ├── Dockerfile.frontend.dev      # Frontend development Dockerfile
│   ├── package.json                 # Node.js dependencies
│   └── src/                         # React source code
├── docker-compose.yml               # Production compose file
├── docker-compose.dev.yml           # Development compose file
├── nginx.conf                       # Nginx configuration for frontend
├── .dockerignore                    # Files to exclude from Docker builds
├── README.md                        # Main project documentation
└── DOCKER_README.md                 # Docker-specific documentation
```