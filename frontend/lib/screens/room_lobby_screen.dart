import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:the_heist/core/app_config.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';
import 'package:the_heist/models/role.dart';
import 'package:the_heist/models/scenario.dart';
import 'package:the_heist/services/roles_service.dart';
import 'package:the_heist/services/scenarios_service.dart';
import 'package:the_heist/services/websocket_service.dart';
import 'package:the_heist/widgets/common/heist_primary_button.dart';
import 'package:the_heist/widgets/common/top_toast.dart';
import 'package:the_heist/widgets/common/section_header.dart';
import 'package:the_heist/widgets/modals/scenario_selection_modal.dart';
import 'package:the_heist/screens/scenario_details_screen.dart';

/// Simplified lobby: room code, player list, scenario picker, Continue button.
/// Role selection now lives on ScenarioDetailsScreen.
class RoomLobbyScreen extends StatefulWidget {
  final String roomCode;
  final String playerName;
  final WebSocketService wsService;

  const RoomLobbyScreen({
    super.key,
    required this.roomCode,
    required this.playerName,
    required this.wsService,
  });

  @override
  State<RoomLobbyScreen> createState() => _RoomLobbyScreenState();
}

class _RoomLobbyScreenState extends State<RoomLobbyScreen> {
  List<Map<String, dynamic>> _players = [];
  String? _myPlayerId;
  bool _isHost = false;
  String _selectedScenarioId = 'museum_gala_vault';

  List<Role> _availableRoles = [];
  List<Scenario> _availableScenarios = [];
  bool _scenariosLoading = true;

  final List<StreamSubscription> _subs = [];

  @override
  void initState() {
    super.initState();
    _loadData();
    _setupWebSocketListeners();
  }

  @override
  void dispose() {
    for (final sub in _subs) {
      sub.cancel();
    }
    super.dispose();
  }

  Future<void> _loadData() async {
    final roles = await RolesService.loadRoles();
    final scenarios = await ScenariosService.loadScenarios();
    if (!mounted) return;
    setState(() {
      _availableRoles = roles;
      _availableScenarios = scenarios;
      _scenariosLoading = false;
    });
    // Send the default scenario selection to the backend so it's set
    // even if the host never opens the scenario picker
    if (_isHost) {
      widget.wsService.selectScenario(_selectedScenarioId);
    }
  }

  void _setupWebSocketListeners() {
    final latestState = widget.wsService.latestRoomState;
    if (latestState != null) {
      _processRoomState(latestState);
    }

    _subs.add(widget.wsService.roomState.listen((msg) {
      _processRoomState(msg);
    }));

    _subs.add(widget.wsService.playerJoined.listen((msg) {
      setState(() => _players.add(msg['player']));
      _showToast('${msg['player']['name']} joined');
    }));

    _subs.add(widget.wsService.scenarioSelected.listen((msg) {
      setState(() {
        _selectedScenarioId = msg['scenario_id'] as String;
      });
    }));

    _subs.add(widget.wsService.lobbyAdvanced.listen((msg) {
      _navigateToScenarioDetails();
    }));

    _subs.add(widget.wsService.errors.listen((msg) {
      _showToast(msg['message'] ?? 'An error occurred', isError: true);
    }));
  }

