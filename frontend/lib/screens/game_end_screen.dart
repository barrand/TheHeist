import 'dart:math';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';
import 'package:the_heist/widgets/common/heist_primary_button.dart';
import 'package:the_heist/widgets/common/heist_secondary_button.dart';

/// Game end screen showing heist completion with crew celebration
class GameEndScreen extends StatelessWidget {
  final bool success;
  final String? summary;
  final String scenario;
  final String objective;
  final List<Map<String, dynamic>>? players;
  final VoidCallback onReturnToMenu;
  final VoidCallback? onPlayAgain;
  
  // Random image selection - pick one of 9 celebration images
  static final int _randomImageNumber = Random().nextInt(9) + 1; // 1-9
  
  const GameEndScreen({
    super.key,
    required this.success,
    this.summary,
    required this.scenario,
    required this.objective,
    this.players,
    required this.onReturnToMenu,
    this.onPlayAgain,
  });
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: EdgeInsets.all(AppDimensions.containerPadding),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Crew celebration/failure image
                _buildCrewImage(),
                
                SizedBox(height: AppDimensions.spaceLG),
                
                // Success/Failure headline
                _buildHeadline(),
                
                SizedBox(height: AppDimensions.spaceMD),
                
                // Flavor text
                _buildFlavorText(),
                
                SizedBox(height: AppDimensions.spaceXL),
                
                // Story section
                if (success) _buildStorySection(),
                
                // What went wrong section (failure only)
                if (!success && summary != null) _buildFailureReason(),
                
                SizedBox(height: AppDimensions.spaceLG),
                
                // The Crew section
                _buildCrewSection(),
                
                SizedBox(height: AppDimensions.spaceXL),
                
