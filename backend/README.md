# Backend API

The backend API for the OPTCG project, containing the endpoints for the agents and the card database.

## Setup and Runtime

1. **Prerequisites:** Make sure you have set up the Python virtual environment and installed dependencies as described in the [main project README](../README.md).

2. **Change the current directory to the `backend/` folder.**

3. **Set up environment:**

   ```bash
   # Copy the environment template (if you haven't already)
   cp example.env .env  # Add your API_KEYS
   ```

4. **Running the API:**

   ```bash
   # Development with auto-reload
   uvicorn optcg.api:app --reload --host 0.0.0.0 --port 8000

   # Or direct execution
   python src/optcg/api.py
   ```

## API Documentation

For complete API documentation with interactive examples, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Quick Start Examples

### Chat with Agent
```bash
curl -X POST http://localhost:8000/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the One Piece TCG rules?", "agent_type": "rulebook"}'
```

### Search Cards
```bash
curl -X POST http://localhost:8000/cards/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Luffy", "power": 2000}'
```

#### Parameter Notes
- String parameters perform partial text matching within the text
- **counter:** Use `"-"` to search for cards without a counter value
- **cost/power:** Use `0` to search for 0-cost/power cards, omit to ignore these filters
- **set:** Use full set codes like `"OP01"`, `"ST01"`, etc.

### Get Specific Card
```bash
curl -X GET 'http://localhost:8000/cards/OP01-025'
```

**For all parameters, response schemas, and interactive testing, see `/docs`**