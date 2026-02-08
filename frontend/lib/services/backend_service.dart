import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/npc.dart';

/// Service for communicating with The Heist Python backend
/// 
/// Architecture:
/// Flutter UI -> BackendService -> Python FastAPI -> Gemini API
class BackendService {
  static final BackendService _instance = BackendService._internal();
  factory BackendService() => _instance;
  
  BackendService._internal();
  
  String _baseUrl = 'http://localhost:8000';
  
  void setBaseUrl(String url) {
    _baseUrl = url;
    print('🔧 BackendService: Base URL set to $_baseUrl');
  }

  // ============================================================
  // New conversation system
  // ============================================================

  /// Start a conversation with an NPC by choosing a cover story
  Future<StartConversationResult> startConversation({
    required String npcId,
    required String coverId,
    required String roomCode,
    required String playerId,
    List<String> targetOutcomes = const [],
  }) async {
    print('💬 BackendService: Starting conversation with $npcId as $coverId (outcomes: $targetOutcomes)');
    
    try {
      final url = Uri.parse('$_baseUrl/api/npc/start-conversation');
      
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'npc_id': npcId,
          'cover_id': coverId,
          'room_code': roomCode,
          'player_id': playerId,
          'target_outcomes': targetOutcomes,
        }),
      );
      
      print('💬 BackendService: Start conversation status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return StartConversationResult.fromJson(data);
      } else if (response.statusCode == 429) {
        // Cooldown
        throw CooldownException(response.body);
      } else {
        throw Exception('Backend returned ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      if (e is CooldownException) rethrow;
      print('❌ BackendService: Start conversation error: $e');
      rethrow;
    }
  }

  /// Send a chosen quick response in an active conversation
  Future<ConversationTurnResult> sendConversationChoice({
    required int responseIndex,
    required String roomCode,
    required String playerId,
    required String npcId,
  }) async {
    print('💬 BackendService: Sending choice $responseIndex to $npcId');
    
    try {
      final url = Uri.parse('$_baseUrl/api/npc/chat');
      
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'response_index': responseIndex,
          'room_code': roomCode,
          'player_id': playerId,
          'npc_id': npcId,
        }),
      );
      
      print('💬 BackendService: Chat status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ConversationTurnResult.fromJson(data);
      } else {
        throw Exception('Backend returned ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      print('❌ BackendService: Chat error: $e');
      rethrow;
    }
  }

  /// Check cooldown status for a player-NPC pair
  Future<CooldownStatus> checkCooldown({
    required String npcId,
    required String roomCode,
    required String playerId,
  }) async {
    try {
      final url = Uri.parse(
        '$_baseUrl/api/npc/cooldown-status/$npcId?room_code=$roomCode&player_id=$playerId'
      );
      
      final response = await http.get(url);
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return CooldownStatus(
          inCooldown: data['in_cooldown'] ?? false,
          remainingSeconds: data['cooldown_remaining_seconds'],
        );
      }
      return CooldownStatus(inCooldown: false);
    } catch (e) {
      return CooldownStatus(inCooldown: false);
    }
  }

  // ============================================================
  // Legacy endpoints (kept for backward compatibility)
  // ============================================================

  /// Get NPC response to player message (legacy)
  Future<NPCResponse> getNPCResponse({
    required NPC npc,
    required List<Objective> objectives,
    required String playerMessage,
    required List<ChatMessage> conversationHistory,
    String difficulty = 'medium',
  }) async {
    try {
      final url = Uri.parse('$_baseUrl/api/npc/legacy/chat');
      
      final requestBody = {
        'npc': {
          'id': npc.id,
          'name': npc.name,
          'role': npc.role,
          'personality': npc.personality,
          'location': npc.location,
        },
        'objectives': objectives.map((obj) => {
          'id': obj.id,
          'description': obj.description,
          'confidence': obj.confidence.name,
          'is_completed': obj.isCompleted,
        }).toList(),
        'player_message': playerMessage,
        'conversation_history': conversationHistory.map((msg) => {
          'text': msg.text,
          'isPlayer': msg.isPlayer,
          'timestamp': msg.timestamp.toIso8601String(),
        }).toList(),
        'difficulty': difficulty,
      };
      
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestBody),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return NPCResponse(
          text: data['text'] as String,
          revealedObjectives: (data['revealed_objectives'] as List<dynamic>)
              .map((e) => e.toString())
              .toList(),
        );
      } else {
        throw Exception('Backend returned ${response.statusCode}');
      }
    } catch (e) {
      return NPCResponse(
        text: 'Sorry, I\'m having trouble hearing you right now.',
        revealedObjectives: [],
      );
    }
  }
  
  /// Generate quick response suggestions (legacy)
  Future<List<String>> generateQuickResponses({
    required NPC npc,
    required List<Objective> objectives,
    required List<ChatMessage> conversationHistory,
  }) async {
    try {
      final url = Uri.parse('$_baseUrl/api/npc/legacy/quick-responses');
      
      final requestBody = {
        'npc': {
          'id': npc.id,
          'name': npc.name,
          'role': npc.role,
          'personality': npc.personality,
          'location': npc.location,
        },
        'objectives': objectives.map((obj) => {
          'id': obj.id,
          'description': obj.description,
          'confidence': obj.confidence.name,
          'is_completed': obj.isCompleted,
        }).toList(),
        'conversation_history': conversationHistory.map((msg) => {
          'text': msg.text,
          'isPlayer': msg.isPlayer,
          'timestamp': msg.timestamp.toIso8601String(),
        }).toList(),
      };
      
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestBody),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return (data['responses'] as List<dynamic>)
            .map((e) => e.toString())
            .toList();
      }
      return _getFallbackResponses();
    } catch (e) {
      return _getFallbackResponses();
    }
  }
  
  List<String> _getFallbackResponses() {
    return [
      'Tell me more about your work here.',
      'Have you noticed anything unusual?',
      'How long have you been in this position?',
    ];
  }
  
  /// Check if backend is available
  Future<bool> checkHealth() async {
    try {
      final url = Uri.parse('$_baseUrl/health');
      final response = await http.get(url).timeout(
        const Duration(seconds: 5),
      );
      return response.statusCode == 200;
    } catch (e) {
      print('⚠️ BackendService: Health check failed: $e');
      return false;
    }
  }
}

