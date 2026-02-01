import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_dimensions.dart';

/// Section header with consistent styling
/// Used to separate content sections on screens
class SectionHeader extends StatelessWidget {
  final String text;
  final EdgeInsetsGeometry? margin;

  const SectionHeader({
    Key? key,
    required this.text,
    this.margin,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: margin ??
          EdgeInsets.only(
            top: AppDimensions.spaceXL,
            bottom: AppDimensions.spaceMD,
          ),
      child: Text(
        text.toUpperCase(),
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: AppColors.textTertiary,
          letterSpacing: 1,
        ),
      ),
    );
  }
}
