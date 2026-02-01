import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_dimensions.dart';

enum BadgeType {
  team,
  minigame,
  npc,
  discovery,
  completed,
}

/// Badge widget for task types and status indicators
class HeistBadge extends StatelessWidget {
  final String text;
  final BadgeType type;

  const HeistBadge({
    Key? key,
    required this.text,
    required this.type,
  }) : super(key: key);

  Color get _backgroundColor {
    switch (type) {
      case BadgeType.team:
        return AppColors.info;
      case BadgeType.minigame:
        return AppColors.warning;
      case BadgeType.npc:
        return AppColors.accentSecondary;
      case BadgeType.discovery:
        return AppColors.accentTertiary;
      case BadgeType.completed:
        return AppColors.success;
    }
  }

  Color get _textColor {
    return AppColors.bgPrimary;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: AppDimensions.spaceSM,
        vertical: AppDimensions.spaceXS,
      ),
      decoration: BoxDecoration(
        color: _backgroundColor,
        borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
      ),
      child: Text(
        text.toUpperCase(),
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: _textColor,
          letterSpacing: 0.5,
        ),
      ),
    );
  }
}
