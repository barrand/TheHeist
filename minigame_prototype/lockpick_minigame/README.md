# Minigame Prototypes

A Flutter app showcasing 8 different minigame prototypes for The Heist.

## Included Minigames

### 1. 🔓 Lockpick (Safe Cracker)
**Mechanic**: Drag pins vertically to find correct positions
- Visual feedback via color (red → orange → yellow → green)
- 5 pins to solve
- Based on `lockpick_timing` from roles.json

### 2. 🎮 Simon Says (Hacker)
**Mechanic**: Memorize and repeat button pattern
- 4 colored buttons
- Pattern grows by 1 each round
- Complete 5 rounds to win
- Based on `simon_says_sequence` from roles.json

### 3. 🔐 Dial Safe (Safe Cracker)
**Mechanic**: Rotate dial to hit target numbers
- Drag to rotate the dial
- Hit 3 target numbers in sequence
- Allows ±2 tolerance for success
- Based on `dial_rotation` from roles.json

### 4. 💪 Button Mash (Muscle)
**Mechanic**: Tap as fast as possible
- Reach 50 taps within 10 seconds
- Progress bar shows completion
- Based on `button_mash_barrier` from roles.json

### 5. 👆 Timing Tap (Pickpocket) ⭐ BALANCED
**Mechanic**: Tap when shrinking circle reaches green zone
- Circle shrinks toward center with visual feedback
- **20% success zone** - challenging but fair
- **Visual green zone indicator** clearly shows target
- **Slower animation** (2.5s) for better reaction time
- **Real-time feedback** - "PERFECT!" or "Too early/late"
- Circle glows green when in success zone
- Hit the zone 5 times to win
- Based on `timing_tap` from roles.json

### 6. 🔌 Wire Connect (Hacker) ⭐ DISCOVERY PUZZLE
**Mechanic**: Figure out whether wires match by color or symbol
- **Left wires**: Each has BOTH color and symbol (Red Star, Blue Circle, etc.)
- **Right ports**: Each shows EITHER color OR symbol (mystery!)
- **Discovery element**: Try connections to learn the pattern
- Wrong attempts flash red with feedback
- Correct connections lock in with curved wires
- 5 wires total with trial and error
- Must figure out which attribute (color/symbol) each port matches
- Based on `wire_connecting` from roles.json

### 7. 💳 Card Swipe (Insider) ⭐ IMPROVED
**Mechanic**: Swipe card at the right speed in a terminal
- **Visual card movement** - see the card slide as you swipe
- **Terminal display** shows "READING..." status
- **Card slot visualization** with guide lines
- Swipe horizontally - not too fast, not too slow
- Target speed zone: 200-600 pixels/second
- Visual speed meter with color gradient
- Card animates back to center after each attempt
- Get 3 perfect swipes to win
- Touch/swipe gestures work great on mobile
- Based on `badge_swipe` from roles.json

### 8. 🧗 Rhythm Climb (Cat Burglar) ⭐ GUITAR HERO STYLE
**Mechanic**: Tap when the note hits the target line (like Guitar Hero!)
- **Moving note visualization** - cyan circle travels down the highway
- **Clear target zone** - green "TAP HERE" indicator
- **Easy to see timing** - tap when note overlaps target
- Visual note highway with borders
- Tap on time to climb one step
- Miss twice in a row and you slip down
- Progress bar and height counter
- Reach height 10 to win
- Much clearer than the old pulsing beat
- Based on `climbing_rhythm` from roles.json

## How to Run

```bash
cd minigame_prototype/lockpick_minigame
flutter run
```

Or on specific platforms:
```bash
flutter run -d chrome      # Web browser
flutter run -d macos       # macOS desktop
flutter run -d <device>    # iOS/Android device
```

## UI Features

- **Grid Menu**: 2-column grid of minigame cards on home screen
- **Easy Navigation**: Tap a card to play, back button to return to menu
- **Role Labels**: Each card shows which role it belongs to
- **Touch-Friendly**: Large tap targets, works great on mobile
- **Consistent Theme**: Dark theme matching The Heist aesthetic
- **Win/Fail Screens**: Clear feedback on success or failure
- **Reset/Retry**: Easy to replay each minigame

## Recent Improvements ✨

### Latest Updates (Based on Playtesting)

#### Timing Tap - Balanced Difficulty
- **20% success zone** (was 30%, then 10%) - challenging but achievable
- Green zone clearly visible
- Slower 2.5s animation
- Real-time feedback with colors

#### Wire Connect - Fixed & Improved
- **Two-step tap system**: Select left, then tap matching right
- Visual selection indicators (arrows, glowing)
- Shows selected wire name at top
- Curved wire drawing
- Works perfectly on touchscreens

#### Card Swipe - Visual Feedback
- **Animated card movement** as you swipe
- **Terminal/reader UI** with status display
- Card shows in slot with guide lines
- Animates back to center after each swipe
- Speed meter visualization
- Touch gestures fully supported

#### Rhythm Climb - Guitar Hero Style
- **Moving note system** instead of pulsing beat
- Note travels down a "highway"
- **Clear green target zone** - "TAP HERE"
- Timing is immediately obvious
- Progress bar and height counter
- Much more intuitive than before

## Mobile Web & Touch Support 📱

**All minigames are fully touch-enabled and work great on mobile web!**

- **Drag gestures**: Lockpick pins, Dial safe rotation, Card swipe
- **Tap gestures**: All buttons, Wire connect, Timing tap, Rhythm climb
- **Visual feedback**: Every interaction has clear visual response
- **Responsive UI**: Scales to different screen sizes
- **Touch-friendly targets**: All buttons and interactive elements are large enough

Tested on iOS Safari, Android Chrome, and desktop browsers.

## Notes

- All minigames are self-contained and independent
- No persistence or scoring across sessions
- Throwaway/prototype code - feel free to experiment!
- Difficulties can be easily adjusted by changing constants
- Each minigame has been playtested and balanced for fun
- Works on desktop (mouse) and mobile (touch) equally well

## Difficulty Adjustments

Easy tweaks you can make:
- **Lockpick**: Change `_pinCount` or success threshold
- **Simon Says**: Adjust rounds needed (currently 5)
- **Dial Safe**: Change tolerance or number of steps
- **Button Mash**: Adjust target taps or time limit
- **Timing Tap**: Widen/narrow success zone (currently 0.35-0.65)
- **Wire Connect**: Add more wires or timed mode
- **Card Swipe**: Adjust speed range or successes needed
- **Rhythm Climb**: Change target height or slip penalty

## Next Steps

- Test each minigame for fun factor ✅
- Adjust difficulty curves ✅ (Timing Tap improved)
- Add sound effects and haptic feedback
- Consider which mechanics work best for touch screens
- Integrate favorites into main game
