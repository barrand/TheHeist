import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_dimensions.dart';

/// Reusable card widget with consistent styling
/// Supports selected state for highlighting
class HeistCard extends StatelessWidget {
  final Widget child;
  final VoidCallback? onTap;
  final bool selected;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;

  const HeistCard({
    Key? key,
    required this.child,
    this.onTap,
    this.selected = false,
    this.padding,
    this.margin,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
        border: Border.all(
          color: selected ? AppColors.accentPrimary : AppColors.borderSubtle,
          width: selected ? 2 : 1,
        ),
        boxShadow: selected
            ? [
                BoxShadow(
                  color: AppColors.glowAccent,
                  blurRadius: 12,
                  offset: Offset(0, 4),
                ),
              ]
            : null,
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
          child: Padding(
            padding: padding ?? EdgeInsets.all(AppDimensions.cardPadding),
            child: child,
          ),
        ),
      ),
    );
  }
}
