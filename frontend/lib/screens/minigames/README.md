# Minigame System

All minigames have been moved from the prototype to the main project with full difficulty support.

## Structure

```
frontend/lib/
├── models/
│   └── minigame.dart                    # Difficulty enum and data models
├── screens/
│   └── minigames/
│       └── minigame_hub_screen.dart     # Main hub with difficulty selector
└── widgets/
    └── minigames/
        ├── shared_ui.dart               # Shared UI components
        ├── lockpick_minigame.dart       # Safe Cracker
        ├── simon_says_minigame.dart     # Hacker
        ├── dial_safe_minigame.dart      # Safe Cracker
        ├── button_mash_minigame.dart    # Muscle
        ├── timing_tap_minigame.dart     # Pickpocket
        ├── wire_connect_minigame.dart   # Hacker
        ├── card_swipe_minigame.dart     # Insider
        ├── rhythm_climb_minigame.dart   # Cat Burglar
        └── logic_clues_minigame.dart    # Mastermind
```

## Difficulty System

Each minigame now accepts a `MinigameDifficulty` parameter with three levels:
- **Easy**: More forgiving settings, fewer requirements
- **Medium**: Balanced challenge (original prototype difficulty)
- **Hard**: Increased precision, speed, or targets

### Per-Minigame Difficulty Settings

#### Lockpick
- Easy: 3 pins, 92% precision
- Medium: 5 pins, 95% precision
- Hard: 7 pins, 97% precision

#### Simon Says
- Easy: 4 rounds, slower (700ms flash)
- Medium: 5 rounds, medium speed (600ms)
- Hard: 7 rounds, faster (400ms)

#### Dial Safe
- Easy: 2 numbers, ±3 tolerance
- Medium: 3 numbers, ±2 tolerance
- Hard: 4 numbers, ±1 tolerance

#### Button Mash
- Easy: 30 taps in 15s
- Medium: 50 taps in 10s
- Hard: 70 taps in 8s

#### Timing Tap
- Easy: 3 successes, 30% zone (3s cycle)
- Medium: 5 successes, 20% zone (2.5s cycle)
- Hard: 7 successes, 14% zone (2s cycle)

#### Wire Connect
- Easy: 3 wires to connect
- Medium: 5 wires to connect
- Hard: 7 wires to connect

#### Card Swipe
- Easy: 2 successes, 150-700 speed
- Medium: 3 successes, 200-600 speed
- Hard: 5 successes, 300-500 speed

#### Rhythm Climb
- Easy: 6 height, slower (2.5s), 10% hit zone
- Medium: 10 height, medium (2s), 8% hit zone
- Hard: 15 height, faster (1.6s), 6% hit zone

#### Logic Clues
- Easy: 3 boxes, simpler clues
- Medium: 4 boxes, moderate clues
- Hard: 5 boxes, complex clues

## Usage

To navigate to the minigame hub:

```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => const MinigameHubScreen(),
  ),
);
```

The difficulty selector appears at the top of the hub screen. When a user selects a minigame, it will launch with the currently selected difficulty.

## Adding New Minigames

1. Create a new file in `widgets/minigames/`
2. Extend `StatefulWidget` with a `MinigameDifficulty difficulty` parameter
3. Implement different settings based on the difficulty
4. Add the minigame to `_implementedMinigames` map in `minigame_hub_screen.dart`
5. Update the corresponding `MinigameInfo` in `_roles` to set `isImplemented: true`
