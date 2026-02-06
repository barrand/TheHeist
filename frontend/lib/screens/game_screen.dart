import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';
import 'package:the_heist/services/websocket_service.dart';
import 'package:the_heist/widgets/common/heist_primary_button.dart';
import 'package:the_heist/models/item.dart';

/// Game screen where players complete their tasks
class GameScreen extends StatefulWidget {
  final WebSocketService wsService;
  final String scenario;
  final String objective;
  final List<dynamic> yourTasks;
  final String? playerRole;
  final List<Map<String, dynamic>>? allPlayers;
  final String? myPlayerId;
  
  const GameScreen({
    super.key,
    required this.wsService,
    required this.scenario,
    required this.objective,
    required this.yourTasks,
    this.playerRole,
    this.allPlayers,
    this.myPlayerId,
  });
  
  @override
  State<GameScreen> createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> {
  List<Map<String, dynamic>> _myTasks = [];
  final List<String> _completedTaskIds = [];
  bool _gameEnded = false;
  String? _gameResult;
  String? _gameSummary;
  String _currentLocation = 'Safe House'; // All games start at Safe House
  bool _showCompletedTasks = false;
  
  // Track all players, NPCs, and locations
  List<Map<String, dynamic>> _allPlayers = [];
  List<Map<String, dynamic>> _npcs = [];
  List<Map<String, dynamic>> _allLocations = [];
  String? _myPlayerId;
  
  // Inventory tracking
  final List<Item> _myInventory = [];
  
  @override
  void initState() {
    super.initState();
    _myTasks = widget.yourTasks.map((t) => Map<String, dynamic>.from(t)).toList();
    
    // Initialize with passed-in player data if available
    if (widget.allPlayers != null) {
      _allPlayers = widget.allPlayers!.map((p) => Map<String, dynamic>.from(p)).toList();
    }
    if (widget.myPlayerId != null) {
      _myPlayerId = widget.myPlayerId;
    }
    
    _setupWebSocketListeners();
  }
  
  void _setupWebSocketListeners() {
    // Task completed (by anyone)
    widget.wsService.taskCompleted.listen((message) {
      final taskId = message['task_id'];
      final playerName = message['by_player_name'];
      
      setState(() {
        _completedTaskIds.add(taskId);
        
        // Update task status if it's mine
        final taskIndex = _myTasks.indexWhere((t) => t['id'] == taskId);
        if (taskIndex != -1) {
          _myTasks[taskIndex]['status'] = 'completed';
        }
      });
      
      _showSnackBar('$playerName completed a task!');
    });
    
    // Task unlocked (new task available for me)
    widget.wsService.taskUnlocked.listen((message) {
      final task = message['task'];
      setState(() {
        _myTasks.add(Map<String, dynamic>.from(task));
      });
      _showSnackBar('New task available!', color: AppColors.success);
    });
    
    // Search results received
    widget.wsService.searchResults.listen((message) {
      final items = (message['items'] as List)
          .map((item) => Item.fromJson(item))
          .toList();
      _showSearchResults(items);
    });
    
    // Item picked up (by anyone)
    widget.wsService.itemPickedUp.listen((message) {
      final playerId = message['player_id'];
      final playerName = message['player_name'];
      final item = Item.fromJson(message['item']);
      
      // If I picked it up, add to my inventory
      if (playerId == _myPlayerId) {
        setState(() {
          _myInventory.add(item);
        });
        _showSnackBar('Picked up: ${item.name}', color: AppColors.success);
      } else {
        _showSnackBar('$playerName picked up: ${item.name}');
      }
    });
    
    // Item transferred (by anyone)
    widget.wsService.itemTransferred.listen((message) {
      final fromPlayerId = message['from_player_id'];
      final fromPlayerName = message['from_player_name'];
      final toPlayerId = message['to_player_id'];
      final toPlayerName = message['to_player_name'];
      final item = Item.fromJson(message['item']);
      
      // If I received it, add to my inventory
      if (toPlayerId == _myPlayerId) {
        setState(() {
          _myInventory.add(item);
        });
        _showSnackBar('$fromPlayerName gave you: ${item.name}', color: AppColors.success);
      }
      // If I gave it away, remove from my inventory
      else if (fromPlayerId == _myPlayerId) {
        setState(() {
          _myInventory.removeWhere((i) => i.id == item.id);
        });
        _showSnackBar('Gave ${item.name} to $toPlayerName');
      }
      // Otherwise just notify
      else {
        _showSnackBar('$fromPlayerName gave ${item.name} to $toPlayerName');
      }
    });
    
    // Info messages (e.g., item use feedback)
    widget.wsService.info.listen((message) {
      final infoMessage = message['message'] as String?;
      if (infoMessage != null) {
        _showSnackBar(infoMessage, color: AppColors.info);
      }
    });
    
    // Listen for all messages
    widget.wsService.messages.listen((message) {
      // Game ended
      if (message['type'] == 'game_ended') {
        setState(() {
          _gameEnded = true;
          _gameResult = message['result'];
          _gameSummary = message['summary'];
        });
      }
      
      // Player moved location
      if (message['type'] == 'player_moved') {
        final playerId = message['player_id'];
        final newLocation = message['location'];
        
        setState(() {
          final playerIndex = _allPlayers.indexWhere((p) => p['id'] == playerId);
          if (playerIndex != -1) {
            _allPlayers[playerIndex]['location'] = newLocation;
          }
        });
      }
      
      // Room state (includes all players and game state)
      if (message['type'] == 'room_state') {
        setState(() {
          _myPlayerId = message['your_player_id'];
          _allPlayers = List<Map<String, dynamic>>.from(message['players'] ?? []);
        });
      }
      
      // Game started (includes NPCs and locations)
      if (message['type'] == 'game_started') {
        setState(() {
          if (message.containsKey('npcs')) {
            _npcs = List<Map<String, dynamic>>.from(message['npcs'] ?? []);
            debugPrint('🎮 Received ${_npcs.length} NPCs from game_started message');
            for (var npc in _npcs) {
              debugPrint('   NPC: ${npc['name']} at ${npc['location']}');
            }
          }
          if (message.containsKey('locations')) {
            _allLocations = List<Map<String, dynamic>>.from(message['locations'] ?? []);
            debugPrint('🗺️ Received ${_allLocations.length} locations from game_started message');
            for (var loc in _allLocations) {
              debugPrint('   Location: ${loc['name']}');
            }
          }
        });
      }
    });
  }
  
  void _showSnackBar(String message, {Color? color}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color ?? AppColors.info,
        duration: const Duration(seconds: 2),
      ),
    );
  }
  
  void _completeTask(String taskId, String taskType) {
    // For now, all tasks complete immediately
    // Later we'll add minigames, NPC conversations, etc.
    widget.wsService.completeTask(taskId);
    
    setState(() {
      final taskIndex = _myTasks.indexWhere((t) => t['id'] == taskId);
      if (taskIndex != -1) {
        _myTasks[taskIndex]['status'] = 'in_progress';
      }
    });
  }
  
  String _getTaskTypeLabel(String type) {
    switch (type) {
      case 'minigame':
        return '🎮 Minigame';
      case 'npc_llm':
        return '💬 Talk to NPC';
      case 'search':
        return '🔍 Search';
      case 'handoff':
        return '🤝 Hand Off Item';
      case 'info_share':
        return '🗣️ Share Info';
      case 'discovery':
        return '🎯 Explore';
      default:
        return type;
    }
  }
  
  String _formatRoleName(String role) {
    // Convert snake_case to Title Case
    return role.split('_').map((word) {
      return word[0].toUpperCase() + word.substring(1);
    }).join(' ');
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameEnded) {
      return _buildGameEndedScreen();
    }
    
    // Group tasks by location
    // Tasks at current location OR tasks that can be done anywhere (discovery, info_share)
    final tasksHere = _myTasks.where((t) {
      if (t['status'] == 'completed') return false;
      
      final location = t['location'] as String?;
      final type = t['type'] as String?;
      
      // Discovery and info_share tasks can be done from anywhere
      if (type == 'discovery' || type == 'info_share') return true;
      
      // Other tasks must be at specific location
      return location == _currentLocation;
    }).toList();
    
    final tasksElsewhere = _myTasks.where((t) {
      if (t['status'] == 'completed') return false;
      
      final location = t['location'] as String?;
      final type = t['type'] as String?;
      
      // Discovery and info_share are never "elsewhere"
      if (type == 'discovery' || type == 'info_share') return false;
      
      return location != _currentLocation;
    }).toList();
    
    final completedTasks = _myTasks.where((t) => t['status'] == 'completed').toList();
    
    final totalTasks = _myTasks.length;
    final completedCount = completedTasks.length;
    
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      body: SafeArea(
        child: Column(
          children: [
            // Top bar - Location & Progress
            _buildTopBar(completedCount, totalTasks),
            
            // Scrollable content
            Expanded(
              child: SingleChildScrollView(
                child: Padding(
                  padding: EdgeInsets.all(AppDimensions.containerPadding),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Team Objective
                      _buildTeamObjective(),
                      
                      SizedBox(height: AppDimensions.spaceLG),
                      
                      // Who's here section
                      _buildWhosHere(),
                      
                      SizedBox(height: AppDimensions.spaceLG),
                      
                      // Your Tasks header
                      if (widget.playerRole != null) ...[
                        Text(
                          'YOUR TASKS (${_formatRoleName(widget.playerRole!)})',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.5,
                          ),
                        ),
                        SizedBox(height: AppDimensions.spaceSM),
                      ],
                      
                      // Ready to do here
                      if (tasksHere.isNotEmpty) ...[
                        Text(
                          '✅ READY TO DO HERE',
                          style: TextStyle(
                            color: AppColors.success,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1,
                          ),
                        ),
                        SizedBox(height: AppDimensions.spaceSM),
                        ...tasksHere.map((task) => _buildTaskCard(task, isAtCurrentLocation: true)),
                      ],
                      
                      // Requires travel
                      if (tasksElsewhere.isNotEmpty) ...[
                        if (tasksHere.isNotEmpty) SizedBox(height: AppDimensions.spaceMD),
                        Text(
                          '📍 REQUIRES TRAVEL',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1,
                          ),
                        ),
                        SizedBox(height: AppDimensions.spaceSM),
                        ...tasksElsewhere.map((task) => _buildTaskCard(task, isAtCurrentLocation: false)),
                      ],
                      
                      // Completed section
                      if (completedTasks.isNotEmpty) ...[
                        SizedBox(height: AppDimensions.spaceMD),
                        Divider(color: AppColors.borderSubtle),
                        SizedBox(height: AppDimensions.spaceMD),
                        InkWell(
                          onTap: () {
                            setState(() {
                              _showCompletedTasks = !_showCompletedTasks;
                            });
                          },
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                '✅ COMPLETED (${completedTasks.length})',
                                style: TextStyle(
                                  color: AppColors.success,
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  letterSpacing: 1,
                                ),
                              ),
                              Icon(
                                _showCompletedTasks ? Icons.expand_less : Icons.expand_more,
                                color: AppColors.textSecondary,
                              ),
                            ],
                          ),
                        ),
                        if (_showCompletedTasks) ...[
                          SizedBox(height: AppDimensions.spaceSM),
                          ...completedTasks.map((task) => _buildTaskCard(task, isAtCurrentLocation: false)),
                        ],
                      ],
                      
                      SizedBox(height: 80), // Space for bottom nav
                    ],
                  ),
                ),
              ),
            ),
            
            // Bottom navigation
            _buildBottomNav(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildTopBar(int completedCount, int totalTasks) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        border: Border(
          bottom: BorderSide(color: AppColors.borderSubtle, width: 1),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Location image (16:9 aspect ratio)
          Container(
            width: double.infinity,
            height: 150,
            color: AppColors.bgPrimary,
            child: Image.network(
              'http://localhost:8000/images/${widget.scenario}/location_${_currentLocation.toLowerCase().replaceAll(' ', '_')}.png',
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                // Fallback to gradient if image not available
                return Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        AppColors.bgPrimary,
                        AppColors.bgSecondary,
                      ],
                    ),
                  ),
                  child: Center(
                    child: Icon(
                      Icons.location_on,
                      size: 48,
                      color: AppColors.accentPrimary.withOpacity(0.3),
                    ),
                  ),
                );
              },
            ),
          ),
          
          // Location name and controls row
          Padding(
            padding: EdgeInsets.symmetric(
              horizontal: AppDimensions.containerPadding,
              vertical: AppDimensions.spaceMD,
            ),
            child: Row(
              children: [
                Icon(Icons.location_on, color: AppColors.accentPrimary, size: 20),
                SizedBox(width: 6),
                Expanded(
                  child: Text(
                    _currentLocation,
                    style: TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                // Search room button
                IconButton(
                  icon: Icon(Icons.search, color: AppColors.accentPrimary, size: 22),
                  onPressed: _searchRoom,
                  padding: EdgeInsets.all(4),
                  constraints: BoxConstraints(),
                  tooltip: 'Search room',
                ),
                SizedBox(width: 4),
                // Bag button with count badge
                Stack(
                  children: [
                    IconButton(
                      icon: Icon(Icons.shopping_bag_outlined, color: AppColors.accentPrimary, size: 22),
                      onPressed: _showInventory,
                      padding: EdgeInsets.all(4),
                      constraints: BoxConstraints(),
                      tooltip: 'Inventory',
                    ),
                    if (_myInventory.isNotEmpty)
                      Positioned(
                        right: 0,
                        top: 0,
                        child: Container(
                          padding: EdgeInsets.all(3),
                          decoration: BoxDecoration(
                            color: AppColors.accentSecondary,
                            shape: BoxShape.circle,
                          ),
                          constraints: BoxConstraints(
                            minWidth: 16,
                            minHeight: 16,
                          ),
                          child: Text(
                            '${_myInventory.length}',
                            style: TextStyle(
                              color: AppColors.bgPrimary,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      ),
                  ],
                ),
                SizedBox(width: 8),
                Text(
                  '$completedCount/$totalTasks',
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                SizedBox(width: 6),
                Icon(Icons.timer, color: AppColors.textSecondary, size: 18),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildTeamObjective() {
    return Container(
      padding: EdgeInsets.all(AppDimensions.containerPadding),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
        border: Border.all(color: AppColors.accentPrimary, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '🎯 TEAM OBJECTIVE',
            style: TextStyle(
              color: AppColors.accentPrimary,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
            ),
          ),
          SizedBox(height: AppDimensions.spaceSM),
          Text(
            widget.objective,
            style: TextStyle(
              color: AppColors.textPrimary,
              fontSize: 15,
              fontWeight: FontWeight.w500,
            ),
          ),
          SizedBox(height: AppDimensions.spaceXS),
          Row(
            children: [
              Icon(Icons.people, color: AppColors.textSecondary, size: 14),
              SizedBox(width: 4),
              Text(
                'Team task',
                style: TextStyle(
                  color: AppColors.textSecondary,
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildWhosHere() {
    // Get players at current location (excluding self)
    final playersHere = _allPlayers.where((player) => 
      player['location'] == _currentLocation && player['id'] != _myPlayerId
    ).toList();
    
    // Get NPCs at current location
    final npcsHere = _npcs.where((npc) => 
      npc['location'] == _currentLocation
    ).toList();
    
    // Debug logging
    debugPrint('🏠 WHO\'S HERE Debug:');
    debugPrint('   Current location: $_currentLocation');
    debugPrint('   My player ID: $_myPlayerId');
    debugPrint('   Total players: ${_allPlayers.length}');
    debugPrint('   Players here: ${playersHere.length}');
    debugPrint('   Total NPCs: ${_npcs.length}');
    debugPrint('   NPCs here: ${npcsHere.length}');
    
    // Don't show section if no one else is here
    if (playersHere.isEmpty && npcsHere.isEmpty) {
      return SizedBox.shrink();
    }
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '👥 WHO\'S HERE',
          style: TextStyle(
            color: AppColors.textSecondary,
            fontSize: 12,
            fontWeight: FontWeight.bold,
            letterSpacing: 1,
          ),
        ),
        SizedBox(height: AppDimensions.spaceSM),
        
        // Players
        ...playersHere.map((player) {
          final name = player['name'] ?? 'Unknown';
          final role = player['role'];
          final roleDisplay = role != null ? _formatRoleName(role) : '';
          
          return Container(
            margin: EdgeInsets.only(bottom: AppDimensions.spaceXS),
            padding: EdgeInsets.symmetric(
              horizontal: AppDimensions.spaceSM,
              vertical: AppDimensions.spaceXS,
            ),
            decoration: BoxDecoration(
              color: AppColors.bgSecondary,
              borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
              border: Border.all(color: AppColors.borderSubtle, width: 1),
            ),
            child: Row(
              children: [
                Icon(Icons.person, color: AppColors.accentSecondary, size: 18),
                SizedBox(width: AppDimensions.spaceXS),
                Expanded(
                  child: Text(
                    '$name${roleDisplay.isNotEmpty ? " ($roleDisplay)" : ""}',
                    style: TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          );
        }),
        
        // NPCs
        ...npcsHere.map((npc) {
          final name = npc['name'] ?? 'Unknown';
          final role = npc['role'] ?? '';
          
          return Container(
            margin: EdgeInsets.only(bottom: AppDimensions.spaceXS),
            padding: EdgeInsets.symmetric(
              horizontal: AppDimensions.spaceSM,
              vertical: AppDimensions.spaceXS,
            ),
            decoration: BoxDecoration(
              color: AppColors.bgSecondary,
              borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
              border: Border.all(color: AppColors.borderSubtle, width: 1),
            ),
            child: Row(
              children: [
                Text('💬', style: TextStyle(fontSize: 18)),
                SizedBox(width: AppDimensions.spaceXS),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        name,
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      if (role.isNotEmpty)
                        Text(
                          role,
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 12,
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }
  
  Widget _buildBottomNav() {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: AppDimensions.containerPadding,
        vertical: AppDimensions.spaceSM,
      ),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        border: Border(
          top: BorderSide(color: AppColors.borderSubtle, width: 1),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildNavButton(Icons.map, 'Map', _showMapDialog),
          _buildNavButton(Icons.backpack, 'Bag', _showInventory),
          _buildNavButton(Icons.search, 'Search', _searchRoom),
        ],
      ),
    );
  }
  
  Widget _buildNavButton(IconData icon, String label, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: AppColors.textSecondary, size: 24),
          SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              color: AppColors.textSecondary,
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }
  
  void _showMapDialog() {
    // Use all locations from game state, or fall back to locations from tasks
    List<String> locationNames;
    if (_allLocations.isNotEmpty) {
      // Use locations sent from backend
      locationNames = _allLocations
          .map((loc) => loc['name'] as String)
          .toList();
    } else {
      // Fallback: extract from tasks
      final Set<String> taskLocations = _myTasks
          .map((task) => task['location'] as String?)
          .where((loc) => loc != null && loc.isNotEmpty)
          .cast<String>()
          .toSet();
      taskLocations.add('Safe House');
      locationNames = taskLocations.toList();
    }
    
    final sortedLocations = locationNames..sort();
    
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: AppColors.bgPrimary,
          title: Row(
            children: [
              Icon(Icons.map, color: AppColors.accentPrimary, size: 24),
              SizedBox(width: 8),
              Text(
                'LOCATIONS',
                style: TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Spacer(),
              IconButton(
                icon: Icon(Icons.close, color: AppColors.textSecondary),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),
          titlePadding: EdgeInsets.all(16),
          contentPadding: EdgeInsets.fromLTRB(16, 0, 16, 16),
          content: SizedBox(
            width: double.maxFinite,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Current Location Section
                Text(
                  'CURRENT',
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                  ),
                ),
                SizedBox(height: 8),
                Container(
                  padding: EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.accentPrimary.withAlpha(26),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppColors.accentPrimary, width: 2),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.location_on, color: AppColors.accentPrimary, size: 24),
                      SizedBox(width: 12),
                      Text(
                        _currentLocation,
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Spacer(),
                      Text(
                        '⭐',
                        style: TextStyle(fontSize: 20),
                      ),
                    ],
                  ),
                ),
                
                SizedBox(height: 20),
                
                // Other Locations Section
                Text(
                  'ACCESSIBLE',
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                  ),
                ),
                SizedBox(height: 8),
                
                // List of other locations
                ...sortedLocations
                    .where((loc) => loc != _currentLocation)
                    .map((location) {
                  final isLocked = false; // TODO: Implement lock logic
                  
                  return Container(
                    margin: EdgeInsets.only(bottom: 8),
                    child: ElevatedButton(
                      onPressed: isLocked ? null : () {
                        Navigator.pop(context);
                        setState(() {
                          _currentLocation = location;
                        });
                        _showSnackBar('Traveled to $location', color: AppColors.success);
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.bgSecondary,
                        foregroundColor: AppColors.textPrimary,
                        padding: EdgeInsets.all(12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                          side: BorderSide(color: AppColors.borderSubtle),
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            isLocked ? Icons.lock : Icons.place,
                            color: isLocked ? AppColors.textTertiary : AppColors.textSecondary,
                            size: 24,
                          ),
                          SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              location,
                              style: TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                          if (!isLocked)
                            Icon(Icons.arrow_forward, color: AppColors.accentPrimary, size: 20),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ],
            ),
          ),
        );
      },
    );
  }
  
  Widget _buildTaskCard(Map<String, dynamic> task, {required bool isAtCurrentLocation}) {
    final String taskId = task['id'] ?? '';
    final String description = task['description'] ?? 'Unknown task';
    final String location = task['location'] ?? 'Unknown';
    final String status = task['status'] ?? 'locked';
    final String type = task['type'] ?? 'minigame';
    final String? minigameId = task['minigame_id'];
    
    final bool isAvailable = status == 'available';
    final bool isCompleted = status == 'completed';
    
    // Gray out if not at current location
    final bool isGrayedOut = !isAtCurrentLocation && !isCompleted;
    
    return InkWell(
      onTap: isGrayedOut ? _showMapDialog : null,
      child: Container(
        margin: EdgeInsets.only(bottom: AppDimensions.spaceSM),
        padding: EdgeInsets.all(AppDimensions.containerPadding),
        decoration: BoxDecoration(
          color: isCompleted
              ? AppColors.success.withAlpha(26)
              : isGrayedOut
                  ? AppColors.bgSecondary.withAlpha(128)
                  : AppColors.bgSecondary,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          border: Border.all(
            color: isAvailable && isAtCurrentLocation
                ? AppColors.accentPrimary
                : isCompleted
                    ? AppColors.success
                    : AppColors.borderSubtle,
            width: isAvailable && isAtCurrentLocation ? 2 : 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Task name/description
            Text(
              description,
              style: TextStyle(
                color: isGrayedOut ? AppColors.textSecondary : AppColors.textPrimary,
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
            
            SizedBox(height: AppDimensions.spaceXS),
            
            // Type label & minigame ID
            Row(
              children: [
                Text(
                  _getTaskTypeLabel(type),
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 11,
                  ),
                ),
                if (minigameId != null) ...[
                  SizedBox(width: AppDimensions.spaceXS),
                  Text(
                    minigameId,
                    style: TextStyle(
                      color: AppColors.textTertiary,
                      fontSize: 10,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ],
            ),
            
            // Location indicator (only for location-specific tasks)
            if (type != 'discovery' && type != 'info_share') ...[
              SizedBox(height: AppDimensions.spaceXS),
              Row(
                children: [
                  Icon(Icons.location_on, color: AppColors.textSecondary, size: 12),
                  SizedBox(width: 4),
                  Text(
                    location,
                    style: TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ],
            
            // Action indicator
            if (isAvailable && isAtCurrentLocation) ...[
              SizedBox(height: AppDimensions.spaceXS),
              Text(
                '⚡ Tap to start',
                style: TextStyle(
                  color: AppColors.accentPrimary,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
            
            if (isGrayedOut) ...[
              SizedBox(height: AppDimensions.spaceXS),
              Row(
                children: [
                  Icon(Icons.map, color: AppColors.textSecondary, size: 12),
                  SizedBox(width: 4),
                  Text(
                    'Use Map to travel here',
                    style: TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ],
            
            if (isCompleted)
              Padding(
                padding: EdgeInsets.only(top: AppDimensions.spaceXS),
                child: Row(
                  children: [
                    Icon(Icons.check_circle, color: AppColors.success, size: 14),
                    SizedBox(width: 4),
                    Text(
                      'Completed',
                      style: TextStyle(
                        color: AppColors.success,
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            
            // Action button for available tasks at current location
            if (isAvailable && isAtCurrentLocation) ...[
              SizedBox(height: AppDimensions.spaceMD),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => _completeTask(taskId, type),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.accentPrimary,
                    padding: EdgeInsets.symmetric(vertical: 12),
                  ),
                  child: Text(
                    'Start Task',
                    style: TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildGameEndedScreen() {
    final bool won = _gameResult == 'success';
    
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: EdgeInsets.all(AppDimensions.space2XL),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  won ? Icons.celebration : Icons.error_outline,
                  size: 100,
                  color: won ? AppColors.success : AppColors.danger,
                ),
                SizedBox(height: AppDimensions.spaceLG),
                Text(
                  won ? '🎉 SUCCESS!' : '❌ FAILED',
                  style: TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: won ? AppColors.success : AppColors.danger,
                  ),
                ),
                SizedBox(height: AppDimensions.spaceMD),
                if (_gameSummary != null)
                  Text(
                    _gameSummary!,
                    style: TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 16,
                    ),
                    textAlign: TextAlign.center,
                  ),
                SizedBox(height: AppDimensions.spaceXL),
                HeistPrimaryButton(
                  text: 'Return to Lobby',
                  onPressed: () {
                    widget.wsService.disconnect();
                    Navigator.of(context).popUntil((route) => route.isFirst);
                  },
                  icon: Icons.home,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  // Search current room
  void _searchRoom() {
    widget.wsService.searchRoom();
    _showSnackBar('Searching $_currentLocation...', color: AppColors.info);
  }
  
  // Show search results modal
  void _showSearchResults(List<Item> items) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.75,
        decoration: BoxDecoration(
          color: AppColors.bgSecondary,
          borderRadius: BorderRadius.vertical(top: Radius.circular(AppDimensions.radiusLG)),
          border: Border.all(color: AppColors.borderSubtle),
        ),
        child: Column(
          children: [
            // Header
            Container(
              padding: EdgeInsets.all(AppDimensions.containerPadding),
              decoration: BoxDecoration(
                border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
              ),
              child: Row(
                children: [
                  Icon(Icons.search, color: AppColors.accentPrimary),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Search Results: $_currentLocation',
                      style: TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.close, color: AppColors.textSecondary),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
            // Items list
            Expanded(
              child: items.isEmpty
                  ? Center(
                      child: Text(
                        'No items found',
                        style: TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 16,
                        ),
                      ),
                    )
                  : ListView.builder(
                      padding: EdgeInsets.all(AppDimensions.containerPadding),
                      itemCount: items.length,
                      itemBuilder: (context, index) {
                        final item = items[index];
                        return Container(
                          margin: EdgeInsets.only(bottom: AppDimensions.spaceMD),
                          padding: EdgeInsets.all(AppDimensions.containerPadding),
                          decoration: BoxDecoration(
                            color: AppColors.bgPrimary,
                            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                            border: Border.all(color: AppColors.borderSubtle),
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Item image (80x80)
                              Container(
                                width: 80,
                                height: 80,
                                decoration: BoxDecoration(
                                  color: AppColors.bgSecondary,
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: AppColors.accentSecondary),
                                ),
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(7),
                                  child: Image.network(
                                    'http://localhost:8000/images/${widget.scenario}/item_${item.id}.png',
                                    fit: BoxFit.cover,
                                    errorBuilder: (context, error, stackTrace) {
                                      // Fallback icon if image not available
                                      return Center(
                                        child: Icon(
                                          Icons.inventory_2,
                                          color: AppColors.accentSecondary,
                                          size: 40,
                                        ),
                                      );
                                    },
                                  ),
                                ),
                              ),
                              SizedBox(width: 12),
                              // Item details
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      item.name,
                                      style: TextStyle(
                                        color: AppColors.textPrimary,
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    SizedBox(height: 4),
                                    Text(
                                      item.description,
                                      style: TextStyle(
                                        color: AppColors.textSecondary,
                                        fontSize: 13,
                                      ),
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    if (item.requiredFor != null) ...[
                                      SizedBox(height: 4),
                                      Text(
                                        'Required for: ${item.requiredFor}',
                                        style: TextStyle(
                                          color: AppColors.accentPrimary,
                                          fontSize: 11,
                                          fontStyle: FontStyle.italic,
                                        ),
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                        // Pick Up button below the row
                        SizedBox(height: 12),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: () {
                              Navigator.pop(context);
                              widget.wsService.pickUpItem(item.id);
                              _showSnackBar('Picked up: ${item.name}', color: AppColors.success);
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.accentPrimary,
                              padding: EdgeInsets.symmetric(vertical: 10),
                            ),
                            child: Text('Pick Up'),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  // Show inventory screen
  void _showInventory() {
    if (_myInventory.isEmpty) {
      _showSnackBar('Your bag is empty', color: AppColors.info);
      return;
    }
    
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.7,
        decoration: BoxDecoration(
          color: AppColors.bgSecondary,
          borderRadius: BorderRadius.vertical(top: Radius.circular(AppDimensions.radiusLG)),
          border: Border.all(color: AppColors.borderSubtle),
        ),
        child: Column(
          children: [
            // Header
            Container(
              padding: EdgeInsets.all(AppDimensions.containerPadding),
              decoration: BoxDecoration(
                border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
              ),
              child: Row(
                children: [
                  Icon(Icons.shopping_bag, color: AppColors.accentPrimary),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Your Inventory',
                      style: TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.close, color: AppColors.textSecondary),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
            // Items list
            Expanded(
              child: ListView.builder(
                padding: EdgeInsets.all(AppDimensions.containerPadding),
                itemCount: _myInventory.length,
                itemBuilder: (context, index) {
                  final item = _myInventory[index];
                  return Container(
                    margin: EdgeInsets.only(bottom: AppDimensions.spaceMD),
                    padding: EdgeInsets.all(AppDimensions.containerPadding),
                    decoration: BoxDecoration(
                      color: AppColors.bgPrimary,
                      borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                      border: Border.all(color: AppColors.accentSecondary),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Item image (80x80)
                        Container(
                          width: 80,
                          height: 80,
                          decoration: BoxDecoration(
                            color: AppColors.bgSecondary,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: AppColors.accentSecondary),
                          ),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(7),
                            child: Image.network(
                              'http://localhost:8000/images/${widget.scenario}/item_${item.id}.png',
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) {
                                // Fallback icon if image not available
                                return Center(
                                  child: Icon(
                                    Icons.inventory_2,
                                    color: AppColors.accentSecondary,
                                    size: 40,
                                  ),
                                );
                              },
                            ),
                          ),
                        ),
                        SizedBox(width: 12),
                        // Item details
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item.name,
                                style: TextStyle(
                                  color: AppColors.textPrimary,
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              SizedBox(height: 4),
                              Text(
                                item.description,
                                style: TextStyle(
                                  color: AppColors.textSecondary,
                                  fontSize: 13,
                                ),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                              if (item.requiredFor != null) ...[
                                SizedBox(height: 4),
                                Text(
                                  'Required for: ${item.requiredFor}',
                                  style: TextStyle(
                                    color: AppColors.accentPrimary,
                                    fontSize: 11,
                                    fontStyle: FontStyle.italic,
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                // Action buttons below the item
                SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                              child: OutlinedButton.icon(
                                onPressed: () => _showTransferDialog(item),
                                icon: Icon(Icons.send, size: 16),
                                label: Text('Transfer'),
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: AppColors.accentPrimary,
                                  side: BorderSide(color: AppColors.accentPrimary),
                                  padding: EdgeInsets.symmetric(vertical: 8),
                                ),
                              ),
                            ),
                            SizedBox(width: 8),
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: () => _useItem(item),
                                icon: Icon(Icons.touch_app, size: 16),
                                label: Text('Use'),
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: AppColors.accentSecondary,
                                  side: BorderSide(color: AppColors.accentSecondary),
                                  padding: EdgeInsets.symmetric(vertical: 8),
                                ),
                              ),
                            ),
                            SizedBox(width: 8),
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: () => _dropItem(item),
                                icon: Icon(Icons.delete_outline, size: 16),
                                label: Text('Drop'),
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: AppColors.textSecondary,
                                  side: BorderSide(color: AppColors.borderSubtle),
                                  padding: EdgeInsets.symmetric(vertical: 8),
                                ),
                              ),
                    ),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    ),
          ],
        ),
      ),
    );
  }
  
  // Show transfer dialog
  void _showTransferDialog(Item item) {
    // Get players in same location
    final playersHere = _allPlayers.where((p) {
      return p['id'] != _myPlayerId && p['location'] == _currentLocation;
    }).toList();
    
    if (playersHere.isEmpty) {
      _showSnackBar('No other players in this location', color: AppColors.warning);
      return;
    }
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.bgSecondary,
        title: Text(
          'Transfer ${item.name}',
          style: TextStyle(color: AppColors.textPrimary),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Select a player in $_currentLocation:',
              style: TextStyle(color: AppColors.textSecondary),
            ),
            SizedBox(height: 16),
            ...playersHere.map((player) {
              return Container(
                margin: EdgeInsets.only(bottom: 8),
                child: HeistPrimaryButton(
                  text: player['name'],
                  onPressed: () {
                    widget.wsService.handoffItem(item.id, player['id']);
                    Navigator.pop(context); // Close transfer dialog
                    Navigator.pop(context); // Close inventory
                    _showSnackBar('Transferring ${item.name} to ${player['name']}...');
                  },
                  icon: Icons.person,
                ),
              );
            }).toList(),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel', style: TextStyle(color: AppColors.textSecondary)),
          ),
        ],
      ),
    );
  }
  
  // Use an item
  void _useItem(Item item) {
    widget.wsService.useItem(item.id);
    Navigator.pop(context); // Close inventory
    // Backend will send info message with result
  }
  
  // Drop an item
  void _dropItem(Item item) {
    widget.wsService.dropItem(item.id);
    setState(() {
      _myInventory.removeWhere((i) => i.id == item.id);
    });
    Navigator.pop(context); // Close inventory
    _showSnackBar('Dropped ${item.name} in $_currentLocation', color: AppColors.info);
  }
}
