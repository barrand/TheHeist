import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_dimensions.dart';
import '../models/npc.dart';
import '../services/backend_service.dart';
import '../widgets/npc/objective_card.dart';
import '../widgets/npc/chat_bubble.dart';
import '../widgets/npc/quick_response_button.dart';
import '../widgets/common/heist_primary_button.dart';
import '../widgets/common/heist_text_field.dart';

/// NPC Conversation Screen (Screen 10)
/// Free-form conversation with NPCs using LLM via Python backend
/// Hybrid interaction: Quick responses + free-form text
/// 
/// Architecture: Flutter UI -> BackendService -> Python FastAPI -> Gemini
class NPCConversationScreen extends StatefulWidget {
  final NPC npc;
  final List<Objective> objectives;
  final String apiKey;  // NOTE: Not used anymore, backend has the key
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
  final BackendService _backendService = BackendService();
  
  List<ChatMessage> _messages = [];
  List<Objective> _objectives = [];
  List<String> _quickResponses = [];
  bool _showQuickResponses = true; // Show quick responses
  bool _isLoading = false;
  bool _isInitialized = false;
  bool _missionCompleted = false; // Track if objectives completed
  bool _missionFailed = false; // Track if conversation failed

  @override
  void initState() {
    super.initState();
    _objectives = List.from(widget.objectives);
    _checkBackendHealth();
    _generateInitialQuickResponses();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _checkBackendHealth() async {
    print('🏥 Checking backend health...');
    try {
      final isHealthy = await _backendService.checkHealth();
      setState(() {
        _isInitialized = isHealthy;
      });
      
      if (isHealthy) {
        print('✅ Backend is healthy');
        _initializeConversation();
      } else {
        print('⚠️ Backend health check failed');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Backend server is not responding. Make sure it\'s running on http://localhost:8000'),
              duration: Duration(seconds: 5),
            ),
          );
        }
      }
    } catch (e) {
      print('❌ Error checking backend health: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to connect to backend: $e')),
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
  }
  
  Future<void> _generateInitialQuickResponses() async {
    // Wait a bit for health check to complete
    await Future.delayed(const Duration(milliseconds: 500));
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
      // Use fallback responses if backend not available
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
      print('🎲 Generating quick responses via backend...');
      final responses = await _backendService.generateQuickResponses(
        npc: widget.npc,
        objectives: _objectives,
        conversationHistory: _messages,
      );
      
      setState(() {
        _quickResponses = responses;
      });
      print('✅ Got ${responses.length} quick responses: $responses');
      print('   _showQuickResponses = $_showQuickResponses');
    } catch (e) {
      print('❌ Error generating quick responses: $e');
      // Keep existing responses or use fallback
    }
  }

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty || !_isInitialized) return;
    if (_missionCompleted || _missionFailed) return; // Don't allow messaging if mission ended

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
      print('💬 Sending message to backend...');
      // Get NPC response from backend (which calls Gemini)
      final response = await _backendService.getNPCResponse(
        npc: widget.npc,
        objectives: _objectives,
        playerMessage: text,
        conversationHistory: _messages,
        difficulty: widget.difficulty,
      );
      
      print('✅ Got NPC response: "${response.text}"');
      
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
            print('🎯 Objective completed: ${_objectives[index].description}');
          }
        }
        
        _isLoading = false;
      });
      
      _scrollToBottom();
      
      // Generate new quick responses
      await _generateQuickResponses();
      
      // Show success if objectives were revealed
      if (response.revealedObjectives.isNotEmpty) {
        // Check if all objectives are completed
        final allCompleted = _objectives.every((obj) => obj.isCompleted);
        if (allCompleted) {
          setState(() {
            _missionCompleted = true;
          });
        }
      }
    } catch (e) {
      print('❌ Error getting NPC response: $e');
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
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
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
      body: SafeArea(
        child: Column(
          children: [
            // Scrollable top section with objectives and image
            Expanded(
              child: CustomScrollView(
                controller: _scrollController,
                slivers: [
                  // Objectives section
                  SliverToBoxAdapter(
                    child: Container(
                      padding: EdgeInsets.all(AppDimensions.containerPadding),
                      child: ObjectiveCard(
                        objectives: _objectives,
                        npcName: widget.npc.name,
                      ),
                    ),
                  ),
                  
                  // NPC portrait section (nice big image!)
                  if (widget.npc.imageUrl != null)
                    SliverToBoxAdapter(
                      child: Container(
                        padding: EdgeInsets.symmetric(
                          horizontal: AppDimensions.containerPadding,
                          vertical: AppDimensions.spaceSM,
                        ),
                        child: Center(
                          child: Container(
                            width: 300,  // Nice big size!
                            height: 300,
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: AppColors.accentPrimary,
                                width: 4,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: AppColors.accentPrimary.withValues(alpha: 0.3),
                                  blurRadius: 20,
                                  spreadRadius: 2,
                                ),
                              ],
                            ),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(12),
                              child: Image.asset(
                                widget.npc.imageUrl!,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) {
                                  return Container(
                                    color: AppColors.bgTertiary,
                                    child: Icon(
                                      Icons.person,
                                      color: AppColors.textSecondary,
                                      size: 80,
                                    ),
                                  );
                                },
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  
                  // Personality text
                  SliverToBoxAdapter(
                    child: Container(
                      padding: EdgeInsets.symmetric(
                        horizontal: AppDimensions.containerPadding,
                        vertical: AppDimensions.spaceXS,
                      ),
                      child: Text(
                        widget.npc.personality,
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 11,
                          color: AppColors.textTertiary,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                  ),
                  
                  SliverToBoxAdapter(
                    child: Divider(color: AppColors.borderSubtle, height: 1),
                  ),
                  
                  SliverToBoxAdapter(
                    child: SizedBox(height: AppDimensions.spaceXS),
                  ),
                  
                  // Chat messages
                  SliverList(
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        if (index == _messages.length && _isLoading) {
                          return Padding(
                            padding: EdgeInsets.symmetric(
                              horizontal: AppDimensions.containerPadding,
                              vertical: AppDimensions.spaceMD,
                            ),
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
                        
                        return Padding(
                          padding: EdgeInsets.symmetric(
                            horizontal: AppDimensions.containerPadding,
                          ),
                          child: ChatBubble(
                            message: _messages[index],
                            npcName: widget.npc.name,
                          ),
                        );
                      },
                      childCount: _messages.length + (_isLoading ? 1 : 0),
                    ),
                  ),
                  
                  // Success/Failure banner
                  if (_missionCompleted || _missionFailed)
                    SliverToBoxAdapter(
                      child: Container(
                        margin: EdgeInsets.all(AppDimensions.containerPadding),
                        padding: EdgeInsets.all(AppDimensions.cardPadding * 1.5),
                        decoration: BoxDecoration(
                          color: _missionCompleted ? Color(0xFF1E4D2B) : Color(0xFF4D1E1E),
                          borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
                          border: Border.all(
                            color: _missionCompleted ? AppColors.success : AppColors.error,
                            width: 3,
                          ),
                        ),
                        child: Column(
                          children: [
                            Icon(
                              _missionCompleted ? Icons.check_circle_rounded : Icons.cancel_rounded,
                              color: _missionCompleted ? AppColors.success : AppColors.error,
                              size: 64,
                            ),
                            SizedBox(height: AppDimensions.spaceMD),
                            Text(
                              _missionCompleted ? '🎉 MISSION SUCCESS!' : '❌ MISSION FAILED',
                              style: TextStyle(
                                fontSize: 28,
                                fontWeight: FontWeight.bold,
                                color: _missionCompleted ? AppColors.success : AppColors.error,
                              ),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: AppDimensions.spaceSM),
                            Text(
                              _missionCompleted 
                                  ? 'You successfully obtained all the information you needed!'
                                  : 'The NPC became suspicious and ended the conversation.',
                              style: TextStyle(
                                fontSize: 15,
                                color: AppColors.textPrimary,
                              ),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: AppDimensions.spaceLG),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: () => Navigator.pop(context),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppColors.accentPrimary,
                                  padding: EdgeInsets.symmetric(
                                    horizontal: 32,
                                    vertical: 16,
                                  ),
                                ),
                                child: Text(
                                  'Return to Mission Select',
                                  style: TextStyle(
                                    color: AppColors.bgPrimary,
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  
                  // Bottom padding for chat
                  SliverToBoxAdapter(
                    child: SizedBox(height: 80),
                  ),
                ],
              ),
            ),
            
            // Input section (fixed at bottom)
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
                  // DEBUG: Show state
                  Text(
                    'DEBUG: show=$_showQuickResponses, count=${_quickResponses.length}',
                    style: TextStyle(color: Colors.yellow, fontSize: 10),
                  ),
                  
                  // Quick responses (horizontal scroll)
                  if (_showQuickResponses && _quickResponses.isNotEmpty) ...[
                    Text(
                      'QUICK RESPONSES',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textTertiary,
                        letterSpacing: 1,
                      ),
                    ),
                    SizedBox(height: 8),
                    // Vertical list of quick responses for better text display
                    ...List.generate(_quickResponses.length, (index) {
                      return Padding(
                        padding: EdgeInsets.only(bottom: 6),
                        child: InkWell(
                          onTap: () => _sendMessage(_quickResponses[index]),
                          borderRadius: BorderRadius.circular(8),
                          child: Container(
                            width: double.infinity,
                            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                            decoration: BoxDecoration(
                              color: AppColors.bgTertiary,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: AppColors.accentPrimary),
                            ),
                            child: Row(
                              children: [
                                Text(
                                  '💬',
                                  style: TextStyle(fontSize: 14),
                                ),
                                SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    _quickResponses[index],
                                    style: TextStyle(
                                      color: AppColors.textPrimary,
                                      fontSize: 13,
                                    ),
                                    maxLines: 3,  // Allow up to 3 lines
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                Icon(
                                  Icons.send,
                                  size: 14,
                                  color: AppColors.accentPrimary,
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    }),
                    SizedBox(height: 8),
                    Divider(color: AppColors.borderSubtle, height: 1),
                    SizedBox(height: 8),
                  ],
                  
                  // Text input with inline send button
                  Row(
                    children: [
                      Expanded(
                        child: HeistTextField(
                          controller: _messageController,
                          hintText: _missionCompleted || _missionFailed 
                              ? 'Mission ended' 
                              : 'Type your response...',
                          maxLines: 1,
                          onChanged: (_) => setState(() {}),
                          enabled: !_missionCompleted && !_missionFailed,
                        ),
                      ),
                      SizedBox(width: 8),
                      // Send button
                      SizedBox(
                        width: 80,
                        height: 40,
                        child: ElevatedButton(
                          onPressed: _messageController.text.trim().isEmpty || _isLoading || _missionCompleted || _missionFailed
                              ? null
                              : () => _sendMessage(_messageController.text),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.accentPrimary,
                            padding: EdgeInsets.zero,
                          ),
                          child: _isLoading 
                              ? SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: AppColors.textPrimary,
                                  ),
                                )
                              : Text(
                                  'Send',
                                  style: TextStyle(
                                    color: AppColors.textPrimary,
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                        ),
                      ),
                    ],
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
