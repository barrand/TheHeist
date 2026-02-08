# Minigame Prototype Test Harness

This folder contains a **test harness** for quick minigame testing and development.

## Purpose

The prototype app imports and runs the **production minigame code** from `frontend/lib/widgets/minigames/`.

- **Quick testing**: Run minigames instantly without launching the full app
- **Isolated environment**: Test minigames in isolation with all difficulty levels
- **Fast iteration**: Quickly verify changes to production minigame code
- **Mobile testing**: Easy testing on physical devices or web

## Important

⚠️ **This is NOT production code** - it's a convenience tool for testing.

The minigames themselves are imported from the production codebase at `frontend/lib/widgets/minigames/`. Any changes to minigame logic should be made in those production files, not here.

## Running the Prototype

```bash
cd minigame_prototype/lockpick_minigame
flutter pub get
flutter run
```

Or for web testing:
```bash
flutter run -d chrome
```

## What's Tested

All implemented minigames with full difficulty support (Easy/Medium/Hard):
- Lockpick (Safe Cracker)
- Dial Safe (Safe Cracker)
- Simon Says (Hacker)
- Wire Connect (Hacker)
- Badge Swipe (Insider)
- Button Mash (Muscle)
- Timing Tap (Pickpocket)
- Rhythm Climb (Cat Burglar)
- Logic Clues (Mastermind)

## Structure

```
minigame_prototype/
└── lockpick_minigame/        # Test harness Flutter app
    ├── lib/
    │   └── main.dart          # Imports production widgets
    └── pubspec.yaml           # Depends on frontend package
```

The `main.dart` file provides a simple navigation UI to test all minigames with different difficulty settings.