  void _processRoomState(Map<String, dynamic> message) {
    setState(() {
      _players = List<Map<String, dynamic>>.from(message['players'] ?? []);
      _myPlayerId = message['your_player_id'];
      final isHostValue = message['is_host'];
      _isHost = isHostValue == true || isHostValue == 'true' || isHostValue == 1;

      if (message['scenario'] != null) {
        _selectedScenarioId = message['scenario'] as String;
      }
    });

    // If the room is already in SETUP, jump straight to scenario details
    if (message['status'] == 'setup') {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _navigateToScenarioDetails();
      });
    }
  }

  void _showToast(String message, {bool isError = false}) {
    showTopToast(context, message, color: isError ? AppColors.danger : AppColors.success);
  }

  void _copyRoomCode() {
    Clipboard.setData(ClipboardData(text: widget.roomCode));
    _showToast('Room code copied');
  }

  void _onSelectScenario(String scenarioId) {
    widget.wsService.selectScenario(scenarioId);
    setState(() => _selectedScenarioId = scenarioId);
  }

  void _onContinue() {
    if (!_isHost) return;
    if (_players.length < 2) {
      _showToast('Need at least 2 players', isError: true);
      return;
    }
    widget.wsService.lobbyAdvance();
  }

  void _navigateToScenarioDetails() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => ScenarioDetailsScreen(
          roomCode: widget.roomCode,
          playerName: widget.playerName,
          wsService: widget.wsService,
          scenarioId: _selectedScenarioId,
          players: _players,
          myPlayerId: _myPlayerId,
          isHost: _isHost,
          availableRoles: _availableRoles,
          availableScenarios: _availableScenarios,
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Build
  // ---------------------------------------------------------------------------

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        title: const Text('Room Lobby'),
        backgroundColor: AppColors.bgSecondary,
        actions: [
          IconButton(
            icon: const Icon(Icons.exit_to_app),
            onPressed: () {
              widget.wsService.disconnect();
              Navigator.of(context).pop();
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: EdgeInsets.all(AppDimensions.space2XL),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildRoomCodeCard(),
                SizedBox(height: AppDimensions.space2XL),
                _buildScenarioSection(),
                SizedBox(height: AppDimensions.space2XL),
                const SectionHeader(text: 'Players'),
                SizedBox(height: AppDimensions.spaceMD),
                _buildPlayersList(),
                SizedBox(height: AppDimensions.space2XL),
                _buildContinueSection(),
                SizedBox(height: AppDimensions.spaceLG),
                _buildLeaveRoomButton(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRoomCodeCard() {
    return Container(
      padding: EdgeInsets.all(AppDimensions.containerPadding),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
        border: Border.all(color: AppColors.accentPrimary, width: 2),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Room Code: ${widget.roomCode}',
                  style: TextStyle(
                    color: AppColors.accentPrimary,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 4,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '(${_players.length} of 12 players)',
                  style: TextStyle(color: AppColors.textSecondary, fontSize: 14),
                ),
              ],
            ),
          ),
          IconButton(
            icon: Icon(Icons.copy, color: AppColors.accentPrimary, size: 28),
            onPressed: _copyRoomCode,
            tooltip: 'Copy Room Code',
          ),
        ],
      ),
    );
  }

  Widget _buildScenarioSection() {
    if (_scenariosLoading) {
      return Center(child: CircularProgressIndicator(color: AppColors.accentPrimary));
    }
    if (_availableScenarios.isEmpty) {
      return Center(child: Text('No scenarios available', style: TextStyle(color: AppColors.textSecondary)));
    }

    final selectedScenario = _availableScenarios.firstWhere(
      (s) => s.scenarioId == _selectedScenarioId,
      orElse: () => _availableScenarios.first,
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text('🎬', style: TextStyle(fontSize: 20)),
            const SizedBox(width: 8),
            Text(
              'SCENARIO',
              style: TextStyle(
                color: AppColors.textTertiary,
                fontSize: 12,
                fontWeight: FontWeight.w600,
                letterSpacing: 1,
              ),
            ),
          ],
        ),
        SizedBox(height: AppDimensions.spaceMD),
        InkWell(
          onTap: _isHost
              ? () {
                  showDialog(
                    context: context,
                    builder: (_) => ScenarioSelectionModal(
                      availableScenarios: _availableScenarios,
                      currentScenarioId: _selectedScenarioId,
                      availableRoles: _availableRoles,
                      onSelectScenario: _onSelectScenario,
                    ),
                  );
                }
              : null,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          child: Container(
            padding: EdgeInsets.all(AppDimensions.spaceLG),
            decoration: BoxDecoration(
              color: AppColors.bgSecondary,
              borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
              border: Border.all(
                color: _isHost ? AppColors.accentPrimary : AppColors.borderSubtle,
                width: _isHost ? 2 : 1,
              ),
            ),
            child: Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
                  child: Image.asset(
                    'assets/static/${selectedScenario.scenarioId}.png',
                    width: 80,
                    height: 80,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Container(
                      width: 80,
                      height: 80,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: AppColors.bgTertiary,
                        borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
                      ),
                      child: Text(selectedScenario.themeIcon, style: const TextStyle(fontSize: 40)),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        selectedScenario.name,
                        style: TextStyle(color: AppColors.textPrimary, fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        selectedScenario.objective,
                        style: TextStyle(color: AppColors.textSecondary, fontSize: 12),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                if (_isHost) Icon(Icons.chevron_right, color: AppColors.textSecondary),
              ],
            ),
          ),
        ),
        if (_isHost) ...[
          const SizedBox(height: 4),
          Text('Tap to browse all scenarios', style: TextStyle(color: AppColors.textTertiary, fontSize: 12)),
        ],
      ],
    );
  }

  Widget _buildPlayersList() {
    if (_players.isEmpty) {
      return Container(
        padding: EdgeInsets.all(AppDimensions.spaceLG),
        decoration: BoxDecoration(
          color: AppColors.bgSecondary,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
        ),
        child: Text(
          'Waiting for players...',
          style: TextStyle(color: AppColors.textSecondary, fontSize: 14, fontStyle: FontStyle.italic),
        ),
      );
    }

    return Container(
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
      ),
      child: Column(
        children: _players.asMap().entries.map((entry) {
          final player = entry.value;
          final isMe = player['id'] == _myPlayerId;
          final isPlayerHost = entry.key == 0;

          return Container(
            padding: EdgeInsets.all(AppDimensions.spaceLG),
            decoration: BoxDecoration(
              border: Border(
                bottom: entry.key < _players.length - 1
                    ? BorderSide(color: AppColors.borderSubtle, width: 1)
                    : BorderSide.none,
              ),
            ),
            child: Row(
              children: [
                Text(isPlayerHost ? '👑' : '👤', style: const TextStyle(fontSize: 20)),
                SizedBox(width: AppDimensions.spaceSM),
                Expanded(
                  child: Text(
                    isMe ? 'You' : player['name'] ?? 'Unknown',
                    style: TextStyle(color: AppColors.textPrimary, fontSize: 16, fontWeight: FontWeight.w500),
                  ),
                ),
                Icon(Icons.circle, color: AppColors.success, size: 10),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildContinueSection() {
    if (!_isHost) {
      return Container(
        padding: EdgeInsets.all(AppDimensions.spaceMD),
        decoration: BoxDecoration(
          color: AppColors.bgSecondary,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
        ),
        child: Row(
          children: [
            SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.accentPrimary),
            ),
            const SizedBox(width: 12),
            Text(
              'Waiting for host to continue...',
              style: TextStyle(color: AppColors.textSecondary, fontSize: 14, fontStyle: FontStyle.italic),
            ),
          ],
        ),
      );
    }

    final canContinue = _players.length >= 2;

    return Column(
      children: [
        if (!canContinue)
          Container(
            padding: EdgeInsets.all(AppDimensions.spaceMD),
            margin: EdgeInsets.only(bottom: AppDimensions.spaceMD),
            decoration: BoxDecoration(
              color: AppColors.danger.withAlpha(26),
              borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
              border: Border.all(color: AppColors.danger.withAlpha(128)),
            ),
            child: Row(
              children: [
                Icon(Icons.warning, color: AppColors.danger, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Need at least ${2 - _players.length} more player to continue',
                    style: TextStyle(color: AppColors.danger, fontSize: 14, fontWeight: FontWeight.w500),
                  ),
                ),
              ],
            ),
          ),
        if (canContinue)
          Padding(
            padding: EdgeInsets.only(bottom: AppDimensions.spaceSM),
            child: Text(
              'When your crew is here, hit Continue',
              style: TextStyle(color: AppColors.textSecondary, fontSize: 13),
              textAlign: TextAlign.center,
            ),
          ),
        HeistPrimaryButton(
          text: 'Continue',
          onPressed: canContinue ? _onContinue : null,
          icon: Icons.arrow_forward,
        ),
      ],
    );
  }

  Widget _buildLeaveRoomButton() {
    return Center(
      child: TextButton(
        onPressed: () {
          widget.wsService.disconnect();
          Navigator.of(context).pop();
        },
        child: Text(
          'Leave Room',
          style: TextStyle(color: AppColors.textSecondary, fontSize: 14, decoration: TextDecoration.underline),
        ),
      ),
    );
  }
}
