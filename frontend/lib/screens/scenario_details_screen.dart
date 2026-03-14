import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';
import 'package:the_heist/models/role.dart';
import 'package:the_heist/models/scenario.dart';
import 'package:the_heist/services/backend_service.dart';
import 'package:the_heist/services/websocket_service.dart';
import 'package:the_heist/widgets/common/heist_primary_button.dart';
import 'package:the_heist/widgets/common/top_toast.dart';
import 'package:the_heist/widgets/modals/role_selection_modal.dart';
import 'package:the_heist/screens/game_screen.dart';
import 'package:the_heist/screens/room_lobby_screen.dart';

/// Screen where players see Quick Start / Custom options and claim roles.
class ScenarioDetailsScreen extends StatefulWidget {
  final String roomCode;
  final String playerName;
  final WebSocketService wsService;
  final String scenarioId;
  final List<Map<String, dynamic>> players;
  final String? myPlayerId;
  final bool isHost;
  final List<Role> availableRoles;
  final List<Scenario> availableScenarios;

  const ScenarioDetailsScreen({
    super.key,
    required this.roomCode,
    required this.playerName,
    required this.wsService,
    required this.scenarioId,
    required this.players,
    required this.myPlayerId,
    required this.isHost,
    required this.availableRoles,
    required this.availableScenarios,
  });

  @override
  State<ScenarioDetailsScreen> createState() => _ScenarioDetailsScreenState();
}

class _ScenarioDetailsScreenState extends State<ScenarioDetailsScreen> {
  late List<Map<String, dynamic>> _players;
  late String? _myPlayerId;
  late bool _isHost;
  String? _myRole;
  String _myDifficulty = 'medium';

  List<Map<String, dynamic>> _quickScenarios = [];
  bool _quickLoading = true;

  bool _isGenerating = false;
  String _generationTitle = 'Building Your Scenario';
  final List<String> _generationSteps = [];

  StreamSubscription? _modalSub;
  ScrollController? _modalScrollController;

  static const _heistMessages = [
    'Prepping the getaway car...',
    'Investigating the premises...',
    'Reaching out to seedy contacts...',
    'Reviewing the blueprints...',
    'Preparing disguises...',
  ];

  final List<StreamSubscription> _subs = [];
  final Map<String, String> _roleGenders = {};
  final _rng = Random();

  String _genderFor(String roleId) {
    return _roleGenders.putIfAbsent(roleId, () => _rng.nextBool() ? 'female' : 'male');
  }

  @override
  void initState() {
    super.initState();
    _players = List<Map<String, dynamic>>.from(widget.players);
    _myPlayerId = widget.myPlayerId;
    _isHost = widget.isHost;
    _setupListeners();
    _loadQuickScenarios();
  }

  @override
  void dispose() {
    for (final sub in _subs) {
      sub.cancel();
    }
    super.dispose();
  }

  void _setupListeners() {
    _subs.add(widget.wsService.roleSelected.listen((msg) {
      setState(() {
        final pid = msg['player_id'];
        final role = msg['role'];
        final difficulty = msg['difficulty'] ?? 'medium';
        final idx = _players.indexWhere((p) => p['id'] == pid);
        if (idx != -1) {
          _players[idx]['role'] = role;
          _players[idx]['difficulty'] = difficulty;
        }
        if (pid == _myPlayerId) {
          _myRole = (role == null || role == '') ? null : role;
          _myDifficulty = difficulty;
        }
      });
    }));

    _subs.add(widget.wsService.lobbyRetreated.listen((_) {
      _navigateBackToLobby();
    }));

    _subs.add(widget.wsService.scenarioGenerating.listen((msg) {
      final text = msg['message'] as String? ?? '';
      final isImagePhase = text.startsWith('🖼️') || text.startsWith('🎨') || text.startsWith('🎭 Sketching');
      final isPrepPhase = text.startsWith('🎯');
      if (!_isGenerating) {
        setState(() {
          _isGenerating = true;
          _generationSteps.clear();
          _generationTitle = isImagePhase
              ? 'Creating Images'
              : isPrepPhase
                  ? 'Preparing'
                  : 'Building Your Scenario';
          _generationSteps.add(text);
        });
        _showGenerationModal();
      } else {
        setState(() {
          if (isImagePhase) _generationTitle = 'Creating Images';
          final isCount = text.contains(RegExp(r'\(\d+/\d+\)'));
          if (isCount && _generationSteps.isNotEmpty) {
            _generationSteps.last = text;
          } else {
            _generationSteps.add(text);
          }
        });
      }
    }));

    _subs.add(widget.wsService.gameStarted.listen((msg) {
      if (_isGenerating && Navigator.canPop(context)) {
        Navigator.of(context).pop();
        _dismissGenerationModal();
        _isGenerating = false;
      }
      _navigateToGame(msg);
    }));

    _subs.add(widget.wsService.errors.listen((msg) {
      showTopToast(context, msg['message'] ?? 'Error', color: AppColors.danger);
    }));
  }

