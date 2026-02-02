import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';
import 'package:the_heist/services/websocket_service.dart';
import 'package:the_heist/widgets/common/heist_primary_button.dart';
import 'package:the_heist/widgets/common/heist_secondary_button.dart';
import 'package:the_heist/widgets/common/section_header.dart';
import 'package:the_heist/widgets/modals/role_selection_modal.dart';

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
  String _selectedScenario = 'museum_gala_vault';
  
  // Available roles
  final List<Map<String, String>> _availableRoles = [
    {'id': 'mastermind', 'name': 'Mastermind', 'icon': '🧠'},
    {'id': 'hacker', 'name': 'Hacker', 'icon': '💻'},
    {'id': 'safe_cracker', 'name': 'Safe Cracker', 'icon': '🔓'},
    {'id': 'insider', 'name': 'Insider', 'icon': '🕵️'},
    {'id': 'driver', 'name': 'Driver', 'icon': '🚗'},
    {'id': 'grifter', 'name': 'Grifter', 'icon': '🎭'},
    {'id': 'muscle', 'name': 'Muscle', 'icon': '💪'},
    {'id': 'lookout', 'name': 'Lookout', 'icon': '👀'},
  ];
  
  @override
  void initState() {
    super.initState();
    _setupWebSocketListeners();
  }
  
  void _setupWebSocketListeners() {
    debugPrint('🔧 LOBBY: Setting up WebSocket listeners');
    
    // Room state (initial)
    widget.wsService.roomState.listen((message) {
      debugPrint('🏠 LOBBY: Received room_state message: $message');
      setState(() {
        _players = List<Map<String, dynamic>>.from(message['players'] ?? []);
        _myPlayerId = message['your_player_id'];
        _isHost = message['is_host'] ?? false;
        
        debugPrint('🏠 LOBBY: Parsed players: $_players');
        debugPrint('🏠 LOBBY: My player ID: $_myPlayerId');
        debugPrint('🏠 LOBBY: Am I host? $_isHost');
        
        // Find my role
        final myPlayer = _players.firstWhere(
          (p) => p['id'] == _myPlayerId,
          orElse: () => {},
        );
        _myRole = myPlayer['role'];
        debugPrint('🏠 LOBBY: My initial role: $_myRole');
      });
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
    
    // Game started
    widget.wsService.gameStarted.listen((message) {
      // Navigate to game screen
      Navigator.of(context).pushReplacementNamed(
        '/game',
        arguments: {
          'wsService': widget.wsService,
          'scenario': message['scenario'],
          'objective': message['objective'],
          'your_tasks': message['your_tasks'],
        },
      );
    });
    
    // Errors
    widget.wsService.errors.listen((message) {
      _showSnackBar(message['message'] ?? 'An error occurred', isError: true);
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
    
    // Check if all players have roles
    final allHaveRoles = _players.every((p) => p['role'] != null && p['role'] != '');
    if (!allHaveRoles) {
      _showSnackBar('All players must select roles first', isError: true);
      return;
    }
    
    if (_players.length < 3) {
      _showSnackBar('Need at least 3 players to start', isError: true);
      return;
    }
    
    widget.wsService.startGame(_selectedScenario);
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
  
  Widget _buildScenarioSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text('🎭', style: TextStyle(fontSize: 20)),
            SizedBox(width: 8),
            Text(
              _isHost ? 'SCENARIO SELECTION' : 'SCENARIO',
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
        Container(
          padding: EdgeInsets.all(AppDimensions.spaceLG),
          decoration: BoxDecoration(
            color: AppColors.bgSecondary,
            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
            border: Border.all(color: AppColors.accentPrimary.withAlpha(128)),
          ),
          child: Text(
            'Museum Gala Vault Heist',
            style: TextStyle(
              color: AppColors.textPrimary,
              fontSize: 16,
            ),
          ),
        ),
        if (!_isHost) ...[
          SizedBox(height: AppDimensions.spaceSM),
          Text(
            'Required: Mastermind, Hacker, Safe Cracker',
            style: TextStyle(
              color: AppColors.textSecondary,
              fontSize: 12,
            ),
          ),
        ],
      ],
    );
  }
  
  Widget _buildRoleSelectorButton() {
    final roleName = _myRole != null
        ? _availableRoles.firstWhere(
            (r) => r['id'] == _myRole,
            orElse: () => {'name': 'Unknown', 'icon': ''},
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
                    Text(
                      roleName!['icon']!,
                      style: TextStyle(fontSize: 20),
                    ),
                    SizedBox(width: 8),
                  ],
                  Expanded(
                    child: Text(
                      _myRole == null ? 'Select Your Role' : roleName!['name']!,
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
          final roleName = hasRole
              ? _availableRoles.firstWhere(
                  (r) => r['id'] == player['role'],
                  orElse: () => {'name': 'No Role', 'icon': ''},
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
                          roleName!['name']!,
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
    final allHaveRoles = _players.isNotEmpty && 
        _players.every((p) => p['role'] != null && p['role'] != '');
    final enoughPlayers = _players.length >= 3;
    
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
                  'Need ${3 - _players.length} more player${_players.length == 2 ? '' : 's'} to start',
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
