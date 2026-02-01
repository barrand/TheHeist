# NPC Character Color Integration Guide

How to integrate your UI color scheme into character portraits for a cohesive visual experience.

---

## 🎨 Why This Matters

Your NPCs should **visually match your app theme**:
- Characters feel like part of the game, not stock images
- Reinforces brand identity
- Creates memorable, consistent aesthetic
- Players associate colors with your game

---

## 🎭 Color Scheme Examples

### Option 1: GOLD HEIST

**UI Colors:**
- Primary: Gold `#D4AF37`
- Secondary: Bronze `#8B7355`
- Background: Black `#0F0F0F`

**NPC Color Accents:**
```bash
--accent-colors "gold"
```

**Visual Elements:**
- Gold jewelry (watches, rings, necklaces)
- Bronze belt buckles, badges
- Warm metallic accessories
- Gold watch faces
- Bronze buttons
- Champagne-colored details

**Example Characters:**
- **Security Guard:** Gold badge, bronze uniform buttons
- **Grifter:** Gold watch, bronze cufflinks
- **Museum Curator:** Gold-rimmed glasses, bronze brooch

---

### Option 2: ELECTRIC BLUE

**UI Colors:**
- Primary: Electric Cyan `#00D9FF`
- Secondary: Purple `#7B61FF`
- Background: Dark Navy `#0A0E1A`

**NPC Color Accents:**
```bash
--accent-colors "blue"
```

**Visual Elements:**
- Cyan glowing elements (eyes, tech)
- Electric blue LED accessories
- Purple neon highlights
- Turquoise watch faces
- Blue-lit tech devices
- Cyan headphone lights

**Example Characters:**
- **Hacker:** Cyan glowing laptop, purple hoodie highlights
- **Tech Guard:** Blue LED earpiece, cyan badge light
- **Drone Pilot:** Electric blue visor, purple tech vest

---

### Option 3: NEON PURPLE

**UI Colors:**
- Primary: Vibrant Purple `#B565FF`
- Secondary: Magenta `#FF00FF`
- Background: Purple-Black `#0D0517`

**NPC Color Accents:**
```bash
--accent-colors "purple"
```

**Visual Elements:**
- Vibrant purple clothing accents
- Magenta accessories (scarves, ties)
- Cyan blue highlights
- Purple jewelry
- Magenta pocket squares
- Neon purple trim

**Example Characters:**
- **Night Club Owner:** Purple suit, magenta tie
- **Street Artist:** Purple spray paint, magenta bandana
- **Casino Dealer:** Vibrant purple vest, cyan bow tie

---

### Option 4: CRIMSON RED

**UI Colors:**
- Primary: Hot Red `#FF2E63`
- Secondary: Orange `#FF9500`
- Background: Almost Black `#120508`

**NPC Color Accents:**
```bash
--accent-colors "red"
```

**Visual Elements:**
- Red bandanas, scarves
- Orange highlights in clothing
- Warm red tones
- Red accessories
- Orange tool accents
- Yellow-orange details

**Example Characters:**
- **Demolitions Expert:** Red bandana, orange tool belt
- **Getaway Driver:** Red racing jacket, orange accents
- **Muscle:** Red tactical vest, orange safety stripes

---

### Option 5: EMERALD GREEN

**UI Colors:**
- Primary: Bright Emerald `#00FF88`
- Secondary: Gold `#FFD700`
- Background: Dark Forest `#0A1410`

**NPC Color Accents:**
```bash
--accent-colors "green"
```

**Visual Elements:**
- Emerald green money-themed details
- Gold jewelry and accessories
- Turquoise tech elements
- Green dollar sign motifs
- Gold watch, rings
- Money green highlights

**Example Characters:**
- **Bank Manager:** Green tie, gold cufflinks
- **Accountant:** Emerald green reading glasses, gold pen
- **Vault Keeper:** Green uniform trim, gold badge

---

### Option 6: AMBER SUNSET

