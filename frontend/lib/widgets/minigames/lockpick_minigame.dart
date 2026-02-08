import 'dart:math';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

class LockpickMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;
  
  const LockpickMinigame({super.key, required this.difficulty});

  @override
  State<LockpickMinigame> createState() => _LockpickMinigameState();
}

class _LockpickMinigameState extends State<LockpickMinigame> {
  late int _pinCount;
  late List<double> _pinPositions;
  late List<double> _targetPositions;
  late List<bool> _pinsSolved;
  int _attempts = 0;
  bool _gameWon = false;
  late double _proximityThreshold;
  
  @override
  void initState() {
    super.initState();
    _initializeGame();
  }
  
  void _initializeGame() {
    final random = Random();
    // Difficulty: number of pins and precision required
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _pinCount = 3;
        _proximityThreshold = 0.92; // More lenient
        break;
      case MinigameDifficulty.medium:
        _pinCount = 5;
        _proximityThreshold = 0.95;
        break;
      case MinigameDifficulty.hard:
        _pinCount = 7;
        _proximityThreshold = 0.97; // More precise
        break;
    }
    
    _pinPositions = List.generate(_pinCount, (_) => 0.0);
    _targetPositions = List.generate(_pinCount, (_) => random.nextDouble());
    _pinsSolved = List.generate(_pinCount, (_) => false);
    _attempts = 0;
    _gameWon = false;
  }
  
  void _resetGame() {
    setState(() {
      _initializeGame();
    });
  }
  
  double _getProximity(int pinIndex) {
    final diff = (_pinPositions[pinIndex] - _targetPositions[pinIndex]).abs();
    return 1.0 - diff;
  }
  
  Color _getProximityColor(int pinIndex) {
    if (_pinsSolved[pinIndex]) return AppColors.success;
    final proximity = _getProximity(pinIndex);
    if (proximity > _proximityThreshold) return AppColors.success.withOpacity(0.7);
    if (proximity > 0.85) return Colors.yellow.shade300;
    if (proximity > 0.70) return Colors.orange.shade300;
    return Colors.red.shade300;
  }
  
  void _onPinDragged(int pinIndex, double delta) {
    setState(() {
      _pinPositions[pinIndex] = (_pinPositions[pinIndex] + delta).clamp(0.0, 1.0);
      _pinsSolved[pinIndex] = _getProximity(pinIndex) > _proximityThreshold;
      if (_pinsSolved.every((solved) => solved)) {
        _gameWon = true;
      }
    });
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('UNLOCKED!', Icons.lock_open, _resetGame);
    }
    
    return Column(
      children: [
        buildStatsBar(
          'Attempts: $_attempts',
          'Solved: ${_pinsSolved.where((s) => s).length}/$_pinCount',
        ),
        const SizedBox(height: 20),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'Drag each pin to find the correct position.\nGreen = locked!',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 16, color: AppColors.textSecondary, height: 1.5),
          ),
        ),
        const SizedBox(height: 20),
        Expanded(
          child: Center(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(_pinCount, (index) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    child: _buildPin(index),
                  );
                }),
              ),
            ),
          ),
        ),
      ],
    );
  }
  
  Widget _buildPin(int index) {
    final color = _getProximityColor(index);
    final isSolved = _pinsSolved[index];
    
    return GestureDetector(
      onVerticalDragUpdate: (details) {
        _onPinDragged(index, -details.delta.dy / 300);
        _attempts++;
      },
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 40,
            height: 300,
            decoration: BoxDecoration(
              color: AppColors.bgSecondary,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.borderSubtle, width: 2),
            ),
            child: Stack(
              children: [
                Positioned(
                  bottom: _pinPositions[index] * 260 + 20,
                  left: 0,
                  right: 0,
                  child: Container(
                    height: 20,
                    margin: const EdgeInsets.symmetric(horizontal: 8),
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(10),
                      boxShadow: [
                        BoxShadow(
                          color: color.withOpacity(0.5),
                          blurRadius: isSolved ? 15 : 5,
                          spreadRadius: isSolved ? 2 : 0,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: isSolved ? AppColors.success : Colors.grey.shade800,
              shape: BoxShape.circle,
              border: Border.all(
                color: isSolved ? AppColors.success.withOpacity(0.7) : Colors.grey.shade600,
                width: 2,
              ),
            ),
            child: Icon(
              isSolved ? Icons.check : Icons.lock,
              color: Colors.white,
              size: 20,
            ),
          ),
        ],
      ),
    );
  }
}
