# sail-2025-optcg
This is our repo for the N+1 SAIL Program through UW-Madison

## Project Structure
- `python-src/` - Backend API and agent logic
- `frontend/` - React frontend with Vite

## Backend API
### Setup
```bash
# Install runtime dependencies
pip install -r requirements.txt

# Development runtime dependencies (Not needed to run API)
pip install -r requirements-dev.txt

# Set up environment
cp .env.example .env  # Add your OPENAI_API_KEY
```

### Running the API
```bash
# Development with auto-reload
uvicorn python-src.optcg.api:app --reload --host 127.0.0.1 --port 8000

# Or direct execution
cd python-src
python optcg/api.py
```

## API Endpoints
- `GET /` - API status
- `GET /agents` - Available agent types  
- `POST /chat` - Chat with agents
- `GET /health` - Health check

### Example Usage
### Example Usage
### Example Usage
The `thread_id` parameter is optional and does not need to be specified.

**Using curl:**
Without specifying a thread id
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the One Piece TCG rules?", "agent_type": "rulebook"}'
```

Specifying a thread id
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the One Piece TCG rules?", "agent_type": "rulebook", "thread_id": "sample-thread-id"}'
```

Windows PowerShell (if needed):
```powershell
curl.exe -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "What are the One Piece TCG rules?", "agent_type": "rulebook", "thread_id": "sample-thread-id"}'
```

**Using Python requests:**
```python
import requests
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What are the One Piece TCG rules?",
        "agent_type": "rulebook",
        "thread_id": "sample-thread-id"
    }
)
print(response.json())
```

**Using JavaScript/Node.js:**
```javascript
const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: "What are the One Piece TCG rules?",
        agent_type: "rulebook",
        thread_id: "sample-thread-id"
    })
});
const data = await response.json();
console.log(data);
```