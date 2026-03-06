import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/screens/minigames/minigame_hub_screen.dart';

void main() {
  runApp(const MinigamePrototypeApp());
}

class MinigamePrototypeApp extends StatelessWidget {
  const MinigamePrototypeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Minigame Prototypes',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: AppColors.bgPrimary,
        primaryColor: AppColors.bgSecondary,
      ),
      home: const MinigameHubScreen(),
    );
  }
}
