# Backend API

The backend API for the OPTCG project, containing the endpoints for the agents, and the card database.


## API Documentation

For complete API documentation with interactive examples, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Quick Start Examples

### Chat with Agent
```bash
curl -X POST http://localhost:8000/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the One Piece TCG rules?", "agent_type": "multi-agent"}'
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