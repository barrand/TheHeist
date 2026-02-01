# The Heist - Design System

## 🎨 Visual Identity

**Theme:** Heist/Noir with Modern Tech  
**Mood:** Sleek, mysterious, high-stakes, professional criminal crew  
**Style:** Dark, gold accents, Borderlands-inspired characters  
**Target:** Mobile-first, touch-friendly, accessible

---

## 🎨 Color Palette

### Primary Colors

**Background:**
```css
--color-bg-primary:    #0F0F0F  /* Deep black - main background */
--color-bg-secondary:  #1E1E1E  /* Dark gray - cards, modals */
--color-bg-tertiary:   #2A2A2A  /* Medium gray - inputs, hover states */
```

**Accent/Interactive:**
```css
--color-accent-primary:   #D4AF37  /* Gold - primary buttons, highlights */
--color-accent-hover:     #E5C158  /* Lighter gold - hover state */
--color-accent-pressed:   #B8941F  /* Darker gold - pressed state */
```

**Text:**
```css
--color-text-primary:     #FFFFFF  /* White - main text */
--color-text-secondary:   #B0B0B0  /* Light gray - secondary text */
--color-text-tertiary:    #888888  /* Medium gray - hints, disabled */
--color-text-gold:        #D4AF37  /* Gold - highlights, CTAs */
```

**Borders:**
```css
--color-border-subtle:    #333333  /* Dark gray - subtle dividers */
--color-border-medium:    #444444  /* Medium gray - card borders */
--color-border-accent:    #D4AF37  /* Gold - focused, selected */
```

### Semantic Colors

**Success/Positive:**
```css
--color-success:       #4CAF50  /* Green - success, available */
--color-success-bg:    #1E3A1E  /* Dark green - success background */
--color-success-dim:   #2D5F2D  /* Dim green - low confidence */
```

**Warning/Caution:**
```css
--color-warning:       #FFA726  /* Orange - warnings, action needed */
--color-warning-bg:    #3A2A1E  /* Dark orange - warning background */
--color-warning-dim:   #5F4A2D  /* Dim orange - prerequisites */
```

**Danger/Failure:**
```css
--color-danger:        #E53935  /* Red - errors, failure */
--color-danger-bg:     #3A1E1E  /* Dark red - error background */
--color-danger-dim:    #5F2D2D  /* Dim red - low confidence */
```

**Info/Neutral:**
```css
--color-info:          #42A5F5  /* Blue - info, neutral actions */
--color-info-bg:       #1E2A3A  /* Dark blue - info background */
```

**Confidence Indicators:**
```css
--confidence-high:     #4CAF50  /* Green dots 🟢 */
--confidence-medium:   #FFC107  /* Yellow dots 🟡 */
--confidence-low:      #E53935  /* Red dots 🔴 */
--confidence-empty:    #555555  /* Gray dots ⚪ */
--confidence-action:   #FF9800  /* Orange dots 🟠 */
```

---

## 📝 Typography

### Font Families

**Primary Font (UI):**
```css
--font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
                 'Roboto', 'Helvetica Neue', Arial, sans-serif;
```
- Clean, readable, system fonts
- Excellent on mobile
- Fast loading (no web fonts needed for MVP)

**Monospace Font (Codes, Technical):**
```css
--font-mono: 'SF Mono', 'Courier New', Consolas, monospace;
```
- For room codes (4S2X)
- Technical data
- Chat timestamps

**Optional Future (Dramatic Headers):**
```css
--font-headline: 'Bebas Neue', Impact, sans-serif;
```
- For dramatic moments ("MISSION COMPLETE!")
- Landing page title
- Requires web font (add later)

### Font Sizes

**Mobile Scale (Base 16px):**
```css
--text-xs:      12px   /* Hints, timestamps, fine print */
--text-sm:      14px   /* Secondary text, descriptions */
--text-base:    16px   /* Body text, default */
--text-lg:      18px   /* Card titles, NPC names */
--text-xl:      20px   /* Section headers */
--text-2xl:     24px   /* Screen titles */
--text-3xl:     32px   /* Page titles, dramatic moments */
```

