# Role Images: Diversity & UI Improvements ✅

Complete update of role images with diverse characters and enhanced UI display.

## 🌍 Diversity Improvements

### Gender Distribution
- **Male (5):** Mastermind, Safe Cracker, Insider, Lookout, Cleaner
- **Female (5):** Hacker, Driver, Muscle, Fence, Cat Burglar
- **Non-binary (2):** Grifter, Pickpocket

### Ethnicity Distribution
All 12 roles now feature diverse, specific character designs:

1. **Mastermind** - Distinguished older Indian man
2. **Hacker** - Young Korean woman
3. **Safe Cracker** - Middle Eastern man
4. **Driver** - Latina woman
5. **Insider** - Professional Black man
6. **Grifter** - Charismatic androgynous European person (non-binary)
7. **Muscle** - Imposing Polynesian woman with muscular build
8. **Lookout** - Sharp-eyed South Asian man
9. **Fence** - Street-smart older white woman
10. **Cat Burglar** - Agile Japanese woman
11. **Cleaner** - Meticulous Scandinavian man
12. **Pickpocket** - Street-smart young Southeast Asian person (non-binary)

## 🎨 UI Enhancements

### Role Selection Modal

#### Before:
- 60x60px images
- Only role name displayed
- No role information
- Generic layout

#### After:
- **80x80px images** (33% larger!)
- **Role name + description**
- **Minigames list** (up to 3 displayed)
- **Enhanced layout** with better spacing
- **Better visual hierarchy**

### Features
```
┌────────────────────────────────────────┐
│  [80x80 Portrait]  Mastermind          │
│                    Strategic planner   │
│                    who coordinates...  │
│                                        │
│                    Minigames:          │
│                    • Pattern Memory    │
│                    • Time Allocation   │
└────────────────────────────────────────┘
```

## 📂 New Files Created

### 1. `app/lib/models/role.dart`
Role data model with:
- `Role` class (roleId, name, description, minigames, icon)
- `Minigame` class (id, description, displayName)
- JSON parsing from roles.json
- Emoji icon mapping

### 2. `app/lib/services/roles_service.dart`
Service for loading roles:
- `loadRoles()` - Load all roles from JSON
- `getRole(roleId)` - Get specific role
- Caching for performance

### 3. `app/assets/data/roles.json`
Full role data copied from `data/roles.json` including:
- 12 role definitions
- Descriptions for each role
- Minigames (4 per hacker, 3 per other roles)

## 📝 Files Modified

### 1. `scripts/generate_role_images.py`
Updated all role definitions with:
- Specific genders (male/female/non-binary)
- Diverse ethnicities with detail
- Better character descriptions

**Example:**
```python
"hacker": {
    "gender": "female",
    "ethnicity": "young Korean woman",
    # ... rest of design
}
```

### 2. `app/lib/widgets/modals/role_selection_modal.dart`
Major UI overhaul:
- Changed from `List<Map<String, String>>` to `List<Role>`
- Larger images (80x80px)
- Added role descriptions
- Added minigames list
- Better layout with Column structure
- Enhanced visual design

### 3. `app/lib/screens/room_lobby_screen.dart`
Updated to use new Role model:
- Load roles from RolesService
- Updated role selector button
- Updated player list display
- Changed from Map lookups to Role objects

### 4. `app/pubspec.yaml`
Added assets:
```yaml
assets:
  - assets/data/  # For roles.json
```

### 5. `scripts/generate_npc_image.py`
Model documentation updated:
- Updated from "nano-banana" references
- Changed to "Gemini 2.5 Flash Image"
- (Note: imagen-4.0 not available for generateContent API)

## 🚀 Image Generation

### Model Used
- **Gemini 2.5 Flash Image** (`gemini-2.5-flash-image`)
- Tried `imagen-4.0-generate-001` but not supported for `generateContent` API
- Current model works well for Borderlands-style character portraits

### All 12 Images Regenerated
✅ All role portraits generated with new diverse characters  
✅ Copied to `app/assets/roles/`  
✅ ~80 seconds total generation time  
✅ Purple theme maintained across all images

## 📱 User Experience Improvements

### Before
- Generic emoji icons
- No context about roles
- Small images
- Unclear what each role does

### After
- **Professional character portraits** showing diversity
- **Role descriptions** help players understand each role
- **Minigames preview** shows what gameplay to expect
- **Larger images** make characters visible and engaging
- **Inclusive representation** across gender and ethnicity

## 🎯 Benefits

1. **Representation Matters**
   - Players see themselves reflected in character options
   - Diverse team reflects global player base
   - Inclusive design philosophy

2. **Better Decision Making**
   - Descriptions help players choose roles that match playstyle
   - Minigames preview sets expectations
   - Visual + text information aids understanding

3. **Professional Polish**
   - Larger images showcase art quality
   - Detailed descriptions show depth
   - Cohesive purple theme creates atmosphere

4. **Accessibility**
   - Text descriptions support understanding
   - Multiple information types (visual, text, list)
   - Clear hierarchy helps scanning

## 🧪 Testing Checklist

- [ ] Flutter app builds without errors
- [ ] Role selection modal opens successfully
- [ ] All 12 role images display correctly
- [ ] Role descriptions appear for each role
- [ ] Minigames list shows (when applicable)
- [ ] Images are 80x80px (larger than before)
- [ ] Fallback to emoji works if image missing
- [ ] Role selector button shows portrait
- [ ] Player list shows role names correctly

## 📊 Diversity Stats

- **Geographic Representation:** 10+ regions/ethnicities
- **Gender Balance:** 5 male, 5 female, 2 non-binary
- **Age Range:** Young adults to older professionals
- **Body Types:** Varied (athletic, muscular, average)
- **Presentation:** Professional to street-smart

## 🎨 Visual Consistency

All images maintain:
- ✅ Borderlands comic book art style
- ✅ Purple accent theme
- ✅ Dark heist atmosphere
- ✅ Character uniqueness
- ✅ Professional quality

---

**Updated:** February 2, 2026  
**Model:** Gemini 2.5 Flash Image  
**Images:** 12 diverse character portraits  
**UI:** Enhanced role selection modal  
**Theme:** Purple night heist atmosphere
