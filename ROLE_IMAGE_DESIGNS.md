# Role Character Portrait Designs

## Overview

Character portraits for all 12 heist roles using the same Borderlands art style as NPCs. Each role has a distinctive design that reflects their specialty and personality.

**Art Style:** 2D illustration, comic book style, bold thick outlines, cell-shaded, Borderlands game aesthetic

**Output Location:** `output/role_images/{role_id}.png`

**Usage in UI:** These images replace emoji icons in the role selection modal

---

## 🎭 The 12 Roles

### 1. Mastermind
**Role:** Strategic Planner  
**Character:** Distinguished older person in tailored suit with tactical vest  
**Setting:** Command center with blueprints and monitors  
**Personality:** Commanding and intelligent, natural leader  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Holding tablet with blueprints, smart glasses, rolled-up sleeves  

**Minigames:** None (coordinates others)  
**Description:** The strategic brain behind every operation - calm, collected, always three steps ahead

---

### 2. Hacker
**Role:** Tech Specialist  
**Character:** Young Asian person in tech hoodie with AR glasses  
**Setting:** Dark room with glowing monitors showing code  
**Personality:** Tech-obsessed genius, in the zone  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Neon underglow, tangled cables, fingerless gloves, laptop  

**Minigames:**
- Wire connecting
- Simon says sequence
- Cipher wheel alignment
- Card swipe

**Description:** Master of digital security - if it's electronic, they can crack it

---

### 3. Safe Cracker
**Role:** Lock Expert  
**Character:** Middle Eastern person in worn leather jacket with tool belt  
**Setting:** Vault room with massive safe door  
**Personality:** Patient craftsman, meticulous perfectionist  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Stethoscope against safe, lockpicking tools, magnifying headset  

**Minigames:**
- Dial rotation
- Lockpick timing
- Listen for clicks

**Description:** No lock too complex, no vault too secure - patient hands and sharp ears

---

### 4. Driver
**Role:** Getaway Specialist  
**Character:** Latina person in leather racing jacket  
**Setting:** Urban street at night with getaway car  
**Personality:** Fearless adrenaline junkie, ice-cool under pressure  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Aviator sunglasses, driving gloves, car keys, racing watch  

**Minigames:**
- Steering obstacle course
- Fuel pump
- Parking precision

**Description:** Born behind the wheel - lightning reflexes and intimate knowledge of every back street

---

### 5. Insider
**Role:** Legitimate Access  
**Character:** Professional Black person in crisp business suit  
**Setting:** Corporate office lobby with security checkpoint  
**Personality:** Legitimate and above suspicion, dual identity  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Company ID badge, briefcase, access card, perfectly groomed  

**Minigames:**
- Badge swipe
- Memory matching
- Inventory check

**Description:** The key to the front door - legitimate employee with insider knowledge and access

---

### 6. Grifter
**Role:** Social Engineer  
**Character:** Charismatic European person in expensive designer suit  
**Setting:** Elegant hotel lobby or gala event  
**Personality:** Silver-tongued smooth talker  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Champagne glass, silk pocket square, fake IDs in pocket, luxury watch  

**Minigames:**
- Timed dialogue choices
- Emotion matching
- Convincing sequence

**Description:** Master manipulator - a different story for every mark, charm that opens any door

---

### 7. Muscle
**Role:** Physical Security  
**Character:** Imposing build, diverse ethnicity  
**Setting:** Industrial warehouse with dramatic lighting  
**Personality:** Quiet intensity, speaks through presence  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Tactical gear, reinforced vest, ear piece, utility belt  

**Minigames:**
- Takedown timing
- Button mash barrier
- Reaction time

**Description:** The enforcer - handles physical obstacles and provides silent intimidation when needed

---

### 8. Lookout
**Role:** Surveillance Expert  
**Character:** Sharp-eyed South Asian person  
**Setting:** Rooftop overlooking city at dusk  
**Personality:** Hyper-aware eagle eye  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Binoculars, night vision goggles, radio, tablet with camera feeds  

**Minigames:**
- Spot the difference
- Whack-a-mole threats
- Pattern memorization

**Description:** Eyes and ears of the operation - never misses a detail, sees threats before they arrive

---

### 9. Fence
**Role:** Equipment Supplier  
**Character:** Street-smart diverse person  
**Setting:** Cluttered back-alley shop with stolen goods  
**Personality:** Wheeler-dealer, knows the value of everything  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Examining jewel with loupe, vintage jacket with pins, rings and necklaces  

**Minigames:**
- Item matching
- Haggling slider
- Quality inspection

