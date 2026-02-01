import 'package:google_generative_ai/google_generative_ai.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/npc.dart';

/// Service for interacting with Google Gemini API
class GeminiService {
  late final GenerativeModel _model;
  late final GenerativeModel _chatModel;
  
  static final GeminiService _instance = GeminiService._internal();
  factory GeminiService() => _instance;
  
  GeminiService._internal();
  
  /// Initialize the service with API key (directly or from environment)
  Future<void> initialize({String? apiKey}) async {
    String? key = apiKey;
    
    print('🔧 GeminiService: Initializing...');
    
    // If no API key provided, try loading from .env
    if (key == null || key.isEmpty) {
      try {
        await dotenv.load(fileName: ".env");
        key = dotenv.env['GEMINI_API_KEY'];
        print('🔧 GeminiService: Loaded API key from .env');
      } catch (e) {
        // .env might not exist in web build, that's okay
        print('⚠️ GeminiService: Could not load .env: $e');
      }
    } else {
      print('🔧 GeminiService: Using provided API key');
    }
    
    if (key == null || key.isEmpty) {
      throw Exception('API key required. Please provide in settings.');
    }
    
    print('🔧 GeminiService: API key present (${key.substring(0, 10)}...)');
    
    // Model for chat interactions
    // Use gemini-pro which IS available in v1beta API
    try {
      print('🔧 GeminiService: Creating model with gemini-pro (v1beta compatible)');
      _chatModel = GenerativeModel(
        model: 'gemini-pro',
        apiKey: key,
        generationConfig: GenerationConfig(
          temperature: 0.7,
          maxOutputTokens: 200,
        ),
      );
      
      _model = GenerativeModel(
        model: 'gemini-pro',
        apiKey: key,
      );
      
      print('✅ GeminiService: Models initialized with gemini-pro');
    } catch (e) {
      print('❌ GeminiService: Error creating models: $e');
      rethrow;
    }
  }
  
  /// Generate quick response suggestions based on conversation context
  Future<List<String>> generateQuickResponses({
    required NPC npc,
    required List<Objective> objectives,
    required List<ChatMessage> conversationHistory,
  }) async {
    final prompt = '''
You are generating 3 quick response options for a player talking to an NPC in a heist game.

NPC: ${npc.name} - ${npc.role}
Personality: ${npc.personality}

Objectives the player is trying to learn:
${objectives.where((o) => !o.isCompleted).map((o) => '- ${o.description}').join('\n')}

Recent conversation:
${conversationHistory.takeLast(4).map((m) => '${m.isPlayer ? "Player" : npc.name}: ${m.text}').join('\n')}

Generate 3 SHORT response options (max 10 words each):
1. A safe, friendly option
2. A direct question about one objective
3. A creative/indirect approach

Output ONLY the 3 responses, one per line, no numbers or labels.
''';

    try {
      final response = await _chatModel.generateContent([Content.text(prompt)]);
      final text = response.text ?? '';
      return text.split('\n').where((line) => line.trim().isNotEmpty).take(3).toList();
    } catch (e) {
      print('Error generating quick responses: $e');
      return [
        'Tell me more about your work here.',
        'Have you noticed anything unusual?',
        'How long have you been in this position?',
      ];
    }
  }
  
