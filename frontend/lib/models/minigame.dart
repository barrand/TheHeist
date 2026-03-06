/// Minigame difficulty levels
enum MinigameDifficulty {
  easy,
  medium,
  hard;
  
  String get displayName {
    switch (this) {
      case MinigameDifficulty.easy:
        return 'Easy';
      case MinigameDifficulty.medium:
        return 'Medium';
      case MinigameDifficulty.hard:
        return 'Hard';
    }
  }
}

/// Minigame metadata (display only — use MinigameRegistry.isImplemented to check playability)
class MinigameInfo {
  final String id;
  final String name;
  final String description;
  final String roleId;

  const MinigameInfo({
    required this.id,
    required this.name,
    required this.description,
    required this.roleId,
  });
}

/// Role with associated minigames
class RoleMinigames {
  final String roleId;
  final String name;
  final List<MinigameInfo> minigames;

  const RoleMinigames({
    required this.roleId,
    required this.name,
    required this.minigames,
  });
}
