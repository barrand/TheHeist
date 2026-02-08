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

/// Minigame metadata
class MinigameInfo {
  final String id;
  final String name;
  final String description;
  final String roleId;
  final bool isImplemented;

  const MinigameInfo({
    required this.id,
    required this.name,
    required this.description,
    required this.roleId,
    this.isImplemented = false,
  });
}

/// Role with minigames
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
