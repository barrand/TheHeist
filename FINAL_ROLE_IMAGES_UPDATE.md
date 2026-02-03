# Final Role Images Update ✅

All 24 role images regenerated with Imagen 4.0, updated ages, and 2020 setting.

## 🎨 Key Changes

### 1. **Imagen 4.0 (High Quality)**
- ✅ Switched from Gemini Flash to **Imagen 4.0**
- ✅ Using correct API: `client.models.generate_images()`
- ✅ Higher quality, more detailed character portraits
- ✅ Better prompt adherence

### 2. **Age Updates**
- **Mastermind:** Changed from "older distinguished" to **40 years old**
- **Fence:** Changed from "older" to **40 years old**
- **Pickpocket:** Now **15 years old** (young street-smart teen)
- **Lookout:** Now **15 years old** (sharp-eyed teen)

### 3. **Time Period: Year 2020**
- All images now set in **year 2020** (contemporary)
- **No futuristic elements** - realistic 2020 technology
- Added to art style prompt: "contemporary clothing and technology (not futuristic)"

### 4. **UI Enhancement**
- Role images increased to **100px × 100px** (from 80px)
- Better visibility of character details
- More prominent in role selection modal

### 5. **Binary Gender System**
- Only **Male** and **Female** (removed non-binary)
- **Female is default** selection
- 24 total images (12 roles × 2 genders)

## 📊 Complete Role Roster

### Age Distribution
```
15 years old (2 roles): Pickpocket, Lookout
20s (3 roles):          Hacker, Cat Burglar, Insider  
30s (5 roles):          Driver, Safe Cracker, Grifter, Muscle, Cleaner
40s (2 roles):          Mastermind, Fence
```

### Ethnicity Distribution (Both Genders)
1. **Mastermind** - 40-year-old Indian (male/female)
2. **Hacker** - Young Korean (male/female)
3. **Safe Cracker** - Middle Eastern (male/female)
4. **Driver** - Latina/Latino (male/female)
5. **Insider** - Professional Black (male/female)
6. **Grifter** - Charismatic European (male/female)
7. **Muscle** - Imposing Polynesian (male/female)
8. **Lookout** - 15-year-old South Asian (male/female)
9. **Fence** - 40-year-old White (male/female)
10. **Cat Burglar** - Agile Japanese (male/female)
11. **Cleaner** - Meticulous Scandinavian (male/female)
12. **Pickpocket** - 15-year-old Southeast Asian (male/female)

## 🖼️ Image Details

### Generation
- **Model:** Imagen 4.0 (`imagen-4.0-generate-001`)
- **Quality:** High-resolution professional portraits
- **Style:** Borderlands 2D illustration
- **Theme:** Purple night heist atmosphere
- **Era:** Year 2020 (contemporary, not futuristic)
- **Size:** ~1.5-2.0MB per image

### File Naming
- **Format:** `{role_id}_{gender}.png`
- **Examples:**
  - `mastermind_female.png`
  - `mastermind_male.png`
  - `pickpocket_female.png`
  - `pickpocket_male.png`

### Locations
```
scripts/output/role_images/    ← Generated images (24 files)
app/assets/roles/              ← Flutter assets (24 files)
```

## 💻 Technical Changes

### Image Generation Script (`generate_npc_image.py`)

**Before (Gemini Flash):**
```python
response = client.models.generate_content(
    model='gemini-2.5-flash-image',
    contents=[prompt],
)
for part in response.parts:
    if part.inline_data:
        image = part.as_image()
```

**After (Imagen 4.0):**
```python
response = client.models.generate_images(
    model='imagen-4.0-generate-001',
    prompt=prompt,
    config=types.GenerateImagesConfig(
        number_of_images=1,
    )
)
for generated_image in response.generated_images:
    generated_image.image.save(output_path)
```

### Art Style Prompt Addition
```python
HEIST_GAME_ART_STYLE = """2D illustration, comic book art style,
bold thick outlines, cell-shaded, flat colors with subtle gradients,
Borderlands game aesthetic, graphic novel style,
vibrant saturated colors, stylized proportions, hand-drawn look,
inked linework, simplified details, expressive characters,
set in year 2020, contemporary clothing and technology (not futuristic)"""
```

### Role Design Updates (`generate_role_images_gendered.py`)
```python
"mastermind": {
    "ethnicity": "distinguished 40-year-old Indian",  # Updated age
    # ...
}

"fence": {
    "ethnicity": "street-smart 40-year-old white",  # Updated age
    # ...
}

"pickpocket": {
    "ethnicity": "street-smart 15-year-old Southeast Asian",  # Now teen
    # ...
}

"lookout": {
    "ethnicity": "sharp-eyed 15-year-old South Asian",  # Now teen
    # ...
}
```

