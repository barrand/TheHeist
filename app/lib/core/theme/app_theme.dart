import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'app_dimensions.dart';

/// The Heist - Main Theme Definition
/// Neon Purple theme with all component styles
class AppTheme {
  // Private constructor to prevent instantiation
  AppTheme._();

  /// Build the complete dark theme for The Heist
  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      
      // ============================================
      // Color Scheme
      // ============================================
      colorScheme: ColorScheme.dark(
        primary: AppColors.accentPrimary,
        secondary: AppColors.accentSecondary,
        tertiary: AppColors.accentTertiary,
        surface: AppColors.bgSecondary,
        error: AppColors.danger,
        onPrimary: AppColors.bgPrimary,  // Text on primary buttons
        onSecondary: AppColors.textPrimary,
        onSurface: AppColors.textPrimary,
        onError: AppColors.textPrimary,
      ),
      
      // ============================================
      // Scaffold
      // ============================================
      scaffoldBackgroundColor: AppColors.bgPrimary,
      
      // ============================================
      // Card Theme
      // ============================================
      cardTheme: CardThemeData(
        color: AppColors.bgSecondary,
        elevation: AppDimensions.elevationSM,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
          side: BorderSide(
            color: AppColors.borderSubtle,
            width: 1,
          ),
        ),
        margin: EdgeInsets.zero,
      ),
      
      // ============================================
      // Elevated Button (Primary CTA)
      // ============================================
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.accentPrimary,
          foregroundColor: AppColors.bgPrimary,
          minimumSize: Size.fromHeight(AppDimensions.buttonHeight),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          ),
          textStyle: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
          elevation: AppDimensions.elevationMD,
          shadowColor: AppColors.glowAccent,
        ),
      ),
      
      // ============================================
      // Outlined Button (Secondary)
      // ============================================
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.textPrimary,
          side: BorderSide(
            color: AppColors.borderMedium,
            width: 2,
          ),
          minimumSize: Size.fromHeight(AppDimensions.buttonHeight),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          ),
          textStyle: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      
      // ============================================
      // Text Button
      // ============================================
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: AppColors.textSecondary,
          textStyle: TextStyle(
            fontSize: 14,
            decoration: TextDecoration.underline,
          ),
        ),
      ),
      
      // ============================================
      // Input Decoration
      // ============================================
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.bgTertiary,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          borderSide: BorderSide(color: AppColors.borderSubtle),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          borderSide: BorderSide(color: AppColors.borderSubtle),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          borderSide: BorderSide(
            color: AppColors.accentPrimary,
            width: 2,
          ),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          borderSide: BorderSide(color: AppColors.danger),
        ),
        contentPadding: EdgeInsets.all(AppDimensions.spaceMD),
        hintStyle: TextStyle(color: AppColors.textTertiary),
      ),
      
      // ============================================
      // Text Theme
      // ============================================
      textTheme: TextTheme(
        // Display styles (large headers)
        displayLarge: TextStyle(
          fontSize: 32,
          fontWeight: FontWeight.bold,
          color: AppColors.textPrimary,
        ),
        displayMedium: TextStyle(
          fontSize: 24,
          fontWeight: FontWeight.bold,
          color: AppColors.textPrimary,
        ),
        displaySmall: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
        
        // Headline styles (section headers)
        headlineMedium: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: AppColors.accentPrimary,
          letterSpacing: 0.5,
        ),
        headlineSmall: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
        
        // Body styles
        bodyLarge: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.normal,
          color: AppColors.textPrimary,
        ),
        bodyMedium: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.normal,
          color: AppColors.textSecondary,
        ),
        bodySmall: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.normal,
          color: AppColors.textTertiary,
        ),
        
        // Label styles (buttons, badges)
        labelLarge: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
        labelMedium: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
        labelSmall: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
      ),
      
      // ============================================
      // App Bar
      // ============================================
      appBarTheme: AppBarTheme(
        backgroundColor: AppColors.bgPrimary,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: AppColors.textPrimary,
        ),
        iconTheme: IconThemeData(
          color: AppColors.textPrimary,
          size: AppDimensions.iconLG,
        ),
      ),
      
      // ============================================
      // Bottom Navigation
      // ============================================
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: AppColors.bgSecondary,
        selectedItemColor: AppColors.accentPrimary,
        unselectedItemColor: AppColors.textTertiary,
        type: BottomNavigationBarType.fixed,
        elevation: AppDimensions.elevationLG,
        selectedLabelStyle: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.normal,
        ),
      ),
      
      // ============================================
      // Divider
      // ============================================
      dividerTheme: DividerThemeData(
        color: AppColors.borderSubtle,
        thickness: 1,
        space: 1,
      ),
      
      // ============================================
      // Icon Theme
      // ============================================
      iconTheme: IconThemeData(
        color: AppColors.textPrimary,
        size: AppDimensions.iconMD,
      ),
      
      // ============================================
      // Floating Action Button
      // ============================================
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: AppColors.accentPrimary,
        foregroundColor: AppColors.bgPrimary,
        elevation: AppDimensions.elevationMD,
      ),
      
      // ============================================
      // Dialog
      // ============================================
      dialogTheme: DialogThemeData(
        backgroundColor: AppColors.bgSecondary,
        elevation: AppDimensions.elevationLG,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusXL),
          side: BorderSide(
            color: AppColors.borderMedium,
          ),
        ),
      ),
      
      // ============================================
      // Bottom Sheet
      // ============================================
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: AppColors.bgSecondary,
        elevation: AppDimensions.elevationLG,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(AppDimensions.radiusXL),
            topRight: Radius.circular(AppDimensions.radiusXL),
          ),
        ),
      ),
      
      // ============================================
      // Chip
      // ============================================
      chipTheme: ChipThemeData(
        backgroundColor: AppColors.bgTertiary,
        labelStyle: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
        padding: EdgeInsets.symmetric(
          horizontal: AppDimensions.spaceSM,
          vertical: AppDimensions.spaceXS,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
        ),
      ),
    );
  }
}
