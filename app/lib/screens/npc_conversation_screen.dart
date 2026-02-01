import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_dimensions.dart';
import '../models/npc.dart';
import '../services/gemini_service.dart';
import '../widgets/npc/objective_card.dart';
import '../widgets/npc/chat_bubble.dart';
import '../widgets/npc/quick_response_button.dart';
import '../widgets/common/heist_primary_button.dart';
import '../widgets/common/heist_text_field.dart';

/// NPC Conversation Screen (Screen 10)
/// Free-form conversation with NPCs using LLM
/// Hybrid interaction: Quick responses + free-form text
class NPCConversationScreen extends StatefulWidget {
  final NPC npc;
  final List<Objective> objectives;
  final String apiKey;
  final String difficulty;

  const NPCConversationScreen({
    Key? key,
    required this.npc,
    required this.objectives,
    required this.apiKey,
    this.difficulty = 'medium',
  }) : super(key: key);

  @override
  State<NPCConversationScreen> createState() => _NPCConversationScreenState();
}

class _NPCConversationScreenState extends State<NPCConversationScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final GeminiService _geminiService = GeminiService();
  
  List<ChatMessage> _messages = [];
  List<Objective> _objectives = [];
  List<String> _quickResponses = [];
  bool _showQuickResponses = true;
  bool _isLoading = false;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _objectives = List.from(widget.objectives);
    _initializeGemini();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _initializeGemini() async {
    try {
      await _geminiService.initialize(apiKey: widget.apiKey);
      setState(() {
        _isInitialized = true;
      });
      _initializeConversation();
    } catch (e) {
      print('Error initializing Gemini: $e');
      // Show error to user
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to initialize AI: $e')),
        );
      }
    }
  }

  void _initializeConversation() {
    // Add initial NPC greeting
    setState(() {
      _messages.add(ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        text: _getGreeting(),
        isPlayer: false,
        timestamp: DateTime.now(),
      ));
    });
    
    // Generate initial quick responses
    _generateQuickResponses();
  }

  String _getGreeting() {
    final greetings = [
      "Hello. Can I help you with something?",
      "Hi there. What brings you here?",
      "Good to see you. What's up?",
    ];
    return greetings[DateTime.now().millisecond % greetings.length];
  }

  Future<void> _generateQuickResponses() async {
    if (!_isInitialized) {
      // Use fallback responses if not initialized
      setState(() {
        _quickResponses = [
          "Hi, I'm new here. Just getting oriented.",
          "I was hoping to ask you a few questions.",
          "Nice to meet you. How long have you worked here?",
        ];
      });
      return;
    }

    try {
      final responses = await _geminiService.generateQuickResponses(
        npc: widget.npc,
        objectives: _objectives,
        conversationHistory: _messages,
      );
      
      setState(() {
        _quickResponses = responses;
      });
    } catch (e) {
      print('Error generating quick responses: $e');
      // Keep existing responses or use fallback
    }
  }

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty || !_isInitialized) return;

    setState(() {
      _isLoading = true;
      
      // Add player message
      _messages.add(ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        text: text,
        isPlayer: true,
        timestamp: DateTime.now(),
      ));
    });

    _messageController.clear();
    _scrollToBottom();

    try {
      // Get NPC response from Gemini
      final response = await _geminiService.getNPCResponse(
        npc: widget.npc,
        objectives: _objectives,
        playerMessage: text,
        conversationHistory: _messages,
        difficulty: widget.difficulty,
      );
      
      setState(() {
        // Add NPC response
        _messages.add(ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: response.text,
          isPlayer: false,
          timestamp: DateTime.now(),
        ));
        
        // Update objectives if any were revealed
        for (final objectiveId in response.revealedObjectives) {
          final index = _objectives.indexWhere((o) => o.id == objectiveId);
          if (index != -1) {
            _objectives[index] = _objectives[index].copyWith(isCompleted: true);
          }
        }
        
        _isLoading = false;
      });
      
      _scrollToBottom();
      
      // Generate new quick responses
      await _generateQuickResponses();
      
      // Show success if objectives were revealed
      if (response.revealedObjectives.isNotEmpty) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('✅ Information obtained!'),
              backgroundColor: AppColors.success,
              duration: Duration(seconds: 2),
            ),
          );
        }
      }
    } catch (e) {
      print('Error getting NPC response: $e');
      setState(() {
        _messages.add(ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: "Sorry, I didn't catch that. Could you repeat?",
          isPlayer: false,
          timestamp: DateTime.now(),
        ));
        _isLoading = false;
      });
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    Future.delayed(Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        backgroundColor: AppColors.bgPrimary,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () => Navigator.pop(context),
        ),
        title: Row(
          children: [
            // NPC thumbnail (larger for better visibility)
            if (widget.npc.imageUrl != null)
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: AppColors.accentPrimary,
                    width: 3,
                  ),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(9),
                  child: Image.asset(
                    widget.npc.imageUrl!,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        color: AppColors.bgTertiary,
                        child: Icon(
                          Icons.person,
                          color: AppColors.textSecondary,
                          size: 32,
                        ),
                      );
                    },
                  ),
                ),
              ),
            SizedBox(width: AppDimensions.spaceMD),
            
            // NPC info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.npc.name,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  Text(
                    widget.npc.role,
                    style: TextStyle(
                      fontSize: 13,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Objectives section (always visible)
            Container(
              padding: EdgeInsets.all(AppDimensions.containerPadding),
              child: ObjectiveCard(
                objectives: _objectives,
                npcName: widget.npc.name,
              ),
            ),
            
            // MASSIVE NPC portrait section (80-90% width)
            if (widget.npc.imageUrl != null)
              Container(
                padding: EdgeInsets.symmetric(
                  horizontal: AppDimensions.containerPadding,
                  vertical: AppDimensions.spaceMD,
                ),
                child: LayoutBuilder(
                  builder: (context, constraints) {
                    final imageSize = constraints.maxWidth * 0.85; // 85% of screen width
                    return Center(
                      child: Container(
                        width: imageSize,
                        height: imageSize,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: AppColors.accentPrimary,
                            width: 5,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.accentPrimary.withValues(alpha: 0.4),
                              blurRadius: 30,
                              spreadRadius: 5,
                            ),
                          ],
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(15),
                          child: Image.asset(
                            widget.npc.imageUrl!,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                color: AppColors.bgTertiary,
                                child: Icon(
                                  Icons.person,
                                  color: AppColors.textSecondary,
                                  size: imageSize * 0.4,
                                ),
                              );
                            },
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            
            // Personality text
            Container(
              padding: EdgeInsets.symmetric(
                horizontal: AppDimensions.containerPadding,
                vertical: AppDimensions.spaceXS,
              ),
              child: Text(
                widget.npc.personality,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 12,
                  color: AppColors.textTertiary,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
            
            Divider(color: AppColors.borderSubtle, height: 1),
            
            SizedBox(height: AppDimensions.spaceMD),
            
            // Chat history
            Expanded(
              child: Container(
                padding: EdgeInsets.symmetric(
                  horizontal: AppDimensions.containerPadding,
                ),
                child: ListView.builder(
                  controller: _scrollController,
                  itemCount: _messages.length + (_isLoading ? 1 : 0),
                  itemBuilder: (context, index) {
                    if (index == _messages.length && _isLoading) {
                      return Padding(
                        padding: EdgeInsets.symmetric(vertical: AppDimensions.spaceMD),
                        child: Center(
                          child: Text(
                            '...',
                            style: TextStyle(
                              color: AppColors.textSecondary,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      );
                    }
                    
                    return ChatBubble(
                      message: _messages[index],
                      npcName: widget.npc.name,
                    );
                  },
                ),
              ),
            ),
            
            // Input section
            Container(
              padding: EdgeInsets.all(AppDimensions.containerPadding),
              decoration: BoxDecoration(
                color: AppColors.bgSecondary,
                border: Border(
                  top: BorderSide(
                    color: AppColors.borderSubtle,
                  ),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Quick responses or free-form input
                  if (_showQuickResponses) ...[
                    // Quick responses section
                    if (_quickResponses.isNotEmpty) ...[
                      Text(
                        'QUICK RESPONSES',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textTertiary,
                          letterSpacing: 1,
                        ),
                      ),
                      SizedBox(height: AppDimensions.spaceSM),
                      ..._quickResponses.map((response) {
                        return QuickResponseButton(
                          text: response,
                          onTap: () => _sendMessage(response),
                        );
                      }).toList(),
                    ],
                    
                    // Divider
                    Padding(
                      padding: EdgeInsets.symmetric(vertical: AppDimensions.spaceSM),
                      child: Row(
                        children: [
                          Expanded(child: Divider(color: AppColors.borderSubtle)),
                          Padding(
                            padding: EdgeInsets.symmetric(horizontal: AppDimensions.spaceMD),
                            child: Text(
                              'OR TYPE YOUR OWN',
                              style: TextStyle(
                                fontSize: 11,
                                color: AppColors.textTertiary,
                                letterSpacing: 0.5,
                              ),
                            ),
                          ),
                          Expanded(child: Divider(color: AppColors.borderSubtle)),
                        ],
                      ),
                    ),
                  ],
                  
                  // Text input
                  HeistTextField(
                    controller: _messageController,
                    hintText: 'Type your response...',
                    maxLines: 2,
                    onChanged: (_) => setState(() {}),
                  ),
                  
                  SizedBox(height: AppDimensions.spaceMD),
                  
                  // Send button
                  HeistPrimaryButton(
                    text: 'Send Message',
                    onPressed: _messageController.text.trim().isEmpty
                        ? null
                        : () => _sendMessage(_messageController.text),
                    loading: _isLoading,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