  Future<void> _loadQuickScenarios() async {
    final results = await BackendService().getQuickScenarios(_players.length);
    if (!mounted) return;
    setState(() {
      _quickScenarios = results;
      _quickLoading = false;
    });
  }

  // ---------------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------------

  void _claimRole(String roleId) {
    final taken = _players.any((p) => p['role'] == roleId && p['id'] != _myPlayerId);
    if (taken) {
      showTopToast(context, 'Role already taken', color: AppColors.danger);
      return;
    }
    widget.wsService.selectRole(roleId, difficulty: _myDifficulty);
    setState(() => _myRole = roleId);
  }

  void _changeDifficulty(String d) {
    setState(() => _myDifficulty = d);
    if (_myRole != null) {
      widget.wsService.selectRole(_myRole!, difficulty: d);
    }
  }

  void _onStartGame() {
    if (!_isHost) return;
    final allHaveRoles = _players.isNotEmpty && _players.every((p) => p['role'] != null && p['role'] != '');
    if (!allHaveRoles) {
      showTopToast(context, 'All players must pick a role', color: AppColors.danger);
      return;
    }
    widget.wsService.startGame(widget.scenarioId);
  }

  void _onBack() {
    if (_isHost) {
      widget.wsService.lobbyRetreat();
    }
  }

