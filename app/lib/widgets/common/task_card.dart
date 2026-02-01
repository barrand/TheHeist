import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_dimensions.dart';

/// Task card with icon, title, and location
/// Shows available tasks in the game
class TaskCard extends StatelessWidget {
  final String icon;
  final String title;
  final String location;
  final VoidCallback? onTap;
  final bool available;

  const TaskCard({
    Key? key,
    required this.icon,
    required this.title,
    required this.location,
    this.onTap,
    this.available = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.only(bottom: AppDimensions.spaceMD),
      decoration: BoxDecoration(
        color: available ? AppColors.bgSecondary : AppColors.bgSecondary.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
        border: Border.all(
          color: AppColors.borderSubtle,
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: available ? onTap : null,
          borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
          child: Padding(
            padding: EdgeInsets.all(AppDimensions.cardPadding),
            child: Row(
              children: [
                // Task icon
                Text(
                  icon,
                  style: TextStyle(fontSize: 24),
                ),
                SizedBox(width: AppDimensions.spaceMD),
                
                // Task details
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: available ? AppColors.textPrimary : AppColors.textTertiary,
                        ),
                      ),
                      SizedBox(height: AppDimensions.spaceXS),
                      Row(
                        children: [
                          Text(
                            '📍',
                            style: TextStyle(fontSize: 12),
                          ),
                          SizedBox(width: AppDimensions.spaceXS),
                          Text(
                            location,
                            style: TextStyle(
                              fontSize: 12,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                
                // Arrow indicator if available
                if (available)
                  Icon(
                    Icons.chevron_right,
                    color: AppColors.textSecondary,
                    size: AppDimensions.iconLG,
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
