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
        ├── logic_clues_minigame.dart    # Mastermind
        ├── doodle_climb_minigame.dart   # Cat Burglar
        ├── tag_evidence_minigame.dart   # Cleaner
        ├── item_matching_minigame.dart  # Fence
        ├── steering_obstacle_minigame.dart  # Driver
        ├── whack_a_threat_minigame.dart    # Lookout
        └── emotion_matching_minigame.dart  # Grifter
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
- Easy: 7 rounds, slower base (speed increases each round)
- Medium: 8 rounds, medium base (speed increases each round)
- Hard: 10 rounds, faster base (speed increases each round)

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
- Hard: 9 wires to connect (no instruction text)

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
- Hard: 6 boxes, relative-only clues (no direct positions—requires chain deduction)

#### Tag Evidence
- Tag evidence markers in numerical order (1→2→3…); wrong order = fail
- Easy: 6 markers, 12s, 2 decoys (-2s each)
- Medium: 9 markers, 10s, 4 decoys (-3s each)
- Hard: 12 markers, 11s, 6 decoys (-4s each)

#### Item Match
- Each difficulty uses a different item set (no duplicates across levels); items align with companies
- Easy: 3 pairs (Oil Painting→Metro Gallery, Diamond Ring→Brilliant Acquisitions, Vintage Watch→Chrono Trade), 1 strike allowed
- Medium: 4 pairs (Confidential Files, Bronze Statue, Gold Bars, Pearl Necklace), no mistakes
- Hard: 6 pairs (Stamp Album, Ming Vase, Rare Coins, Rare Book, Fur Coat, Wine Crate), no mistakes

#### Emotion Match (Grifter)
- Tap the facial expression (emoji) that fits the social situation
- Easy: 4 rounds, 3 options, 4 strikes allowed
- Medium: 6 rounds, 4 options, 3 strikes
- Hard: 8 rounds, 5 options, 2 strikes

#### Whack-a-Threat (Lookout)
- Tap threats (guard, alarm) on camera feeds; avoid decoys (civilians)
- Easy: 2×2 grid, 8 threats, 3 misses / 2 wrong taps allowed
- Medium: 3×2 grid, 12 threats
- Hard: 3×3 grid, 18 threats, 2 misses / 1 wrong tap

#### Obstacle Course (Driver)
- Crossy Road–style: drive forward, drag/arrows to move, dodge cars/barriers/cones; obstacles come from the top; speed increases with distance; health bar (car -40, barrier -25, cone -15)
- Easy: 4000m, speed ramps
- Medium: 6000m, faster ramp
- Hard: 8000m, fastest ramp

#### Doodle Climb
- Easy: Target 200, 80px platforms, slower gravity, bigger jump
- Medium: Target 400, 70px platforms, standard physics
- Hard: Target 600, 55px platforms, faster gravity, tighter timing

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
