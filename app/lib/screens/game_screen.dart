import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';
import 'package:the_heist/services/websocket_service.dart';
import 'package:the_heist/widgets/common/section_header.dart';
import 'package:the_heist/widgets/common/heist_primary_button.dart';
import 'package:the_heist/widgets/common/task_card.dart';

/// Game screen where players complete their tasks
class GameScreen extends StatefulWidget {
  final WebSocketService wsService;
  final String scenario;
  final String objective;
  final List<dynamic> yourTasks;
  
  const GameScreen({
    super.key,
    required this.wsService,
    required this.scenario,
    required this.objective,
    required this.yourTasks,
  });
  
  @override
  State<GameScreen> createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> {
  List<Map<String, dynamic>> _myTasks = [];
  List<String> _completedTaskIds = [];
  bool _gameEnded = false;
  String? _gameResult;
  String? _gameSummary;
  
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
  
  @override
  Widget build(BuildContext context) {
    if (_gameEnded) {
      return _buildGameEndedScreen();
    }
    
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        title: const Text('The Heist'),
        backgroundColor: AppColors.bgSecondary,
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: EdgeInsets.all(AppDimensions.space2XL),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Objective card
                _buildObjectiveCard(),
                
                SizedBox(height: AppDimensions.spaceLG),
                
                // Progress indicator
                _buildProgressIndicator(),
                
                SizedBox(height: AppDimensions.spaceLG),
                
                // Your tasks
                const SectionHeader(text: 'Your Tasks'),
                SizedBox(height: AppDimensions.spaceMD),
                
                if (_myTasks.isEmpty)
                  _buildEmptyState()
                else
                  ..._myTasks.map((task) => _buildTaskCard(task)),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildObjectiveCard() {
    return Container(
      padding: EdgeInsets.all(AppDimensions.containerPadding),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
        border: Border.all(color: AppColors.accentPrimary, width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.flag,
                color: AppColors.accentPrimary,
                size: 24,
              ),
              SizedBox(width: AppDimensions.spaceSM),
              Text(
                'OBJECTIVE',
                style: TextStyle(
                  color: AppColors.accentPrimary,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                ),
              ),
            ],
          ),
          SizedBox(height: AppDimensions.spaceSM),
          Text(
            widget.objective,
            style: TextStyle(
              color: AppColors.textPrimary,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildProgressIndicator() {
    final totalTasks = _myTasks.length;
    final completedTasks = _myTasks.where((t) => t['status'] == 'completed').length;
    final progress = totalTasks > 0 ? completedTasks / totalTasks : 0.0;
    
    return Container(
      padding: EdgeInsets.all(AppDimensions.containerPadding),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Your Progress',
                style: TextStyle(
                  color: AppColors.textSecondary,
                  fontSize: 12,
                ),
              ),
              Text(
                '$completedTasks / $totalTasks tasks',
                style: TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          SizedBox(height: AppDimensions.spaceSM),
          ClipRRect(
            borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 8,
              backgroundColor: AppColors.bgTertiary,
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.accentPrimary),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildTaskCard(Map<String, dynamic> task) {
    final String taskId = task['id'] ?? '';
    final String description = task['description'] ?? 'Unknown task';
    final String location = task['location'] ?? 'Unknown';
    final String status = task['status'] ?? 'locked';
    final String type = task['type'] ?? 'minigame';
    
    final bool isAvailable = status == 'available';
    final bool isCompleted = status == 'completed';
    final bool isLocked = status == 'locked';
    
    return Container(
      margin: EdgeInsets.only(bottom: AppDimensions.spaceMD),
      padding: EdgeInsets.all(AppDimensions.containerPadding),
      decoration: BoxDecoration(
        color: isCompleted
            ? AppColors.success.withAlpha(26)
            : isLocked
                ? AppColors.bgSecondary.withAlpha(128)
                : AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
        border: Border.all(
          color: isAvailable
              ? AppColors.accentPrimary
              : isCompleted
                  ? AppColors.success
                  : AppColors.borderSubtle,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: isCompleted
                      ? AppColors.success
                      : isLocked
                          ? AppColors.textTertiary
                          : AppColors.accentPrimary,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  taskId,
                  style: TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              SizedBox(width: AppDimensions.spaceSM),
              Text(
                _getTaskTypeLabel(type),
                style: TextStyle(
                  color: AppColors.textSecondary,
                  fontSize: 12,
                ),
              ),
              const Spacer(),
              if (isCompleted)
                Icon(Icons.check_circle, color: AppColors.success, size: 20),
              if (isLocked)
                Icon(Icons.lock, color: AppColors.textTertiary, size: 20),
            ],
          ),
          
          SizedBox(height: AppDimensions.spaceSM),
          
          // Description
          Text(
            description,
            style: TextStyle(
              color: isLocked ? AppColors.textTertiary : AppColors.textPrimary,
              fontSize: 14,
            ),
          ),
          
          SizedBox(height: AppDimensions.spaceSM),
          
          // Location
          Row(
            children: [
              Icon(
                Icons.location_on,
                color: AppColors.textSecondary,
                size: 14,
              ),
              SizedBox(width: 4),
              Text(
                location,
                style: TextStyle(
                  color: AppColors.textSecondary,
                  fontSize: 12,
                ),
              ),
            ],
          ),
          
          // Action button
          if (isAvailable) ...[
            SizedBox(height: AppDimensions.spaceMD),
            HeistPrimaryButton(
              text: 'Complete Task',
              onPressed: () => _completeTask(taskId, type),
              icon: Icons.check,
            ),
          ],
        ],
      ),
    );
  }
  
  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: EdgeInsets.all(AppDimensions.containerPadding),
        child: Column(
          children: [
            Icon(
              Icons.inbox,
              size: 64,
              color: AppColors.textTertiary,
            ),
            SizedBox(height: AppDimensions.spaceMD),
            Text(
              'No tasks yet',
              style: TextStyle(
                color: AppColors.textSecondary,
                fontSize: 16,
              ),
            ),
            Text(
              'Wait for your teammates to unlock tasks',
              style: TextStyle(
                color: AppColors.textTertiary,
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
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
