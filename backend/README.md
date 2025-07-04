# Backend API

The backend API for the OPTCG project, containing the endpoints for the agents.

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