### Font Weights

```css
--weight-normal:   400  /* Body text */
--weight-medium:   500  /* Card titles, labels */
--weight-semibold: 600  /* Buttons, important text */
--weight-bold:     700  /* Headers, emphasis */
```

### Line Heights

```css
--leading-tight:   1.25  /* Compact headers */
--leading-normal:  1.5   /* Body text, readable */
--leading-relaxed: 1.75  /* Longer paragraphs */
```

---

## 📐 Spacing System

**8px Base Grid:**

```css
--space-xs:   4px    /* Tiny gaps */
--space-sm:   8px    /* Small gaps, tight spacing */
--space-md:   12px   /* Default spacing */
--space-lg:   16px   /* Card padding, section gaps */
--space-xl:   20px   /* Large section spacing */
--space-2xl:  24px   /* Screen padding */
--space-3xl:  32px   /* Major section gaps */
```

**Container Padding:**
```css
--container-padding: 20px  /* Left/right screen padding */
--card-padding:      16px  /* Inside cards/modals */
```

---

## 🎯 Component Styles

### Buttons

**Primary Button (Gold CTAs):**
```css
background: #D4AF37  /* Gold */
color: #0F0F0F       /* Black text */
padding: 12px 24px
border-radius: 8px
font-weight: 600
font-size: 14px
min-height: 44px     /* Touch target */
border: none
box-shadow: 0 2px 8px rgba(212, 175, 55, 0.3)

/* Hover */
background: #E5C158

/* Pressed */
background: #B8941F
transform: scale(0.98)

/* Disabled */
background: #555555
color: #888888
cursor: not-allowed
```

**Secondary Button (Outline):**
```css
background: transparent
color: #FFFFFF
border: 2px solid #444444
padding: 12px 24px
border-radius: 8px
font-weight: 600
font-size: 14px
min-height: 44px

/* Hover */
border-color: #D4AF37
color: #D4AF37

/* Pressed */
background: #1E1E1E
```

**Text Button (Subtle Actions):**
```css
background: transparent
color: #B0B0B0
border: none
padding: 8px 16px
font-size: 14px
text-decoration: underline

/* Hover */
color: #FFFFFF
```

### Cards & Containers

**Standard Card:**
```css
background: #1E1E1E
border: 1px solid #333333
border-radius: 12px
padding: 16px
box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3)
```

**Selected/Active Card:**
```css
background: #1E1E1E
border: 2px solid #D4AF37  /* Gold border */
border-radius: 12px
padding: 16px
box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2)
```

**Modal Overlay:**
```css
background: rgba(0, 0, 0, 0.85)  /* Dark translucent */
backdrop-filter: blur(4px)        /* Blur background */
```

**Modal Content:**
```css
background: #1E1E1E
border: 1px solid #444444
border-radius: 16px
padding: 24px
max-width: 480px
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5)
```

### Input Fields

**Text Input:**
```css
background: #2A2A2A
border: 1px solid #3A3A3A
border-radius: 8px
padding: 12px
color: #FFFFFF
font-size: 14px
min-height: 44px

/* Focus */
border-color: #D4AF37
outline: none
box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1)

/* Disabled */
background: #1A1A1A
color: #666666
```

**Dropdown/Select:**
```css
background: #2A2A2A
border: 1px solid #3A3A3A
border-radius: 8px
padding: 12px 16px
color: #FFFFFF
font-size: 14px
min-height: 44px
cursor: pointer

/* Chevron icon on right */
background-image: url('chevron-down.svg')
background-position: right 12px center
background-repeat: no-repeat
padding-right: 40px
```

### Chat Bubbles

**NPC Message (Left-aligned):**
```css
background: #2A2A2A
border: 1px solid #3A3A3A
border-radius: 12px 12px 12px 4px  /* Flat bottom-left */
padding: 12px 16px
color: #FFFFFF
max-width: 80%
margin-bottom: 8px
```

**Player Message (Right-aligned):**
```css
background: #D4AF37  /* Gold */
border: none
border-radius: 12px 12px 4px 12px  /* Flat bottom-right */
padding: 12px 16px
color: #0F0F0F       /* Black text */
max-width: 80%
margin-bottom: 8px
margin-left: auto
```

