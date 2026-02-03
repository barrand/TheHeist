# Gender Toggle & 200px Images Update ✅

Final UI enhancement: Gender toggle in role selection modal + massive 200px character portraits!

## 🎨 Major Updates

### 1. **Gender Toggle in Role Selection**
Players can now change gender **inside the role selection modal**!

**Before:**
- Gender selected once at name entry
- No way to switch without leaving lobby

**After:**
- Gender toggle at top of role selection modal
- **"Show as: [Female] [Male]"** toggle buttons
- Instant switching between male/female versions
- Starts with player's initial choice

### 2. **Massive 200px Images**
Character portraits are now **HUGE** for maximum visibility!

**Size Progression:**
- Original: 60px × 60px
- First update: 80px × 80px  
- Second update: 100px × 100px
- **Final: 200px × 200px** ✨

### 3. **Wider Modal**
Expanded modal to accommodate larger images:
- Width: 400px → **600px**
- Height: 80% → **85%** of screen
- Better showcases Imagen 4.0 quality

## 📱 New UI Layout

### Role Selection Modal

```
┌─────────────────────────────────────────────┐
│  SELECT YOUR ROLE                      ✕    │
│                                             │
│  Show as: [Female] Male  ← Toggle here!    │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  [200x200]   MASTERMIND             │   │
│  │  Portrait    Strategic planner who  │   │
│  │              coordinates the...     │   │
│  │                                     │   │
│  │              Minigames:             │   │
│  │              • None (pure strategy) │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  [200x200]   HACKER                 │   │
│  │  Portrait    Disables security...   │   │
│  │                                     │   │
│  │              Minigames:             │   │
│  │              • Wire Connecting      │   │
│  │              • Simon Says Sequence  │   │
│  │              • Cipher Wheel         │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Visual Hierarchy
1. **Modal header** with title and close button
2. **Gender toggle** prominently displayed
3. **Large portraits** (200px) dominate each card
4. **Role info** beside portrait (name, description)
5. **Minigames list** below description

## 💻 Technical Implementation

### Role Selection Modal (`role_selection_modal.dart`)

**Changed from StatelessWidget to StatefulWidget:**
```dart
class RoleSelectionModal extends StatefulWidget {
  final String initialGender; // Renamed from playerGender
  // ...
}

class _RoleSelectionModalState extends State<RoleSelectionModal> {
  late String _selectedGender; // Local state for gender
  
  @override
  void initState() {
    super.initState();
    _selectedGender = widget.initialGender; // Start with player's choice
  }
}
```

**Gender Toggle UI:**
```dart
Row(
  children: [
    Text('Show as: '),
    GestureDetector(
      onTap: () => setState(() => _selectedGender = 'female'),
      child: Container(/* Female button */),
    ),
    GestureDetector(
      onTap: () => setState(() => _selectedGender = 'male'),
      child: Container(/* Male button */),
    ),
  ],
)
```

**Image Loading with State:**
```dart
Image.asset(
  'assets/roles/${roleId}_$_selectedGender.png', // Uses local state!
  width: 200,
  height: 200,
)
```

### Modal Dimensions
```dart
Container(
  constraints: BoxConstraints(
    maxWidth: 600,  // Was 400px
    maxHeight: MediaQuery.of(context).size.height * 0.85,  // Was 0.8
  ),
)
```

## ✨ User Experience

### Gender Exploration Flow
1. Enter name as "Alex"
2. Select **Female** at entry (default)
3. Open role selection modal
4. Browse roles as female characters (200px portraits)
5. Toggle to **Male** to see male versions
6. Compare both versions
7. Toggle back to **Female**
8. Select role (e.g., Female Korean Hacker)

### Benefits
- **Instant switching** - See both genders without leaving modal
- **Large images** - 200px showcases Imagen 4.0 quality
- **Exploration** - Players can browse both versions
- **Flexibility** - Not locked into initial choice
- **Visual impact** - Huge portraits create connection

## 🎯 Design Features

### Gender Toggle
- **Compact placement** - Right below header, doesn't crowd
- **Clear labels** - "Show as: Female | Male"
- **Visual feedback** - Gold highlight on selected
- **Instant update** - All 12 role images switch immediately

### 200px Images
- **2× larger** than previous version (100px)
- **4× larger** than original (60px → 200px)
- **High visibility** - See character details clearly
- **Premium feel** - Professional game UI quality

### Layout Adjustments
- **Wider modal** - 600px accommodates large images
- **Taller modal** - 85% height for scrolling
- **Better spacing** - Images don't feel cramped
- **Aligned text** - Description and minigames align properly

## 📊 Size Comparison

### Image Evolution
```
Original:  60px  ■
Update 1:  80px  ■■
Update 2: 100px  ■■■
FINAL:    200px  ■■■■■■  ← 3.3× larger!
```

### Visual Impact
- **60px:** Could see character, details unclear
- **80px:** Better visibility, still small
- **100px:** Good size, character recognizable
- **200px:** Stunning detail, professional game quality ✨

## 🎮 Player Flow Examples

### Scenario 1: Female Player Exploring
```
1. Enter name: "Maria"
2. Default gender: [Female] Male
3. Join lobby
4. Open role selection
5. See: 200px portraits of all female characters
6. Click "Show as: Male" 
7. View: All roles switch to male versions
8. Click "Show as: Female"
9. Back to: Female versions
10. Select: Female Polynesian Muscle
```

### Scenario 2: Male Player Direct Selection
```
1. Enter name: "David"
2. Select: Female [Male]
3. Join lobby
4. Open role selection
5. See: 200px portraits of all male characters
6. Select: Male Middle Eastern Safe Cracker
   (No need to toggle - already showing males)