**UI Colors:**
- Primary: Warm Orange `#FF8C42`
- Secondary: Mustard `#FFCA3A`
- Background: Dark Brown `#1A0F08`

**NPC Color Accents:**
```bash
--accent-colors "orange"
```

**Visual Elements:**
- Warm orange clothing elements
- Mustard yellow accessories
- Retro 70s color palette
- Orange-brown tones
- Vintage warm colors
- Sunset-inspired hues

**Example Characters:**
- **Vintage Car Dealer:** Orange shirt, mustard yellow tie
- **Retro Bartender:** Warm orange vest, yellow suspenders
- **Pawn Shop Owner:** Orange flannel, mustard yellow cap

---

## 🛠️ How to Use

### Method 1: Use Preset Scheme Name

```bash
python generate_npc_image.py \
  --name "Maria Santos" \
  --role "Security Guard" \
  --gender female \
  --ethnicity "Latina" \
  --clothing "security uniform" \
  --background "loading dock" \
  --expression "friendly" \
  --accent-colors "gold"
```

**Available schemes:**
- `"gold"` - Gold Heist
- `"blue"` - Electric Blue
- `"purple"` - Neon Purple
- `"red"` - Crimson Red
- `"green"` - Emerald Green
- `"orange"` - Amber Sunset

### Method 2: Custom Color List

```bash
python generate_npc_image.py \
  --name "Alex Rivera" \
  --role "Hacker" \
  --gender person \
  --clothing "hoodie" \
  --background "server room" \
  --accent-colors "cyan glowing laptop screen, purple LED keyboard, electric blue hoodie trim"
```

---

## 🎨 Mixing & Matching

### Primary Color (Always Present)
Your main UI accent should appear prominently:
- Jewelry (gold, silver, turquoise)
- Tech elements (glowing, LED)
- Clothing highlights (trim, pockets)
- Accessories (watches, badges)

### Secondary Color (Subtle)
Add secondary accent sparingly:
- Small details (buttons, pins)
- Background elements
- Complementary accessories

### Don't Overdo It
- **Good:** 2-3 accent color elements per character
- **Bad:** Every piece of clothing matches UI exactly
- **Goal:** Subtle theme reinforcement, not costume party

---

## 📸 Visual Consistency Tips

### DO:
✅ Add themed jewelry/accessories  
✅ Integrate color into natural elements (clothing trim, badges)  
✅ Use glowing tech elements for modern themes  
✅ Match intensity (vibrant UI = vibrant NPCs)  
✅ Keep character personality primary, colors secondary  

### DON'T:
❌ Make every NPC wear same color outfit  
❌ Override character's role (don't make janitor wear gold suit)  
❌ Force unnatural color combinations  
❌ Sacrifice character variety for color matching  
❌ Make colors more prominent than character identity  

---

## 🎯 Character Role Examples

### Gold Heist Scheme

| Role | Color Integration |
|------|-------------------|
| Security Guard | Gold badge, bronze uniform buttons |
| Museum Curator | Gold-rimmed glasses, bronze brooch |
| Vault Keeper | Gold watch, bronze key ring |
| Grifter | Gold cufflinks, champagne tie |
| Janitor | Gold wedding ring, bronze name tag |

### Electric Blue Scheme

| Role | Color Integration |
|------|-------------------|
| Hacker | Cyan glowing laptop, purple hoodie |
| Tech Support | Blue LED earpiece, cyan ID badge |
| Security (Tech) | Electric blue uniform trim, purple badge glow |
| Drone Operator | Cyan visor, purple tech vest |
| IT Manager | Blue tie with purple geometric pattern |

### Neon Purple Scheme

| Role | Color Integration |
|------|-------------------|
| Night Guard | Purple flashlight beam, magenta badge |
| Casino Dealer | Vibrant purple vest, cyan bow tie |
| Club Owner | Purple suit jacket, magenta pocket square |
| Street Vendor | Purple cart awning, magenta sign |
| Bartender | Purple apron, neon cyan bar lights |

---