// ============================================================
// Result models
// ============================================================

class StartConversationResult {
  final String greeting;
  final List<QuickResponseOption> quickResponses;
  final int suspicion;
  final String npcName;
  final String npcRole;
  final String coverLabel;
  final List<Map<String, dynamic>> infoObjectives;
  final List<Map<String, dynamic>> actionObjectives;

  StartConversationResult({
    required this.greeting,
    required this.quickResponses,
    required this.suspicion,
    required this.npcName,
    required this.npcRole,
    required this.coverLabel,
    this.infoObjectives = const [],
    this.actionObjectives = const [],
  });

  factory StartConversationResult.fromJson(Map<String, dynamic> json) {
    return StartConversationResult(
      greeting: json['greeting'] ?? '',
      quickResponses: (json['quick_responses'] as List<dynamic>? ?? [])
          .map((e) => QuickResponseOption.fromJson(e as Map<String, dynamic>))
          .toList(),
      suspicion: json['suspicion'] ?? 0,
      npcName: json['npc_name'] ?? '',
      npcRole: json['npc_role'] ?? '',
      coverLabel: json['cover_label'] ?? '',
      infoObjectives: List<Map<String, dynamic>>.from(json['info_objectives'] ?? []),
      actionObjectives: List<Map<String, dynamic>>.from(json['action_objectives'] ?? []),
    );
  }
}

class ConversationTurnResult {
  final String npcResponse;
  final List<String> outcomes;
  final int suspicion;
  final int suspicionDelta;
  final List<QuickResponseOption> quickResponses;
  final bool conversationFailed;
  final double? cooldownUntil;
  final List<String> completedTasks;

  ConversationTurnResult({
    required this.npcResponse,
    required this.outcomes,
    required this.suspicion,
    required this.suspicionDelta,
    required this.quickResponses,
    required this.conversationFailed,
    this.cooldownUntil,
    this.completedTasks = const [],
  });

  factory ConversationTurnResult.fromJson(Map<String, dynamic> json) {
    return ConversationTurnResult(
      npcResponse: json['npc_response'] ?? '',
      outcomes: List<String>.from(json['outcomes'] ?? []),
      suspicion: json['suspicion'] ?? 0,
      suspicionDelta: json['suspicion_delta'] ?? 0,
      quickResponses: (json['quick_responses'] as List<dynamic>? ?? [])
          .map((e) => QuickResponseOption.fromJson(e as Map<String, dynamic>))
          .toList(),
      conversationFailed: json['conversation_failed'] ?? false,
      cooldownUntil: json['cooldown_until']?.toDouble(),
      completedTasks: List<String>.from(json['completed_tasks'] ?? []),
    );
  }
}

class CooldownStatus {
  final bool inCooldown;
  final int? remainingSeconds;

  CooldownStatus({required this.inCooldown, this.remainingSeconds});
}

class CooldownException implements Exception {
  final String message;
  CooldownException(this.message);
  @override
  String toString() => message;
}

/// Response from NPC (legacy)
class NPCResponse {
  final String text;
  final List<String> revealedObjectives;
  
  NPCResponse({
    required this.text,
    required this.revealedObjectives,
  });
}
