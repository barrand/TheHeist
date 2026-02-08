import 'dart:async';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

class ButtonMashMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;
  
  const ButtonMashMinigame({super.key, required this.difficulty});

  @override
  State<ButtonMashMinigame> createState() => _ButtonMashMinigameState();
}

class _ButtonMashMinigameState extends State<ButtonMashMinigame> {
  int _taps = 0;
  late int _targetTaps;
  bool _gameWon = false;
  Timer? _timer;
  late int _timeLeft;
  late int _startTime;
  
  @override
  void initState() {
    super.initState();
    // Difficulty: target taps and time
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _targetTaps = 30;
        _startTime = 15;
        break;
      case MinigameDifficulty.medium:
        _targetTaps = 50;
        _startTime = 10;
        break;
      case MinigameDifficulty.hard:
        _targetTaps = 70;
        _startTime = 8;
        break;
    }
    _timeLeft = _startTime;
    _startTimer();
  }
  
  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
  
  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        _timeLeft--;
        if (_timeLeft <= 0) {
          timer.cancel();
        }
      });
    });
  }
  
  void _onTap() {
    if (_gameWon || _timeLeft <= 0) return;
    
    setState(() {
      _taps++;
      if (_taps >= _targetTaps) {
        _gameWon = true;
        _timer?.cancel();
      }
    });
  }
  
  void _resetGame() {
    setState(() {
      _taps = 0;
      _gameWon = false;
      _timeLeft = _startTime;
    });
    _timer?.cancel();
    _startTimer();
  }
  
  @override
  Widget build(BuildContext context) {
    final progress = _taps / _targetTaps;
    
    if (_gameWon) {
      return buildWinScreen('SMASHED!', Icons.fitness_center, _resetGame);
    }
    
    if (_timeLeft <= 0 && !_gameWon) {
      return buildFailScreen(_resetGame);
    }
    
    return Column(
      children: [
        buildStatsBar(
          'Taps: $_taps / $_targetTaps',
          'Time: ${_timeLeft}s',
        ),
        const SizedBox(height: 20),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'TAP AS FAST AS YOU CAN!',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 20,
              color: AppColors.textPrimary,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
            ),
          ),
        ),
        const SizedBox(height: 40),
        // Progress bar
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 40),
          child: Column(
            children: [
              LinearProgressIndicator(
                value: progress,
                minHeight: 20,
                backgroundColor: Colors.grey.shade800,
                valueColor: AlwaysStoppedAnimation<Color>(
                  progress > 0.7 ? AppColors.success : Colors.orange,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${(progress * 100).toInt()}%',
                style: const TextStyle(fontSize: 18, color: AppColors.textSecondary),
              ),
            ],
          ),
        ),
        const SizedBox(height: 60),
        // Big tap button
        Expanded(
          child: Center(
            child: GestureDetector(
              onTap: _onTap,
              child: Container(
                width: 250,
                height: 250,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.red.withOpacity(0.3),
                  border: Border.all(color: Colors.red, width: 5),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.red.withOpacity(0.5),
                      blurRadius: 30,
                      spreadRadius: 10,
                    ),
                  ],
                ),
                child: const Center(
                  child: Text(
                    'TAP!',
                    style: TextStyle(
                      fontSize: 48,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
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
