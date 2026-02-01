# Flutter Theming & Design System Implementation Guide

## 🎨 Flutter Built-in Theming (Recommended for MVP)

Flutter has excellent built-in theming support. **No extra packages needed!**

### Basic ThemeData Setup

```dart
import 'package:flutter/material.dart';

class HeistTheme {
  // Define your colors as static constants
  static const Color bgPrimary = Color(0xFF0F0F0F);
  static const Color bgSecondary = Color(0xFF1E1E1E);
  static const Color bgTertiary = Color(0xFF2A2A2A);
  
  static const Color accentPrimary = Color(0xFFD4AF37);  // Gold
  static const Color accentLight = Color(0xFFE5C158);
  static const Color accentDark = Color(0xFFB8941F);
  
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFB0B0B0);
  static const Color textTertiary = Color(0xFF888888);
  
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFFA726);
  static const Color danger = Color(0xFFE53935);
  
  // Build the ThemeData
  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      
      // Color scheme
      colorScheme: ColorScheme.dark(
        primary: accentPrimary,
        secondary: accentLight,
        surface: bgSecondary,
        background: bgPrimary,
        error: danger,
      ),
      
      // Scaffold
      scaffoldBackgroundColor: bgPrimary,
      
      // Card theme
      cardTheme: CardTheme(
        color: bgSecondary,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: Color(0xFF333333), width: 1),
        ),
      ),
      
      // Elevated button (primary CTA)
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: accentPrimary,
          foregroundColor: bgPrimary,  // Black text on gold
          minimumSize: Size.fromHeight(44),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          textStyle: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
          elevation: 4,
        ),
      ),
      
      // Outlined button (secondary)
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: textPrimary,
          side: BorderSide(color: Color(0xFF444444), width: 2),
          minimumSize: Size.fromHeight(44),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          textStyle: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      
      // Text button
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: textSecondary,
          textStyle: TextStyle(
            fontSize: 14,
            decoration: TextDecoration.underline,
          ),
        ),
      ),
      
      // Input decoration
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: bgTertiary,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: Color(0xFF3A3A3A)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: Color(0xFF3A3A3A)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: accentPrimary, width: 2),
        ),
        contentPadding: EdgeInsets.all(12),
        hintStyle: TextStyle(color: textTertiary),
      ),
      
      // Text theme
      textTheme: TextTheme(
        displayLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: textPrimary),
        displayMedium: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: textPrimary),
        displaySmall: TextStyle(fontSize: 20, fontWeight: FontWeight.w600, color: textPrimary),
        
        headlineMedium: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: accentPrimary),
        headlineSmall: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: textPrimary),
        
        bodyLarge: TextStyle(fontSize: 16, fontWeight: FontWeight.normal, color: textPrimary),
        bodyMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.normal, color: textSecondary),
        bodySmall: TextStyle(fontSize: 12, fontWeight: FontWeight.normal, color: textTertiary),
        
        labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: textPrimary),
      ),
      
      // App bar
      appBarTheme: AppBarTheme(
        backgroundColor: bgPrimary,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: textPrimary,
        ),
      ),
      
      // Bottom navigation
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: bgSecondary,
        selectedItemColor: accentPrimary,
        unselectedItemColor: textTertiary,
        type: BottomNavigationBarType.fixed,
      ),
    );
  }
}

// Usage in main.dart
void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'The Heist',
      theme: HeistTheme.darkTheme,  // Apply your theme
      home: LandingPage(),
    );
  }
}
```

---

## 📦 Helpful Flutter Packages

### 1. **flutter_riverpod** (State Management)
Not directly theming, but essential for managing theme switching

```yaml
dependencies:
  flutter_riverpod: ^2.5.0
```

**Use case:** Let users switch between color schemes (Gold, Blue, Purple)

```dart
// theme_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

final themeProvider = StateNotifierProvider<ThemeNotifier, ThemeMode>((ref) {
  return ThemeNotifier();
});

class ThemeNotifier extends StateNotifier<ThemeMode> {
  ThemeNotifier() : super(ThemeMode.dark);
  
  void toggleTheme() {
    state = state == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
  }
  
  void setColorScheme(String scheme) {
    // Switch between Gold, Blue, Purple, etc.
  }
}
```

### 2. **google_fonts** (Typography)
Easily add custom fonts without manual setup

```yaml
dependencies:
  google_fonts: ^6.1.0
```

```dart
import 'package:google_fonts/google_fonts.dart';

textTheme: GoogleFonts.interTextTheme(
  ThemeData.dark().textTheme,
).copyWith(
  displayLarge: GoogleFonts.bebasNeue(fontSize: 32, color: Colors.white),
  bodyLarge: GoogleFonts.inter(fontSize: 16, color: Colors.white),
),
```

