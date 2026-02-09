import 'package:flutter/material.dart';
import '../core/app_config.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_dimensions.dart';
import '../models/npc.dart';
import '../services/backend_service.dart';

/// NPC Conversation Screen with cover fit score system
/// 
/// Phase 1: Player selects a cover story
/// Phase 2: Conversation with quick responses, suspicion meter, no free-form text
/// 
/// NOTE: ElevatedButton theme uses Size.fromHeight() which sets width=infinity.
/// Any ElevatedButton inside a Row MUST override minimumSize to avoid crash.
class NPCConversationScreen extends StatefulWidget {
  final NPC npc;
  final List<Objective> objectives;
  final String apiKey;
  final String difficulty;
  final String? scenarioId;
  final String? roomCode;
  final String? playerId;
  final List<String> targetOutcomes;
  final String missionBrief;

  const NPCConversationScreen({
    Key? key,
    required this.npc,
    required this.objectives,
    required this.apiKey,
    this.difficulty = 'easy',
    this.scenarioId,
    this.roomCode,
    this.playerId,
    this.targetOutcomes = const [],
    this.missionBrief = '',
  }) : super(key: key);

  @override
  State<NPCConversationScreen> createState() => _NPCConversationScreenState();
}

class _NPCConversationScreenState extends State<NPCConversationScreen> {
  final ScrollController _scrollController = ScrollController();
  final BackendService _backendService = BackendService();
  
  // Conversation state
  bool _isCoverSelection = true;
  String? _selectedCoverId;
  String _coverLabel = '';
  List<ChatMessage> _messages = [];
  List<QuickResponseOption> _quickResponses = [];
  List<Map<String, dynamic>> _infoObjectives = [];
  List<Map<String, dynamic>> _actionObjectives = [];
  Set<String> _achievedOutcomes = {};
  int _suspicion = 0;
  bool _isLoading = false;
  bool _conversationFailed = false;
  bool _allOutcomesAchieved = false;

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  String? _getNpcImageUrl() {
    if (widget.scenarioId != null && widget.npc.id.isNotEmpty) {
      return 'http://localhost:8000/api/images/${widget.scenarioId}/npc/${widget.npc.id}';
    }
    return null;
  }

  // ---------------------------------------------------------------------------
  // Cover Selection
  // ---------------------------------------------------------------------------

  Future<void> _selectCover(CoverOption cover) async {
    if (widget.roomCode == null || widget.playerId == null) {
      debugPrint('❌ Missing roomCode or playerId for conversation');
      return;
    }

    setState(() => _isLoading = true);

    try {
      final result = await _backendService.startConversation(
        npcId: widget.npc.id,
        coverId: cover.coverId,
        roomCode: widget.roomCode!,
        playerId: widget.playerId!,
        targetOutcomes: widget.targetOutcomes,
      );

      if (!mounted) return;
      setState(() {
        _isCoverSelection = false;
        _selectedCoverId = cover.coverId;
        _coverLabel = result.coverLabel;
        _suspicion = result.suspicion;
        _quickResponses = result.quickResponses;
        _infoObjectives = result.infoObjectives;
        _actionObjectives = result.actionObjectives;
        _messages.add(ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: result.greeting,
          isPlayer: false,
          timestamp: DateTime.now(),
        ));
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoading = false);
      debugPrint('❌ Error starting conversation: $e');
    }
  }

  // ---------------------------------------------------------------------------
  // Conversation
  // ---------------------------------------------------------------------------

  Future<void> _sendChoice(int index) async {
    if (_isLoading || _conversationFailed || _allOutcomesAchieved) return;
    if (widget.roomCode == null || widget.playerId == null) return;

    final chosen = _quickResponses[index];
    
    setState(() {
      _isLoading = true;
      _messages.add(ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        text: chosen.text,
        isPlayer: true,
        timestamp: DateTime.now(),
      ));
      _quickResponses = [];
    });
    _scrollToBottom();