```

## 📂 Current Assets

### Images in Use
```
app/assets/roles/
├── mastermind_male.png      (200px display)
├── mastermind_female.png    (200px display)
├── hacker_male.png          (200px display)
├── hacker_female.png        (200px display)
├── safe_cracker_male.png    (200px display)
├── safe_cracker_female.png  (200px display)
... (24 total)
```

**Source Resolution:** 1024×1024 (Imagen 4.0)  
**Display Size:** 200×200 (downscaled for UI)  
**Quality:** Excellent detail even at large size

## ✅ Complete Feature Set

### Gender System
- ✅ Gender selection at name entry (Female default)
- ✅ Gender toggle in role selection modal
- ✅ Instant switching between versions
- ✅ 24 total images (12 roles × 2 genders)

### Image System
- ✅ 200px × 200px portraits in modal
- ✅ Imagen 4.0 high quality
- ✅ Year 2020 contemporary setting
- ✅ Purple theme consistent
- ✅ Diverse ethnicities preserved

### Age Distribution
- ✅ 15 years old: Pickpocket, Lookout
- ✅ 20s-30s: Most roles
- ✅ 40 years old: Mastermind, Fence

### UI Improvements
- ✅ Wider modal (600px)
- ✅ Taller modal (85% screen)
- ✅ Role descriptions visible
- ✅ Minigames preview
- ✅ Taken/available states
- ✅ Selection feedback

## 🎨 Visual Excellence

### Why 200px Works
1. **Showcases Imagen 4.0** - High-quality details visible
2. **Character recognition** - Players instantly connect
3. **Professional polish** - AAA game feel
4. **Ethnic features** - Diversity clearly represented
5. **Age appropriate** - 15yo vs 40yo clearly distinct
6. **Style consistency** - Borderlands art shines

### Modal Space Usage
- **Left column (200px):** Character portrait
- **Right column (360px):** Name, description, minigames
- **Top bar:** Gender toggle (Female/Male)
- **Scrollable:** 12 roles fit comfortably

## 🚀 Ready to Test

### Test Checklist
- [ ] Gender toggle switches images instantly
- [ ] 200px images display clearly
- [ ] Modal width accommodates layout
- [ ] Scrolling works smoothly
- [ ] Role descriptions readable
- [ ] Minigames list formatted well
- [ ] Taken roles show correctly
- [ ] Selection feedback works

### Expected Experience
1. **Visual WOW** - 200px portraits are impressive
2. **Instant feedback** - Gender toggle responsive
3. **Easy browsing** - Large images, clear text
4. **Informed choice** - Description + minigames help decide
5. **Personal connection** - See yourself in every role

---

**Final Configuration:**
- **Image Size:** 200px × 200px
- **Modal Width:** 600px
- **Modal Height:** 85% screen
- **Gender Toggle:** Yes (in modal)
- **Default Gender:** Female
- **Total Images:** 24 (12 roles × 2 genders)
- **Model:** Imagen 4.0
- **Setting:** Year 2020
- **Theme:** Purple night heist

**Result:** Professional, inclusive, visually stunning role selection experience! 🎭✨
