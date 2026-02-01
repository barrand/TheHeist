# The Heist - Backend Server

Python FastAPI backend for The Heist multiplayer game.

## Features

- **REST API** for NPC conversations
- **WebSocket** support for real-time multiplayer
- **Gemini AI** integration for dynamic NPC responses
- **CORS** enabled for Flutter web app

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file in project root (if not exists):
```bash
GEMINI_API_KEY=your_api_key_here
```

3. Run the server:
```bash
python backend/main.py
```

Server will start at: **http://localhost:8000**

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
