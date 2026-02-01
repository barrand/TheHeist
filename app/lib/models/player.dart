/// Player model representing a team member
class Player {
  final String id;
  final String name;
  final String? role;
  final bool isReady;
  final bool isHost;

  const Player({
    required this.id,
    required this.name,
    this.role,
    this.isReady = false,
    this.isHost = false,
  });

  Player copyWith({
    String? id,
    String? name,
    String? role,
    bool? isReady,
    bool? isHost,
  }) {
    return Player(
      id: id ?? this.id,
      name: name ?? this.name,
      role: role ?? this.role,
      isReady: isReady ?? this.isReady,
      isHost: isHost ?? this.isHost,
    );
  }
}
