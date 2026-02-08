# Minigame Migration Summary

All minigames have been successfully migrated to their permanent production home with full difficulty support.

## ✅ What Was Done

### 1. Production Code Location
All minigames now live in the main project:

```
frontend/lib/
├── models/
│   └── minigame.dart                    # Difficulty enum & data models
├── screens/
│   └── minigames/
│       └── minigame_hub_screen.dart     # Hub with difficulty selector
└── widgets/
    └── minigames/
        ├── shared_ui.dart               # Shared components
        ├── lockpick_minigame.dart
        ├── simon_says_minigame.dart
        ├── dial_safe_minigame.dart
        ├── button_mash_minigame.dart
        ├── timing_tap_minigame.dart
        ├── wire_connect_minigame.dart
        ├── card_swipe_minigame.dart
        ├── rhythm_climb_minigame.dart
        └── logic_clues_minigame.dart
```

### 2. Difficulty System
Each minigame accepts a `MinigameDifficulty` parameter:
- **Easy**: More forgiving, fewer requirements
- **Medium**: Balanced (original prototype difficulty)
- **Hard**: Increased precision/speed/targets

### 3. Test Harness
The prototype folder now serves as a **test harness** that:
- ✅ Imports production code from `frontend/lib/widgets/minigames/`
- ✅ Provides quick testing without launching full app
- ✅ Includes difficulty selector for testing all modes
- ⚠️ **NOT** production code - just for convenience

## 📁 File Structure

### Production Code (Goes to Production)
- `frontend/lib/models/minigame.dart`
- `frontend/lib/screens/minigames/minigame_hub_screen.dart`
- `frontend/lib/widgets/minigames/*.dart` (all 10 files)

### Test Harness (NOT Production)
- `minigame_prototype/lockpick_minigame/` - Imports & tests production widgets

## 🎮 Using Production Minigames

### In the Main App
```dart
import 'package:the_heist/screens/minigames/minigame_hub_screen.dart';

// Navigate to minigame hub
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => const MinigameHubScreen(),
  ),
);
```

### Individual Minigame
```dart
import 'package:the_heist/widgets/minigames/lockpick_minigame.dart';
import 'package:the_heist/models/minigame.dart';

// Use a specific minigame
LockpickMinigame(difficulty: MinigameDifficulty.medium)
```

## 🧪 Testing with the Prototype

```bash
cd minigame_prototype/lockpick_minigame
flutter pub get
flutter run
# or
flutter run -d chrome  # For web testing
```

The prototype automatically imports the production widgets, so any changes you make to the production code will be reflected in the test harness.

## 🔧 Making Changes

### To modify a minigame:
1. Edit the file in `frontend/lib/widgets/minigames/`
2. Test using the prototype harness OR the full app
3. Commit changes to production code only

### To add a new minigame:
1. Create widget in `frontend/lib/widgets/minigames/your_minigame.dart`
2. Add difficulty support (Easy/Medium/Hard)
3. Add to `_implementedMinigames` map in `minigame_hub_screen.dart`
4. Update role's minigame list to set `isImplemented: true`
5. (Optional) Add to prototype's `main.dart` for quick testing

## 📊 Difficulty Settings Per Game

| Minigame | Easy | Medium | Hard |
|----------|------|--------|------|
| Lockpick | 3 pins, 92% precision | 5 pins, 95% precision | 7 pins, 97% precision |
| Simon Says | 4 rounds, 700ms | 5 rounds, 600ms | 7 rounds, 400ms |
| Dial Safe | 2 numbers, ±3 | 3 numbers, ±2 | 4 numbers, ±1 |
| Button Mash | 30 taps, 15s | 50 taps, 10s | 70 taps, 8s |
| Timing Tap | 3 hits, 30% zone | 5 hits, 20% zone | 7 hits, 14% zone |
| Wire Connect | 3 wires | 5 wires | 7 wires |
| Card Swipe | 2 hits, 150-700 | 3 hits, 200-600 | 5 hits, 300-500 |
| Rhythm Climb | 6 height, 2.5s | 10 height, 2s | 15 height, 1.6s |
| Logic Clues | 3 boxes | 4 boxes | 5 boxes |

## ⚠️ Important Notes

1. **Production code**: `frontend/lib/` - This goes to production
2. **Test harness**: `minigame_prototype/` - This does NOT go to production
3. The test harness imports production widgets via `the_heist` package dependency
4. All game logic changes should be made in `frontend/lib/widgets/minigames/`
5. The prototype is just a convenience wrapper for testing

## ✨ Benefits of This Setup

- **Single source of truth**: All minigame logic in one place
- **Easy testing**: Quick prototype for rapid iteration
- **Difficulty support**: All games scale from easy to hard
- **Organized structure**: Clear separation by role
- **Reusable**: Production widgets can be used anywhere in the app
- **Type-safe**: Full Flutter type checking and analysis
