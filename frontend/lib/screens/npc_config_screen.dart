import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_dimensions.dart';
import '../models/npc.dart';
import '../widgets/common/top_toast.dart';
import '../widgets/common/heist_primary_button.dart';
import '../widgets/common/heist_text_field.dart';
import '../widgets/common/section_header.dart';
import 'npc_conversation_screen.dart';

/// Configuration screen for NPC conversation testing
/// Allows setting API key and difficulty before starting conversation
class NPCConfigScreen extends StatefulWidget {
  final NPC npc;
  final List<Objective> objectives;

  const NPCConfigScreen({
    Key? key,
    required this.npc,
    required this.objectives,
  }) : super(key: key);

  @override
  State<NPCConfigScreen> createState() => _NPCConfigScreenState();
}

class _NPCConfigScreenState extends State<NPCConfigScreen> {
  final TextEditingController _apiKeyController = TextEditingController();
  String _difficulty = 'medium';
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSavedSettings();
  }

  @override
  void dispose() {
    _apiKeyController.dispose();
    super.dispose();
  }

  Future<void> _loadSavedSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _apiKeyController.text = prefs.getString('gemini_api_key') ?? '';
      _difficulty = prefs.getString('difficulty') ?? 'medium';
      _isLoading = false;
    });
  }

  Future<void> _saveSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('gemini_api_key', _apiKeyController.text);
    await prefs.setString('difficulty', _difficulty);
  }

  Future<void> _clearApiKey() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('gemini_api_key');
    setState(() {
      _apiKeyController.clear();
    });
  }

  void _startConversation() async {
    if (_apiKeyController.text.trim().isEmpty) {
      showTopToast(context, 'Please enter your Gemini API key', color: AppColors.danger);
      return;
    }

    // Save settings
    await _saveSettings();

    // Navigate to conversation
    if (mounted) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => NPCConversationScreen(
            npc: widget.npc,
            objectives: widget.objectives,
            apiKey: _apiKeyController.text.trim(),
            difficulty: _difficulty,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: AppColors.bgPrimary,
        body: Center(
          child: CircularProgressIndicator(
            color: AppColors.accentPrimary,
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        backgroundColor: AppColors.bgPrimary,
        elevation: 0,
        title: Text(
          'Setup Conversation',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: AppColors.textPrimary,
          ),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(AppDimensions.containerPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // NPC Info Card
              Container(
                padding: EdgeInsets.all(AppDimensions.cardPadding),
                decoration: BoxDecoration(
                  color: AppColors.bgSecondary,
                  border: Border.all(color: AppColors.borderSubtle),
                  borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
                ),
                child: Row(
                  children: [
                    Text('🎭', style: TextStyle(fontSize: 32)),
                    SizedBox(width: AppDimensions.spaceMD),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.npc.name,
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          Text(
                            widget.npc.role,
                            style: TextStyle(
                              fontSize: 14,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SectionHeader(text: 'Gemini API Key'),

              // API Key input
              HeistTextField(
                controller: _apiKeyController,
                hintText: 'AIza...',
                obscureText: true,
              ),

              SizedBox(height: AppDimensions.spaceSM),

              // Clear key button
              if (_apiKeyController.text.isNotEmpty)
                TextButton(
                  onPressed: _clearApiKey,
                  child: Text(
                    'Clear Saved Key',
                    style: TextStyle(
                      color: AppColors.danger,
                      fontSize: 12,
                    ),
                  ),
                ),

              SizedBox(height: AppDimensions.spaceSM),

              // Link to get API key
              Container(
                padding: EdgeInsets.all(AppDimensions.spaceMD),
                decoration: BoxDecoration(
                  color: AppColors.bgTertiary,
                  border: Border.all(color: AppColors.borderSubtle),
                  borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Don\'t have an API key?',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textSecondary,
                      ),
                    ),
                    SizedBox(height: AppDimensions.spaceXS),
                    Text(
                      'Get one free at: aistudio.google.com/app/apikey',
                      style: TextStyle(
                        fontSize: 11,
                        color: AppColors.accentPrimary,
                      ),
                    ),
                  ],
                ),
              ),

              SectionHeader(text: 'Difficulty'),

              // Difficulty selector
              Container(
                decoration: BoxDecoration(
                  color: AppColors.bgSecondary,
                  border: Border.all(color: AppColors.borderSubtle),
                  borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
                ),
                child: Column(
                  children: [
                    _buildDifficultyOption(
                      'easy',
                      'Easy',
                      'NPCs are helpful and share info easily',
                    ),
                    Divider(height: 1, color: AppColors.borderSubtle),
                    _buildDifficultyOption(
                      'medium',
                      'Medium',
                      'Realistic - need to build some rapport',
                    ),
                    Divider(height: 1, color: AppColors.borderSubtle),
                    _buildDifficultyOption(
                      'hard',
                      'Hard',
                      'NPCs are suspicious and cautious',
                    ),
                  ],
                ),
              ),

              SizedBox(height: AppDimensions.spaceLG),

              // Objectives preview
              Container(
                padding: EdgeInsets.all(AppDimensions.cardPadding),
                decoration: BoxDecoration(
                  color: AppColors.bgTertiary,
                  border: Border.all(color: AppColors.accentPrimary),
                  borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'YOUR OBJECTIVES',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textTertiary,
                        letterSpacing: 1,
                      ),
                    ),
                    SizedBox(height: AppDimensions.spaceSM),
                    ...widget.objectives.map((obj) {
                      return Padding(
                        padding: EdgeInsets.only(bottom: AppDimensions.spaceXS),
                        child: Text(
                          '• ${obj.description}',
                          style: TextStyle(
                            fontSize: 13,
                            color: AppColors.textPrimary,
                          ),
                        ),
                      );
                    }).toList(),
                  ],
                ),
              ),

              SizedBox(height: AppDimensions.spaceLG),

              // Start button
              HeistPrimaryButton(
                text: 'Start Conversation',
                onPressed: _startConversation,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDifficultyOption(String value, String title, String description) {
    final isSelected = _difficulty == value;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          setState(() {
            _difficulty = value;
          });
        },
        child: Container(
          padding: EdgeInsets.all(AppDimensions.cardPadding),
          child: Row(
            children: [
              Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: isSelected
                        ? AppColors.accentPrimary
                        : AppColors.borderSubtle,
                    width: 2,
                  ),
                  color: isSelected
                      ? AppColors.accentPrimary
                      : Colors.transparent,
                ),
                child: isSelected
                    ? Icon(
                        Icons.check,
                        size: 16,
                        color: AppColors.bgPrimary,
                      )
                    : null,
              ),
              SizedBox(width: AppDimensions.spaceMD),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: isSelected
                            ? AppColors.textPrimary
                            : AppColors.textSecondary,
                      ),
                    ),
                    Text(
                      description,
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textTertiary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
