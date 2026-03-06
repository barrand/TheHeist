import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';

/// Wrapper screen that hosts a minigame widget with an app bar and back button.
///
/// Used in two contexts:
///   - Prototype / hub (standalone): [canPop] defaults to true, back button works freely.
///   - In-game: pass [canPop] = false to prevent accidentally dismissing the win screen
///     before the player has tapped "Complete Task". The minigame widget itself also
///     uses [PopScope] on its win state for the same reason.
class MinigameScreen extends StatelessWidget {
  final String title;
  final Widget child;

  const MinigameScreen({
    super.key,
    required this.title,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        backgroundColor: AppColors.bgSecondary,
        title: Text(title),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: child,
    );
  }
}
