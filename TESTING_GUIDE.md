# Testing Guide - Simple & Clean

## Quick Test Flow

### 1. Start the App

```bash
./restart-app.sh
```

This starts:
- Backend on `http://localhost:8000`
- Frontend on `http://localhost:8087`

### 2. Browser 1 (Mastermind)

1. Open `http://localhost:8087`
2. Click **🎭 Test as Mastermind** button
3. Room auto-created with code like `APPLE` ✅
4. Green snackbar shows the room code for 8 seconds
5. Auto-joins with Mastermind role
6. Auto-selects museum_gala_vault scenario
7. Waits in lobby for second player

### 3. Browser 2 (Safe Cracker)

1. Open `http://localhost:8087` (same URL!)
2. Click **🔐 Test as Safe Cracker** button
3. Dialog asks for room code
4. Enter the code from Browser 1 (e.g., `APPLE`)
5. Auto-joins with Safe Cracker role
6. Both players see each other in lobby

### 4. Start the Game

- First player (host) clicks **Start Game**
- Both navigate to GameScreen
- See your tasks!

## What's Automated

✅ **Room creation** - MM button auto-creates room with random code  
✅ **Role selection** - Buttons auto-select MM or SC role  
✅ **Scenario selection** - Auto-selects museum_gala_vault  
✅ **Late joiners** - If you join a game in-progress, you get sent straight to GameScreen  

## What's Manual

📝 **SC joins** - Safe Cracker enters room code from Mastermind  
📝 **Starting game** - Host manually clicks "Start Game" button  
📝 **Task completion** - Click buttons to complete tasks  

## After Hot Reload

1. **Browser 1:** Refresh (Cmd+R) → Click MM button → New room created
2. **Browser 2:** Refresh (Cmd+R) → Click SC button → Enter new room code
3. Back in the lobby!

## Tips

- Use simple room codes like: APPLE, PIANO, TABLE, HOUSE, CHAIR
- First browser = Mastermind (usually host)
- Second browser = Safe Cracker
- Room codes are 4-6 letters (auto-generated or manual)

## File Structure

```
Frontend (Flutter):
  app/lib/screens/landing_page.dart  → Test buttons
  app/lib/screens/room_lobby_screen.dart  → Auto-role selection
  app/lib/screens/game_screen.dart  → Game UI

Backend (Python):
  backend/app/api/websocket.py  → Auto-send game_started to late joiners
  backend/examples/generated_museum_gala_vault_2players.md  → Game data
```

## Clean & Simple! 🎉

No more:
- ❌ URL parameters
- ❌ TEST room special handling  
- ❌ Auto-start timers
- ❌ Complex race condition logic

Just:
- ✅ Click button
- ✅ Enter room code
- ✅ Auto-select role
- ✅ Start game