    try {
      final result = await _backendService.sendConversationChoice(
        responseIndex: index,
        roomCode: widget.roomCode!,
        playerId: widget.playerId!,
        npcId: widget.npc.id,
      );

      if (!mounted) return;
      setState(() {
        _messages.add(ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: result.npcResponse,
          isPlayer: false,
          timestamp: DateTime.now(),
        ));
        _suspicion = result.suspicion;
        _quickResponses = result.quickResponses;
        _conversationFailed = result.conversationFailed;
        _isLoading = false;

        // Track outcomes
        for (final outcome in result.outcomes) {
          _achievedOutcomes.add(outcome);
        }

        // Check if all objectives are done
        final allInfoIds = _infoObjectives.map((o) => o['id'] as String).toSet();
        final allActionIds = _actionObjectives.map((o) => o['id'] as String).toSet();
        final allNeeded = allInfoIds.union(allActionIds);
        if (allNeeded.isNotEmpty && allNeeded.every((id) => _achievedOutcomes.contains(id))) {
          _allOutcomesAchieved = true;
        }
      });
      _scrollToBottom();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _messages.add(ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: "Sorry, I didn't catch that. Could you repeat?",
          isPlayer: false,
          timestamp: DateTime.now(),
        ));
      });
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Build
  // ---------------------------------------------------------------------------

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
        title: Text('Back', style: TextStyle(fontSize: 16, color: AppColors.textPrimary)),
        titleSpacing: -8,
      ),
      body: _isCoverSelection ? _buildCoverSelection() : _buildConversation(),
    );
  }

  // ---------------------------------------------------------------------------
  // Phase 1: Cover Selection
  // ---------------------------------------------------------------------------

  Widget _buildCoverSelection() {
    return Column(
      children: [
        Expanded(
          child: SingleChildScrollView(
            padding: EdgeInsets.all(AppDimensions.containerPadding),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // NPC portrait
                Center(child: _buildNpcPortrait()),
                SizedBox(height: AppDimensions.spaceSM),
                
                // NPC name
                Text(
                  widget.npc.name.toUpperCase(),
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 20, fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary, letterSpacing: 2,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  widget.npc.role,
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 14, color: AppColors.accentPrimary),
                ),
                
                if (widget.npc.personality.isNotEmpty)
                  Padding(
                    padding: EdgeInsets.only(top: AppDimensions.spaceXS, bottom: AppDimensions.spaceMD),
                    child: Text(
                      widget.npc.personality,
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 13, color: AppColors.textSecondary, fontStyle: FontStyle.italic),
                    ),
                  ),
              ],
            ),
          ),
        ),
        
        // Cover story selection (bottom)
        _buildCoverOptions(),
      ],
    );
  }

  Widget _buildCoverOptions() {
    return Container(
      padding: EdgeInsets.all(AppDimensions.containerPadding),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        border: Border(top: BorderSide(color: AppColors.borderSubtle)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(Icons.theater_comedy, color: AppColors.accentPrimary, size: 16),
              SizedBox(width: 6),
              Text(
                'WHAT IS YOUR COVER STORY?',
                style: TextStyle(
                  fontSize: 11, fontWeight: FontWeight.w600,
                  color: AppColors.accentPrimary, letterSpacing: 1.5,
                ),
              ),
            ],
          ),
          SizedBox(height: 10),
          if (_isLoading)
            Center(child: CircularProgressIndicator(color: AppColors.accentPrimary))
          else
            for (final cover in widget.npc.coverOptions) ...[
              _buildCoverButton(cover),
              SizedBox(height: 8),
            ],
        ],
      ),
    );
  }

  /// Split cover description into bold identity + lighter detail.
  /// Splits on first comma, dash, or "who" / "writing" / "considering" etc.
  (String, String) _splitCoverDescription(String desc) {
    // Try splitting on common separator patterns
    final separators = [', ', ' - ', ' — ', ' – '];
    for (final sep in separators) {
      final idx = desc.indexOf(sep);
      if (idx > 0 && idx < desc.length - 1) {
        return (desc.substring(0, idx), desc.substring(idx));
      }
    }
    // Try splitting on connecting words (with a space before)
    final wordPattern = RegExp(r' (?:who |considering |writing |looking |interested |wanting |hoping |trying )');
    final match = wordPattern.firstMatch(desc);
    if (match != null) {
      return (desc.substring(0, match.start), desc.substring(match.start));
    }
    // No split found -- everything is the identity
    return (desc, '');
  }

  Widget _buildCoverButton(CoverOption cover) {
    // Subtle left accent color based on trust level (no label)
    final accentColor = cover.trustLevel == 'high'
        ? AppColors.success
        : cover.trustLevel == 'low'
            ? AppColors.danger
            : AppColors.warning;

    final (identity, detail) = _splitCoverDescription(cover.description);

    return GestureDetector(
      onTap: () => _selectCover(cover),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.bgTertiary,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          border: Border.all(color: AppColors.borderSubtle),
        ),
        clipBehavior: Clip.antiAlias,
        child: IntrinsicHeight(
          child: Row(
            children: [
              // Colored left accent bar
              Container(width: 4, color: accentColor),
              // Cover description with bold identity
              Expanded(
                child: Padding(
                  padding: EdgeInsets.symmetric(vertical: 14, horizontal: 16),
                  child: Text.rich(
                    TextSpan(
                      text: '"',
                      style: TextStyle(
                        fontSize: 14,
                        fontStyle: FontStyle.italic,
                        color: AppColors.textSecondary,
                      ),
                      children: [
                        TextSpan(
                          text: identity,
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        if (detail.isNotEmpty)
                          TextSpan(
                            text: detail,
                            style: TextStyle(
                              fontWeight: FontWeight.w400,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        TextSpan(text: '"'),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Phase 2: Active Conversation
  // ---------------------------------------------------------------------------

  Widget _buildConversation() {
    return Column(
      children: [
        // Suspicion meter
        _buildSuspicionMeter(),
        
        // Mission brief + objectives (pinned at top, not scrollable)
        _buildMissionHeader(),
        
        // Scrollable chat area
        Expanded(
          child: SingleChildScrollView(
            controller: _scrollController,
            padding: EdgeInsets.symmetric(horizontal: AppDimensions.containerPadding),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(height: AppDimensions.spaceSM),
                
                // NPC portrait (smaller in conversation) + name
                Row(
                  children: [
                    SizedBox(
                      width: 56, height: 56,
                      child: _buildNpcPortrait(small: true),
                    ),
                    SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.npc.name.toUpperCase(),
                            style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary, letterSpacing: 0.5),
                          ),
                          Text(
                            'Cover: "$_coverLabel"',
                            style: TextStyle(fontSize: 11, color: AppColors.textTertiary, fontStyle: FontStyle.italic),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                
                SizedBox(height: AppDimensions.spaceSM),
                Divider(color: AppColors.borderSubtle, height: 1),
                SizedBox(height: AppDimensions.spaceSM),
                
                // Chat messages
                for (final message in _messages) _buildChatBubble(message),
                
                // Typing indicator
                if (_isLoading) _buildTypingIndicator(),
                
                // Result banners
                if (_conversationFailed) _buildFailureBanner(),
                if (_allOutcomesAchieved) _buildSuccessBanner(),
                
                SizedBox(height: 16),
              ],
            ),
          ),
        ),
        
        // Quick responses (bottom, no free-form text)
        if (!_conversationFailed && !_allOutcomesAchieved && _quickResponses.isNotEmpty)
          _buildQuickResponses(),
      ],
    );
  }

  Widget _buildMissionHeader() {
    // Don't render anything if there's no mission brief
    if (widget.missionBrief.isEmpty) return SizedBox.shrink();
    
    return Container(
      width: double.infinity,
      padding: EdgeInsets.symmetric(horizontal: AppDimensions.containerPadding, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
      ),
      child: Text(
        widget.missionBrief,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: AppColors.accentPrimary,
          height: 1.3,
        ),
      ),
    );
  }

  Widget _buildSuspicionMeter() {
    // Suspicion 0-5 maps to 0.0-1.0 position on the bar
    final position = (_suspicion / 5.0).clamp(0.0, 1.0);
    // Color interpolates from green -> yellow -> red
    final color = _suspicion <= 1
        ? AppColors.success
        : _suspicion <= 3
            ? AppColors.warning
            : AppColors.danger;
    
    return Container(
      padding: EdgeInsets.symmetric(horizontal: AppDimensions.containerPadding, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
      ),
      child: Column(
        children: [
          // Labels row: Relaxed ... difficulty badge ... Suspicious
          Row(
            children: [
              Text('Relaxed', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w500, color: AppColors.success)),
              Spacer(),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: AppColors.bgTertiary,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  widget.difficulty.toUpperCase(),
                  style: TextStyle(fontSize: 9, fontWeight: FontWeight.w600, color: AppColors.textTertiary, letterSpacing: 0.5),
                ),
              ),
              Spacer(),
              Text('Suspicious', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w500, color: AppColors.danger)),
            ],
          ),
          SizedBox(height: 6),
          // Gradient bar with indicator
          LayoutBuilder(
            builder: (context, constraints) {
              final barWidth = constraints.maxWidth;
              final indicatorOffset = position * (barWidth - 12); // 12 = indicator width
              
              return Stack(
                clipBehavior: Clip.none,
                children: [
                  // Track background with gradient
                  Container(
                    height: 6,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(3),
                      gradient: LinearGradient(
                        colors: [AppColors.success, Color(0xFFFFB800), AppColors.danger],
                        stops: [0.0, 0.5, 1.0],
                      ),
                    ),
                  ),
                  // Dark overlay for unfilled portion
                  Positioned(
                    left: position * barWidth,
                    right: 0,
                    child: Container(
                      height: 6,
                      decoration: BoxDecoration(
                        color: AppColors.bgPrimary.withValues(alpha: 0.7),
                        borderRadius: BorderRadius.horizontal(
                          left: position > 0 ? Radius.zero : Radius.circular(3),
                          right: Radius.circular(3),
                        ),
                      ),
                    ),
                  ),
                  // Triangle indicator
                  Positioned(
                    left: indicatorOffset,
                    top: -6,
                    child: CustomPaint(
                      size: Size(12, 6),
                      painter: _TrianglePainter(color: color),
                    ),
                  ),
                  // Dot indicator on the bar
                  Positioned(
                    left: indicatorOffset + 3,
                    top: 0,
                    child: Container(
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: color,
                        boxShadow: [BoxShadow(color: color.withValues(alpha: 0.5), blurRadius: 4)],
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildQuickResponses() {
    return Container(
      padding: EdgeInsets.all(AppDimensions.containerPadding),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        border: Border(top: BorderSide(color: AppColors.borderSubtle)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            'CHOOSE RESPONSE',
            style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: AppColors.textTertiary, letterSpacing: 1),
          ),
          SizedBox(height: 8),
          for (int i = 0; i < _quickResponses.length; i++) ...[
            _buildQuickResponseButton(_quickResponses[i], i),
            if (i < _quickResponses.length - 1) SizedBox(height: 6),
          ],
        ],
      ),
    );
  }

  Widget _buildQuickResponseButton(QuickResponseOption option, int index) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton(
        onPressed: _isLoading ? null : () => _sendChoice(index),
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.textPrimary,
          side: BorderSide(color: AppColors.borderSubtle),
          padding: EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMD)),
          alignment: Alignment.centerLeft,
        ),
        child: Row(
          children: [
            // Debug fit score (only visible in debug mode)
            if (AppConfig.debugMode)
              Container(
                padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                margin: EdgeInsets.only(right: 10),
                decoration: BoxDecoration(
                  color: _fitScoreColor(option.fitScore).withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'fit:${option.fitScore}',
                  style: TextStyle(
                    fontSize: 10, fontWeight: FontWeight.w700,
                    color: _fitScoreColor(option.fitScore),
                  ),
                ),
              ),
            Expanded(
              child: Text(
                option.text,
                style: TextStyle(fontSize: 14),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _fitScoreColor(int fit) {
    if (fit >= 4) return AppColors.success;
    if (fit == 3) return AppColors.warning;
    return AppColors.danger;
  }

  // ---------------------------------------------------------------------------
  // Chat Bubbles
  // ---------------------------------------------------------------------------

  Widget _buildChatBubble(ChatMessage message) {
    final isPlayer = message.isPlayer;
    return Align(
      alignment: isPlayer ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 4),
        padding: EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        decoration: BoxDecoration(
          color: isPlayer ? AppColors.accentPrimary.withValues(alpha: 0.2) : AppColors.bgTertiary,
          borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
          border: Border.all(
            color: isPlayer ? AppColors.accentPrimary.withValues(alpha: 0.4) : AppColors.borderSubtle,
          ),
        ),
        child: Text(
          message.text,
          style: TextStyle(fontSize: 14, color: AppColors.textPrimary),
        ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 4),
        padding: EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: AppColors.bgTertiary,
          borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
          border: Border.all(color: AppColors.borderSubtle),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.textSecondary)),
            SizedBox(width: 10),
            Text('${widget.npc.name} is thinking...', style: TextStyle(color: AppColors.textSecondary, fontSize: 13, fontStyle: FontStyle.italic)),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Result Banners
  // ---------------------------------------------------------------------------

  Widget _buildFailureBanner() {
    return Container(
      margin: EdgeInsets.symmetric(vertical: AppDimensions.spaceMD),
      padding: EdgeInsets.all(AppDimensions.cardPadding * 1.5),
      decoration: BoxDecoration(
        color: Color(0xFF4D1E1E),
        borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
        border: Border.all(color: AppColors.danger, width: 3),
      ),
      child: Column(
        children: [
          Icon(Icons.cancel_rounded, color: AppColors.danger, size: 48),
          SizedBox(height: AppDimensions.spaceSM),
          Text('CONVERSATION ENDED', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.danger)),
          SizedBox(height: 8),
          Text(
            'The NPC became too suspicious. Try again later or ask a teammate.',
            style: TextStyle(fontSize: 14, color: AppColors.textPrimary),
            textAlign: TextAlign.center,
          ),
          SizedBox(height: AppDimensions.spaceLG),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => Navigator.pop(context, {'failed': true, 'npc_id': widget.npc.id}),
              child: Text('BACK TO GAME', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuccessBanner() {
    return Container(
      margin: EdgeInsets.symmetric(vertical: AppDimensions.spaceMD),
      padding: EdgeInsets.all(AppDimensions.cardPadding * 1.5),
      decoration: BoxDecoration(
        color: Color(0xFF1E4D2B),
        borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
        border: Border.all(color: AppColors.success, width: 3),
      ),
      child: Column(
        children: [
          Icon(Icons.check_circle_rounded, color: AppColors.success, size: 48),
          SizedBox(height: AppDimensions.spaceSM),
          Text('OBJECTIVES COMPLETE!', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.success)),
          SizedBox(height: 8),
          Text(
            'You got everything you needed from this conversation.',
            style: TextStyle(fontSize: 14, color: AppColors.textPrimary),
            textAlign: TextAlign.center,
          ),
          SizedBox(height: AppDimensions.spaceLG),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => Navigator.pop(context, {'success': true}),
              child: Text('CONTINUE', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // NPC Portrait
  // ---------------------------------------------------------------------------

  Widget _buildNpcPortrait({bool small = false}) {
    final size = small ? 120.0 : 280.0;
    return Container(
      width: size, height: size,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(small ? 12 : 16),
        border: Border.all(color: AppColors.accentPrimary, width: small ? 2 : 3),
        boxShadow: [
          BoxShadow(
            color: AppColors.accentPrimary.withValues(alpha: 0.3),
            blurRadius: small ? 10 : 20, spreadRadius: small ? 1 : 2,
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(small ? 10 : 13),
        child: _buildNpcImage(),
      ),
    );
  }

  Widget _buildNpcImage() {
    final imageUrl = _getNpcImageUrl();
    if (imageUrl != null) {
      return Image.network(imageUrl, fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) => _buildImageFallback(),
      );
    }
    return _buildImageFallback();
  }

  Widget _buildImageFallback() {
    return Container(
      color: AppColors.bgTertiary,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.person, color: AppColors.textSecondary, size: 48),
            SizedBox(height: 4),
            Text(widget.npc.name, style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
          ],
        ),
      ),
    );
  }
}

/// Paints a small downward-pointing triangle for the suspicion meter indicator
class _TrianglePainter extends CustomPainter {
  final Color color;
  _TrianglePainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.fill;
    final path = Path()
      ..moveTo(0, 0)
      ..lineTo(size.width, 0)
      ..lineTo(size.width / 2, size.height)
      ..close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(_TrianglePainter oldDelegate) => oldDelegate.color != color;
}
