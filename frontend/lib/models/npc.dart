/// NPC (Non-Player Character) model
class NPC {
  final String id;
  final String name;
  final String role;
  final String? imageUrl;
  final String personality;
  final String location;

  const NPC({
    required this.id,
    required this.name,
    required this.role,
    this.imageUrl,
    required this.personality,
    required this.location,
  });
}

/// Objective that the player is trying to achieve
class Objective {
  final String id;
  final String description;
  final ConfidenceLevel confidence;
  final bool isCompleted;

  const Objective({
    required this.id,
    required this.description,
    required this.confidence,
    this.isCompleted = false,
  });

  Objective copyWith({
    String? id,
    String? description,
    ConfidenceLevel? confidence,
    bool? isCompleted,
  }) {
    return Objective(
      id: id ?? this.id,
      description: description ?? this.description,
      confidence: confidence ?? this.confidence,
      isCompleted: isCompleted ?? this.isCompleted,
    );
  }
}

/// Confidence level that NPC knows the information
enum ConfidenceLevel {
  high,    // 🟢🟢🟢 - NPC likely knows this
  medium,  // 🟡🟡⚪ - NPC might know this
  low,     // 🔴⚪⚪ - NPC probably doesn't know
  action,  // 🟠🟠🟠 - Need to complete prerequisite
}

/// Chat message
class ChatMessage {
  final String id;
  final String text;
  final bool isPlayer;
  final DateTime timestamp;

  const ChatMessage({
    required this.id,
    required this.text,
    required this.isPlayer,
    required this.timestamp,
  });
}
