import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_dimensions.dart';
import '../../models/npc.dart';

/// Displays player objectives with confidence indicators
/// Shows what the team is trying to learn from the NPC
class ObjectiveCard extends StatelessWidget {
  final List<Objective> objectives;
  final String npcName;

  const ObjectiveCard({
    Key? key,
    required this.objectives,
    required this.npcName,
  }) : super(key: key);

  String _getConfidenceEmoji(ConfidenceLevel level) {
    switch (level) {
      case ConfidenceLevel.high:
        return '🟢🟢🟢';
      case ConfidenceLevel.medium:
        return '🟡🟡⚪';
      case ConfidenceLevel.low:
        return '🔴⚪⚪';
      case ConfidenceLevel.action:
        return '🟠🟠🟠';
    }
  }

  String _getSummaryMessage() {
    final highCount = objectives.where((o) => o.confidence == ConfidenceLevel.high && !o.isCompleted).length;
    final completedCount = objectives.where((o) => o.isCompleted).length;
    
    if (completedCount == objectives.length) {
      return 'Success! Mission info obtained!';
    } else if (highCount > 0) {
      return '$npcName likely knows about ${objectives.firstWhere((o) => o.confidence == ConfidenceLevel.high && !o.isCompleted).description}!';
    } else if (objectives.every((o) => o.confidence == ConfidenceLevel.low)) {
      return '$npcName probably doesn\'t know any of this';
    } else {
      return '$npcName might know something';
    }
  }

  String _getHeaderText() {
    final completedCount = objectives.where((o) => o.isCompleted).length;
    
    if (completedCount == objectives.length) {
      return '🎯 OBJECTIVES COMPLETE 🎉';
    } else if (objectives.length == 1) {
      return '🎯 YOUR OBJECTIVE ${objectives.first.confidence == ConfidenceLevel.high ? '✅' : ''}';
    } else {
      return '🎯 WHAT THE TEAM NEEDS';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.bgTertiary,
        border: Border.all(
          color: AppColors.accentPrimary,
          width: 2,
        ),
        borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
      ),
      padding: EdgeInsets.all(AppDimensions.cardPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Text(
            _getHeaderText(),
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppColors.accentLight,
              letterSpacing: 1,
            ),
          ),
          
          SizedBox(height: AppDimensions.spaceMD),
          
          // Objectives list
          ...objectives.map((objective) {
            return Padding(
              padding: EdgeInsets.only(bottom: AppDimensions.spaceSM),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Confidence or completion indicator
                  Text(
                    objective.isCompleted 
                        ? '✅' 
                        : _getConfidenceEmoji(objective.confidence),
                    style: TextStyle(fontSize: 12),
                  ),
                  SizedBox(width: AppDimensions.spaceSM),
                  
                  // Objective text
                  Expanded(
                    child: Text(
                      objective.description,
                      style: TextStyle(
                        fontSize: 14,
                        color: objective.isCompleted
                            ? AppColors.textSecondary
                            : AppColors.textPrimary,
                        decoration: objective.isCompleted
                            ? TextDecoration.lineThrough
                            : null,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
          
          SizedBox(height: AppDimensions.spaceSM),
          
          // Summary message
          Text(
            _getSummaryMessage(),
            style: TextStyle(
              fontSize: 12,
              color: AppColors.textSecondary,
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }
}
