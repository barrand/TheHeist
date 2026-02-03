/// Model for heist roles with descriptions and minigames
class Role {
  final String roleId;
  final String name;
  final String description;
  final List<Minigame> minigames;
  final String icon; // Emoji icon for fallback

  const Role({
    required this.roleId,
    required this.name,
    required this.description,
    required this.minigames,
    required this.icon,
  });

  factory Role.fromJson(Map<String, dynamic> json) {
    return Role(
      roleId: json['role_id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      minigames: (json['minigames'] as List<dynamic>)
          .map((m) => Minigame.fromJson(m as Map<String, dynamic>))
          .toList(),
      icon: _getIconForRole(json['role_id'] as String),
    );
  }

  /// Get emoji icon for role
  static String _getIconForRole(String roleId) {
    switch (roleId) {
      case 'mastermind':
        return '🧠';
      case 'hacker':
        return '💻';
      case 'safe_cracker':
        return '🔓';
      case 'driver':
        return '🚗';
      case 'insider':
        return '🕵️';
      case 'grifter':
        return '🎭';
      case 'muscle':
        return '💪';
      case 'lookout':
        return '👀';
      case 'fence':
        return '🤝';
      case 'cat_burglar':
        return '🐱';
      case 'cleaner':
        return '🧹';
      case 'pickpocket':
        return '🤏';
      default:
        return '❓';
    }
  }
}

/// Model for role minigames
class Minigame {
  final String id;
  final String description;

  const Minigame({
    required this.id,
    required this.description,
  });

  factory Minigame.fromJson(Map<String, dynamic> json) {
    return Minigame(
      id: json['id'] as String,
      description: json['description'] as String,
    );
  }

  /// Get display name from ID (convert snake_case to Title Case)
  String get displayName {
    return id
        .split('_')
        .map((word) => word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }
}
