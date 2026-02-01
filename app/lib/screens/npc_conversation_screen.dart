import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_dimensions.dart';
import '../models/npc.dart';
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

  const NPCConversationScreen({
    Key? key,
    required this.npc,
    required this.objectives,
  }) : super(key: key);

  @override
  State<NPCConversationScreen> createState() => _NPCConversationScreenState();
}

class _NPCConversationScreenState extends State<NPCConversationScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  
  List<ChatMessage> _messages = [];
  List<String> _quickResponses = [];
  bool _showQuickResponses = true;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _initializeConversation();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
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
      "Hey there. Can I help you with something?",
      "Hello. What brings you here?",
      "Good to see you. What's up?",
    ];
    return greetings[DateTime.now().millisecond % greetings.length];
  }

  void _generateQuickResponses() {
    // TODO: Replace with actual LLM generation
    // For now, use placeholder responses
    setState(() {
      _quickResponses = [
        "Hi, I'm new here. Just getting oriented.",
        "I was hoping to ask you a few questions.",
        "Nice to meet you. How long have you worked here?",
      ];
    });
  }

  void _sendMessage(String text) {
    if (text.trim().isEmpty) return;

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

    // TODO: Call LLM API to get NPC response
    // For now, simulate with delay
    Future.delayed(Duration(seconds: 1), () {
      setState(() {
        _messages.add(ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: "That's an interesting question. Let me think about that...",
          isPlayer: false,
          timestamp: DateTime.now(),
        ));
        _isLoading = false;
      });
      
      _scrollToBottom();
      _generateQuickResponses();
    });
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
            // NPC thumbnail
            if (widget.npc.imageUrl != null)
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: AppColors.accentPrimary,
                    width: 2,
                  ),
                  image: DecorationImage(
                    image: AssetImage(widget.npc.imageUrl!),
                    fit: BoxFit.cover,
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
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  Text(
                    widget.npc.role,
                    style: TextStyle(
                      fontSize: 12,
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
                objectives: widget.objectives,
                npcName: widget.npc.name,
              ),
            ),
            
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
