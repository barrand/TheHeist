import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;
import 'package:the_heist/models/scenario.dart';

/// Service for loading and managing heist scenarios
class ScenariosService {
  static List<Scenario>? _cachedScenarios;

  /// Load all scenarios from scenarios.json
  static Future<List<Scenario>> loadScenarios() async {
    if (_cachedScenarios != null) {
      return _cachedScenarios!;
    }

    try {
      final String jsonString =
          await rootBundle.loadString('assets/data/scenarios.json');
      final Map<String, dynamic> jsonData = json.decode(jsonString);
      final List<dynamic> scenariosJson = jsonData['scenarios'] as List<dynamic>;

      _cachedScenarios = scenariosJson
          .map((json) => Scenario.fromJson(json as Map<String, dynamic>))
          .toList();

      return _cachedScenarios!;
    } catch (e) {
      print('Error loading scenarios.json: $e');
      return [];
    }
  }

  /// Get a specific scenario by ID
  static Future<Scenario?> getScenario(String scenarioId) async {
    final scenarios = await loadScenarios();
    try {
      return scenarios.firstWhere((scenario) => scenario.scenarioId == scenarioId);
    } catch (e) {
      return null;
    }
  }

  /// Clear cache (useful for testing)
  static void clearCache() {
    _cachedScenarios = null;
  }
}
