# The Heist - Backend Server

Production-ready Python FastAPI backend for The Heist multiplayer game.

## Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   └── npc.py          # NPC endpoints
│   ├── core/               # Configuration
│   │   ├── __init__.py
│   │   └── config.py       # Settings management
│   ├── models/             # Pydantic models
│   │   ├── __init__.py
│   │   └── npc.py         # NPC data models
│   └── services/           # Business logic
│       ├── __init__.py
│       └── gemini_service.py  # Gemini AI integration
├── run.py                  # Entry point
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## Features

✅ **REST API** for NPC conversations  
✅ **Proper separation of concerns** (routes, services, models)  
✅ **Type hints** and Pydantic validation  
✅ **Environment configuration** with pydantic-settings  
✅ **Dependency injection** pattern  
✅ **Structured logging**  
✅ **Error handling**  
✅ **CORS** enabled for web app  
✅ **Auto-generated docs** at `/docs`  

## Setup

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure environment

Copy the example environment file:
```bash
cp .env.example ../.env
```

Edit `.env` in the project root and add your Gemini API key:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Run the server

```bash
python run.py
```

Server will start at: **http://localhost:8000**  
API docs available at: **http://localhost:8000/docs**

## API Endpoints

## API Endpoints

### Health Check
```
GET /
```

### NPC Chat
```
POST /api/npc/chat
```
Get NPC response to player message.

**Request Body:**
```json
{
  "npc": {
    "id": "1",
    "name": "Sophia Castellano",
    "role": "Museum Night Guard",
    "personality": "Professional, takes job seriously",
    "location": "Museum East Wing"
  },
  "objectives": [
    {
      "id": "obj1",
      "description": "Camera offline schedule",
      "confidence": "high",
      "is_completed": false
    }
  ],
  "player_message": "Tell me about the cameras",
  "conversation_history": [],
  "difficulty": "medium"
}
```

**Response:**
```json
{
  "text": "The cameras? Well, they go offline for maintenance every Tuesday at 3 AM for about 15 minutes.",
  "revealed_objectives": ["obj1"]
}
```

### Quick Responses
```
POST /api/npc/quick-responses
```
Generate 3 quick response suggestions.

**Response:**
```json
{
  "responses": [
    "Tell me more about your work here.",
    "When do the cameras go offline?",
    "Have you noticed anything unusual lately?"
  ]
}
```

### WebSocket
```
WS /ws/{room_code}
```
Real-time communication for multiplayer rooms.

## Testing

Test the API:
```bash
curl http://localhost:8000/
```

Test NPC chat:
```bash
curl -X POST http://localhost:8000/api/npc/chat \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

## Architecture

```
Flutter App (UI)
    ↕ HTTP/WebSocket
Python FastAPI Backend
    ↕ REST API
Google Gemini AI
```

The Flutter app should:
- Display UI
- Send player messages to backend
- Receive NPC responses
- Update UI based on backend responses

The Python backend:
- Handles ALL LLM interactions
- Manages game state
- Detects objective completion
- Broadcasts updates to all players in room
