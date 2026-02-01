import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_dimensions.dart';
import '../../models/player.dart';

/// Player card showing team member info
class PlayerCard extends StatelessWidget {
  final Player player;
  final VoidCallback? onTap;

  const PlayerCard({
    Key? key,
    required this.player,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.only(bottom: AppDimensions.spaceMD),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
        border: Border.all(
          color: AppColors.borderSubtle,
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
          child: Padding(
            padding: EdgeInsets.all(AppDimensions.cardPadding),
            child: Row(
              children: [
                // Player avatar/icon
                Container(
                  width: AppDimensions.avatarMD,
                  height: AppDimensions.avatarMD,
                  decoration: BoxDecoration(
                    color: AppColors.bgTertiary,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: player.isHost
                          ? AppColors.accentPrimary
                          : AppColors.borderSubtle,
                      width: 2,
                    ),
                  ),
                  child: Center(
                    child: Text(
                      player.name.isNotEmpty
                          ? player.name[0].toUpperCase()
                          : '?',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ),
                ),
                
                SizedBox(width: AppDimensions.spaceMD),
                
                // Player info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            player.name,
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          if (player.isHost) ...[
                            SizedBox(width: AppDimensions.spaceXS),
                            Text(
                              '👑',
                              style: TextStyle(fontSize: 14),
                            ),
                          ],
                        ],
                      ),
                      SizedBox(height: AppDimensions.spaceXS),
                      Text(
                        player.role ?? 'No role selected',
                        style: TextStyle(
                          fontSize: 12,
                          color: player.role != null
                              ? AppColors.textSecondary
                              : AppColors.textTertiary,
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Ready status indicator
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: player.isReady
                        ? AppColors.success
                        : AppColors.textTertiary,
                    shape: BoxShape.circle,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