**Recommended fonts for heist theme:**
- **Inter** - Clean, modern UI (body text)
- **Bebas Neue** - Bold headers (dramatic moments)
- **Rajdhani** - Tech/heist aesthetic
- **Orbitron** - Cyberpunk/tech heist

### 3. **flex_color_scheme** (Advanced Theming)
Generate beautiful color schemes automatically

```yaml
dependencies:
  flex_color_scheme: ^7.3.0
```

```dart
import 'package:flex_color_scheme/flex_color_scheme.dart';

theme: FlexThemeData.dark(
  scheme: FlexScheme.gold,  // Or custom colors
  surfaceMode: FlexSurfaceMode.highScaffoldLowSurface,
  blendLevel: 20,
  appBarStyle: FlexAppBarStyle.background,
  subThemesData: const FlexSubThemesData(
    blendOnLevel: 20,
    blendOnColors: false,
    useTextTheme: true,
    useM2StyleDividerInM3: true,
    buttonMinSize: Size(64, 44),  // Touch targets
    elevatedButtonRadius: 8.0,
    outlinedButtonRadius: 8.0,
    inputDecoratorRadius: 8.0,
  ),
  visualDensity: FlexColorScheme.comfortablePlatformDensity,
  fontFamily: GoogleFonts.inter().fontFamily,
);
```

**Pros:**
- Generates harmonious colors automatically
- Handles light/dark mode
- Material 3 support

**Cons:**
- Another dependency
- Less control than custom theme
- Overkill for MVP

### 4. **dynamic_color** (Material You / Android 12+)
Extract colors from user's wallpaper (Android 12+)

```yaml
dependencies:
  dynamic_color: ^1.7.0
```

```dart
import 'package:dynamic_color/dynamic_color.dart';

DynamicColorBuilder(
  builder: (lightColorScheme, darkColorScheme) {
    return MaterialApp(
      theme: ThemeData(
        colorScheme: lightColorScheme ?? HeistTheme.goldScheme,
      ),
      darkTheme: ThemeData(
        colorScheme: darkColorScheme ?? HeistTheme.goldScheme,
      ),
    );
  },
);
```

**Use case:** Optional feature - match user's device theme

### 5. **theme_tailor** (Code Generation for Themes)
Generate type-safe theme classes from your colors

```yaml
dev_dependencies:
  theme_tailor: ^3.0.0
  build_runner: ^2.4.0
```

```dart
import 'package:theme_tailor_annotation/theme_tailor_annotation.dart';

part 'app_theme.tailor.dart';

@TailorMixin()
class AppTheme extends ThemeExtension<AppTheme> with _$AppThemeTailorMixin {
  const AppTheme({
    required this.accentPrimary,
    required this.accentSecondary,
    required this.bgPrimary,
    required this.bgSecondary,
  });

  final Color accentPrimary;
  final Color accentSecondary;
  final Color bgPrimary;
  final Color bgSecondary;
}

// Run: flutter pub run build_runner build
```

**Pros:**
- Type-safe theme access
- Easy to extend
- No runtime errors

**Cons:**
- Code generation overhead
- Extra build step

---

## 🎯 Recommended Approach for The Heist

### For MVP (Start Simple):

**✅ Use Built-in Flutter ThemeData**
- No extra packages
- Fast to implement
- Fully featured
- Easy to customize

**✅ Add google_fonts** (optional, later)
- Only if you want custom fonts
- Otherwise use system fonts (faster)

**✅ Add riverpod** (when needed)
- For state management (not just theming)
- When you need to switch schemes

### For Later (Post-Launch):

**Consider flex_color_scheme** if:
- Users request light mode
- You want automatic color harmonization
- Material 3 support needed

**Consider dynamic_color** if:
- Android 12+ users want personalization
- Marketing differentiator

---

## 🎨 Easy Theme Switching Example

```dart
// Define multiple color schemes
class HeistColorSchemes {
  static ColorScheme get goldHeist => ColorScheme.dark(
    primary: Color(0xFFD4AF37),
    secondary: Color(0xFF8B7355),
    surface: Color(0xFF1E1E1E),
    background: Color(0xFF0F0F0F),
  );
  
  static ColorScheme get electricBlue => ColorScheme.dark(
    primary: Color(0xFF00D9FF),
    secondary: Color(0xFF7B61FF),
    surface: Color(0xFF151B2E),
    background: Color(0xFF0A0E1A),
  );
  
  static ColorScheme get neonPurple => ColorScheme.dark(
    primary: Color(0xFFB565FF),
    secondary: Color(0xFFFF00FF),
    surface: Color(0xFF1A0F2E),
    background: Color(0xFF0D0517),
  );
}

// Use in your app
class TheHeistApp extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedScheme = ref.watch(colorSchemeProvider);
    
    return MaterialApp(
      theme: ThemeData(
        colorScheme: selectedScheme,
        // ... rest of theme
      ),
      home: LandingPage(),
    );
  }
}
```

