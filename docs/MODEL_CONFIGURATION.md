# Model Configuration Guide

This document explains how AI models are configured and used across The Heist project.

## 📍 Centralized Configuration

All model configurations are centralized in **two places**:

1. **Backend Runtime Models** → `backend/app/core/config.py`
2. **Scripts/Generation Models** → `backend/scripts/config.py`

Both read from the same `.env` file in the project root.

## 🤖 Model Types & Usage

### 1. Experience Generation Model

**Purpose:** Generate full heist experiences with task dependency trees, NPCs, discovery systems

**Location:** `backend/scripts/config.py` → `GEMINI_EXPERIENCE_MODEL`

**Default:** `gemini-2.5-flash`

**Why this model:**
- Long context window for detailed prompts
- Structured output for task trees
- Creative but consistent
- Fast and cost-effective

**Used by:**
- `backend/scripts/generate_experience.py`

**Override in .env:**
```bash
GEMINI_EXPERIENCE_MODEL=gemini-2.5-flash
```

---

### 2. NPC Interaction Model

**Purpose:** Real-time NPC dialogue responses during gameplay

**Location:** `backend/app/core/config.py` → `gemini_npc_model`

**Default:** `gemini-2.0-flash-lite`

**Why this model:**
- Ultra-fast response times
- No thinking tokens (lower latency)
- Cheapest for high-volume requests
- Good conversational quality

**Used by:**
- `backend/app/services/npc_conversation_service.py`

**Override in .env:**
```bash
GEMINI_NPC_MODEL=gemini-2.0-flash-lite
```

---

### 3. Quick Response Suggestion Model

**Purpose:** Generate player chat response suggestions

**Location:** `backend/app/core/config.py` → `gemini_quick_response_model`

**Default:** `gemini-2.0-flash-lite`

**Why this model:**
- Same as NPC model (fast, cheap)
- Quick suggestions need low latency
- Simple task, doesn't need advanced reasoning

**Used by:**
- `backend/app/services/npc_conversation_service.py` (quick responses)

**Override in .env:**
```bash
GEMINI_QUICK_RESPONSE_MODEL=gemini-2.0-flash-lite
```

---

### 4. Image Generation Models

**Purpose:** Generate visual assets for roles, scenarios, NPCs, objects

**Location:** `scripts/config.py` → `IMAGEN_MODEL`, `GEMINI_IMAGE_MODEL`

**Defaults:**
- **Imagen 4.0:** `imagen-4.0-generate-001`
- **Gemini 2.5 Flash Image:** `gemini-2.5-flash-latest-image`

**Why these models:**
- **Imagen 4.0:** Best quality for character portraits (roles, player avatars)
- **Gemini 2.5 Flash Image:** Faster and cheaper for NPCs and objects

**Used by:**
- `scripts/generate_npc_image.py` (roles, player avatars → Imagen 4.0)
- `scripts/generate_npc_image_fast.py` (NPCs, objects → Gemini 2.5 Flash Image)
- `scripts/generate_scene_image.py` (scenario locations → Imagen 4.0)

**Override:** These are hardcoded in `scripts/config.py` for clarity, but could be moved to `.env` if needed.

---

## 🔧 How to Change Models

### Option 1: Edit .env File (Recommended)

Add or update these lines in `/path/to/project/.env`:

```bash
# Experience generation
GEMINI_EXPERIENCE_MODEL=gemini-2.5-flash

# NPC interactions (runtime)
GEMINI_NPC_MODEL=gemini-2.0-flash-lite

# Quick responses (runtime)
GEMINI_QUICK_RESPONSE_MODEL=gemini-2.0-flash-lite
```

### Option 2: Edit Config Files Directly

**For backend runtime models:**
- Edit `backend/app/core/config.py`
- Change default values in the `Settings` class

**For script models:**
- Edit `scripts/config.py`
- Change `GEMINI_EXPERIENCE_MODEL`, `IMAGEN_MODEL`, etc.

---

## 📊 Model Comparison

| Model | Speed | Cost | Quality | Best For |
|-------|-------|------|---------|----------|
| `gemini-2.5-flash` | Fast | $$ | High | Experience generation, complex tasks |
| `gemini-2.0-flash-lite` | Ultra-fast | $ | Good | Real-time NPC chat, quick responses |
| `imagen-4.0-generate-001` | Slow | $$$ | Excellent | Character portraits, key visuals |
| `gemini-2.5-flash-latest-image` | Fast | $ | Good | NPCs, objects, background art |

---

## 🚨 Important Notes

1. **No mixing of model names:** Always use the exact model identifier from Google's API docs
2. **Backend needs restart:** Changing `.env` requires backend restart to pick up new values
3. **Scripts read .env directly:** No restart needed, but rerun the script
4. **API key is shared:** All models use the same `GEMINI_API_KEY`
5. **Costs add up:** Monitor usage at https://aistudio.google.com/

---

## 🔍 Debugging Model Issues

### "Model not found" errors

Check that your model name matches exactly:
- ✅ `gemini-2.5-flash` (correct)
- ❌ `models/gemini-2.5-flash` (wrong for new SDK)
- ❌ `gemini-1.5-flash` (old version)

### Backend using wrong model

1. Check `.env` has correct value
2. Restart backend: `cd backend && pkill -f uvicorn && python3 -m uvicorn app.main:app --reload`
3. Check logs for "Initialized NPC Conversation Service - NPC model: ..."

### Scripts using wrong model

1. Check `.env` has correct value
2. Rerun script: `python3 scripts/generate_experience.py ...`
3. Check output for "Model: gemini-2.5-flash" line

---

## 📚 References

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Model Pricing](https://ai.google.dev/pricing)
- Backend config: `backend/app/core/config.py`
- Scripts config: `scripts/config.py`
