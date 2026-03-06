import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/minigame_registry.dart';
import 'package:the_heist/screens/minigames/minigame_screen.dart';

/// Hub screen showing all minigames organized by role.
/// Used in both the standalone prototype app and the in-app debug menu.
class MinigameHubScreen extends StatefulWidget {
  const MinigameHubScreen({super.key});

  @override
  State<MinigameHubScreen> createState() => _MinigameHubScreenState();
}

class _MinigameHubScreenState extends State<MinigameHubScreen> {
  MinigameDifficulty _selectedDifficulty = MinigameDifficulty.medium;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        backgroundColor: AppColors.bgSecondary,
        title: const Text('Minigame Hub'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Column(
          children: [
            _buildDifficultySelector(),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: MinigameRegistry.allByRole.length,
                itemBuilder: (context, index) =>
                    _buildRoleSection(context, MinigameRegistry.allByRole[index]),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDifficultySelector() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        color: AppColors.bgSecondary,
        border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
      ),
      child: Column(
        children: [
          const Text(
            'Difficulty',
            style: TextStyle(
              color: AppColors.textSecondary,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: MinigameDifficulty.values.map((diff) {
              final isSelected = _selectedDifficulty == diff;
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: GestureDetector(
                  onTap: () => setState(() => _selectedDifficulty = diff),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                    decoration: BoxDecoration(
                      color: isSelected ? AppColors.accentPrimary : Colors.transparent,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: isSelected ? AppColors.accentPrimary : AppColors.borderSubtle,
                        width: 1.5,
                      ),
                    ),
                    child: Text(
                      diff.displayName,
                      style: TextStyle(
                        color: isSelected ? AppColors.bgPrimary : AppColors.textSecondary,
                        fontSize: 14,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildRoleSection(BuildContext context, RoleMinigames role) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 4),
          child: Text(
            role.name.toUpperCase(),
            style: const TextStyle(
              color: AppColors.accentPrimary,
              fontSize: 13,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.0,
            ),
          ),
        ),
        ...role.minigames.map((minigame) => _buildMinigameRow(context, minigame)),
        const SizedBox(height: 12),
      ],
    );
  }

  Widget _buildMinigameRow(BuildContext context, MinigameInfo minigame) {
    final implemented = MinigameRegistry.isImplemented(minigame.id);

    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: GestureDetector(
        onTap: implemented
            ? () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => MinigameScreen(
                      title: minigame.name,
                      child: MinigameRegistry.build(minigame.id, _selectedDifficulty),
                    ),
                  ),
                );
              }
            : null,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: implemented
                ? AppColors.bgSecondary
                : AppColors.bgSecondary.withOpacity(0.3),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: implemented
                  ? AppColors.borderSubtle
                  : AppColors.borderSubtle.withOpacity(0.3),
              width: 1,
            ),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      minigame.name,
                      style: TextStyle(
                        color: implemented
                            ? AppColors.textPrimary
                            : AppColors.textSecondary.withOpacity(0.5),
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      minigame.description,
                      style: TextStyle(
                        color: implemented
                            ? AppColors.textSecondary
                            : AppColors.textSecondary.withOpacity(0.4),
                        fontSize: 11,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              if (implemented)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    color: AppColors.success.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: AppColors.success, width: 1),
                  ),
                  child: const Text(
                    '✓',
                    style: TextStyle(
                      color: AppColors.success,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                )
              else
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'TODO',
                    style: TextStyle(
                      color: AppColors.textSecondary.withOpacity(0.5),
                      fontSize: 9,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
