# Services Architecture

Services are separated by **purpose** and **lifecycle** to maintain clean separation of concerns.

## 🎮 **Runtime Services** (Backend Production)

Services that run during gameplay in the FastAPI backend.

### 1. `npc_conversation_service.py` ✅ IMPLEMENTED

**Purpose:** Real-time NPC chat interactions during gameplay

**Responsibilities:**
- Generate NPC responses to player messages
- Detect when objectives are revealed in conversation
- Generate quick response suggestions for players
- Manage conversation difficulty (easy/medium/hard)

**Gemini Model:** `gemini-1.5-flash-8b`
- ⚡ Fast response times for real-time gameplay
- 💰 Cost-effective for high-volume conversations
- 🎯 Optimized for dialogue generation

**Used by:** `/api/npc/chat` and `/api/npc/quick-responses` endpoints

---

### 2. `content_generation_service.py` 🔜 TODO

**Purpose:** Generate dynamic game content on-the-fly (future)

**Responsibilities:**
- Generate new tasks/objectives during gameplay
- Create random events and plot twists
- Procedural mission variations
- Dynamic NPC personality quirks

**Gemini Model:** `gemini-2.5-flash`
- More capable for complex creative generation
- Used sparingly (only when needed during game)

**Used by:** Game logic when dynamic content is needed

---

## 🛠️ **Pre-Production Services** (Scripts)

Services that run before gameplay to create content assets.

### 3. Image Generation Service

**Location:** `scripts/generate_npc_image.py`

**Purpose:** Generate NPC character portrait images

**Responsibilities:**
- Create character images in Borderlands art style
- Integrate UI theme accent colors
- Maintain character consistency
- Support various character parameters (gender, ethnicity, clothing, etc.)

**Gemini Model:** `gemini-2.5-flash-image` (nano-banana)
- ⚡ Lightning fast image generation
- 💰 Significantly cheaper than Imagen 4
- 🎭 Character consistency across generations

**Usage:**
```bash
python scripts/generate_npc_image.py \
  --name "Rosa Martinez" \
  --role "Parking Attendant" \
  --gender female \
  --ethnicity "Latina" \
  --clothing "reflective vest" \
  --background "parking garage" \
  --expression "bored" \
  --accent-colors "purple"
```

---

### 4. Experience Generation Service

**Location:** `scripts/generate_experience.py`

**Purpose:** Generate complete mission scenarios

**Responsibilities:**
- Create mission dependency trees
- Generate NPC personalities and objectives
- Define locations and inventory items
- Create task chains with proper dependencies
- Output complete mission markdown files

**Gemini Model:** `gemini-2.5-flash`
- More capable for complex scenario planning
- Longer context window for detailed missions

**Usage:**
```bash
python scripts/generate_experience.py \
  --scenario museum_gala_vault \
  --roles mastermind hacker safe_cracker \
  --output examples/generated_heist.md
```

---

## 🔮 **Future Services**

### 5. `map_generation_service.py` (Future)
- Generate visual maps for missions
- Room layouts and connections
- Could use DALL-E or Midjourney

### 6. `voice_service.py` (Future)
- Text-to-speech for NPC dialogue
- Voice cloning for character consistency
- Could use ElevenLabs or Google TTS

### 7. `moderation_service.py` (Future)
- Filter inappropriate player messages
- Validate user-generated content
- Use OpenAI Moderation API

---

## 📊 **Service Comparison**

| Service | Location | Model | Use Case | Speed | Cost |
|---------|----------|-------|----------|-------|------|
| NPC Conversation | Backend | gemini-1.5-flash-8b | Real-time chat | ⚡⚡⚡ | 💰 |
| Content Generation | Backend | gemini-2.5-flash | Dynamic events | ⚡⚡ | 💰💰 |
| Image Generation | Scripts | gemini-2.5-flash-image | NPC portraits | ⚡⚡⚡ | 💰 |
| Experience Generation | Scripts | gemini-2.5-flash | Mission creation | ⚡ | 💰💰 |

---

## 🏗️ **Architecture Principles**

1. **Separation by Purpose** - Each service has one clear responsibility
2. **Separation by Lifecycle** - Runtime vs pre-production services separated
3. **Model Selection** - Use fastest/cheapest model that meets requirements
4. **Dependency Injection** - Services injected via FastAPI Depends()
5. **Error Handling** - All services have proper try/except and fallbacks
6. **Logging** - Structured logging for debugging and monitoring

---

## 🚀 **Adding New Services**

When adding a new service:

1. **Create service file:** `app/services/your_service.py`
2. **Define class:** `YourService` with clear docstrings
3. **Add to `__init__.py`:** Export in `app/services/__init__.py`
4. **Create dependency:** Injection function in relevant API route
5. **Document here:** Add to this README
6. **Write tests:** Unit tests in `tests/services/`

Example:
```python
# app/services/your_service.py
class YourService:
    """
    Brief description
    
    Responsibilities:
    - List what it does
    - One line per responsibility
    """
    
    def __init__(self):
        settings = get_settings()
        # Initialize
    
    async def your_method(self, param: str) -> str:
        """Clear docstring"""
        try:
            # Implementation
            pass
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
```
