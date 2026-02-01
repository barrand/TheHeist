"""
The Heist - Backend API Server
FastAPI + WebSockets for real-time multiplayer heist game
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

app = FastAPI(title="The Heist API", version="1.0.0")

# Enable CORS for Flutter web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Flutter app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Use the model that works
model = genai.GenerativeModel('gemini-2.0-flash-exp')


# ============================================
# Data Models
# ============================================

class Objective(BaseModel):
    id: str
    description: str
    confidence: str  # high, medium, low, action
    is_completed: bool = False


class NPCInfo(BaseModel):
    id: str
    name: str
    role: str
    personality: str
    location: str


class ChatRequest(BaseModel):
    npc: NPCInfo
    objectives: List[Objective]
    player_message: str
    conversation_history: List[Dict[str, str]]
    difficulty: str = "medium"


class QuickResponsesRequest(BaseModel):
    npc: NPCInfo
    objectives: List[Objective]
    conversation_history: List[Dict[str, str]]


class ChatResponse(BaseModel):
    text: str
    revealed_objectives: List[str]


# ============================================
# Helper Functions
# ============================================

def get_difficulty_instructions(difficulty: str) -> str:
    """Get NPC behavior instructions based on difficulty"""
    if difficulty.lower() == "easy":
        return """
- Be helpful and forthcoming
- Share information after 1-2 questions
- Give clear hints if they're on the right track
"""
    elif difficulty.lower() == "hard":
        return """
- Be cautious and suspicious
- Require significant rapport building
- Only share information if they ask the perfect question
- May lie or mislead if they're too direct
"""
    else:  # medium
        return """
- Be realistic - friendly but not too forthcoming
- Share information after building some rapport
- Give subtle hints if they're getting warm
"""


def detect_revealed_objectives(npc_text: str, objectives: List[Objective]) -> List[str]:
    """Detect which objectives were revealed in the NPC's response"""
    revealed = []
    lower_text = npc_text.lower()
    
    for objective in objectives:
        if objective.is_completed:
            continue
        
        # Simple keyword detection - check if key words from objective appear in response
        keywords = objective.description.lower().split()
        keyword_matches = sum(1 for k in keywords if len(k) > 3 and k in lower_text)
        
        # If multiple keywords match, likely revealed
        if keyword_matches >= 2:
            revealed.append(objective.id)
    
    return revealed


# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "The Heist Backend",
        "version": "1.0.0"
    }


@app.post("/api/npc/chat", response_model=ChatResponse)
async def npc_chat(request: ChatRequest):
    """
    Get NPC response to player message
    Handles LLM interaction and objective detection
    """
    print(f"💬 NPC Chat: {request.npc.name} <- '{request.player_message}'")
    
    # Build system prompt
    objectives_text = "\n".join([
        f"- {obj.description} ({'you definitely know this' if obj.confidence == 'high' else 'you might know this' if obj.confidence == 'medium' else 'you do not know this'})"
        for obj in request.objectives
        if obj.confidence in ['high', 'medium']
    ])
    
    system_prompt = f"""You are {request.npc.name}, a {request.npc.role}.
Personality: {request.npc.personality}
Location: {request.npc.location}

The player is a member of a heist crew trying to gather information from you.

Information you know (and can share if asked properly):
{objectives_text}

Difficulty: {request.difficulty}
{get_difficulty_instructions(request.difficulty)}

IMPORTANT: 
- Stay in character at all times
- Be natural and conversational
- Share information gradually, not all at once
- If they ask about something you don't know, you genuinely don't know
- Keep responses under 3 sentences
- Don't be too obvious about having "quest information"

Player says: "{request.player_message}"

Respond naturally as {request.npc.name}:"""
    
    try:
        # Call Gemini
        response = model.generate_content(system_prompt)
        npc_text = response.text
        
        print(f"💬 NPC Response: '{npc_text}'")
        
        # Detect revealed objectives
        revealed = detect_revealed_objectives(npc_text, request.objectives)
        
        if revealed:
            print(f"✅ Revealed objectives: {revealed}")
        
        return ChatResponse(
            text=npc_text,
            revealed_objectives=revealed
        )
    
    except Exception as e:
        print(f"❌ Error in NPC chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/npc/quick-responses")
async def generate_quick_responses(request: QuickResponsesRequest):
    """
    Generate 3 quick response suggestions based on conversation context
    """
    print(f"🎲 Generating quick responses for {request.npc.name}")
    
    # Get last few messages for context
    recent_messages = request.conversation_history[-4:] if len(request.conversation_history) > 4 else request.conversation_history
    conversation_context = "\n".join([
        f"{'Player' if msg['isPlayer'] else request.npc.name}: {msg['text']}"
        for msg in recent_messages
    ])
    
    objectives_text = "\n".join([
        f"- {obj.description}"
        for obj in request.objectives
        if not obj.is_completed
    ])
    
    prompt = f"""Generate 3 SHORT response options for a player talking to an NPC in a heist game.

NPC: {request.npc.name} - {request.npc.role}
Personality: {request.npc.personality}

Objectives the player is trying to learn:
{objectives_text}

Recent conversation:
{conversation_context}

Generate 3 SHORT responses (max 10 words each):
1. A safe, friendly option
2. A direct question about one objective
3. A creative/indirect approach

Output ONLY the 3 responses, one per line, no numbers or labels."""
    
    try:
        response = model.generate_content(prompt)
        responses = response.text.strip().split('\n')
        responses = [r.strip() for r in responses if r.strip()][:3]
        
        # Fallback if LLM doesn't give good responses
        if len(responses) < 3:
            responses = [
                "Tell me more about your work here.",
                "Have you noticed anything unusual?",
                "How long have you been in this position?",
            ]
        
        print(f"🎲 Quick responses: {responses}")
        return {"responses": responses}
    
    except Exception as e:
        print(f"❌ Error generating quick responses: {e}")
        # Return fallback responses
        return {
            "responses": [
                "Tell me more about your work here.",
                "Have you noticed anything unusual?",
                "How long have you been in this position?",
            ]
        }


# ============================================
# WebSocket for Real-time Game Updates
# ============================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_code: str):
        await websocket.accept()
        if room_code not in self.active_connections:
            self.active_connections[room_code] = []
        self.active_connections[room_code].append(websocket)
        print(f"✅ Client connected to room {room_code}")
    
    def disconnect(self, websocket: WebSocket, room_code: str):
        if room_code in self.active_connections:
            self.active_connections[room_code].remove(websocket)
            print(f"❌ Client disconnected from room {room_code}")
    
    async def broadcast(self, message: dict, room_code: str):
        if room_code in self.active_connections:
            for connection in self.active_connections[room_code]:
                await connection.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    """
    WebSocket endpoint for real-time game communication
    """
    await manager.connect(websocket, room_code)
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast to all clients in the room
            await manager.broadcast(data, room_code)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting The Heist Backend Server...")
    print(f"📡 API: http://localhost:8000")
    print(f"🔌 WebSocket: ws://localhost:8000/ws/{{room_code}}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