## 🔄 Testing Your Theme

### Generate Test Characters

Create 3 diverse NPCs with your chosen scheme:

```bash
# Test 1: Professional
python generate_npc_image.py --name "Test Guard" --role "Security" \
  --gender male --clothing "uniform" --accent-colors "gold"

# Test 2: Casual
python generate_npc_image.py --name "Test Vendor" --role "Food Truck Owner" \
  --gender female --clothing "apron" --accent-colors "gold"

# Test 3: Tech
python generate_npc_image.py --name "Test Hacker" --role "IT Staff" \
  --gender person --clothing "hoodie" --accent-colors "gold"
```

### Evaluate:
- [ ] Do colors feel natural on characters?
- [ ] Is the theme recognizable but not overwhelming?
- [ ] Do characters still have individual personalities?
- [ ] Would these look good next to your UI buttons?
- [ ] Do the colors work across different roles?

---

## 🎨 Logo Integration

Use the same accent colors in your app logo:

### Gold Heist Logo
- Icon: Gold crown or vault
- Background: Black
- Accent: Bronze outline

### Electric Blue Logo
- Icon: Cyan circuit board or mask
- Background: Dark navy
- Accent: Purple glow

### Neon Purple Logo
- Icon: Purple diamond or heist mask
- Background: Purple-black
- Accent: Magenta/cyan highlights

---

## 💡 Pro Tips

1. **Generate All NPCs Together:** Batch generate with same scheme for consistency
2. **Store Scheme in DB:** Save chosen color scheme with scenario data
3. **Regenerate If Needed:** Easy to update all NPCs if you change scheme
4. **Test on Real Devices:** Colors look different on phone vs desktop
5. **User Preference (Later):** Let users switch themes, regenerate NPCs
6. **Seasonal Themes:** Create holiday variants (red/green Christmas, orange/black Halloween)

---

## 🚀 Batch Generation Script

Create `batch_generate_npcs.sh`:

```bash
#!/bin/bash
# Generate all NPCs for a scenario with consistent color scheme

SCHEME="gold"  # Change to your chosen scheme

python generate_npc_image.py --name "Maria Santos" --role "Security Guard" \
  --gender female --ethnicity "Latina" --clothing "uniform" \
  --background "loading dock" --expression "friendly" --accent-colors "$SCHEME"

python generate_npc_image.py --name "Tommy Chen" --role "Food Truck Owner" \
  --gender male --ethnicity "Asian" --clothing "apron" \
  --background "food truck" --expression "chatty" --accent-colors "$SCHEME"

python generate_npc_image.py --name "Rosa Martinez" --role "Parking Attendant" \
  --gender female --ethnicity "Latina" --clothing "vest" \
  --background "parking garage" --expression "bored" --accent-colors "$SCHEME"

echo "✅ All NPCs generated with $SCHEME color scheme!"
```

Make executable:
```bash
chmod +x batch_generate_npcs.sh
```

---

## 📊 Scheme Recommendations by Scenario

| Scenario Type | Best Scheme | Why |
|---------------|-------------|-----|
| Museum Heist | **Gold** | Classic, elegant, valuable artifacts |
| Bank Robbery | **Green** | Money theme, vault vibes |
| Tech Company | **Blue** | Modern, digital, cyberpunk |
| Casino Heist | **Purple** | Night life, Vegas, stylish |
| Train Robbery | **Orange** | Vintage, retro, warm |
| High-Rise | **Red** | High stakes, adrenaline |

---

## 🎯 Final Checklist

Before committing to a color scheme:

- [ ] Generated 3+ test NPCs with scheme
- [ ] Placed NPCs next to UI mockups (visual check)
- [ ] Tested on mobile device (real colors)
- [ ] Verified colors work across diverse characters
- [ ] Confirmed logo uses same palette
- [ ] Team agrees on choice
- [ ] Ready to batch generate all NPCs

---

**Ready to generate themed NPCs?** Pick your scheme and start creating a cohesive visual world! 🎨✨
