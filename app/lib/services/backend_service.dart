import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/npc.dart';

/// Service for communicating with The Heist Python backend
/// 
/// This service handles all communication with the FastAPI backend,
/// which in turn manages interactions with Gemini AI.
/// 
/// Architecture:
/// Flutter UI -> BackendService -> Python FastAPI -> Gemini API
class BackendService {
  static final BackendService _instance = BackendService._internal();
  factory BackendService() => _instance;
  
  BackendService._internal();
  
  // Backend URL - can be configured via environment or settings
  String _baseUrl = 'http://localhost:8000';
  
  /// Set custom backend URL (useful for production deployment)
  void setBaseUrl(String url) {
    _baseUrl = url;
    print('🔧 BackendService: Base URL set to $_baseUrl');
  }
  
  /// Get NPC response to player message
  /// 
  /// Calls POST /api/npc/chat on the backend
  Future<NPCResponse> getNPCResponse({
    required NPC npc,
    required List<Objective> objectives,
    required String playerMessage,
    required List<ChatMessage> conversationHistory,
    String difficulty = 'medium',
  }) async {
    print('💬 BackendService: Getting NPC response for: "$playerMessage"');
    
    try {
      final url = Uri.parse('$_baseUrl/api/npc/chat');
      
      // Convert Flutter models to JSON for backend API
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
          'timestamp': msg.timestamp,
        }).toList(),
        'difficulty': difficulty,
      };
      
      print('💬 BackendService: Calling backend at $url');
      
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestBody),
      );
      
      print('💬 BackendService: Response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final npcText = data['text'] as String;
        final revealedObjectives = (data['revealed_objectives'] as List<dynamic>)
            .map((e) => e.toString())
            .toList();
        
        print('💬 BackendService: NPC says: "$npcText"');
        print('💬 BackendService: Revealed objectives: $revealedObjectives');
        
        return NPCResponse(
          text: npcText,
          revealedObjectives: revealedObjectives,
        );
      } else {
        print('❌ BackendService: Error ${response.statusCode}: ${response.body}');
        throw Exception('Backend returned ${response.statusCode}: ${response.body}');
      }
    } catch (e, stackTrace) {
      print('❌ BackendService: ERROR: $e');
      print('❌ BackendService: Stack trace: $stackTrace');
      
      // Return fallback response instead of throwing
      return NPCResponse(
        text: 'Sorry, I\'m having trouble hearing you right now. Could you repeat that?',
        revealedObjectives: [],
      );
    }
  }
  
  /// Generate quick response suggestions for the player
  /// 
  /// Calls POST /api/npc/quick-responses on the backend
  Future<List<String>> generateQuickResponses({
    required NPC npc,
    required List<Objective> objectives,
    required List<ChatMessage> conversationHistory,
  }) async {
    print('🎲 BackendService: Generating quick responses');
    
    try {
      final url = Uri.parse('$_baseUrl/api/npc/quick-responses');
      
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
          'timestamp': msg.timestamp,
        }).toList(),
      };
      
      print('🎲 BackendService: Calling backend at $url');
      
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestBody),
      );
      
      print('🎲 BackendService: Response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final responses = (data['responses'] as List<dynamic>)
            .map((e) => e.toString())
            .toList();
        
        print('🎲 BackendService: Got ${responses.length} quick responses');
        return responses;
      } else {
        print('❌ BackendService: Error ${response.statusCode}: ${response.body}');
        return _getFallbackResponses();
      }
    } catch (e, stackTrace) {
      print('❌ BackendService: ERROR: $e');
      print('❌ BackendService: Stack trace: $stackTrace');
      return _getFallbackResponses();
    }
  }
  
  /// Fallback responses if backend is unavailable
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

/// Response from NPC including text and revealed information
class NPCResponse {
  final String text;
  final List<String> revealedObjectives;
  
  NPCResponse({
    required this.text,
    required this.revealedObjectives,
  });
}