  void _navigateBackToLobby() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => RoomLobbyScreen(
          roomCode: widget.roomCode,
          playerName: widget.playerName,
          wsService: widget.wsService,
        ),
      ),
    );
  }

  void _navigateToGame(Map<String, dynamic> msg) {
    final briefing = msg['briefing'] as Map<String, dynamic>?;
    final hasBriefing = briefing != null &&
        (briefing['overview'] as String? ?? '').isNotEmpty;

    if (hasBriefing) {
      _showBriefingModal(briefing!, msg);
    } else {
      _pushGameScreen(msg);
    }
  }

  void _pushGameScreen(Map<String, dynamic> msg) {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => GameScreen(
          wsService: widget.wsService,
          scenario: msg['scenario'],
          experienceId: msg['experience_id'] ?? msg['scenario'],
          objective: msg['objective'],
          yourTasks: msg['your_tasks'] ?? [],
          playerRole: _myRole,
          allPlayers: _players,
          myPlayerId: _myPlayerId,
          roomCode: widget.roomCode,
          locations: List<Map<String, dynamic>>.from(msg['locations'] ?? []),
          npcs: List<Map<String, dynamic>>.from(msg['npcs'] ?? []),
          startingLocation: msg['starting_location'] as String?,
        ),
      ),
    );
  }

  void _showBriefingModal(Map<String, dynamic> briefing, Map<String, dynamic> gameMsg) {
    final overview = briefing['overview'] as String? ?? '';
    final roleBriefings = briefing['role_briefings'] as Map<String, dynamic>? ?? {};
    final myBriefing = _myRole != null ? roleBriefings[_myRole] as String? ?? '' : '';

    showDialog(
      context: context,
      barrierDismissible: false,
      barrierColor: Colors.black.withOpacity(0.92),
      builder: (ctx) => PopScope(
        canPop: false,
        child: Dialog(
          backgroundColor: AppColors.bgPrimary,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
            side: BorderSide(color: AppColors.accentPrimary, width: 2),
          ),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 440),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(AppDimensions.radiusLG),
                      topRight: Radius.circular(AppDimensions.radiusLG),
                    ),
                    child: AspectRatio(
                      aspectRatio: 16 / 9,
                      child: Image.asset(
                        'assets/static/${widget.scenarioId}.png',
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => const SizedBox.shrink(),
                      ),
                    ),
                  ),
                  Padding(
                    padding: EdgeInsets.all(AppDimensions.spaceXL),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Center(
                          child: Text(
                            'MISSION BRIEFING',
                            style: TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                              color: AppColors.accentPrimary,
                              letterSpacing: 2,
                            ),
                          ),
                        ),
                        SizedBox(height: AppDimensions.spaceLG),
                        if (overview.isNotEmpty) ...[
                          Text(
                            overview,
                            style: TextStyle(
                              color: AppColors.textPrimary,
                              fontSize: 15,
                              fontStyle: FontStyle.italic,
                              height: 1.5,
                            ),
                          ),
                          SizedBox(height: AppDimensions.spaceLG),
                        ],
                        if (myBriefing.isNotEmpty) ...[
                          Text(
                            'YOUR ROLE',
                            style: TextStyle(
                              color: AppColors.accentPrimary,
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 1,
                            ),
                          ),
                          SizedBox(height: AppDimensions.spaceSM),
                          Container(
                            padding: EdgeInsets.all(AppDimensions.spaceMD),
                            decoration: BoxDecoration(
                              color: AppColors.accentPrimary.withAlpha(20),
                              borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                              border: Border.all(color: AppColors.accentPrimary.withAlpha(80)),
                            ),
                            child: Text(
                              myBriefing,
                              style: TextStyle(
                                color: AppColors.textPrimary,
                                fontSize: 14,
                                height: 1.5,
                              ),
                            ),
                          ),
                          SizedBox(height: AppDimensions.spaceLG),
                        ],
                        SizedBox(
                          width: double.infinity,
                          child: HeistPrimaryButton(
                            text: 'BEGIN HEIST',
                            onPressed: () {
                              Navigator.of(ctx).pop();
                              _pushGameScreen(gameMsg);
                            },
                            icon: Icons.play_arrow,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _openCustomRolePicker() {
    showDialog(
      context: context,
      builder: (_) => RoleSelectionModal(
        availableRoles: widget.availableRoles,
        currentRole: _myRole,
        players: _players,
        onSelectRole: _claimRole,
        initialGender: 'female',
      ),
    );
  }

  void _dismissGenerationModal() {
    _modalSub?.cancel();
    _modalSub = null;
    _modalScrollController?.dispose();
    _modalScrollController = null;
  }

  void _showGenerationModal() {
    _modalScrollController = ScrollController();

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => PopScope(
        canPop: false,
        child: StatefulBuilder(
          builder: (ctx, setModalState) {
            _modalSub ??= widget.wsService.scenarioGenerating.listen((_) {
              setModalState(() {});
              WidgetsBinding.instance.addPostFrameCallback((_) {
                if (_modalScrollController?.hasClients ?? false) {
                  _modalScrollController!.animateTo(
                    _modalScrollController!.position.maxScrollExtent,
                    duration: const Duration(milliseconds: 200),
                    curve: Curves.easeOut,
                  );
                }
              });
            });
            return Dialog(
              backgroundColor: AppColors.bgPrimary,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
                side: BorderSide(color: AppColors.accentPrimary, width: 2),
              ),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 400, maxHeight: 480),
                child: Padding(
                  padding: EdgeInsets.all(AppDimensions.spaceXL),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        _generationTitle,
                        style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.accentPrimary),
                      ),
                      SizedBox(height: AppDimensions.spaceMD),
                      SizedBox(width: 28, height: 28, child: CircularProgressIndicator(strokeWidth: 3, valueColor: AlwaysStoppedAnimation(AppColors.accentPrimary))),
                      SizedBox(height: AppDimensions.spaceMD),
                      if (_generationSteps.isNotEmpty)
                        Flexible(
                          child: ListView.builder(
                            controller: _modalScrollController,
                            shrinkWrap: true,
                            itemCount: _generationSteps.length,
                            itemBuilder: (_, i) {
                              final isLatest = i == _generationSteps.length - 1;
                              return Padding(
                                padding: const EdgeInsets.symmetric(vertical: 3),
                                child: Text(
                                  _generationSteps[i],
                                  style: TextStyle(
                                    fontSize: isLatest ? 15 : 13,
                                    color: isLatest ? AppColors.textPrimary : AppColors.textSecondary.withAlpha(128),
                                    fontWeight: isLatest ? FontWeight.w600 : FontWeight.normal,
                                  ),
                                ),
                              );
                            },
                          ),
                        )
                      else
                        StreamBuilder<int>(
                          stream: Stream.periodic(const Duration(seconds: 2), (i) => i % _heistMessages.length),
                          builder: (_, snap) {
                            final idx = snap.data ?? 0;
                            return AnimatedSwitcher(
                              duration: const Duration(milliseconds: 300),
                              child: Text(_heistMessages[idx], key: ValueKey(idx), style: TextStyle(fontSize: 16, color: AppColors.textSecondary), textAlign: TextAlign.center),
                            );
                          },
                        ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Build
  // ---------------------------------------------------------------------------

  @override
  Widget build(BuildContext context) {
    final scenario = widget.availableScenarios.firstWhere(
      (s) => s.scenarioId == widget.scenarioId,
      orElse: () => widget.availableScenarios.first,
    );

    final allHaveRoles = _players.isNotEmpty && _players.every((p) => p['role'] != null && p['role'] != '');
    final playersWithoutRoles = _players.where((p) => p['role'] == null || p['role'] == '').length;

    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        title: const Text('Scenario Details'),
        backgroundColor: AppColors.bgSecondary,
        leading: _isHost
            ? IconButton(icon: const Icon(Icons.arrow_back), onPressed: _onBack)
            : null,
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: EdgeInsets.all(AppDimensions.space2XL),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Scenario header
                _buildScenarioHeader(scenario),
                SizedBox(height: AppDimensions.space2XL),

                // Quick Start section
                if (!_quickLoading && _quickScenarios.isNotEmpty) ...[
                  _buildQuickStartSection(),
                  SizedBox(height: AppDimensions.space2XL),
                ],

                // Custom section
                _buildCustomSection(),
                SizedBox(height: AppDimensions.space2XL),

                // Difficulty (after claiming a role)
                if (_myRole != null) ...[
                  _buildDifficultySelector(),
                  SizedBox(height: AppDimensions.space2XL),
                ],

                // Status + Start
                _buildStatusAndStart(allHaveRoles, playersWithoutRoles),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildScenarioHeader(Scenario scenario) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Image.asset(
            'assets/static/${scenario.scenarioId}.png',
            height: 160,
            fit: BoxFit.cover,
            errorBuilder: (_, __, ___) => Container(
              height: 160,
              color: AppColors.bgTertiary,
              alignment: Alignment.center,
              child: Text(scenario.themeIcon, style: const TextStyle(fontSize: 60)),
            ),
          ),
          Padding(
            padding: EdgeInsets.all(AppDimensions.spaceLG),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  scenario.name,
                  style: TextStyle(color: AppColors.textPrimary, fontSize: 20, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 6),
                Text(
                  scenario.objective,
                  style: TextStyle(color: AppColors.textSecondary, fontSize: 14, height: 1.4),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStartSection() {
    final readyScenarios = _quickScenarios.where((q) => q['ready'] == true).toList();
    if (readyScenarios.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.flash_on, color: AppColors.accentPrimary, size: 20),
            const SizedBox(width: 8),
            Text(
              'QUICK START',
              style: TextStyle(color: AppColors.textTertiary, fontSize: 12, fontWeight: FontWeight.w600, letterSpacing: 1),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          'Ready to play — no wait!',
          style: TextStyle(color: AppColors.textSecondary, fontSize: 13),
        ),
        SizedBox(height: AppDimensions.spaceMD),
        for (final qs in readyScenarios) _buildQuickCard(qs),
      ],
    );
  }

  Widget _buildQuickCard(Map<String, dynamic> qs) {
    final roles = List<String>.from(qs['roles'] ?? []);

    return Container(
      margin: EdgeInsets.only(bottom: AppDimensions.spaceMD),
      padding: EdgeInsets.all(AppDimensions.spaceLG),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
        border: Border.all(color: AppColors.accentPrimary.withAlpha(128)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${_players.length} Players',
            style: TextStyle(color: AppColors.textSecondary, fontSize: 12, fontWeight: FontWeight.w600),
          ),
          SizedBox(height: AppDimensions.spaceMD),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: roles.map((roleId) => _buildRoleChip(roleId)).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildRoleChip(String roleId) {
    final role = widget.availableRoles.firstWhere(
      (r) => r.roleId == roleId,
      orElse: () => Role(roleId: roleId, name: roleId, description: '', minigames: [], icon: '❓'),
    );

    final claimedBy = _players.firstWhere(
      (p) => p['role'] == roleId,
      orElse: () => {},
    );
    final isClaimed = claimedBy.isNotEmpty;
    final isMe = isClaimed && claimedBy['id'] == _myPlayerId;
    final claimerName = isClaimed ? (isMe ? 'You' : claimedBy['name'] ?? '?') : null;

    final gender = _genderFor(roleId);

    return GestureDetector(
      onTap: isClaimed ? null : () => _claimRole(roleId),
      child: Container(
        width: 140,
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 10),
        decoration: BoxDecoration(
          color: isMe
              ? AppColors.accentPrimary.withAlpha(40)
              : isClaimed
                  ? AppColors.bgTertiary
                  : AppColors.bgSecondary,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          border: Border.all(
            color: isMe
                ? AppColors.accentPrimary
                : isClaimed
                    ? AppColors.borderSubtle
                    : AppColors.accentPrimary.withAlpha(128),
            width: isMe ? 2 : 1,
          ),
        ),
        child: Column(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
              child: Image.asset(
                'assets/static/${roleId}_$gender.png',
                width: 112,
                height: 112,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => Container(
                  width: 112,
                  height: 112,
                  alignment: Alignment.center,
                  child: Text(role.icon, style: const TextStyle(fontSize: 48)),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              role.name,
              style: TextStyle(color: AppColors.textPrimary, fontSize: 14, fontWeight: FontWeight.w600),
              textAlign: TextAlign.center,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            Text(
              claimerName ?? 'CLAIM',
              style: TextStyle(
                color: isClaimed
                    ? (isMe ? AppColors.accentPrimary : AppColors.textSecondary)
                    : AppColors.accentPrimary,
                fontSize: 13,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCustomSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.palette, color: AppColors.textTertiary, size: 20),
            const SizedBox(width: 8),
            Text(
              'CUSTOM GAME',
              style: TextStyle(color: AppColors.textTertiary, fontSize: 12, fontWeight: FontWeight.w600, letterSpacing: 1),
            ),
          ],
        ),
        SizedBox(height: AppDimensions.spaceMD),
        Container(
          padding: EdgeInsets.all(AppDimensions.spaceLG),
          decoration: BoxDecoration(
            color: AppColors.bgSecondary,
            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
            border: Border.all(color: AppColors.borderSubtle),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Choose any role with any scenario.',
                style: TextStyle(color: AppColors.textSecondary, fontSize: 14),
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(Icons.schedule, size: 14, color: AppColors.textSecondary),
                  const SizedBox(width: 4),
                  Text(
                    '~7 min to generate',
                    style: TextStyle(color: AppColors.textSecondary, fontSize: 12, fontWeight: FontWeight.w500),
                  ),
                ],
              ),
              SizedBox(height: AppDimensions.spaceMD),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: _openCustomRolePicker,
                  icon: const Icon(Icons.person_add, size: 18),
                  label: Text(_myRole != null ? 'Change Role' : 'Choose Your Role'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppColors.accentPrimary,
                    side: BorderSide(color: AppColors.accentPrimary),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDifficultySelector() {
    final options = ['easy', 'medium', 'hard'];
    final labels = {'easy': 'Easy', 'medium': 'Medium', 'hard': 'Hard'};

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.speed, size: 18, color: AppColors.textTertiary),
            const SizedBox(width: 8),
            Text(
              'YOUR DIFFICULTY',
              style: TextStyle(color: AppColors.textTertiary, fontSize: 12, fontWeight: FontWeight.w600, letterSpacing: 1),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            for (int i = 0; i < options.length; i++) ...[
              Expanded(
                child: GestureDetector(
                  onTap: () => _changeDifficulty(options[i]),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    decoration: BoxDecoration(
                      color: _myDifficulty == options[i]
                          ? AppColors.accentPrimary.withAlpha(51)
                          : AppColors.bgSecondary,
                      borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
                      border: Border.all(
                        color: _myDifficulty == options[i] ? AppColors.accentPrimary : AppColors.borderSubtle,
                        width: _myDifficulty == options[i] ? 2 : 1,
                      ),
                    ),
                    child: Center(
                      child: Text(
                        labels[options[i]]!,
                        style: TextStyle(
                          color: _myDifficulty == options[i] ? AppColors.accentPrimary : AppColors.textSecondary,
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              if (i < options.length - 1) const SizedBox(width: 8),
            ],
          ],
        ),
      ],
    );
  }

  Widget _buildStatusAndStart(bool allHaveRoles, int playersWithoutRoles) {
    return Column(
      children: [
        if (allHaveRoles)
          Container(
            padding: EdgeInsets.all(AppDimensions.spaceMD),
            margin: EdgeInsets.only(bottom: AppDimensions.spaceMD),
            decoration: BoxDecoration(
              color: AppColors.success.withAlpha(26),
              borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
              border: Border.all(color: AppColors.success.withAlpha(128)),
            ),
            child: Row(
              children: [
                Icon(Icons.check_circle, color: AppColors.success, size: 20),
                const SizedBox(width: 8),
                Text('All players ready!', style: TextStyle(color: AppColors.success, fontSize: 14, fontWeight: FontWeight.w600)),
              ],
            ),
          )
        else
          Padding(
            padding: EdgeInsets.only(bottom: AppDimensions.spaceMD),
            child: Text(
              'Waiting for $playersWithoutRoles more player${playersWithoutRoles == 1 ? '' : 's'} to claim a role...',
              style: TextStyle(color: AppColors.textSecondary, fontSize: 13),
              textAlign: TextAlign.center,
            ),
          ),
        if (_isHost)
          HeistPrimaryButton(
            text: 'Start Game',
            onPressed: allHaveRoles ? _onStartGame : null,
            icon: Icons.play_arrow,
          )
        else
          Container(
            padding: EdgeInsets.all(AppDimensions.spaceMD),
            decoration: BoxDecoration(
              color: AppColors.bgSecondary,
              borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.accentPrimary)),
                const SizedBox(width: 12),
                Text('Waiting for host to start...', style: TextStyle(color: AppColors.textSecondary, fontSize: 14)),
              ],
            ),
          ),
      ],
    );
  }
}