### Task Cards

**Available Task (Can Do Now):**
```css
background: #1E1E1E
border: 1px solid #333333
border-radius: 12px
padding: 16px
cursor: pointer

/* Hover */
border-color: #D4AF37
transform: translateY(-2px)
box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2)
```

**Locked/Travel Task (Grayed Out):**
```css
background: #1A1A1A
border: 1px solid #2A2A2A
border-radius: 12px
padding: 16px
opacity: 0.6
cursor: pointer  /* Still clickable to view */
```

**Completed Task:**
```css
background: #1A1A1A
border: 1px solid #2D5F2D  /* Dark green */
border-radius: 12px
padding: 16px
opacity: 0.7
```

### Badges & Indicators

**Team Task Badge:**
```css
background: #42A5F5  /* Blue */
color: #FFFFFF
padding: 4px 8px
border-radius: 4px
font-size: 11px
font-weight: 600
text-transform: uppercase
```

**Item Count Badge:**
```css
background: #E53935  /* Red */
color: #FFFFFF
padding: 2px 6px
border-radius: 10px  /* Pill shape */
font-size: 11px
font-weight: 700
min-width: 18px
text-align: center
```

**Status Indicator Dot:**
```css
/* Online/Active */
background: #4CAF50  /* Green */
width: 8px
height: 8px
border-radius: 50%
display: inline-block

/* Idle */
background: #FFC107  /* Yellow */

/* Offline */
background: #666666  /* Gray */
```

---

## 🎭 Icons & Imagery

### Icon Style

**Use Emoji as Icons (MVP):**
- ✅ No icon library needed
- ✅ Colorful, expressive
- ✅ Works everywhere
- ✅ Large enough for touch

**Examples:**
- 🎮 Minigames
- 💬 NPC conversations
- 🔍 Search tasks
- 🤝 Item handoffs
- 🗣️ Info sharing
- 🎯 Objectives
- 📍 Locations
- 👥 Team
- 🗺️ Map
- 🎒 Inventory

**Future: Custom Icon Set**
- Consider Feather Icons or Heroicons
- Borderlands-style outlined icons
- Match character art aesthetic

### Character Portraits

**Style:** Borderlands (from nano-banana)
```
Size: 280x280px (large, prominent)
Style: 2D illustration, comic book, cell-shaded
Colors: Vibrant, saturated
Outlines: Bold, thick black lines
Format: PNG with transparency
```

### Backgrounds & Textures

**Solid Colors (MVP):**
- Keep it simple
- Dark gradients optional
- No patterns (distracting)

**Future Enhancements:**
- Subtle noise texture
- Dark grid pattern
- Animated particles

---

## 📏 Layout & Grid

### Container Widths

```css
--max-width-mobile:  480px   /* Mobile portrait */
--max-width-tablet:  768px   /* Tablet portrait */
--max-width-desktop: 1024px  /* Optional desktop */
```

**Centered Container:**
```css
max-width: 480px
margin: 0 auto
padding: 20px
```

### Spacing Patterns

**Vertical Rhythm:**
```css
Section gaps:     24px (--space-2xl)
Card gaps:        16px (--space-lg)
Element gaps:     12px (--space-md)
Tight gaps:       8px  (--space-sm)
```

**Touch Targets:**
```css
Minimum size:     44x44px (Apple/Google guidelines)
Preferred:        48x48px (more generous)
Button padding:   12px 24px (creates good hit area)
```

---

## 🎯 Border Radius Scale

```css
--radius-sm:   4px   /* Small elements, badges */
--radius-md:   8px   /* Buttons, inputs */
--radius-lg:   12px  /* Cards, task cards */
--radius-xl:   16px  /* Modals, large containers */
--radius-full: 9999px /* Pills, avatars, badges */
```

**Consistency:**
- Buttons: 8px
- Cards: 12px
- Modals: 16px
- Chat bubbles: 12px (with one flat corner)

---

## 🌑 Shadows & Depth

