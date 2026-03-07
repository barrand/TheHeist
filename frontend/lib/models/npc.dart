/// NPC (Non-Player Character) model
class NPC {
  final String id;
  final String name;
  final String role;
  final String? imageUrl;
  final String personality;
  final String location;
  final List<CoverOption> coverOptions;

  const NPC({
    required this.id,
    required this.name,
    required this.role,
    this.imageUrl,
    required this.personality,
    required this.location,
    this.coverOptions = const [],
  });
}

/// Cover story option for NPC conversation
class CoverOption {
  final String coverId;
  final String description;

  const CoverOption({
    required this.coverId,
    required this.description,
  });

  factory CoverOption.fromJson(Map<String, dynamic> json) {
    return CoverOption(
      coverId: json['cover_id'] ?? '',
      description: json['description'] ?? '',
    );
  }
}

/// Quick response option with rapport delta
class QuickResponseOption {
  final String text;
  final int fitScore;
  final bool isWildcard;

  const QuickResponseOption({
    required this.text,
    required this.fitScore,
    this.isWildcard = false,
  });

  factory QuickResponseOption.fromJson(Map<String, dynamic> json) {
    return QuickResponseOption(
      text: json['text'] ?? '',
      fitScore: json['fit_score'] ?? 0,
      isWildcard: json['is_wildcard'] ?? false,
    );
  }
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
  final bool isOpening;

  const ChatMessage({
    required this.id,
    required this.text,
    required this.isPlayer,
    required this.timestamp,
    this.isOpening = false,
  });
}