## 📱 Flutter UI Updates

### Role Selection Modal
- Images: **100px × 100px** (increased from 80px)
- Path: `assets/roles/{roleId}_{playerGender}.png`
- Fallback: Emoji icon if image not found

### Landing Page
- Gender selector defaults to **Female**
- Clear toggle between Female and Male
- Gender passed to lobby and role selection

## ✨ Character Design Highlights

### Teen Characters (Age 15)
- **Pickpocket** - Young Southeast Asian street kid with quick hands
- **Lookout** - Sharp-eyed South Asian teen with surveillance skills

### 40-Something Professionals
- **Mastermind** - Distinguished 40yo Indian strategic leader
- **Fence** - Experienced 40yo street-smart dealer

### Contemporary 2020 Setting
- No sci-fi elements
- Realistic 2020 technology (smartphones, tablets, laptops)
- Contemporary fashion and equipment
- Urban environments from 2020 era

## 🎯 Benefits

### Player Experience
1. **Personal representation** - Choose gender, see yourself in roles
2. **Age diversity** - From teens (15) to experienced pros (40s)
3. **Ethnic diversity** - 12 different backgrounds represented
4. **Visual quality** - Imagen 4.0 high-resolution portraits
5. **Contemporary** - Relatable 2020 setting, not sci-fi

### Design Improvements
1. **Larger images** - 100px shows character details clearly
2. **Better quality** - Imagen 4.0 more detailed than Flash
3. **Age appropriate** - Realistic age ranges for each role
4. **Time period consistency** - All set in 2020

## 📦 Assets Generated

### Total Count
- **24 PNG images** (12 roles × 2 genders)
- **~40MB total** (~1.5-2.0MB each)
- **1024×1024 resolution** (Imagen 4.0 default)

### Organization
```
app/assets/roles/
├── mastermind_male.png       (40yo Indian man)
├── mastermind_female.png     (40yo Indian woman)
├── hacker_male.png           (Korean man)
├── hacker_female.png         (Korean woman)
├── safe_cracker_male.png     (Middle Eastern man)
├── safe_cracker_female.png   (Middle Eastern woman)
├── driver_male.png           (Latino man)
├── driver_female.png         (Latina woman)
├── insider_male.png          (Black man)
├── insider_female.png        (Black woman)
├── grifter_male.png          (European man)
├── grifter_female.png        (European woman)
├── muscle_male.png           (Polynesian man)
├── muscle_female.png         (Polynesian woman)
├── lookout_male.png          (15yo South Asian boy)
├── lookout_female.png        (15yo South Asian girl)
├── fence_male.png            (40yo White man)
├── fence_female.png          (40yo White woman)
├── cat_burglar_male.png      (Japanese man)
├── cat_burglar_female.png    (Japanese woman)
├── cleaner_male.png          (Scandinavian man)
├── cleaner_female.png        (Scandinavian woman)
├── pickpocket_male.png       (15yo SE Asian boy)
└── pickpocket_female.png     (15yo SE Asian girl)
```

## 🚀 Ready to Test

### Player Flow
1. Launch app → Land on welcome screen
2. Click "CREATE ROOM" or "JOIN ROOM"
3. Enter name
4. **Select gender: [Female] Male** ← Female is default
5. Enter lobby
6. Open role selection
7. See all 12 roles as chosen gender with **100px portraits**
8. View role descriptions and minigames
9. Select role

### Visual Experience
- **Large portraits** showcase Imagen 4.0 quality
- **2020 aesthetic** feels contemporary and relatable
- **Age diversity** from teens to experienced professionals
- **Gender matching** creates personal connection

## 📝 Summary

✅ **Imagen 4.0** - Higher quality images  
✅ **100px images** - Better visibility  
✅ **Updated ages** - Mastermind & Fence (40s), Pickpocket & Lookout (15)  
✅ **Year 2020** - Contemporary setting, not futuristic  
✅ **Binary gender** - Male & Female only  
✅ **Female default** - Progressive choice  
✅ **24 images** - Complete coverage  
✅ **Diverse cast** - 12 ethnicities represented  

---

**Generated:** February 2, 2026  
**Model:** Imagen 4.0 (`imagen-4.0-generate-001`)  
**Generation Time:** ~65 seconds for all 24 images  
**Resolution:** 1024×1024 per image  
**Art Style:** Borderlands 2D illustration  
**Setting:** Year 2020 (contemporary)  
**Theme:** Purple night heist atmosphere