  /// Get NPC response using direct REST API (bypassing package wrapper)
  Future<NPCResponse> getNPCResponseViaREST({
    required NPC npc,
    required List<Objective> objectives,
    required String playerMessage,
    required List<ChatMessage> conversationHistory,
    required String apiKey,
    String difficulty = 'medium',
  }) async {
    print('💬 GeminiService: Getting NPC response via REST API for: "$playerMessage"');
    
    final systemPrompt = '''
You are ${npc.name}, a ${npc.role}.
Personality: ${npc.personality}
Location: ${npc.location}

The player is a member of a heist crew trying to gather information from you.

Information you know (and can share if asked properly):
${objectives.map((o) {
      if (o.confidence == ConfidenceLevel.high) {
        return '- ${o.description} (you definitely know this)';
      } else if (o.confidence == ConfidenceLevel.medium) {
        return '- ${o.description} (you might know this)';
      } else {
        return null;
      }
    }).where((s) => s != null).join('\n')}

Difficulty: $difficulty
${_getDifficultyInstructions(difficulty)}

IMPORTANT: 
- Stay in character at all times
- Be natural and conversational
- Share information gradually, not all at once
- If they ask about something you don't know, you genuinely don't know
- Keep responses under 3 sentences
- Don't be too obvious about having "quest information"

Player says: "$playerMessage"

Respond naturally as ${npc.name}:
''';

    try {
      // Make direct REST API call to Gemini (using v1beta which has gemini-1.5-flash)
      final url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$apiKey';
      
      print('💬 GeminiService: Calling Gemini REST API (v1beta/gemini-1.5-flash)...');
      
      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'contents': [{
            'parts': [{'text': systemPrompt}]
          }],
          'generationConfig': {
            'temperature': 0.7,
            'maxOutputTokens': 200,
          }
        }),
      );
      
      print('💬 GeminiService: Got response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final npcText = data['candidates']?[0]?['content']?['parts']?[0]?['text'] ?? 'Sorry, I didn\'t catch that.';
        
        print('💬 GeminiService: Response text: "$npcText"');
        
        // Check if any objectives were revealed
        final revealedObjectives = _detectRevealedObjectives(npcText, objectives);
        print('💬 GeminiService: Revealed objectives: $revealedObjectives');
        
        return NPCResponse(
          text: npcText,
          revealedObjectives: revealedObjectives,
        );
      } else {
        print('❌ GeminiService: REST API error: ${response.statusCode} - ${response.body}');
        return NPCResponse(
          text: 'Sorry, I didn\'t catch that. Could you repeat?',
          revealedObjectives: [],
        );
      }
    } catch (e, stackTrace) {
      print('❌ GeminiService: ERROR calling REST API: $e');
      print('❌ GeminiService: Stack trace: $stackTrace');
      return NPCResponse(
        text: 'Sorry, I didn\'t catch that. Could you repeat?',
        revealedObjectives: [],
      );
    }
  }

  /// Get NPC response to player message (OLD METHOD - DEPRECATED)
  Future<NPCResponse> getNPCResponse({
    required NPC npc,
    required List<Objective> objectives,
    required String playerMessage,
    required List<ChatMessage> conversationHistory,
    String difficulty = 'medium',
  }) async {
    print('💬 GeminiService: Getting NPC response for: "$playerMessage"');
    
    final systemPrompt = '''
You are ${npc.name}, a ${npc.role}.
Personality: ${npc.personality}
Location: ${npc.location}

The player is a member of a heist crew trying to gather information from you.

Information you know (and can share if asked properly):
${objectives.map((o) {
      if (o.confidence == ConfidenceLevel.high) {
        return '- ${o.description} (you definitely know this)';
      } else if (o.confidence == ConfidenceLevel.medium) {
        return '- ${o.description} (you might know this)';
      } else {
        return null;
      }
    }).where((s) => s != null).join('\n')}

Difficulty: $difficulty
${_getDifficultyInstructions(difficulty)}

IMPORTANT: 
- Stay in character at all times
- Be natural and conversational
- Share information gradually, not all at once
- If they ask about something you don't know, you genuinely don't know
- Keep responses under 3 sentences
- Don't be too obvious about having "quest information"

Respond naturally to their question.
''';

    try {
      print('💬 GeminiService: Creating chat with ${conversationHistory.length} history messages');
      
      final chat = _chatModel.startChat(
        history: conversationHistory.take(conversationHistory.length - 1).map((msg) {
          return Content.text(msg.text);
        }).toList(),
      );
      
      print('💬 GeminiService: Sending message to Gemini...');
      final response = await chat.sendMessage(Content.text('$systemPrompt\n\nPlayer: $playerMessage\n\nRespond as ${npc.name}:'));
      print('💬 GeminiService: Got response from Gemini');
      
      final npcText = response.text ?? 'I\'m not sure what to say to that.';
      print('💬 GeminiService: Response text: "$npcText"');
      
      // Check if any objectives were revealed
      final revealedObjectives = _detectRevealedObjectives(npcText, objectives);
      print('💬 GeminiService: Revealed objectives: $revealedObjectives');
      
      return NPCResponse(
        text: npcText,
        revealedObjectives: revealedObjectives,
      );
    } catch (e, stackTrace) {
      print('❌ GeminiService: ERROR getting NPC response: $e');
      print('❌ GeminiService: Stack trace: $stackTrace');
      return NPCResponse(
        text: 'Sorry, I didn\'t catch that. Could you repeat?',
        revealedObjectives: [],
      );
    }
  }
  
  String _getDifficultyInstructions(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return '''
- Be helpful and forthcoming
- Share information after 1-2 questions
- Give clear hints if they're on the right track
''';
      case 'hard':
        return '''
- Be cautious and suspicious
- Require significant rapport building
- Only share information if they ask the perfect question
- May lie or mislead if they're too direct
''';
      default: // medium
        return '''
- Be realistic - friendly but not too forthcoming
- Share information after building some rapport
- Give subtle hints if they're getting warm
''';
    }
  }
  
  List<String> _detectRevealedObjectives(String npcText, List<Objective> objectives) {
    final revealed = <String>[];
    final lowerText = npcText.toLowerCase();
    
    for (final objective in objectives) {
      if (objective.isCompleted) continue;
      
      // Simple keyword detection - check if key words from objective appear in response
      final keywords = objective.description.toLowerCase().split(' ');
      final keywordMatches = keywords.where((k) => 
        k.length > 3 && lowerText.contains(k)
      ).length;
      
      // If multiple keywords match, likely revealed
      if (keywordMatches >= 2) {
        revealed.add(objective.id);
      }
    }
    
    return revealed;
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

extension<T> on List<T> {
  List<T> takeLast(int n) {
    if (length <= n) return this;
    return sublist(length - n);
  }
}
