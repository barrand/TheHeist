import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';
import 'package:the_heist/services/websocket_service.dart';
import 'package:the_heist/widgets/common/heist_primary_button.dart';
import 'package:the_heist/widgets/common/heist_secondary_button.dart';
import 'package:the_heist/widgets/common/section_header.dart';

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
    
    if (_myRole != null) {
      // Already have a role - deselect first
      _showSnackBar('Deselect your current role first');
      return;
    }
    
    // Check if role is already taken
    final isTaken = _players.any((p) => p['role'] == roleId);
    debugPrint('🎭 LOBBY: Is role $roleId taken? $isTaken');
    if (isTaken) {
      final takenBy = _players.firstWhere((p) => p['role'] == roleId);
      debugPrint('🎭 LOBBY: Role taken by: ${takenBy['name']} (${takenBy['id']})');
      _showSnackBar('Role already taken', isError: true);
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
                // Room code display
                _buildRoomCodeCard(),
                
                SizedBox(height: AppDimensions.spaceLG),
                
                // Players list
                const SectionHeader(text: 'Players'),
                SizedBox(height: AppDimensions.spaceSM),
                _buildPlayersList(),
                
                SizedBox(height: AppDimensions.spaceLG),
                
                // Role selection
                const SectionHeader(text: 'Select Your Role'),
                SizedBox(height: AppDimensions.spaceSM),
                _buildRoleSelection(),
                
                SizedBox(height: AppDimensions.spaceLG),
                
                // Start button (host only)
                if (_isHost) _buildStartButton(),
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
      child: Column(
        children: [
          Text(
            'Room Code',
            style: TextStyle(
              color: AppColors.textSecondary,
              fontSize: 14,
            ),
          ),
          SizedBox(height: AppDimensions.spaceSM),
          Text(
            widget.roomCode,
            style: TextStyle(
              color: AppColors.accentPrimary,
              fontSize: 36,
              fontWeight: FontWeight.bold,
              letterSpacing: 8,
            ),
          ),
          SizedBox(height: AppDimensions.spaceSM),
          HeistSecondaryButton(
            text: 'Copy Code',
            onPressed: _copyRoomCode,
            icon: Icons.copy,
          ),
        ],
      ),
    );
  }
  
  Widget _buildPlayersList() {
    return Column(
      children: _players.map((player) {
        final isMe = player['id'] == _myPlayerId;
        final roleName = _availableRoles.firstWhere(
          (r) => r['id'] == player['role'],
          orElse: () => {'name': '', 'icon': ''},
        );
        
        return Container(
          margin: EdgeInsets.only(bottom: AppDimensions.spaceSM),
          padding: EdgeInsets.all(AppDimensions.containerPadding),
          decoration: BoxDecoration(
            color: isMe ? AppColors.accentPrimary.withAlpha(51) : AppColors.bgSecondary,
            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
            border: isMe ? Border.all(color: AppColors.accentPrimary) : null,
          ),
          child: Row(
            children: [
              Icon(
                isMe ? Icons.person : Icons.person_outline,
                color: AppColors.textPrimary,
              ),
              SizedBox(width: AppDimensions.spaceSM),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      player['name'] ?? 'Unknown',
                      style: TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (player['role'] != null && player['role'] != '')
                      Text(
                        '${roleName['icon']} ${roleName['name']}',
                        style: TextStyle(
                          color: AppColors.accentPrimary,
                          fontSize: 14,
                        ),
                      ),
                  ],
                ),
              ),
              if (isMe && _isHost)
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.accentPrimary,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'HOST',
                    style: TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
        );
      }).toList(),
    );
  }
  
  Widget _buildRoleSelection() {
    return Wrap(
      spacing: AppDimensions.spaceSM,
      runSpacing: AppDimensions.spaceSM,
      children: _availableRoles.map((role) {
        final isSelected = _myRole == role['id'];
        final takenByPlayer = _players.firstWhere(
          (p) => p['role'] == role['id'],
          orElse: () => <String, dynamic>{},
        );
        final isTaken = takenByPlayer.isNotEmpty;
        final isAvailable = !isTaken || isSelected;
        final takenByName = isTaken ? takenByPlayer['name'] : null;
        
        return InkWell(
          onTap: isAvailable ? () => isSelected ? _deselectRole() : _selectRole(role['id']!) : null,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          child: Container(
            padding: EdgeInsets.symmetric(
              horizontal: AppDimensions.spaceMD,
              vertical: AppDimensions.spaceSM,
            ),
            decoration: BoxDecoration(
              color: isSelected
                  ? AppColors.accentPrimary
                  : isTaken
                      ? AppColors.bgTertiary.withAlpha(128)
                      : AppColors.bgSecondary,
              borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
              border: Border.all(
                color: isSelected 
                    ? AppColors.accentLight 
                    : isTaken 
                        ? AppColors.danger.withAlpha(128) 
                        : AppColors.borderSubtle,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  '${role['icon']} ${role['name']}',
                  style: TextStyle(
                    color: isSelected
                        ? AppColors.textPrimary
                        : isTaken
                            ? AppColors.textTertiary
                            : AppColors.textPrimary,
                    fontSize: 14,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                  ),
                ),
                if (isTaken && !isSelected) ...[
                  SizedBox(height: 2),
                  Text(
                    'taken by $takenByName',
                    style: TextStyle(
                      color: AppColors.danger,
                      fontSize: 10,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      }).toList(),
    );
  }
  
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