**Description:** The connect - if you need it, they can get it, for the right price

---

### 10. Cat Burglar
**Role:** Stealth Infiltrator  
**Character:** Agile East Asian person  
**Setting:** High-rise exterior at night, dangling from rope  
**Personality:** Graceful shadow, moves like smoke  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Black stealth suit, climbing harness, grappling equipment, balaclava  

**Minigames:**
- Climbing rhythm
- Laser maze timing
- Balance meter

**Description:** Gravity-defying infiltrator - goes over, under, and through where others can't follow

---

### 11. Cleaner
**Role:** Evidence Expert  
**Character:** Meticulous European person  
**Setting:** Sterile workspace with UV lights  
**Personality:** Ghost who leaves no trace  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Dark suit, latex gloves, UV flashlight, spray bottle, forensic equipment  

**Minigames:**
- Swipe fingerprints
- Tap evidence markers
- Trash disposal

**Description:** Makes it like you were never there - erases evidence, cleans up mistakes, ghosts the scene

---

### 12. Pickpocket
**Role:** Sleight of Hand Artist  
**Character:** Street-smart young diverse person  
**Setting:** Crowded street or train station  
**Personality:** Ghost in plain sight, invisible in crowds  
**Colors:** Purple theme (vibrant purple, magenta, cyan)  
**Details:** Inconspicuous casual clothes, hidden pockets, wallet half-visible in hand  

**Minigames:**
- Timing tap
- Quick pocket search
- Distraction meter

**Description:** Fingers faster than the eye - lifts wallets, keys, and badges without anyone noticing

---

## Generation Commands

### Generate All Roles
```bash
cd scripts
python generate_role_images.py
```

### Generate Specific Role
```bash
python generate_role_images.py --role hacker
python generate_role_images.py --role safe_cracker
python generate_role_images.py --role cat_burglar
```

### List All Roles
```bash
python generate_role_images.py --list
```

---

## Color Scheme

All roles use the unified purple night heist theme for visual consistency:

- **Purple Theme:** Vibrant purple clothing accents, magenta accessories, cyan highlights
- Applies to all 12 roles for cohesive visual identity
- Creates consistent Borderlands-style aesthetic across all characters

---

## Technical Details

- **Model:** Gemini 2.5 Flash Image (nano-banana)
- **Art Style:** Borderlands comic book aesthetic
- **Resolution:** High-quality portrait (varies by generation)
- **Format:** PNG with transparency where applicable
- **Watermark:** Includes SynthID authenticity mark
- **Speed:** Lightning fast (~1-3 seconds per image)
- **Cost:** Very cost-effective for batch generation

---

## Integration with UI

### Current: Emoji Icons
```dart
Icon(Icons.person, size: 48)  // Generic icon
```

### Updated: Character Portraits
```dart
Image.asset(
  'assets/roles/mastermind.png',
  width: 120,
  height: 120,
  fit: BoxFit.cover,
)
```

### Role Selection Modal Update
Replace emoji icons (⭐, 🔓, 💻, etc.) with character portrait images for:
- More personality and character
- Visual consistency with NPC portraits
- Professional game aesthetic
- Helps players connect with their role choice

---

## Asset Path Structure

```
app/
  assets/
    roles/
      mastermind.png
      hacker.png
      safe_cracker.png
      driver.png
      insider.png
      grifter.png
      muscle.png
      lookout.png
      fence.png
      cat_burglar.png
      cleaner.png
      pickpocket.png
```

Don't forget to update `pubspec.yaml`:
```yaml
flutter:
  assets:
    - assets/roles/
```

---

## Benefits

✅ **Visual Consistency:** Matches NPC Borderlands art style  
✅ **Character Identity:** Each role has unique personality  
✅ **Professional Polish:** Game-quality character art  
✅ **Player Connection:** Helps players visualize their role  
✅ **Thematic Cohesion:** Color-coded by heist type  
✅ **Memorable:** Distinctive designs aid recognition  
✅ **Scalable:** Easy to add new roles in future

---

## Next Steps

1. ✅ Generate all 12 role portraits
2. Copy images to Flutter assets folder
3. Update `pubspec.yaml` to include role images
4. Update role selection modal to use images
5. Test image loading and display
6. Adjust sizing/layout as needed
7. Consider adding subtle animations (fade-in, hover effects)

---

## Design Philosophy

Each role portrait tells a story:
- **Clothing** reflects their specialty
- **Background** shows their typical environment
- **Expression** captures their personality
- **Details** hint at their methods
- **Pose** conveys their confidence level

The goal is that players can understand what a role does just by looking at the portrait, even before reading the description.