**Elevation System (Material-inspired):**

```css
/* Subtle (cards on background) */
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.3);

/* Medium (modals, hovering cards) */
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);

/* Large (full-screen modals) */
--shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);

/* Accent glow (gold buttons, selected items) */
--shadow-accent: 0 2px 8px rgba(212, 175, 55, 0.3);
--shadow-accent-lg: 0 4px 16px rgba(212, 175, 55, 0.4);
```

---

## ⚡ Animation & Transitions

### Timing Functions

```css
--ease-out:     cubic-bezier(0.33, 1, 0.68, 1)     /* Smooth deceleration */
--ease-in-out:  cubic-bezier(0.65, 0, 0.35, 1)     /* Smooth both ends */
--ease-bounce:  cubic-bezier(0.68, -0.55, 0.265, 1.55)  /* Playful bounce */
```

### Durations

```css
--duration-fast:   150ms   /* Quick feedback (hover, press) */
--duration-normal: 250ms   /* Standard transitions */
--duration-slow:   400ms   /* Smooth, dramatic (modals) */
```

### Common Transitions

**Button Hover:**
```css
transition: all 150ms ease-out;
```

**Card Hover:**
```css
transition: transform 250ms ease-out, box-shadow 250ms ease-out;
```

**Modal Open:**
```css
animation: slideUp 400ms ease-out;

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(100px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Success Animation:**
```css
animation: pulse 400ms ease-in-out;

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
```

---

## 📱 Component Patterns

### Headers

**Screen Title:**
```css
font-size: 24px       (--text-2xl)
font-weight: 700      (--weight-bold)
color: #FFFFFF        (--color-text-primary)
margin-bottom: 16px
```

**Section Title:**
```css
font-size: 18px       (--text-lg)
font-weight: 600      (--weight-semibold)
color: #D4AF37        (--color-text-gold)
margin-bottom: 12px
text-transform: uppercase
letter-spacing: 0.5px
```

**Subsection/Label:**
```css
font-size: 12px       (--text-xs)
font-weight: 600      (--weight-semibold)
color: #888888        (--color-text-tertiary)
text-transform: uppercase
letter-spacing: 1px
margin-bottom: 8px
```

### Lists

**Player List Item:**
```css
display: flex
align-items: center
padding: 12px
background: #1E1E1E
border: 1px solid #333333
border-radius: 8px
gap: 12px
min-height: 56px  /* Comfortable tap target */
```

**Task List Item:**
```css
padding: 16px
background: #1E1E1E
border: 1px solid #333333
border-radius: 12px
margin-bottom: 12px
cursor: pointer
min-height: 80px
```

### Status Messages

**Toast Notification:**
```css
background: #2A2A2A
border: 1px solid #444444
border-radius: 8px
padding: 12px 16px
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4)
position: fixed
bottom: 80px
left: 20px
right: 20px
max-width: 440px
margin: 0 auto
animation: slideUp 250ms ease-out
z-index: 1000
```

**Success Banner:**
```css
background: #1E3A1E  /* Dark green */
border: 2px solid #4CAF50
color: #FFFFFF
padding: 20px
border-radius: 12px
text-align: center
```

**Failure Banner:**
```css
background: #3A1E1E  /* Dark red */
border: 2px solid #E53935
color: #FFFFFF
padding: 20px
border-radius: 12px
text-align: center
```

---

## 🎨 Design Inspiration

### Reference Games/Apps

**Borderlands Series:**
- Cell-shaded art style
- Bold outlines
- Vibrant colors on dark backgrounds
- Comic book aesthetic

**Among Us:**
- Simple, chunky UI
- Clear iconography
- High contrast
- Mobile-friendly

**Jackbox Games:**
- Large text for readability
- Simple color schemes
- Party game accessibility
- Works on any device

**Escape Room Apps:**
- Puzzle-focused UI
- Minimal chrome
- Immersive dark themes
- Clear objectives

### Design Tools

**For Prototyping:**
- **Figma** (recommended, free, collaborative)
- **Sketch** (Mac only)
- **Adobe XD** (feature-rich)

**For Color Exploration:**
- [Coolors.co](https://coolors.co/) - palette generator
- [Paletton](https://paletton.com/) - color scheme designer
- [Adobe Color](https://color.adobe.com/) - advanced tool

**For Typography:**
- [Google Fonts](https://fonts.google.com/) - free web fonts
- [Type Scale](https://typescale.com/) - generate size scales
- [Modular Scale](https://www.modularscale.com/) - harmonic scales

---

## 🚀 Implementation Guidelines

### Flutter/Dart Considerations

**Theme Definition:**
```dart
ThemeData(
  brightness: Brightness.dark,
  primaryColor: Color(0xFFD4AF37),  // Gold
  scaffoldBackgroundColor: Color(0xFF0F0F0F),  // Black
  cardColor: Color(0xFF1E1E1E),  // Dark gray
  
  textTheme: TextTheme(
    bodyLarge: TextStyle(fontSize: 16, color: Colors.white),
    bodyMedium: TextStyle(fontSize: 14, color: Color(0xFFB0B0B0)),
    titleLarge: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
  ),
  
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: Color(0xFFD4AF37),
      foregroundColor: Color(0xFF0F0F0F),
      minimumSize: Size.fromHeight(44),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
    ),
  ),
)
```

### CSS Variables (Web)

```css
:root {
  /* Colors */
  --color-bg-primary: #0F0F0F;
  --color-bg-secondary: #1E1E1E;
  --color-accent-primary: #D4AF37;
  --color-text-primary: #FFFFFF;
  
  /* Spacing */
  --space-md: 12px;
  --space-lg: 16px;
  
  /* Typography */
  --text-base: 16px;
  --weight-semibold: 600;
  
  /* Borders */
  --radius-md: 8px;
  --radius-lg: 12px;
}

