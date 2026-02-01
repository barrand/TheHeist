import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_dimensions.dart';
import '../widgets/common/heist_primary_button.dart';
import '../widgets/common/heist_secondary_button.dart';
import 'npc_test_screen.dart';

/// Landing Page - First screen of the app
/// Users can create a new room or join an existing one
class LandingPage extends StatelessWidget {
  const LandingPage({Key? key}) : super(key: key);

  void _onCreateRoom(BuildContext context) {
    // TODO: Navigate to Room Lobby as host
    print('Create Room tapped');
  }

  void _onJoinRoom(BuildContext context) {
    // TODO: Show Join Room modal
    print('Join Room tapped');
  }

  void _onTestNPC(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => NPCTestScreen()),
    );
  }

  void _onHowToPlay(BuildContext context) {
    // TODO: Show How to Play modal
    print('How to Play tapped');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      body: SafeArea(
        child: Container(
          constraints: BoxConstraints(
            maxWidth: AppDimensions.maxWidthMobile,
          ),
          margin: EdgeInsets.symmetric(
            horizontal: AppDimensions.containerPadding,
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Spacer(flex: 2),
              
              // App Title
              Text(
                'THE HEIST 🎭',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                  letterSpacing: 2,
                ),
              ),
              
              SizedBox(height: AppDimensions.spaceMD),
              
              // Tagline
              Text(
                'Collaborative Heist Game',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  color: AppColors.textSecondary,
                  letterSpacing: 0.5,
                ),
              ),
              
              SizedBox(height: AppDimensions.space3XL),
              
              // Create Room Button
              HeistPrimaryButton(
                text: 'CREATE ROOM',
                icon: Icons.add_circle_outline,
                onPressed: () => _onCreateRoom(context),
              ),
              
              SizedBox(height: AppDimensions.spaceLG),
              
              // Join Room Button
              HeistSecondaryButton(
                text: 'JOIN ROOM',
                icon: Icons.login,
                onPressed: () => _onJoinRoom(context),
              ),
              
              SizedBox(height: AppDimensions.spaceLG),
              
              // Test NPC Button (for development)
              HeistSecondaryButton(
                text: 'TEST NPC CONVERSATION',
                icon: Icons.chat_bubble_outline,
                onPressed: () => _onTestNPC(context),
              ),
              
              Spacer(flex: 3),
              
              // How to Play Link
              TextButton(
                onPressed: () => _onHowToPlay(context),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'How to Play',
                      style: TextStyle(
                        color: AppColors.textSecondary,
                        fontSize: 14,
                      ),
                    ),
                    SizedBox(width: AppDimensions.spaceXS),
                    Icon(
                      Icons.info_outline,
                      color: AppColors.textSecondary,
                      size: AppDimensions.iconMD,
                    ),
                  ],
                ),
              ),
              
              SizedBox(height: AppDimensions.spaceSM),
              
              // Version number
              Text(
                'v0.1.0',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 10,
                  color: AppColors.textTertiary,
                ),
              ),
              
              SizedBox(height: AppDimensions.spaceLG),
            ],
          ),
        ),
      ),
    );
  }
}
