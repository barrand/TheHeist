# Minigame Test Harness

A standalone Flutter app that imports and tests the **production minigame widgets** from the main project.

## Important

⚠️ This is a **test harness only** - not production code.

All minigame widgets are imported from `frontend/lib/widgets/minigames/`. Changes to game logic should be made in those production files, not here.

## How to Run

From the project root:

```bash
cd minigame_prototype/lockpick_minigame
flutter pub get  # Install dependencies (including frontend package)
flutter run
```

Or for web:
```bash
flutter run -d chrome
```

Or on specific platforms:
```bash
flutter run -d macos       # macOS desktop
flutter run -d <device>    # iOS/Android device
```

## Features

- **Difficulty Selector**: Test Easy, Medium, and Hard difficulty for each minigame
- **All Roles**: Browse minigames organized by role (Mastermind, Hacker, Safe Cracker, etc.)
- **Quick Access**: Instantly launch any implemented minigame
- **Production Code**: Tests the actual widgets that will be used in the game

## Included Minigames

All 9 implemented minigames with full difficulty support:

### Mastermind
- **Logic Clues**: Arrange colored boxes using logical clues

### Hacker
- **Wire Connect**: Match wires by color or symbol through trial and error
- **Simon Says**: Memorize and repeat increasingly complex color patterns

### Safe Cracker
- **Dial Safe**: Rotate the dial to the correct combination
- **Lockpick**: Position pins precisely to unlock

### Muscle
- **Button Mash**: Tap rapidly to break through obstacles

### Insider
- **Badge Swipe**: Swipe the card at the perfect speed

### Pickpocket
- **Timing Tap**: Tap when the shrinking circle enters the target zone

### Cat Burglar
- **Rhythm Climb**: Guitar Hero-style rhythm game with moving target zones

## UI Features

- **Role-based Organization**: Minigames grouped by character role
- **Implemented Status**: Visual indicators (✓) for completed minigames, TODO badges for unimplemented ones
- **Difficulty Toggle**: Switch between Easy, Medium, Hard at the top of the screen
- **Compact Layout**: Scrollable list optimized for both mobile and desktop
- **Back Navigation**: Easy return to the main menu from any minigame

## Mobile Web & Touch Support

All minigames are fully functional on mobile web with touchscreen support.

## Adding New Minigames

To test new minigames in this harness:

1. Create the minigame widget in `frontend/lib/widgets/minigames/`
2. Add it to the `_implementedMinigames` map in this file's `main.dart`
3. Update the corresponding role's minigame list to set `isImplemented: true`
4. Run `flutter pub get` if needed
5. Launch the test harness
