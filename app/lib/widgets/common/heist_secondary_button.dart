import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_dimensions.dart';

/// Secondary button with outline style
/// Used for less prominent actions like "Leave Room", "Cancel", etc.
class HeistSecondaryButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool fullWidth;
  final IconData? icon;

  const HeistSecondaryButton({
    Key? key,
    required this.text,
    this.onPressed,
    this.fullWidth = true,
    this.icon,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: fullWidth ? double.infinity : null,
      height: AppDimensions.buttonHeight,
      child: OutlinedButton(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.textPrimary,
          side: BorderSide(
            color: AppColors.borderMedium,
            width: 2,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          ),
          padding: EdgeInsets.symmetric(
            horizontal: AppDimensions.spaceXL,
            vertical: AppDimensions.spaceMD,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (icon != null) ...[
              Icon(icon, size: AppDimensions.iconMD),
              SizedBox(width: AppDimensions.spaceSM),
            ],
            Text(
              text,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
