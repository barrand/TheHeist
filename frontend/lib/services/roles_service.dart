import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;
import 'package:the_heist/models/role.dart';

/// Service for loading and managing heist roles
class RolesService {
  static List<Role>? _cachedRoles;

  /// Load all roles from roles.json
  static Future<List<Role>> loadRoles() async {
    if (_cachedRoles != null) {
      return _cachedRoles!;
    }

    try {
      final String jsonString =
          await rootBundle.loadString('assets/data/roles.json');
      final Map<String, dynamic> jsonData = json.decode(jsonString);
      final List<dynamic> rolesJson = jsonData['roles'] as List<dynamic>;

      _cachedRoles = rolesJson
          .map((json) => Role.fromJson(json as Map<String, dynamic>))
          .toList();

      return _cachedRoles!;
    } catch (e) {
      print('Error loading roles.json: $e');
      return [];
    }
  }

  /// Get a specific role by ID
  static Future<Role?> getRole(String roleId) async {
    final roles = await loadRoles();
    try {
      return roles.firstWhere((role) => role.roleId == roleId);
    } catch (e) {
      return null;
    }
  }

  /// Clear cache (useful for testing)
  static void clearCache() {
    _cachedRoles = null;
  }
}
