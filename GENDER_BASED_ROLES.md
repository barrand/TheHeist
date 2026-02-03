# Gender-Based Role System ✅

Players now select their gender and see all roles represented as their chosen gender!

## 🎭 System Overview

### Player Experience
1. **Name Input** - Player enters their name
2. **Gender Selection** - Choose Female (default) or Male
3. **Role Images** - All 12 roles display as the selected gender
4. **Personal Connection** - Players see themselves in every role option

### Default Gender
- **Female is the default** selection
- Players can toggle to Male if preferred
- Gender selection appears in both "Create Room" and "Join Room" dialogs

## 🖼️ Image System

### Generated Images
- **24 total images** (12 roles × 2 genders)
- **Naming convention:** `{role_id}_{gender}.png`
  - Example: `mastermind_female.png`, `mastermind_male.png`

### Ethnicities (Consistent Across Genders)

| Role | Ethnicity | Male Example | Female Example |
|------|-----------|--------------|----------------|
| Mastermind | Distinguished older Indian | Indian man | Indian woman |
| Hacker | Young Korean | Korean man | Korean woman |
| Safe Cracker | Middle Eastern | Middle Eastern man | Middle Eastern woman |
| Driver | Latina/Latino | Latino man | Latina woman |
| Insider | Professional Black | Black man | Black woman |
| Grifter | Charismatic European | European man | European woman |
| Muscle | Imposing Polynesian | Polynesian man | Polynesian woman |
| Lookout | Sharp-eyed South Asian | South Asian man | South Asian woman |
| Fence | Street-smart older white | White man | White woman |
| Cat Burglar | Agile Japanese | Japanese man | Japanese woman |
| Cleaner | Meticulous Scandinavian | Scandinavian man | Scandinavian woman |
| Pickpocket | Street-smart young SE Asian | SE Asian man | SE Asian woman |

## 💻 Technical Implementation

### Frontend (Flutter)

#### 1. Landing Page (`landing_page.dart`)
```dart
// Gender selector in name dialog (defaults to female)
String selectedGender = 'female';

// Gender selection UI
Row(
  children: [
    GestureDetector(
      onTap: () => setState(() => selectedGender = 'female'),
      child: Container(/* Female button */),
    ),
    GestureDetector(
      onTap: () => setState(() => selectedGender = 'male'),
      child: Container(/* Male button */),
    ),
  ],
)
```

#### 2. Room Lobby (`room_lobby_screen.dart`)
```dart
class RoomLobbyScreen extends StatefulWidget {
  final String playerGender; // 'male' or 'female'
  // ...
}

// Image path uses gender
Image.asset('assets/roles/${roleId}_${playerGender}.png')
```

#### 3. Role Selection Modal (`role_selection_modal.dart`)
```dart
class RoleSelectionModal extends StatelessWidget {
  final String playerGender; // Passed from lobby
  // ...
  
  // 100px images with gender suffix
  Image.asset(
    'assets/roles/${roleId}_$playerGender.png',
    width: 100,
    height: 100,
  )
}
```

### Backend (Python)

#### Image Generation Script (`generate_role_images_gendered.py`)

**Key Features:**
- Gender-neutral ethnicity definitions
- Automatic gendered string conversion
- Batch generation for both genders

**Usage:**
```bash
# Generate all 24 images (12 roles × 2 genders)
python3 generate_role_images_gendered.py

# Generate all female versions only
python3 generate_role_images_gendered.py --gender female

# Generate specific role (both genders)
python3 generate_role_images_gendered.py --role hacker

# Generate specific role as male only
python3 generate_role_images_gendered.py --role hacker --gender male
```

**Role Design Structure:**
```python
ROLE_DESIGNS = {
    "hacker": {
        "name": "The Hacker",
        "role": "Tech Specialist",
        "ethnicity": "young Korean",  # Gender-neutral!
        "clothing": "tech hoodie...",
        # ... other attributes
    }
}

# Automatic conversion
def get_ethnicity_for_gender(ethnicity, gender):
    if gender == "male":
        return f"{ethnicity} man"
    else:  # female
        return f"{ethnicity} woman"
```

## 🎨 UI Enhancements

