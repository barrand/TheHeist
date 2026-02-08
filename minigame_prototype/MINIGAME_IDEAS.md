# Minigame Ideas for The Heist

Quick reference for different minigame types to prototype.

## 1. Lockpicking 🔓
**Status**: ✅ Prototype created in `lockpick_minigame/` (Tab 1)

**Mechanic**: Drag pins vertically to find correct positions
- Visual feedback via color (red → orange → yellow → green)
- 5 pins to solve
- No time limit in prototype

**Variations to Try**:
- Tension wrench mechanic (two-stage process)
- Random "jiggles" that reset progress
- Different lock types (basic, advanced, masterwork)
- Time pressure mode

---

## 2. Hacking/Password Cracking 💻
**Status**: ✅ Multiple implementations!
- **Simon Says** - Tab 2: Pattern memory minigame
- **Wire Connect** - Tab 6: Match colored wires to ports

**Current Implementations**:

### Simon Says (Tab 2)
- 4 colored buttons flash in sequence
- Player must repeat the pattern
- Pattern grows longer each round (5 rounds to win)

### Wire Connect (Tab 6)
- 4 colored wires on left, shuffled ports on right
- Tap left ports to auto-connect to matching colors
- All 4 must be connected correctly
- Based on `wire_connecting` from roles.json

**Other Mechanic Options to Try**:
- **Grid Pattern**: Connect nodes in correct sequence (like Android unlock)
- **Code Matrix**: Find correct characters highlighted in scrolling text
- **Binary Decoder**: Match binary patterns to decrypt codes
- **Port Scanner**: Find open ports by trial and error with clues

**UI Ideas**:
- Terminal/console aesthetic
- Matrix-style falling characters
- Progress bars and system logs
- "Access Granted" animations

---

## 3. Safe Cracking 🔐
**Status**: ✅ Dial rotation implemented in `lockpick_minigame/` (Tab 3)

**Current Implementation**: Dial rotation
- Drag to rotate circular dial
- Digital display shows current number (0-99)
- Hit 3 target numbers in sequence (±2 tolerance)
- Submit button to lock in each number

**Enhancements to Try**:
- **Haptic Feedback**: Vibration at correct numbers
- **Direction Indicators**: Right → Left → Right pattern
- **Audio Cues**: Listen for tumbler sounds
- **Tighter Tolerance**: Exact numbers only

**UI Improvements**:
- Sound wave visualizer showing feedback
- More realistic dial appearance
- Rotation direction arrows

---

## 4. Wire Cutting/Bomb Defusal 💣
**Status**: ⏳ Not yet implemented

**Mechanic Options**:
- **Color Sequence**: Cut wires in correct color order
- **Simon Says**: Repeat pattern shown
- **Rule-Based**: Follow complex rules (e.g., "cut red if blue is present")
- **Time Pressure**: Countdown timer with consequences

**UI Ideas**:
- Top-down view of device
- Wire diagram with labels
- Timer with tension music
- Sparks/effects when cutting

**Implementation Priority**: Medium - Good for Hacker role

---

## 5. Stealth/Timing ⏱️
**Status**: ✅ Multiple implementations!
- **Timing Tap** - Tab 5: Precision timing minigame
- **Card Swipe** - Tab 7: Speed-based timing
- **Rhythm Climb** - Tab 8: Beat-based timing

**Current Implementations**:

### Timing Tap (Tab 5) ⭐ IMPROVED
- Circle shrinks toward center with visual feedback
- **30% success zone** with green indicator
- **Slower animation** for better reaction time
- **Real-time feedback** shows success/failure
- 5 successful taps to win

### Card Swipe (Tab 7)
- Swipe at the correct speed (200-600 pixels/sec)
- Too fast or too slow = failure
- Visual speed meter with color gradient
- 3 perfect swipes to win

### Rhythm Climb (Tab 8)
- Tap in rhythm with visual beat indicator
- On-beat taps = climb up
- Off-beat twice = slip down
- Reach height 10 to win

