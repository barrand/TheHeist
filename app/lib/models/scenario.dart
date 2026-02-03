/// Model for heist scenarios
class Scenario {
  final String scenarioId;
  final String name;
  final String theme;
  final String objective;
  final String summary;
  final List<String> rolesRequired;
  final List<String>? locations;

  const Scenario({
    required this.scenarioId,
    required this.name,
    required this.theme,
    required this.objective,
    required this.summary,
    required this.rolesRequired,
    this.locations,
  });

  factory Scenario.fromJson(Map<String, dynamic> json) {
    return Scenario(
      scenarioId: json['scenario_id'] as String,
      name: json['name'] as String,
      theme: json['theme'] as String,
      objective: json['objective'] as String,
      summary: json['summary'] as String,
      rolesRequired: (json['roles_required'] as List<dynamic>)
          .map((role) => role as String)
          .toList(),
      locations: json['locations'] != null
          ? (json['locations'] as List<dynamic>)
              .map((loc) => loc as String)
              .toList()
          : null,
    );
  }

  /// Get emoji icon for theme
  String get themeIcon {
    switch (theme) {
      case 'museum_gala':
        return '🏛️';
      case 'mansion':
        return '🏰';
      case 'casino':
        return '🎰';
      case 'train':
        return '🚂';
      case 'research_lab':
        return '🔬';
      case 'corporate_office':
        return '🏢';
      case 'art_gallery':
        return '🖼️';
      case 'bank':
        return '🏦';
      case 'police_station':
        return '🚔';
      case 'detention_center':
        return '⛓️';
      case 'shipping_yard':
        return '🚢';
      default:
        return '🎭';
    }
  }
}