body {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: var(--text-base);
}
```

---

## ✅ Design Checklist

**Before Building Any Screen:**

- [ ] Use color palette (no random colors)
- [ ] Follow spacing system (8px grid)
- [ ] Minimum 44px touch targets
- [ ] Dark theme throughout
- [ ] Gold for primary actions
- [ ] White text, gray secondary text
- [ ] 12px card border radius
- [ ] 8px button border radius
- [ ] Consistent font sizes
- [ ] Proper contrast ratios (WCAG AA)
- [ ] Test on mobile (portrait 375px wide minimum)

---

## 🎨 Quick Reference

**Most Common Patterns:**

**Primary CTA Button:**
- Gold (#D4AF37) background
- Black (#0F0F0F) text
- 8px radius, 12px/24px padding
- 600 font weight, 14px size

**Card:**
- Dark gray (#1E1E1E) background
- Subtle (#333333) border
- 12px radius, 16px padding
- 2px shadow

**Text Hierarchy:**
- Headers: 24px bold white
- Body: 16px regular white
- Secondary: 14px medium light gray
- Hints: 12px regular gray

**Spacing:**
- Screen padding: 20px
- Between sections: 24px
- Between cards: 16px
- Inside cards: 12px

---

## 💡 Tips for Consistency

1. **Use Design Tokens**: Define all colors/sizes as variables
2. **Component Library**: Build reusable button/card components
3. **Style Guide Reference**: Keep this doc open while coding
4. **Test Dark Mode**: All colors should work on dark background
5. **Accessibility**: Maintain 4.5:1 contrast ratio minimum
6. **Mobile First**: Test on 375px width (iPhone SE)
7. **Touch Friendly**: Never go below 44px for interactive elements
8. **One Gold**: Use accent gold sparingly (makes it impactful)
9. **Consistent Radius**: Always 8px or 12px, never random
10. **Spacing Grid**: Always multiples of 4 or 8

---

## 🎯 Next Steps

1. **Review this design system** with team
2. **Create Figma prototypes** (optional but helpful)
3. **Build Flutter theme** with these tokens
4. **Create reusable components** (buttons, cards, inputs)
5. **Test on real devices** (various screen sizes)
6. **Iterate based on usability** testing

---

*Last Updated: 2026-01-27*  
*Version: 1.0*  
*Status: Ready for Implementation*