**Other Mechanics to Try**:
- **Guard Pattern**: Move when guard isn't looking
- **Camera Dodge**: Time movement between camera sweeps
- **Laser Grid**: Navigate through moving lasers
- **Sound Meter**: Stay below noise threshold

**UI Ideas**:
- Top-down or side view for stealth
- Vision cones for guards
- Rhythm-based timing indicators
- Tension meter

---

## 6. Memory/Pattern Match 🧠
**Status**: ✅ Covered by Simon Says (Tab 2) and Card Swipe (Tab 7)

**Current Implementations**:
- **Simon Says**: Sequence memory and pattern matching
- **Card Swipe**: Timing and precision memory (remembering the right speed)

**Other Mechanic Options to Try**:
- **Card Matching**: Remember positions of items
- **Spot Differences**: Find changes between two scenes
- **Code Memorization**: Remember multi-digit codes shown briefly

**UI Ideas**:
- Clean, focused interface
- Progressive difficulty
- Time bonus for speed
- Mistake counter

**Implementation Priority**: Low - already have pattern memory

---

## 7. Physical Puzzles 🧩
**Status**: ⏳ Not yet implemented

**Mechanic Options**:
- **Sliding Puzzle**: Rearrange tiles to form image
- **Gear Alignment**: Rotate gears to connect paths
- **Pipe Connection**: Connect flow from start to end
- **Mirror Reflection**: Angle mirrors to direct laser

**UI Ideas**:
- Interactive drag/rotate
- Snap-to-grid mechanics
- Visual feedback on valid moves
- "Aha!" moment satisfaction

**Implementation Priority**: Medium - Good variety from action-based games

---

## 8. Button Mashing 💪
**Status**: ✅ Implemented in `lockpick_minigame/` (Tab 4)

**Current Implementation**: Rapid tapping
- Tap a big button as fast as possible
- Reach 50 taps within 10 seconds
- Progress bar shows completion
- Perfect for Muscle role tasks

**Variations to Try**:
- Different tap targets (longer duration, more taps)
- Moving target that needs to be tapped
- Multi-button sequences
- Hold vs tap mechanics

---

## Currently Implemented (8 Minigames)

All located in `lockpick_minigame/` with tab navigation:

1. **Lockpick** (Safe Cracker) - Drag pins to correct positions
2. **Simon Says** (Hacker) - Memorize and repeat patterns
3. **Dial Safe** (Safe Cracker) - Rotate dial to hit numbers
4. **Button Mash** (Muscle) - Tap rapidly to reach goal
5. **Timing Tap** (Pickpocket) - ⭐ IMPROVED - Tap when circle hits green zone
6. **Wire Connect** (Hacker) - Match colored wires to ports
7. **Card Swipe** (Insider) - Swipe at correct speed
8. **Rhythm Climb** (Cat Burglar) - Tap in rhythm to climb

### Recent Improvements ✨
- **Timing Tap**: 3x wider success zone, visual indicators, slower animation, real-time feedback
- Makes the game much more accessible and fun!

Run with: `cd minigame_prototype/lockpick_minigame && flutter run`

---

## Implementation Tips

### Quick Prototyping
1. Start with basic mechanic (no polish)
2. Test core gameplay loop
3. Add feedback (visual/audio)
4. Tune difficulty
5. Add polish only if keeping

### Difficulty Scaling
- **Easy**: 3 pins/wires/steps, generous timing
- **Medium**: 5 pins/wires/steps, moderate timing
- **Hard**: 7+ pins/wires/steps, tight timing

### Integration with Main Game
- Minigames trigger for specific task types
- Success = task completion
- Failure = retry or alternate path
- Optional: Skip minigame for accessibility

### Accessibility Considerations
- Allow skipping minigames
- Adjustable difficulty
- Visual + audio + haptic feedback
- No color-only indicators
- Generous timing options
