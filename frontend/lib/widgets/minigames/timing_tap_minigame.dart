import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

class TimingTapMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;
  
  const TimingTapMinigame({super.key, required this.difficulty});

  @override
  State<TimingTapMinigame> createState() => _TimingTapMinigameState();
}

class _TimingTapMinigameState extends State<TimingTapMinigame> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  bool _gameWon = false;
  int _attempts = 0;
  int _successes = 0;
  String _feedback = '';
  late int _animationDuration;
  late double _zoneStart;
  late double _zoneEnd;
  late int _targetSuccesses;
  
  @override
  void initState() {
    super.initState();
    // Difficulty: speed, zone size, and target
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _animationDuration = 3000;
        _zoneStart = 0.35;
        _zoneEnd = 0.65;
        _targetSuccesses = 3;
        break;
      case MinigameDifficulty.medium:
        _animationDuration = 2500;
        _zoneStart = 0.40;
        _zoneEnd = 0.60;
        _targetSuccesses = 5;
        break;
      case MinigameDifficulty.hard:
        _animationDuration = 2000;
        _zoneStart = 0.43;
        _zoneEnd = 0.57;
        _targetSuccesses = 7;
        break;
    }
    
    _controller = AnimationController(
      vsync: this,
      duration: Duration(milliseconds: _animationDuration),
    )..repeat(reverse: true);
  }
  
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
  
  void _onTap() {
    setState(() {
      _attempts++;
      final value = _controller.value;
      if (value >= _zoneStart && value <= _zoneEnd) {
        _successes++;
        _feedback = 'PERFECT! ✓';
        if (_successes >= _targetSuccesses) {
          _gameWon = true;
          _controller.stop();
        }
      } else {
        _feedback = 'Too early/late ✗';
      }
      
      Future.delayed(const Duration(milliseconds: 500), () {
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
      _gameWon = false;
      _attempts = 0;
      _successes = 0;
    });
    _controller.repeat(reverse: true);
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('PERFECT STEAL!', Icons.check_circle, _resetGame);
    }
    
    return Column(
      children: [
        buildStatsBar(
          'Successes: $_successes / $_targetSuccesses',
          'Attempts: $_attempts',
        ),
        const SizedBox(height: 20),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            children: [
              const Text(
                'Tap when the circle enters the GREEN ZONE!',
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
        const SizedBox(height: 40),
        Expanded(
          child: Center(
            child: AnimatedBuilder(
              animation: _controller,
              builder: (context, child) {
                final value = _controller.value;
                final inGoodZone = value >= _zoneStart && value <= _zoneEnd;
                
                return Stack(
                  alignment: Alignment.center,
                  children: [
                    // Outer boundary
                    Container(
                      width: 300,
                      height: 300,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: AppColors.borderSubtle, width: 3),
                        color: Colors.transparent,
                      ),
                    ),
                    // Success zone indicator (green donut)
                    Container(
                      width: 300 * (1 - _zoneStart),
                      height: 300 * (1 - _zoneStart),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: AppColors.success.withOpacity(0.2),
                        border: Border.all(color: AppColors.success.withOpacity(0.6), width: 2),
                      ),
                    ),
                    // Inner cutout
                    Container(
                      width: 300 * (1 - _zoneEnd),
                      height: 300 * (1 - _zoneEnd),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: AppColors.bgPrimary,
                        border: Border.all(color: AppColors.success.withOpacity(0.6), width: 2),
                      ),
                    ),
                    // Shrinking circle
                    Container(
                      width: 300 * (1 - value),
                      height: 300 * (1 - value),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: inGoodZone 
                            ? AppColors.success.withOpacity(0.4)
                            : AppColors.accentPrimary.withOpacity(0.3),
                        border: Border.all(
                          color: inGoodZone ? AppColors.success : AppColors.accentPrimary,
                          width: 4,
                        ),
                        boxShadow: inGoodZone ? [
                          BoxShadow(
                            color: AppColors.success.withOpacity(0.6),
                            blurRadius: 20,
                            spreadRadius: 5,
                          ),
                        ] : [],
                      ),
                    ),
                    // Center dot
                    Container(
                      width: 20,
                      height: 20,
                      decoration: const BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(40),
          child: ElevatedButton(
            onPressed: _onTap,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.bgSecondary,
              padding: const EdgeInsets.symmetric(horizontal: 60, vertical: 20),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(30),
              ),
            ),
            child: const Text(
              'TAP NOW!',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
          ),
        ),
      ],
    );
  }
}
