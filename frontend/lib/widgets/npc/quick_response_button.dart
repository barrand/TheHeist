import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_dimensions.dart';

/// Quick response suggestion button for NPC conversations
class QuickResponseButton extends StatelessWidget {
  final String text;
  final VoidCallback onTap;

  const QuickResponseButton({
    Key? key,
    required this.text,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.only(bottom: AppDimensions.spaceSM),
      child: Material(
        color: AppColors.bgTertiary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          child: Container(
            padding: EdgeInsets.symmetric(
              horizontal: AppDimensions.cardPadding,
              vertical: AppDimensions.spaceMD,
            ),
            decoration: BoxDecoration(
              border: Border.all(color: AppColors.borderSubtle),
              borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
            ),
            child: Row(
              children: [
                Text(
                  '💬',
                  style: TextStyle(fontSize: 16),
                ),
                SizedBox(width: AppDimensions.spaceMD),
                Expanded(
                  child: Text(
                    text,
                    style: TextStyle(
                      fontSize: 13,
                      color: AppColors.textPrimary,
                    ),
                  ),
                ),
                Icon(
                  Icons.arrow_forward_ios,
                  size: 14,
                  color: AppColors.textTertiary,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
