import 'package:flutter/material.dart';

/// The Heist - Neon Purple Theme Colors
/// Night heist aesthetic: stylish, mysterious, distinctive
class AppColors {
  // Private constructor to prevent instantiation
  AppColors._();

  // ============================================
  // Background Colors
  // ============================================
  
  /// Deep purple-black - main background
  static const Color bgPrimary = Color(0xFF0D0517);
  
  /// Dark purple - cards, modals
  static const Color bgSecondary = Color(0xFF1A0F2E);
  
  /// Medium purple - inputs, hover states
  static const Color bgTertiary = Color(0xFF2A1A45);

  // ============================================
  // Accent Colors
  // ============================================
  
  /// Vibrant purple - primary buttons, highlights
  static const Color accentPrimary = Color(0xFFB565FF);
  
  /// Light purple - hover state
  static const Color accentLight = Color(0xFFD199FF);
  
  /// Deep purple - pressed state
  static const Color accentDark = Color(0xFF8B3FCC);
  
  /// Hot magenta - secondary accents
  static const Color accentSecondary = Color(0xFFFF00FF);
  
  /// Cyan blue - cool accents, success states
  static const Color accentTertiary = Color(0xFF00E5FF);

  // ============================================
  // Text Colors
  // ============================================
  
  /// White - main text
  static const Color textPrimary = Color(0xFFFFFFFF);
  
  /// Light gray - secondary text
  static const Color textSecondary = Color(0xFFB0B0B0);
  
  /// Medium gray - hints, disabled
  static const Color textTertiary = Color(0xFF888888);

  // ============================================
  // Border Colors
  // ============================================
  
  /// Dark gray - subtle dividers
  static const Color borderSubtle = Color(0xFF3A2550);
  
  /// Medium gray - card borders
  static const Color borderMedium = Color(0xFF4A3560);
  
  /// Purple - focused, selected
  static const Color borderAccent = accentPrimary;

  // ============================================
  // Semantic Colors
  // ============================================
  
  /// Cyan - success, available tasks
  static const Color success = Color(0xFF00E5FF);
  
  /// Dark cyan - success background
  static const Color successBg = Color(0xFF1E2A3A);
  
  /// Orange - warnings, action needed
  static const Color warning = Color(0xFFFF6B9D);
  
  /// Dark orange - warning background
  static const Color warningBg = Color(0xFF3A1E2A);
  
  /// Red - errors, failure
  static const Color danger = Color(0xFFE53935);
  
  /// Dark red - error background
  static const Color dangerBg = Color(0xFF3A1E1E);
  
  /// Purple - info, neutral actions
  static const Color info = accentPrimary;
  
  /// Dark purple - info background
  static const Color infoBg = bgSecondary;

  // ============================================
  // Confidence Indicators (for NPC objectives)
  // ============================================
  
  /// Green - high confidence
  static const Color confidenceHigh = Color(0xFF4CAF50);
  
  /// Yellow - medium confidence
  static const Color confidenceMedium = Color(0xFFFFC107);
  
  /// Red - low confidence
  static const Color confidenceLow = Color(0xFFE53935);
  
  /// Gray - empty/unknown
  static const Color confidenceEmpty = Color(0xFF555555);
  
  /// Orange - action needed
  static const Color confidenceAction = Color(0xFFFF9800);

  // ============================================
  // Special Effects
  // ============================================
  
  /// Shadow color for elevated components
  static Color shadowPrimary = Colors.black.withValues(alpha: 0.5);
  
  /// Glow effect for primary accent
  static Color glowAccent = accentPrimary.withValues(alpha: 0.3);
  
  /// Overlay for modals
  static Color overlay = Colors.black.withValues(alpha: 0.85);
}
