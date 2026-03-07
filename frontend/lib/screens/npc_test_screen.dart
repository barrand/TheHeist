import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../core/app_config.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_dimensions.dart';
import '../models/npc.dart';
import '../services/backend_service.dart';
import 'npc_conversation_screen.dart';

class NpcTestScreen extends StatefulWidget {
  const NpcTestScreen({Key? key}) : super(key: key);

  @override
  State<NpcTestScreen> createState() => _NpcTestScreenState();
}

class _NpcTestScreenState extends State<NpcTestScreen> {
  List<Map<String, dynamic>> _scenarios = [];
  List<Map<String, dynamic>> _npcs = [];
  String? _roomCode;
  String? _playerId;
  String? _selectedScenario;
  String _difficulty = 'easy';
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadScenarios();
  }

  Future<void> _loadScenarios() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final url = Uri.parse('${AppConfig.backendUrl}/api/npc/test-scenarios');
      final resp = await http.get(url);
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as List;
        setState(() {
          _scenarios = data.cast<Map<String, dynamic>>();
          _isLoading = false;
        });
      } else {
        setState(() { _error = 'Failed to load scenarios: ${resp.statusCode}'; _isLoading = false; });
      }
    } catch (e) {
      setState(() { _error = 'Error: $e'; _isLoading = false; });
    }
  }

  Future<void> _setupTest(Map<String, dynamic> scenario) async {
    setState(() { _isLoading = true; _error = null; });
    final scenarioId = scenario['scenario_id'] as String;
    final roles = (scenario['roles'] as List).cast<String>().join(',');
    try {
      final url = Uri.parse(
        '${AppConfig.backendUrl}/api/npc/test-setup?scenario_id=$scenarioId&roles=$roles&difficulty=$_difficulty',
      );
      final resp = await http.post(url);
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        setState(() {
          _roomCode = data['room_code'] as String;
          _playerId = data['player_id'] as String;
          _npcs = (data['npcs'] as List).cast<Map<String, dynamic>>();
          _selectedScenario = scenarioId;
          _isLoading = false;
        });
      } else {
        setState(() { _error = 'Setup failed: ${resp.body}'; _isLoading = false; });
      }
    } catch (e) {
      setState(() { _error = 'Error: $e'; _isLoading = false; });
    }
  }

  void _openConversation(Map<String, dynamic> npcData) {
    final coverOptionsRaw = npcData['cover_options'] as List<dynamic>? ?? [];
    final coverOptions = coverOptionsRaw
        .map((c) => CoverOption.fromJson(Map<String, dynamic>.from(c)))
        .toList();

    final npc = NPC(
      id: npcData['id'] ?? '',
      name: npcData['name'] ?? 'Unknown',
      role: npcData['role'] ?? '',
      personality: npcData['personality'] ?? '',
      location: npcData['location'] ?? '',
      coverOptions: coverOptions,
    );

    final targetOutcomes = (npcData['target_outcomes'] as List<dynamic>? ?? []).cast<String>();
    final missionBrief = npcData['task_description'] as String? ?? '';

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => NPCConversationScreen(
          npc: npc,
          objectives: const [],
          apiKey: '',
          difficulty: _difficulty,
          scenarioId: _selectedScenario,
          roomCode: _roomCode,
          playerId: _playerId,
          targetOutcomes: targetOutcomes,
          missionBrief: missionBrief,
        ),
      ),
    );
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
        title: Text('NPC Conversation Tester',
            style: TextStyle(color: AppColors.textPrimary, fontSize: 18)),
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator(color: AppColors.accentPrimary))
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.error_outline, color: AppColors.danger, size: 48),
                        const SizedBox(height: 12),
                        Text(_error!, style: TextStyle(color: AppColors.danger), textAlign: TextAlign.center),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _loadScenarios,
                          style: ElevatedButton.styleFrom(backgroundColor: AppColors.accentPrimary),
                          child: Text('Retry', style: TextStyle(color: AppColors.textPrimary)),
                        ),
                      ],
                    ),
                  ),
                )
              : _npcs.isNotEmpty
                  ? _buildNpcPicker()
                  : _buildScenarioPicker(),
    );
  }

  Widget _buildScenarioPicker() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('DIFFICULTY',
              style: TextStyle(
                  color: AppColors.textTertiary,
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 1.2)),
          const SizedBox(height: 8),
          _buildDifficultyToggle(),
          const SizedBox(height: 24),

          Text('PICK A SCENARIO',
              style: TextStyle(
                  color: AppColors.textTertiary,
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 1.2)),
          const SizedBox(height: 12),

          if (_scenarios.isEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 40),
              child: Text(
                'No generated scenarios found.\nGenerate one first by starting a game.',
                textAlign: TextAlign.center,
                style: TextStyle(color: AppColors.textSecondary, fontSize: 14),
              ),
            ),

          for (final s in _scenarios) ...[
            _buildScenarioCard(s),
            const SizedBox(height: 12),
          ],
        ],
      ),
    );
  }

  Widget _buildDifficultyToggle() {
    return Row(
      children: ['easy', 'medium', 'hard'].map((d) {
        final isSelected = _difficulty == d;
        return Expanded(
          child: GestureDetector(
            onTap: () => setState(() => _difficulty = d),
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 4),
              padding: const EdgeInsets.symmetric(vertical: 10),
              decoration: BoxDecoration(
                color: isSelected ? AppColors.accentPrimary : AppColors.bgSecondary,
                borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                border: Border.all(
                  color: isSelected ? AppColors.accentPrimary : AppColors.borderSubtle,
                ),
              ),
              child: Text(
                d[0].toUpperCase() + d.substring(1),
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: isSelected ? AppColors.bgPrimary : AppColors.textSecondary,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  fontSize: 13,
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildScenarioCard(Map<String, dynamic> scenario) {
    final scenarioId = scenario['scenario_id'] as String? ?? '?';
    final roles = (scenario['roles'] as List?)?.cast<String>() ?? [];
    final displayName = scenarioId.replaceAll('_', ' ').split(' ').map((w) =>
      w.isEmpty ? w : w[0].toUpperCase() + w.substring(1)
    ).join(' ');

    return GestureDetector(
      onTap: () => _setupTest(scenario),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.bgSecondary,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          border: Border.all(color: AppColors.borderSubtle),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(displayName,
                style: TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 16,
                    fontWeight: FontWeight.bold)),
            const SizedBox(height: 6),
            Wrap(
              spacing: 6,
              runSpacing: 4,
              children: roles.map((r) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.accentPrimary.withAlpha(30),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  r.replaceAll('_', ' '),
                  style: TextStyle(color: AppColors.accentPrimary, fontSize: 11),
                ),
              )).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNpcPicker() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              GestureDetector(
                onTap: () => setState(() { _npcs = []; _roomCode = null; _playerId = null; }),
                child: Row(
                  children: [
                    Icon(Icons.arrow_back_ios, color: AppColors.accentPrimary, size: 14),
                    Text('Back to scenarios',
                        style: TextStyle(color: AppColors.accentPrimary, fontSize: 13)),
                  ],
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.bgTertiary,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  _difficulty.toUpperCase(),
                  style: TextStyle(color: AppColors.textTertiary, fontSize: 10, letterSpacing: 1),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          Text('PICK AN NPC TO TALK TO',
              style: TextStyle(
                  color: AppColors.textTertiary,
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 1.2)),
          const SizedBox(height: 12),

          for (final npc in _npcs) ...[
            _buildNpcCard(npc),
            const SizedBox(height: 12),
          ],
        ],
      ),
    );
  }

  Widget _buildNpcCard(Map<String, dynamic> npc) {
    final name = npc['name'] as String? ?? 'Unknown';
    final role = npc['role'] as String? ?? '';
    final personality = npc['personality'] as String? ?? '';
    final location = npc['location'] as String? ?? '';
    final taskDesc = npc['task_description'] as String? ?? '';
    final outcomes = (npc['target_outcomes'] as List?)?.cast<String>() ?? [];

    return GestureDetector(
      onTap: () => _openConversation(npc),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.bgSecondary,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          border: Border.all(color: AppColors.borderSubtle),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 22,
                  backgroundColor: AppColors.accentPrimary.withAlpha(40),
                  child: Icon(Icons.person, color: AppColors.accentPrimary, size: 24),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(name,
                          style: TextStyle(
                              color: AppColors.textPrimary,
                              fontSize: 16,
                              fontWeight: FontWeight.bold)),
                      Text(role,
                          style: TextStyle(color: AppColors.accentPrimary, fontSize: 13)),
                    ],
                  ),
                ),
                Icon(Icons.chat_bubble_outline, color: AppColors.accentPrimary, size: 20),
              ],
            ),

            if (personality.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(personality,
                  style: TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 12,
                      fontStyle: FontStyle.italic),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis),
            ],

            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.location_on, color: AppColors.textTertiary, size: 13),
                const SizedBox(width: 4),
                Text(location.replaceAll('_', ' '),
                    style: TextStyle(color: AppColors.textTertiary, fontSize: 11)),
              ],
            ),

            if (taskDesc.isNotEmpty) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.bgPrimary,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('OBJECTIVE',
                        style: TextStyle(
                            color: AppColors.textTertiary,
                            fontSize: 9,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 1)),
                    const SizedBox(height: 4),
                    Text(taskDesc,
                        style: TextStyle(color: AppColors.textPrimary, fontSize: 12)),
                    if (outcomes.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Wrap(
                        spacing: 4,
                        runSpacing: 4,
                        children: outcomes.map((o) => Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.accentPrimary.withAlpha(20),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            o.replaceAll('_', ' '),
                            style: TextStyle(color: AppColors.accentPrimary, fontSize: 10),
                          ),
                        )).toList(),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