### Gender Selector Design
- **Visual:** Two side-by-side buttons (Female | Male)
- **Colors:**
  - Selected: Gold accent (`AppColors.accentPrimary`)
  - Unselected: Dark tertiary (`AppColors.bgTertiary`)
- **Border:** 2px on selected, subtle on unselected
- **Default:** Female button is pre-selected

### Role Images
- **Size:** 100px × 100px (increased from 80px)
- **Location:** Role selection modal and role selector button
- **Style:** Borderlands art, purple theme
- **Quality:** High-resolution character portraits

## 📂 File Structure

### Generated Images
```
scripts/output/role_images/
├── mastermind_male.png
├── mastermind_female.png
├── hacker_male.png
├── hacker_female.png
├── safe_cracker_male.png
├── safe_cracker_female.png
├── driver_male.png
├── driver_female.png
├── insider_male.png
├── insider_female.png
├── grifter_male.png
├── grifter_female.png
├── muscle_male.png
├── muscle_female.png
├── lookout_male.png
├── lookout_female.png
├── fence_male.png
├── fence_female.png
├── cat_burglar_male.png
├── cat_burglar_female.png
├── cleaner_male.png
├── cleaner_female.png
├── pickpocket_male.png
└── pickpocket_female.png
```

### Flutter Assets
```
app/assets/roles/
├── (same 24 images as above)
```

## ✨ Benefits

### Player Experience
1. **Personal Connection** - See yourself in every role
2. **Representation** - All genders represented equally
3. **Choice** - Simple, clear gender selection
4. **Consistency** - Same ethnicity across genders

### Design Philosophy
1. **Inclusive by Default** - Female is the default choice
2. **Binary Simplicity** - Clear male/female options
3. **Ethnicity Preservation** - Diverse backgrounds maintained
4. **Visual Equity** - Same quality for both genders

### Technical Advantages
1. **Scalable** - Easy to add more genders if needed
2. **Maintainable** - Single ethnicity definition per role
3. **Efficient** - Batch generation for all variations
4. **Flexible** - Players can change their mind anytime

## 🚀 Generation Stats

- **Total Images:** 24 (12 roles × 2 genders)
- **Generation Time:** ~2.5 minutes total
- **Model:** Gemini 2.5 Flash Image
- **Art Style:** Borderlands-style 2D illustration
- **Theme:** Purple night heist atmosphere
- **File Size:** ~1.7-2.2MB per image

## 🎯 User Flow

### Creating a Room
1. Click "CREATE ROOM"
2. Enter your name
3. Select gender (default: Female)
4. Click "Continue"
5. See all roles as your chosen gender

### Joining a Room
1. Click "JOIN ROOM"
2. Enter room code
3. Enter your name
4. Select gender (default: Female)
5. Click "Join"
6. See all roles as your chosen gender

## 📱 UI Mockup

```
┌────────────────────────────────┐
│  Create Room                   │
│                                │
│  Enter your name:              │
│  ┌──────────────────────────┐ │
│  │ [Your Name Here]         │ │
│  └──────────────────────────┘ │
│                                │
│  Select your gender:           │
│  ┌──────────┐  ┌──────────┐  │
│  │ Female   │  │   Male   │  │  ← Female selected
│  └──────────┘  └──────────┘  │     (gold border)
│                                │
│     [Cancel]    [Continue]     │
└────────────────────────────────┘
```

## 🔄 Future Enhancements

### Potential Additions
- Save gender preference locally
- Add non-binary option (would need 36 total images)
- Let players pick from all genders for each role
- Custom avatar builder

### Current Limitations
- Gender selection required each session
- Binary only (male/female)
- Cannot mix genders across roles
- No custom appearance options

## ✅ Testing Checklist

- [ ] Female default selection works
- [ ] Male selection toggles correctly
- [ ] Images load for both genders
- [ ] 100px images display correctly
- [ ] Role selector shows correct gendered image
- [ ] Modal shows correct gendered images
- [ ] Fallback emoji works if image missing
- [ ] Gender persists through entire session

---

**Implementation Date:** February 2, 2026  
**Images Generated:** 24 total (12 roles × 2 genders)  
**Default Gender:** Female  
**Image Size:** 100px × 100px
