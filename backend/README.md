# Backend API

The backend API for the OPTCG project, containing the endpoints for the agents.

## Setup and Runtime

1. **Change the current directory to the `backend/` folder.**
2. **Setup:**

   ```bash
   # Create a new .venv (if you haven't) and activate it
   python -m venv .venv
   # On Windows:
   .venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source .venv/bin/activate.bat

   # Install runtime dependencies
   pip install -r requirements.txt

   # Development runtime dependencies
   # (Not needed to run API)
   pip install -r requirements-dev.txt

   # Set up environment
   cp .env.example .env  # Add your API_KEYS
   ```

3. **Running the API:**

   ```bash
   # Development with auto-reload
   uvicorn src.optcg.api:app --reload --host 127.0.0.1 --port 8000

   # Or direct execution
   \python src.optcg/api.py
   ```

## API Endpoints

- `GET /` - API status
- `GET /agents` - Available agent types
- `POST /chat` - Chat with agents
- `GET /health` - Health check

### Example Usage

The `thread_id` parameter is optional and does not need to be specified.

#### **Curl Request:**

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

#### **Python Requests:**

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

#### **JavaScript/Node.js:**

```javascript
const response = await fetch("http://localhost:8000/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: "What are the One Piece TCG rules?",
    agent_type: "rulebook",
    thread_id: "sample-thread-id",
  }),
});
const data = await response.json();
console.log(data);
```