                // Action buttons
                _buildActionButtons(),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildCrewImage() {
    // Only show image for success - failure uses icon fallback
    if (!success) {
      return Container(
        height: 200,
        decoration: BoxDecoration(
          color: AppColors.bgSecondary,
          borderRadius: BorderRadius.circular(AppDimensions.borderRadiusLG),
          border: Border.all(
            color: AppColors.danger,
            width: 2,
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.warning_amber,
                size: 80,
                color: AppColors.danger.withValues(alpha: 0.5),
              ),
              SizedBox(height: AppDimensions.spaceSM),
              Text(
                '🚨 BUSTED 🚨',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: AppColors.danger,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }
    
    // Randomly select one of the 9 celebration images
    final imagePath = 'assets/static/crew_celebration_success_$_randomImageNumber.png';
    
    return Container(
      height: 200,
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.borderRadiusLG),
        border: Border.all(
          color: AppColors.success,
          width: 2,
        ),
      ),
      clipBehavior: Clip.antiAlias,
      child: Image.asset(
        imagePath,
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) {
          // Fallback to placeholder if image not found
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.celebration,
                  size: 60,
                  color: AppColors.success.withValues(alpha: 0.3),
                ),
                SizedBox(height: AppDimensions.spaceSM),
                Text(
                  '🎉 THE CREW CELEBRATES 🎉',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppColors.success,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          );
        },
      ),
    );
  }
  
  Widget _buildHeadline() {
    return Text(
      success ? '🎉 HEIST COMPLETE! 🎉' : '❌ HEIST FAILED ❌',
      style: TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.bold,
        color: success ? AppColors.success : AppColors.danger,
      ),
      textAlign: TextAlign.center,
    );
  }
  
  Widget _buildFlavorText() {
    final successMessages = [
      "Another job well done for the crew. The prize is yours, and the city will never know what hit them.",
      "Clean getaway, no traces left behind. The crew strikes again.",
      "Perfect execution. Prize secured, and not a single alarm tripped.",
      "They'll be talking about this heist for years. Well done, crew.",
      "In and out, just like the plan. The crew doesn't miss.",
    ];
    
    final failureMessages = [
      "The crew got sloppy. The guards were tipped off and the heist fell apart.",
      "Sirens in the distance. Time to scatter. Better luck next time, crew.",
      "The plan fell apart. Sometimes even the best crews make mistakes.",
      "Busted. The crew will have to lay low for a while.",
      "Not every heist goes as planned. Regroup and try again.",
    ];
    
    final messages = success ? successMessages : failureMessages;
    // Use hash of scenario for consistent but "random" selection
    final messageIndex = scenario.hashCode.abs() % messages.length;
    
    return Container(
      padding: EdgeInsets.all(AppDimensions.spaceMD),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.borderRadiusMD),
        border: Border.all(
          color: success 
              ? AppColors.success.withValues(alpha: 0.3)
              : AppColors.danger.withValues(alpha: 0.3),
        ),
      ),
      child: Text(
        messages[messageIndex],
        style: const TextStyle(
          fontSize: 16,
          color: AppColors.textPrimary,
          fontStyle: FontStyle.italic,
          height: 1.5,
        ),
        textAlign: TextAlign.center,
      ),
    );
  }
  
  Widget _buildStorySection() {
    return Container(
      padding: EdgeInsets.all(AppDimensions.spaceMD),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.borderRadiusMD),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.auto_stories,
                color: AppColors.accentPrimary,
                size: 20,
              ),
              SizedBox(width: AppDimensions.spaceSM),
              const Text(
                'THE STORY',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: AppColors.accentPrimary,
                  letterSpacing: 1.2,
                ),
              ),
            ],
          ),
          SizedBox(height: AppDimensions.spaceSM),
          Divider(color: AppColors.borderSubtle),
          SizedBox(height: AppDimensions.spaceSM),
          Text(
            _generateStoryText(),
            style: const TextStyle(
              fontSize: 14,
              color: AppColors.textSecondary,
              height: 1.6,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildFailureReason() {
    return Container(
      padding: EdgeInsets.all(AppDimensions.spaceMD),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.borderRadiusMD),
        border: Border.all(
          color: AppColors.danger.withValues(alpha: 0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.warning_amber,
                color: AppColors.danger,
                size: 20,
              ),
              SizedBox(width: AppDimensions.spaceSM),
              const Text(
                'WHAT WENT WRONG',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: AppColors.danger,
                  letterSpacing: 1.2,
                ),
              ),
            ],
          ),
          SizedBox(height: AppDimensions.spaceSM),
          Divider(color: AppColors.borderSubtle),
          SizedBox(height: AppDimensions.spaceSM),
          Text(
            summary ?? 'The heist didn\'t go as planned.',
            style: const TextStyle(
              fontSize: 14,
              color: AppColors.textSecondary,
              height: 1.6,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildCrewSection() {
    if (players == null || players!.isEmpty) {
      return const SizedBox.shrink();
    }
    
    return Container(
      padding: EdgeInsets.all(AppDimensions.spaceMD),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.borderRadiusMD),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.people,
                color: AppColors.accentPrimary,
                size: 20,
              ),
              SizedBox(width: AppDimensions.spaceSM),
              const Text(
                'THE CREW',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: AppColors.accentPrimary,
                  letterSpacing: 1.2,
                ),
              ),
            ],
          ),
          SizedBox(height: AppDimensions.spaceSM),
          Divider(color: AppColors.borderSubtle),
          SizedBox(height: AppDimensions.spaceSM),
          ...players!.map((player) {
            final name = player['name'] as String? ?? 'Unknown';
            final role = player['role'] as String? ?? 'Unknown Role';
            return Padding(
              padding: EdgeInsets.only(bottom: AppDimensions.spaceSM),
              child: Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: AppColors.accentPrimary,
                      shape: BoxShape.circle,
                    ),
                  ),
                  SizedBox(width: AppDimensions.spaceSM),
                  Expanded(
                    child: Text(
                      '$name as $role',
                      style: const TextStyle(
                        fontSize: 14,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }
  
  Widget _buildActionButtons() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        HeistPrimaryButton(
          text: 'Return to Menu',
          onPressed: onReturnToMenu,
          icon: Icons.home,
        ),
        if (onPlayAgain != null) ...[
          SizedBox(height: AppDimensions.spaceMD),
          HeistSecondaryButton(
            text: success ? 'Play Again' : 'Try Again',
            onPressed: onPlayAgain!,
            icon: Icons.replay,
          ),
        ],
      ],
    );
  }
  
  String _generateStoryText() {
    // Generate a story summary based on the objective and scenario
    // This is a simplified version - ideally would come from backend
    return 'The crew set out to complete their objective: $objective. '
        'Through careful planning, teamwork, and skillful execution, '
        'the team successfully pulled off the heist and escaped without a trace. '
        'Another perfect job for the crew.';
  }
}