---

## 🔧 Custom Components with Theme

### Custom Button with Theme Colors

```dart
class HeistPrimaryButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final bool loading;
  
  const HeistPrimaryButton({
    required this.text,
    required this.onPressed,
    this.loading = false,
  });
  
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      height: 44,  // Touch target
      decoration: BoxDecoration(
        color: theme.colorScheme.primary,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: theme.colorScheme.primary.withOpacity(0.3),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: loading ? null : onPressed,
          borderRadius: BorderRadius.circular(8),
          child: Center(
            child: loading
              ? SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: theme.scaffoldBackgroundColor,
                  ),
                )
              : Text(
                  text,
                  style: theme.textTheme.labelLarge?.copyWith(
                    color: theme.scaffoldBackgroundColor,
                  ),
                ),
          ),
        ),
      ),
    );
  }
}

// Usage
HeistPrimaryButton(
  text: "START HEIST",
  onPressed: () => startGame(),
)
```

### Custom Card with Theme

```dart
class HeistCard extends StatelessWidget {
  final Widget child;
  final VoidCallback? onTap;
  final bool selected;
  
  const HeistCard({
    required this.child,
    this.onTap,
    this.selected = false,
  });
  
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      decoration: BoxDecoration(
        color: theme.cardTheme.color,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: selected 
            ? theme.colorScheme.primary 
            : Color(0xFF333333),
          width: selected ? 2 : 1,
        ),
        boxShadow: selected ? [
          BoxShadow(
            color: theme.colorScheme.primary.withOpacity(0.2),
            blurRadius: 12,
            offset: Offset(0, 4),
          ),
        ] : null,
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: EdgeInsets.all(16),
            child: child,
          ),
        ),
      ),
    );
  }
}
```

---

## 📱 Accessing Theme Values Anywhere

```dart
// In any widget
final theme = Theme.of(context);

// Use theme colors
Container(
  color: theme.colorScheme.primary,  // Accent color
  child: Text(
    'Hello',
    style: theme.textTheme.bodyLarge,  // Themed text style
  ),
)

// Custom extension for easier access
extension ThemeExtras on BuildContext {
  Color get primaryColor => Theme.of(this).colorScheme.primary;
  Color get backgroundColor => Theme.of(this).scaffoldBackgroundColor;
  Color get cardColor => Theme.of(this).cardTheme.color!;
  
  TextStyle get h1 => Theme.of(this).textTheme.displayLarge!;
  TextStyle get h2 => Theme.of(this).textTheme.displayMedium!;
  TextStyle get body => Theme.of(this).textTheme.bodyLarge!;
}

// Usage
Container(
  color: context.primaryColor,
  child: Text('Hello', style: context.h1),
)
```

---

## 🎨 Design Tokens (Advanced)

For large apps, define semantic tokens:

```dart
class HeistDesignTokens {
  // Spacing
  static const double spaceXS = 4;
  static const double spaceSM = 8;
  static const double spaceMD = 12;
  static const double spaceLG = 16;
  static const double spaceXL = 20;
  static const double space2XL = 24;
  static const double space3XL = 32;
  
  // Border radius
  static const double radiusSM = 4;
  static const double radiusMD = 8;
  static const double radiusLG = 12;
  static const double radiusXL = 16;
  
  // Touch targets
  static const double touchTargetMin = 44;
  static const double touchTargetPreferred = 48;
  
  // Container widths
  static const double maxWidthMobile = 480;
  static const double containerPadding = 20;
  static const double cardPadding = 16;
}

// Usage
Padding(
  padding: EdgeInsets.all(HeistDesignTokens.spaceLG),
  child: ...
)
```

---

## 🚀 Quick Start Recommendation

1. **Copy the ThemeData code** above into `lib/theme/heist_theme.dart`
2. **Choose your color scheme** from COLOR_SCHEME_OPTIONS.md
3. **Update the color constants** in HeistTheme class
4. **Apply theme** in MaterialApp
5. **Build one screen** to test it
6. **Add packages later** as needed

**Don't over-engineer at first!** Flutter's built-in theming is powerful enough for MVP.

---

## 💡 Pro Tips

1. **Use Theme.of(context)** instead of hardcoding colors
2. **Define colors once** in theme, use everywhere
3. **Test on real devices** (colors look different on screens)
4. **Dark mode only** for MVP (easier to nail one theme)
5. **Add light mode later** if users request it
6. **Custom widgets** for repeated patterns (buttons, cards)
7. **Extensions** make theme access cleaner
8. **Hot reload** works great with theme changes!

---

**Next step:** Pick your color scheme, and I'll generate the complete Flutter theme code for you! 🎨
