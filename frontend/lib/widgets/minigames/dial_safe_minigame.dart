import 'dart:math';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

class DialSafeMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;
  
  const DialSafeMinigame({super.key, required this.difficulty});

  @override
  State<DialSafeMinigame> createState() => _DialSafeMinigameState();
}

class _DialSafeMinigameState extends State<DialSafeMinigame> {
  double _rotation = 0.0;
  late List<int> _combination;
  final List<int> _userInput = [];
  int _currentStep = 0;
  bool _gameWon = false;
  late int _tolerance;
  
  @override
  void initState() {
    super.initState();
    // Difficulty: number of steps and tolerance
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _combination = [50, 25];
        _tolerance = 3;
        break;
      case MinigameDifficulty.medium:
        _combination = [15, 73, 42];
        _tolerance = 2;
        break;
      case MinigameDifficulty.hard:
        _combination = [88, 23, 57, 12];
        _tolerance = 1;
        break;
    }
  }
  
  int get _currentNumber => ((_rotation % 360) / 3.6).round() % 100;
  
  void _onDragUpdate(DragUpdateDetails details) {
    setState(() {
      _rotation += details.delta.dx * 0.5;
      _rotation = _rotation % 360;
    });
  }
  
  void _submitNumber() {
    if (_currentStep >= _combination.length) return;
    
    setState(() {
      _userInput.add(_currentNumber);
      
      // Check if correct (with tolerance)
      if (_userInput[_currentStep] >= _combination[_currentStep] - _tolerance &&
          _userInput[_currentStep] <= _combination[_currentStep] + _tolerance) {
        _currentStep++;
        if (_currentStep == _combination.length) {
          _gameWon = true;
        }
      } else {
        // Reset on wrong input
        _userInput.clear();
        _currentStep = 0;
      }
    });
  }
  
  void _resetGame() {
    setState(() {
      _rotation = 0.0;
      _userInput.clear();
      _currentStep = 0;
      _gameWon = false;
    });
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('CRACKED!', Icons.lock_open, _resetGame);
    }
    
    return Column(
      children: [
        buildStatsBar(
          'Step: ${_currentStep + 1} / ${_combination.length}',
          'Target: ${_currentStep < _combination.length ? _combination[_currentStep] : "—"}',
        ),
        const SizedBox(height: 12),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'Drag the dial to the target number, then tap Submit',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 14, color: AppColors.textSecondary, height: 1.4),
          ),
        ),
        const SizedBox(height: 16),
        Expanded(
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Current number display
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 12),
                  decoration: BoxDecoration(
                    color: AppColors.bgSecondary,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.borderSubtle, width: 2),
                  ),
                  child: Text(
                    _currentNumber.toString().padLeft(2, '0'),
                    style: const TextStyle(
                      fontSize: 42,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                // Dial (smaller)
                GestureDetector(
                  onPanUpdate: _onDragUpdate,
                  child: Transform.rotate(
                    angle: _rotation * pi / 180,
                    child: Container(
                      width: 140,
                      height: 140,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: AppColors.bgSecondary,
                        border: Border.all(color: AppColors.borderSubtle, width: 4),
                      ),
                      child: Stack(
                        children: [
                          Center(
                            child: Container(
                              width: 14,
                              height: 14,
                              decoration: const BoxDecoration(
                                color: Colors.white,
                                shape: BoxShape.circle,
                              ),
                            ),
                          ),
                          Positioned(
                            top: 8,
                            left: 60,
                            child: Container(
                              width: 16,
                              height: 44,
                              decoration: BoxDecoration(
                                color: AppColors.accentPrimary,
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                // Submit button
                Padding(
                  padding: const EdgeInsets.only(bottom: 24),
                  child: ElevatedButton(
                    onPressed: _submitNumber,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.bgSecondary,
                      padding: const EdgeInsets.symmetric(horizontal: 36, vertical: 14),
                    ),
                    child: const Text('Submit', style: TextStyle(fontSize: 16)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
