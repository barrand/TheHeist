import 'dart:math';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

class RhythmClimbMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;
  
  const RhythmClimbMinigame({super.key, required this.difficulty});

  @override
  State<RhythmClimbMinigame> createState() => _RhythmClimbMinigameState();
}

class _RhythmClimbMinigameState extends State<RhythmClimbMinigame> with SingleTickerProviderStateMixin {
  late AnimationController _noteController;
  int _height = 0;
  late int _targetHeight;
  bool _gameWon = false;
  String _feedback = '';
  int _consecutiveMisses = 0;
  double _targetLinePosition = 0.7;
  final List<double> _possiblePositions = [0.3, 0.5, 0.7, 0.85];
  late int _noteDuration;
  late double _hitZoneSize;
  
  @override
  void initState() {
    super.initState();
    // Difficulty: target height, speed, hit zone
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _targetHeight = 6;
        _noteDuration = 2500;
        _hitZoneSize = 0.10;
        break;
      case MinigameDifficulty.medium:
        _targetHeight = 10;
        _noteDuration = 2000;
        _hitZoneSize = 0.08;
        break;
      case MinigameDifficulty.hard:
        _targetHeight = 15;
        _noteDuration = 1600;
        _hitZoneSize = 0.06;
        break;
    }
    
    _noteController = AnimationController(
      vsync: this,
      duration: Duration(milliseconds: _noteDuration),
    )..repeat();
  }
  
  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }
  
  void _onTap() {
    final noteValue = _noteController.value;
    final onBeat = (noteValue >= _targetLinePosition - _hitZoneSize && 
                     noteValue <= _targetLinePosition + _hitZoneSize);
    
    setState(() {
      if (onBeat) {
        _height++;
        _consecutiveMisses = 0;
        _feedback = 'PERFECT! ✓';
        
        // Move target
        final currentIndex = _possiblePositions.indexOf(_targetLinePosition);
        final availablePositions = List<double>.from(_possiblePositions);
        if (currentIndex != -1) {
          availablePositions.removeAt(currentIndex);
        }
        _targetLinePosition = availablePositions[Random().nextInt(availablePositions.length)];
        
        if (_height >= _targetHeight) {
          _gameWon = true;
          _noteController.stop();
        }
      } else {
        _consecutiveMisses++;
        _feedback = 'MISSED ✗';
        if (_consecutiveMisses >= 2 && _height > 0) {
          _height--;
        }
      }
      
      Future.delayed(const Duration(milliseconds: 400), () {
        if (mounted) {
          setState(() {
            _feedback = '';
          });
        }
      });
    });
  }
  
  void _resetGame() {
    setState(() {
      _height = 0;
      _gameWon = false;
      _feedback = '';
      _consecutiveMisses = 0;
      _targetLinePosition = 0.7;
    });
    _noteController.repeat();
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('REACHED THE TOP!', Icons.check_circle, _resetGame);
    }
    
    return Column(
      children: [
        buildStatsBar(
          'Height: $_height / $_targetHeight',
          'Miss Streak: $_consecutiveMisses',
        ),
        const SizedBox(height: 20),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            children: [
              const Text(
                'Tap when the note hits the target line!\n⚠️ Target moves after each hit!',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: AppColors.textSecondary, height: 1.5),
              ),
              const SizedBox(height: 8),
              if (_feedback.isNotEmpty)
                Text(
                  _feedback,
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: _feedback.contains('PERFECT') ? AppColors.success : AppColors.danger,
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        // Guitar Hero style note highway
        Expanded(
          child: Container(
            width: 120,
            margin: const EdgeInsets.symmetric(horizontal: 40),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.5),
              border: Border.all(color: AppColors.borderSubtle, width: 2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Stack(
              children: [
                // Target line
                Positioned(
                  top: MediaQuery.of(context).size.height * 0.4 * _targetLinePosition,
                  left: 0,
                  right: 0,
                  child: Container(
                    height: 60,
                    decoration: BoxDecoration(
                      color: AppColors.success.withOpacity(0.3),
                      border: Border.all(color: AppColors.success, width: 3),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Center(
                      child: Text(
                        'TAP HERE',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ),
                // Moving note
                AnimatedBuilder(
                  animation: _noteController,
                  builder: (context, child) {
                    return Positioned(
                      top: MediaQuery.of(context).size.height * 0.4 * _noteController.value,
                      left: 0,
                      right: 0,
                      child: Center(
                        child: Container(
                          width: 50,
                          height: 50,
                          decoration: BoxDecoration(
                            color: AppColors.accentPrimary,
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.white, width: 2),
                            boxShadow: [
                              BoxShadow(
                                color: AppColors.accentPrimary.withOpacity(0.6),
                                blurRadius: 15,
                                spreadRadius: 3,
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.music_note,
                            color: Colors.white,
                            size: 24,
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        // Height indicator
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.stairs, color: AppColors.textSecondary),
            const SizedBox(width: 8),
            Text(
              'Height: $_height / $_targetHeight',
              style: const TextStyle(
                fontSize: 18,
                color: AppColors.textSecondary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        // Progress bar
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 40),
          child: LinearProgressIndicator(
            value: _height / _targetHeight,
            minHeight: 10,
            backgroundColor: Colors.grey.shade800,
            valueColor: AlwaysStoppedAnimation<Color>(
              _height >= _targetHeight * 0.7 ? AppColors.success : AppColors.accentPrimary,
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(30),
          child: GestureDetector(
            onTap: _onTap,
            child: Container(
              width: 200,
              height: 80,
              decoration: BoxDecoration(
                color: AppColors.bgSecondary,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.accentPrimary, width: 2),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.accentPrimary.withOpacity(0.3),
                    blurRadius: 15,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: const Center(
                child: Text(
                  'TAP!',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
