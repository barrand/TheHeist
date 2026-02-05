import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';
import 'package:the_heist/models/role.dart';
import 'package:the_heist/models/scenario.dart';
import 'package:the_heist/services/roles_service.dart';
import 'package:the_heist/services/scenarios_service.dart';
import 'package:the_heist/services/websocket_service.dart';
import 'package:the_heist/widgets/common/heist_primary_button.dart';
import 'package:the_heist/widgets/common/heist_secondary_button.dart';
import 'package:the_heist/widgets/common/section_header.dart';
import 'package:the_heist/widgets/modals/role_selection_modal.dart';
import 'package:the_heist/widgets/modals/scenario_selection_modal.dart';
import 'package:the_heist/screens/game_screen.dart';

/// Room lobby where players join, select roles, and wait for game to start
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
  String? _myRole;
  bool _isHost = false;
  String _selectedScenarioId = 'museum_gala_vault';  // Default to Museum Gala
  
  // Available roles - loaded from roles.json
  List<Role> _availableRoles = [];
  bool _rolesLoading = true;
  
  // Available scenarios - loaded from scenarios.json
  List<Scenario> _availableScenarios = [];
  bool _scenariosLoading = true;
  
  @override
  void initState() {
    super.initState();
    debugPrint('🔧 LOBBY: initState - Setting up room lobby');
    debugPrint('🔧 LOBBY: Room code: ${widget.roomCode}');
    debugPrint('🔧 LOBBY: Player name: ${widget.playerName}');
    _loadRoles();
    _loadScenarios();
    _setupWebSocketListeners();
    
    // Request initial room state
    Future.delayed(Duration(milliseconds: 500), () {
      debugPrint('🔧 LOBBY: Requesting room state update');
      // The WebSocket should have already sent room_state, but let's ensure we have it
    });
  }
  
  Future<void> _loadRoles() async {
    final roles = await RolesService.loadRoles();
    setState(() {
      _availableRoles = roles;
      _rolesLoading = false;
    });
  }
  
  Future<void> _loadScenarios() async {
    final scenarios = await ScenariosService.loadScenarios();
    setState(() {
      _availableScenarios = scenarios;
      _scenariosLoading = false;
    });
  }
  
  void _setupWebSocketListeners() {
    debugPrint('🔧 LOBBY: Setting up WebSocket listeners');
    
    // CRITICAL: Check if we already have a room state from before navigation
    final latestState = widget.wsService.latestRoomState;
    if (latestState != null) {
      debugPrint('🏠 LOBBY: Using cached room_state from WebSocket service');
      _processRoomState(latestState);
    }
    
    // Room state (initial and updates)
    widget.wsService.roomState.listen((message) {
      debugPrint('🏠 LOBBY: Received room_state message: $message');
      _processRoomState(message);
    });
    
    // Player joined
    widget.wsService.playerJoined.listen((message) {
      debugPrint('👤 LOBBY: Player joined message: $message');
      setState(() {
        _players.add(message['player']);
        debugPrint('👤 LOBBY: Added player, now have ${_players.length} players');
      });
      _showSnackBar('${message['player']['name']} joined');
    });
    
    // Role selected
    widget.wsService.roleSelected.listen((message) {
      debugPrint('🎭 LOBBY: Received role_selected message: $message');
      setState(() {
        final playerId = message['player_id'];
        final playerName = message['player_name'];
        final role = message['role'];
        
        debugPrint('🎭 LOBBY: Player $playerName ($playerId) selected role: $role');
        debugPrint('🎭 LOBBY: Current players before update: $_players');
        
        // Update player's role
        final playerIndex = _players.indexWhere((p) => p['id'] == playerId);
        if (playerIndex != -1) {
          _players[playerIndex]['role'] = role;
          debugPrint('🎭 LOBBY: Updated player at index $playerIndex');
          
          // Update my role if it's me
          if (playerId == _myPlayerId) {
            _myRole = role;
            debugPrint('🎭 LOBBY: Updated my role to: $role');
          }
        } else {
          debugPrint('❌ LOBBY: Could not find player $playerId in players list!');
        }
        
        debugPrint('🎭 LOBBY: Current players after update: $_players');
      });
    });
    
    // Game started - navigate to game screen
    widget.wsService.gameStarted.listen((message) {
      debugPrint('🎮 LOBBY: Game started! Navigating to game screen');
      final scenario = message['scenario'];
      final objective = message['objective'];
      final yourTasks = message['your_tasks'] ?? [];
      
      debugPrint('🎮 LOBBY: Scenario: $scenario');
      debugPrint('🎮 LOBBY: Objective: $objective');
      debugPrint('🎮 LOBBY: Tasks count: ${yourTasks.length}');
      
      // Navigate to game screen
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (context) => GameScreen(
            wsService: widget.wsService,
            scenario: scenario,
            objective: objective,
            yourTasks: yourTasks,
            playerRole: _myRole,
            allPlayers: _players,
            myPlayerId: _myPlayerId,
          ),
        ),
      );
    });
    
    // Errors
    widget.wsService.errors.listen((message) {
      _showSnackBar(message['message'] ?? 'An error occurred', isError: true);
    });
  }
  
  void _processRoomState(Map<String, dynamic> message) {
    setState(() {
      _players = List<Map<String, dynamic>>.from(message['players'] ?? []);
      _myPlayerId = message['your_player_id'];
      
      // CRITICAL: Properly handle host status
      final isHostValue = message['is_host'];
      _isHost = isHostValue == true || isHostValue == 'true' || isHostValue == 1;
      
      debugPrint('🏠 LOBBY: Parsed players: $_players');
      debugPrint('🏠 LOBBY: My player ID: $_myPlayerId');
      debugPrint('🏠 LOBBY: Is host raw value: $isHostValue (type: ${isHostValue.runtimeType})');
      debugPrint('🏠 LOBBY: Am I host? $_isHost');
      
      // Find my role
      final myPlayer = _players.firstWhere(
        (p) => p['id'] == _myPlayerId,
        orElse: () => {},
      );
      _myRole = myPlayer['role'];
      debugPrint('🏠 LOBBY: My initial role: $_myRole');
      
      // AUTO-ASSIGN ROLES FOR FAST TESTING
      // Host gets Mastermind, first joiner gets Safe Cracker
      if (_myRole == null || _myRole == '') {
        if (_isHost && _players.length == 1) {
          // Host with no role - auto-select Mastermind
          debugPrint('🎯 AUTO: Selecting Mastermind for host');
          Future.delayed(Duration(milliseconds: 500), () {
            _selectRole('mastermind');
          });
        } else if (!_isHost && _players.length == 2) {
          // First joiner with no role - auto-select Safe Cracker
          final hostHasMastermind = _players.any((p) => p['role'] == 'mastermind');
          if (hostHasMastermind) {
            debugPrint('🎯 AUTO: Selecting Safe Cracker for first joiner');
            Future.delayed(Duration(milliseconds: 500), () {
              _selectRole('safe_cracker');
            });
          }
        }
      }
      
      // AUTO-START for test rooms (when both players have MM and SC)
      if (_players.length == 2) {
        final roles = _players.map((p) => p['role']).toSet();
        if (roles.contains('mastermind') && roles.contains('safe_cracker')) {
          // Both test roles are assigned
          final bothReady = _players.every((p) => p['role'] != null && p['role'] != '');
          if (bothReady && _isHost) {
            debugPrint('⚡ AUTO-START: Both test roles ready, starting game in 2 seconds');
            Future.delayed(Duration(seconds: 2), () {
              if (_isHost && mounted) {
                debugPrint('⚡ AUTO-START: Triggering game start');
                _startGame();
              }
            });
          }
        }
      }
    });
  }
  
  void _showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? AppColors.danger : AppColors.success,
        duration: const Duration(seconds: 2),
      ),
    );
  }
  
  void _selectRole(String roleId) {
    debugPrint('🎭 LOBBY: Attempting to select role: $roleId');
    debugPrint('🎭 LOBBY: My current role: $_myRole');
    debugPrint('🎭 LOBBY: Current players: $_players');
    
    // Allow switching roles directly - no need to deselect first
    
    // Check if role is already taken by someone else
    final isTaken = _players.any((p) => p['role'] == roleId && p['id'] != _myPlayerId);
    debugPrint('🎭 LOBBY: Is role $roleId taken by someone else? $isTaken');
    if (isTaken) {
      final takenBy = _players.firstWhere((p) => p['role'] == roleId);
      debugPrint('🎭 LOBBY: Role taken by: ${takenBy['name']} (${takenBy['id']})');
      _showSnackBar('Role already taken by ${takenBy['name']}', isError: true);
      return;
    }
    
    debugPrint('🎭 LOBBY: Sending selectRole to server...');
    widget.wsService.selectRole(roleId);
    setState(() {
      _myRole = roleId;
      debugPrint('🎭 LOBBY: Optimistically set my role to: $roleId');
    });
  }
  
  void _deselectRole() {
    if (_myRole != null) {
      widget.wsService.selectRole('');  // Empty string to deselect
      setState(() {
        _myRole = null;
      });
    }
  }
  
  void _startGame() {
    if (!_isHost) {
      _showSnackBar('Only the host can start the game', isError: true);
      return;
    }
    
    // Get selected scenario's minimum players
    final selectedScenario = _availableScenarios.isNotEmpty
        ? _availableScenarios.firstWhere(
            (s) => s.scenarioId == _selectedScenarioId,
            orElse: () => _availableScenarios.first,
          )
        : null;
    final minPlayers = selectedScenario?.rolesRequired.length ?? 2;
    
    // Check minimum players
    if (_players.length < minPlayers) {
      _showSnackBar('Need at least $minPlayers players for this scenario', isError: true);
      return;
    }
    
    // Check if all players have roles
    final allHaveRoles = _players.every((p) => p['role'] != null && p['role'] != '');
    if (!allHaveRoles) {
      _showSnackBar('All players must select roles first', isError: true);
      return;
    }
    
    debugPrint('🎮 START: Starting game with scenario: $_selectedScenarioId');
    widget.wsService.startGame(_selectedScenarioId);
  }
  
  void _copyRoomCode() {
    Clipboard.setData(ClipboardData(text: widget.roomCode));
    _showSnackBar('Room code copied to clipboard');
  }
  
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
                // Room code card
                _buildRoomCodeCard(),
                
                SizedBox(height: AppDimensions.space2XL),
                
                // Scenario section
                _buildScenarioSection(),
                
                SizedBox(height: AppDimensions.space2XL),
                
                // Your role selector button
                _buildRoleSelectorButton(),
                
                SizedBox(height: AppDimensions.space2XL),
                
                // Players list
                const SectionHeader(text: 'Players'),
                SizedBox(height: AppDimensions.spaceMD),
                _buildPlayersList(),
                
                SizedBox(height: AppDimensions.space2XL),
                
                // Ready state indicator
                _buildReadyStateIndicator(),
                
                SizedBox(height: AppDimensions.spaceLG),
                
                // Start button (host only)
                if (_isHost) _buildStartButton(),
                
                SizedBox(height: AppDimensions.spaceLG),
                
                // Leave room link
                _buildLeaveRoomButton(),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildRoomCodeCard() {
    final playerCount = _players.length;
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
                SizedBox(height: 4),
                Text(
                  '($playerCount of 12 players)',
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 14,
                  ),
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
  
  void _openScenarioSelectionModal() {
    debugPrint('🎭 SCENARIO: Opening modal with ${_availableScenarios.length} scenarios');
    debugPrint('🎭 SCENARIO: Current scenario: $_selectedScenarioId');
    
    showDialog(
      context: context,
      builder: (context) => ScenarioSelectionModal(
        availableScenarios: _availableScenarios,
        currentScenarioId: _selectedScenarioId,
        availableRoles: _availableRoles,
        onSelectScenario: (scenarioId) {
          debugPrint('🎭 SCENARIO: Selected scenario: $scenarioId');
          setState(() => _selectedScenarioId = scenarioId);
        },
      ),
    );
  }
  
  Widget _buildScenarioSection() {
    if (_scenariosLoading) {
      return Center(
        child: CircularProgressIndicator(color: AppColors.accentPrimary),
      );
    }
    
    if (_availableScenarios.isEmpty) {
      return Center(
        child: Text(
          'No scenarios available',
          style: TextStyle(color: AppColors.textSecondary),
        ),
      );
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
            Text('🎭', style: TextStyle(fontSize: 20)),
            SizedBox(width: 8),
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
        
        // Tappable scenario selector button (opens modal for host)
        InkWell(
          onTap: _isHost ? () {
            debugPrint('🎭 SCENARIO: Tapping scenario button (host: $_isHost)');
            debugPrint('🎭 SCENARIO: Available scenarios: ${_availableScenarios.length}');
            _openScenarioSelectionModal();
          } : null,
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
                // Scenario image - 80px
                ClipRRect(
                  borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
                  child: Image.asset(
                    'assets/scenarios/${selectedScenario.scenarioId}.png',
                    width: 80,
                    height: 80,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      // Fallback to emoji if image not found
                      return Container(
                        width: 80,
                        height: 80,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: AppColors.bgTertiary,
                          borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
                        ),
                        child: Text(
                          selectedScenario.themeIcon,
                          style: TextStyle(fontSize: 40),
                        ),
                      );
                    },
                  ),
                ),
                SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        selectedScenario.name,
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        selectedScenario.objective,
                        style: TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 12,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                if (_isHost)
                  Icon(
                    Icons.chevron_right,
                    color: AppColors.textSecondary,
                  ),
              ],
            ),
          ),
        ),
        if (_isHost) ...[
          SizedBox(height: 4),
          Text(
            'Tap to browse all scenarios',
            style: TextStyle(
              color: AppColors.textTertiary,
              fontSize: 12,
            ),
          ),
        ],
      ],
    );
  }
  
  Widget _buildOldScenarioListForReference() {
    final selectedScenario = _availableScenarios.firstWhere(
      (s) => s.scenarioId == _selectedScenarioId,
      orElse: () => _availableScenarios.first,
    );
    
    return Column(
      children: [
        // If host, show all scenarios to choose from
        if (_isHost) ..._availableScenarios.map((scenario) {
          final isSelected = scenario.scenarioId == _selectedScenarioId;
          return Container(
            margin: EdgeInsets.only(bottom: AppDimensions.spaceSM),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: () => setState(() => _selectedScenarioId = scenario.scenarioId),
                borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                child: Container(
                  padding: EdgeInsets.all(AppDimensions.spaceLG),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? AppColors.accentPrimary.withAlpha(51)
                        : AppColors.bgSecondary,
                    borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                    border: Border.all(
                      color: isSelected
                          ? AppColors.accentPrimary
                          : AppColors.borderSubtle,
                      width: isSelected ? 2 : 1,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            scenario.themeIcon,
                            style: TextStyle(fontSize: 24),
                          ),
                          SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              scenario.name,
                              style: TextStyle(
                                color: AppColors.textPrimary,
                                fontSize: 16,
                                fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                              ),
                            ),
                          ),
                          if (isSelected)
                            Icon(
                              Icons.check_circle,
                              color: AppColors.success,
                              size: 20,
                            ),
                        ],
                      ),
                      SizedBox(height: 6),
                      Text(
                        scenario.summary,
                        style: TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 13,
                          height: 1.3,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      SizedBox(height: 8),
                      Wrap(
                        spacing: 6,
                        runSpacing: 4,
                        children: scenario.rolesRequired.map((roleId) {
                          final role = _availableRoles.firstWhere(
                            (r) => r.roleId == roleId,
                            orElse: () => Role(
                              roleId: roleId,
                              name: roleId,
                              description: '',
                              minigames: [],
                              icon: '❓',
                            ),
                          );
                          return Container(
                            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: AppColors.bgTertiary,
                              borderRadius: BorderRadius.circular(4),
                              border: Border.all(
                                color: AppColors.borderSubtle,
                                width: 1,
                              ),
                            ),
                            child: Text(
                              role.name,
                              style: TextStyle(
                                color: AppColors.textSecondary,
                                fontSize: 11,
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        }),
        
        // If not host, just show selected scenario
        if (!_isHost)
          Container(
            padding: EdgeInsets.all(AppDimensions.spaceLG),
            decoration: BoxDecoration(
              color: AppColors.bgSecondary,
              borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
              border: Border.all(color: AppColors.accentPrimary.withAlpha(128)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      selectedScenario.themeIcon,
                      style: TextStyle(fontSize: 24),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        selectedScenario.name,
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 8),
                Text(
                  selectedScenario.summary,
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 13,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'Required roles:',
                  style: TextStyle(
                    color: AppColors.textTertiary,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                SizedBox(height: 4),
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: selectedScenario.rolesRequired.map((roleId) {
                    final role = _availableRoles.firstWhere(
                      (r) => r.roleId == roleId,
                      orElse: () => Role(
                        roleId: roleId,
                        name: roleId,
                        description: '',
                        minigames: [],
                        icon: '❓',
                      ),
                    );
                    return Container(
                      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppColors.bgTertiary,
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(
                          color: AppColors.borderSubtle,
                          width: 1,
                        ),
                      ),
                      child: Text(
                        role.name,
                        style: TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 11,
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
      ],
    );
  }
  
  Widget _buildRoleSelectorButton() {
    final role = _myRole != null
        ? _availableRoles.firstWhere(
            (r) => r.roleId == _myRole,
            orElse: () => Role(
              roleId: 'unknown',
              name: 'Unknown',
              description: '',
              minigames: [],
              icon: '❓',
            ),
          )
        : null;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text('🎭', style: TextStyle(fontSize: 20)),
            SizedBox(width: 8),
            Text(
              'YOUR ROLE',
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
        Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: _openRoleSelectionModal,
            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
            child: Container(
              padding: EdgeInsets.all(AppDimensions.spaceLG),
              decoration: BoxDecoration(
                color: _myRole == null 
                    ? AppColors.bgSecondary 
                    : AppColors.bgSecondary,
                borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                border: Border.all(
                  color: _myRole == null 
                      ? AppColors.borderSubtle 
                      : AppColors.accentPrimary,
                  width: _myRole == null ? 1 : 2,
                ),
              ),
              child: Row(
                children: [
                  if (_myRole != null) ...[
                    // Show character portrait for selected role (default female)
                    ClipRRect(
                      borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
                      child: Image.asset(
                        'assets/roles/${_myRole}_female.png',
                        width: 80,
                        height: 80,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          // Fallback to emoji if image not found
                          return Container(
                            width: 80,
                            height: 80,
                            alignment: Alignment.center,
                            child: Text(
                              role!.icon,
                              style: TextStyle(fontSize: 40),
                            ),
                          );
                        },
                      ),
                    ),
                    SizedBox(width: 16),
                  ],
                  Expanded(
                    child: Text(
                      _myRole == null ? 'Select Your Role' : role!.name,
                      style: TextStyle(
                        color: _myRole == null 
                            ? AppColors.textTertiary 
                            : AppColors.textPrimary,
                        fontSize: 16,
                        fontWeight: _myRole == null ? FontWeight.normal : FontWeight.w600,
                      ),
                    ),
                  ),
                  Icon(
                    Icons.chevron_right,
                    color: AppColors.textSecondary,
                  ),
                ],
              ),
            ),
          ),
        ),
        SizedBox(height: 4),
        Text(
          _myRole == null ? 'Tap to browse all roles' : 'Tap to change role',
          style: TextStyle(
            color: AppColors.textTertiary,
            fontSize: 12,
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }
  
  void _openRoleSelectionModal() {
    showDialog(
      context: context,
      builder: (context) => RoleSelectionModal(
        availableRoles: _availableRoles,
        currentRole: _myRole,
        players: _players,
        onSelectRole: _selectRole,
        initialGender: 'female', // Default to female
      ),
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
          style: TextStyle(
            color: AppColors.textSecondary,
            fontSize: 14,
            fontStyle: FontStyle.italic,
          ),
        ),
      );
    }
    
    return Container(
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
      ),
      child: Column(
        children: _players.map((player) {
          final isMe = player['id'] == _myPlayerId;
          final isHost = player['id'] == _players.first['id']; // First player is host
          final hasRole = player['role'] != null && player['role'] != '';
          final role = hasRole
              ? _availableRoles.firstWhere(
                  (r) => r.roleId == player['role'],
                  orElse: () => Role(
                    roleId: 'unknown',
                    name: 'No Role',
                    description: '',
                    minigames: [],
                    icon: '❓',
                  ),
                )
              : null;
          
          return Container(
            padding: EdgeInsets.all(AppDimensions.spaceLG),
            decoration: BoxDecoration(
              border: Border(
                bottom: player != _players.last
                    ? BorderSide(color: AppColors.borderSubtle, width: 1)
                    : BorderSide.none,
              ),
            ),
            child: Row(
              children: [
                // Icon: Crown for host, person for others
                Text(
                  isHost ? '👑' : '👤',
                  style: TextStyle(fontSize: 20),
                ),
                SizedBox(width: AppDimensions.spaceSM),
                Expanded(
                  child: Row(
                    children: [
                      Text(
                        isMe ? 'You' : player['name'] ?? 'Unknown',
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      if (hasRole) ...[
                        Text(
                          ' - ',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 16,
                          ),
                        ),
                        Text(
                          role!.name,
                          style: TextStyle(
                            color: AppColors.accentPrimary,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                // Checkmark if role selected
                if (hasRole)
                  Icon(
                    Icons.check_circle,
                    color: AppColors.success,
                    size: 20,
                  ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
  
  Widget _buildReadyStateIndicator() {
    // Get selected scenario's required roles count
    final selectedScenario = _availableScenarios.isNotEmpty
        ? _availableScenarios.firstWhere(
            (s) => s.scenarioId == _selectedScenarioId,
            orElse: () => _availableScenarios.first,
          )
        : null;
    final minPlayers = selectedScenario?.rolesRequired.length ?? 2;
    
    final allHaveRoles = _players.isNotEmpty && 
        _players.every((p) => p['role'] != null && p['role'] != '');
    final enoughPlayers = _players.length >= minPlayers;
    
    if (_isHost) {
      if (!enoughPlayers) {
        return Container(
          padding: EdgeInsets.all(AppDimensions.spaceMD),
          decoration: BoxDecoration(
            color: AppColors.danger.withAlpha(26),
            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
            border: Border.all(color: AppColors.danger.withAlpha(128)),
          ),
          child: Row(
            children: [
              Icon(Icons.warning, color: AppColors.danger, size: 20),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Need at least ${minPlayers - _players.length} more player${_players.length == minPlayers - 1 ? '' : 's'} to start',
                  style: TextStyle(
                    color: AppColors.danger,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
        );
      } else if (!allHaveRoles) {
        return Container(
          padding: EdgeInsets.all(AppDimensions.spaceMD),
          decoration: BoxDecoration(
            color: AppColors.warning.withAlpha(26),
            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
            border: Border.all(color: AppColors.warning.withAlpha(128)),
          ),
          child: Row(
            children: [
              Icon(Icons.info, color: AppColors.warning, size: 20),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'All players must select roles before starting',
                  style: TextStyle(
                    color: AppColors.warning,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
        );
      }
    } else {
      // Non-host view
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
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: AppColors.accentPrimary,
              ),
            ),
            SizedBox(width: 12),
            Text(
              'Waiting for host to start...',
              style: TextStyle(
                color: AppColors.textSecondary,
                fontSize: 14,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      );
    }
    
    return SizedBox.shrink();
  }
  
  Widget _buildLeaveRoomButton() {
    return Center(
      child: TextButton(
        onPressed: () {
          Navigator.of(context).pop();
        },
        child: Text(
          'Leave Room',
          style: TextStyle(
            color: AppColors.textSecondary,
            fontSize: 14,
            decoration: TextDecoration.underline,
          ),
        ),
      ),
    );
  }
  
  // Old inline role selection removed - now using modal
  
  Widget _buildStartButton() {
    final allReady = _players.isNotEmpty && _players.every((p) => p['role'] != null && p['role'] != '');
    
    return Column(
      children: [
        HeistPrimaryButton(
          text: 'Start Game',
          onPressed: allReady ? _startGame : null,
          icon: Icons.play_arrow,
        ),
        if (!allReady)
          Padding(
            padding: EdgeInsets.only(top: AppDimensions.spaceSM),
            child: Text(
              'All players must select roles',
              style: TextStyle(
                color: AppColors.textSecondary,
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
          ),
      ],
    );
  }
}
