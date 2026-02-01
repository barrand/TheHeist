/// The Heist - Design System Dimensions
/// Spacing, sizing, and layout constants
class AppDimensions {
  // Private constructor to prevent instantiation
  AppDimensions._();

  // ============================================
  // Spacing System (8px base grid)
  // ============================================
  
  static const double spaceXS = 4.0;   // Tiny gaps
  static const double spaceSM = 8.0;   // Small gaps, tight spacing
  static const double spaceMD = 12.0;  // Default spacing
  static const double spaceLG = 16.0;  // Card padding, section gaps
  static const double spaceXL = 20.0;  // Large section spacing
  static const double space2XL = 24.0; // Screen padding
  static const double space3XL = 32.0; // Major section gaps

  // ============================================
  // Container Padding
  // ============================================
  
  static const double containerPadding = 20.0;  // Left/right screen padding
  static const double cardPadding = 16.0;       // Inside cards/modals

  // ============================================
  // Border Radius
  // ============================================
  
  static const double radiusSM = 4.0;   // Small elements, badges
  static const double radiusMD = 8.0;   // Buttons, inputs
  static const double radiusLG = 12.0;  // Cards, task cards
  static const double radiusXL = 16.0;  // Modals, large containers
  static const double radiusFull = 9999.0; // Pills, avatars, badges

  // ============================================
  // Touch Targets
  // ============================================
  
  static const double touchTargetMin = 44.0;       // Minimum (Apple/Google)
  static const double touchTargetPreferred = 48.0; // Preferred size
  static const double buttonHeight = 44.0;         // Standard button height

  // ============================================
  // Container Widths
  // ============================================
  
  static const double maxWidthMobile = 480.0;   // Mobile portrait
  static const double maxWidthTablet = 768.0;   // Tablet portrait
  static const double maxWidthDesktop = 1024.0; // Desktop (optional)

  // ============================================
  // Icon Sizes
  // ============================================
  
  static const double iconSM = 16.0;  // Small icons
  static const double iconMD = 20.0;  // Standard icons
  static const double iconLG = 24.0;  // Large icons (navigation)
  static const double iconXL = 32.0;  // Extra large icons

  // ============================================
  // Avatar/Image Sizes
  // ============================================
  
  static const double avatarSM = 32.0;   // Small avatar
  static const double avatarMD = 48.0;   // Standard avatar
  static const double avatarLG = 64.0;   // Large avatar
  static const double npcImage = 280.0;  // NPC character portrait

  // ============================================
  // Elevation (Shadow depth)
  // ============================================
  
  static const double elevationSM = 2.0;  // Subtle (cards)
  static const double elevationMD = 4.0;  // Medium (buttons)
  static const double elevationLG = 8.0;  // Large (modals)

  // ============================================
  // Animation Durations (milliseconds)
  // ============================================
  
  static const int durationFast = 150;    // Quick feedback (hover, press)
  static const int durationNormal = 250;  // Standard transitions
  static const int durationSlow = 400;    // Smooth, dramatic (modals)
}
