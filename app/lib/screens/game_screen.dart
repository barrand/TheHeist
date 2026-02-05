import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';
import 'package:the_heist/services/websocket_service.dart';
import 'package:the_heist/widgets/common/heist_primary_button.dart';

/// Game screen where players complete their tasks
class GameScreen extends StatefulWidget {
  final WebSocketService wsService;
  final String scenario;
  final String objective;
  final List<dynamic> yourTasks;
  final String? playerRole;
  
  const GameScreen({
    super.key,
    required this.wsService,
    required this.scenario,
    required this.objective,
    required this.yourTasks,
    this.playerRole,
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
  String _currentLocation = 'Crew Hideout'; // All games start at Crew Hideout
  bool _showCompletedTasks = false;
  
  @override
  void initState() {
    super.initState();
    _myTasks = widget.yourTasks.map((t) => Map<String, dynamic>.from(t)).toList();
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
    
    // Game ended
    widget.wsService.messages.listen((message) {
      if (message['type'] == 'game_ended') {
        setState(() {
          _gameEnded = true;
          _gameResult = message['result'];
          _gameSummary = message['summary'];
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
    final tasksHere = _myTasks.where((t) => 
      t['location'] == _currentLocation && t['status'] != 'completed'
    ).toList();
    
    final tasksElsewhere = _myTasks.where((t) => 
      t['location'] != _currentLocation && t['status'] != 'completed'
    ).toList();
    
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
      padding: EdgeInsets.symmetric(
        horizontal: AppDimensions.containerPadding,
        vertical: AppDimensions.spaceMD,
      ),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        border: Border(
          bottom: BorderSide(color: AppColors.borderSubtle, width: 1),
        ),
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
          _buildNavButton(Icons.backpack, 'Bag', () {
            _showSnackBar('Inventory coming soon!');
          }),
          _buildNavButton(Icons.search, 'Search', () {
            _showSnackBar('Search room coming soon!');
          }),
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
    // Get all unique locations from tasks
    final Set<String> allLocations = _myTasks
        .map((task) => task['location'] as String?)
        .where((loc) => loc != null && loc.isNotEmpty)
        .cast<String>()
        .toSet();
    
    // Always include Crew Hideout if not already present
    allLocations.add('Crew Hideout');
    
    final sortedLocations = allLocations.toList()..sort();
    
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
            
            // Location indicator
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
}
