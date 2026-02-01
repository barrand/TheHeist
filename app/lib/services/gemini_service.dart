import 'package:google_generative_ai/google_generative_ai.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../models/npc.dart';

/// Service for interacting with Google Gemini API
class GeminiService {
  late final GenerativeModel _model;
  late final GenerativeModel _chatModel;
  
  static final GeminiService _instance = GeminiService._internal();
  factory GeminiService() => _instance;
  
  GeminiService._internal();
  
  /// Initialize the service with API key from environment
  Future<void> initialize() async {
    await dotenv.load(fileName: ".env");
    final apiKey = dotenv.env['GEMINI_API_KEY'];
    
    if (apiKey == null || apiKey.isEmpty) {
      throw Exception('GEMINI_API_KEY not found in .env file');
    }
    
    // Model for chat interactions (fast and cheap)
    // Use model name without "models/" prefix - package adds it automatically
    _chatModel = GenerativeModel(
      model: 'gemini-pro',
      apiKey: apiKey,
    );
    
    // Model for content generation (same for now)
    _model = GenerativeModel(
      model: 'gemini-pro',
      apiKey: apiKey,
    );
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
  
  /// Get NPC response to player message
  Future<NPCResponse> getNPCResponse({
    required NPC npc,
    required List<Objective> objectives,
    required String playerMessage,
    required List<ChatMessage> conversationHistory,
    String difficulty = 'medium',
  }) async {
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
      final chat = _chatModel.startChat(
        history: conversationHistory.take(conversationHistory.length - 1).map((msg) {
          return Content.text(msg.text);
        }).toList(),
      );
      
      final response = await chat.sendMessage(Content.text(playerMessage));
      final npcText = response.text ?? 'I\'m not sure what to say to that.';
      
      // Check if any objectives were revealed
      final revealedObjectives = _detectRevealedObjectives(npcText, objectives);
      
      return NPCResponse(
        text: npcText,
        revealedObjectives: revealedObjectives,
      );
    } catch (e) {
      print('Error getting NPC response: $e');
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
