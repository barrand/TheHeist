import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_dimensions.dart';
import '../../models/npc.dart';

/// Chat message bubble for NPC conversations
class ChatBubble extends StatelessWidget {
  final ChatMessage message;
  final String? npcName;

  const ChatBubble({
    Key? key,
    required this.message,
    this.npcName,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: AppDimensions.spaceMD),
      child: Align(
        alignment: message.isPlayer ? Alignment.centerRight : Alignment.centerLeft,
        child: Container(
          constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width * 0.8,
          ),
          decoration: BoxDecoration(
            color: message.isPlayer
                ? AppColors.accentPrimary
                : AppColors.bgTertiary,
            border: message.isPlayer
                ? null
                : Border.all(color: AppColors.borderSubtle),
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(AppDimensions.radiusLG),
              topRight: Radius.circular(AppDimensions.radiusLG),
              bottomLeft: Radius.circular(
                message.isPlayer ? AppDimensions.radiusLG : AppDimensions.radiusSM,
              ),
              bottomRight: Radius.circular(
                message.isPlayer ? AppDimensions.radiusSM : AppDimensions.radiusLG,
              ),
            ),
          ),
          padding: EdgeInsets.symmetric(
            horizontal: AppDimensions.cardPadding,
            vertical: AppDimensions.spaceMD,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Label (NPC name or "You")
              if (!message.isPlayer && npcName != null) ...[
                Text(
                  npcName!.toUpperCase(),
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textTertiary,
                    letterSpacing: 0.5,
                  ),
                ),
                SizedBox(height: AppDimensions.spaceXS),
              ],
              
              // Message text
              Text(
                message.text,
                style: TextStyle(
                  fontSize: 14,
                  color: message.isPlayer
                      ? AppColors.bgPrimary
                      : AppColors.textPrimary,
                  height: 1.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
