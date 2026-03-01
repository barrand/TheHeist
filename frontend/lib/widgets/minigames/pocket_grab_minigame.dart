import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

/// Hand moves fast at top; tap when it aligns with the object in the pocket to grab.
class PocketGrabMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;

  const PocketGrabMinigame({super.key, required this.difficulty});

  @override
  State<PocketGrabMinigame> createState() => _PocketGrabMinigameState();
}

class _PocketGrabMinigameState extends State<PocketGrabMinigame>
    with SingleTickerProviderStateMixin {
  static const double _gameWidth = 280;
  static const double _gameHeight = 380;
  static const double _handWidth = 50;
  static const double _handHeight = 45;
  static const double _objectSize = 40;

  late Ticker _ticker;
  late double _handVelocity;  // pixels per second, always constant
  late double _amplitude;
  late int _targetGrabs;
  late int _maxMisses;
  late double _tolerance;

  double _handX = 0;
  double _handDirection = 1;  // 1 = right, -1 = left
  double _objectX = 0;
  Duration _lastTick = Duration.zero;
  int _grabs = 0;
  int _misses = 0;
  bool _isGrabbing = false;
  double _grabProgress = 0;
  late Random _random;
  bool _gameWon = false;
  bool _gameOver = false;

  @override
  void initState() {
    super.initState();
    _random = Random();

    // Fixed velocity—NEVER accelerates. Slow the whole time.
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _handVelocity = 200;  // pixels/sec
        _amplitude = 90;
        _targetGrabs = 3;
        _maxMisses = 3;
        _tolerance = 35;
        break;
      case MinigameDifficulty.medium:
        _handVelocity = 260;
        _amplitude = 85;
        _targetGrabs = 4;
        _maxMisses = 2;
        _tolerance = 28;
        break;
      case MinigameDifficulty.hard:
        _handVelocity = 320;
        _amplitude = 80;
        _targetGrabs = 5;
        _maxMisses = 1;
        _tolerance = 22;
        break;
    }

    _resetRound();
    final center = _gameWidth / 2 - _handWidth / 2;
    _handX = center - _amplitude;
    _handDirection = 1;
    _ticker = createTicker(_onTick);
    _ticker.start();
  }

  void _resetRound() {
    _objectX = 40 + _random.nextDouble() * (_gameWidth - 80 - _objectSize);
    _isGrabbing = false;
    _grabProgress = 0;
  }

  void _onTick(Duration elapsed) {
    if (_gameWon || _gameOver || !mounted) return;

    final dt = (elapsed.inMilliseconds - _lastTick.inMilliseconds) / 1000.0;
    _lastTick = elapsed;

    if (_isGrabbing) {
      _grabProgress += dt / 0.25;  // 0.25 sec to complete grab
      if (_grabProgress >= 1) {
        _isGrabbing = false;
        _grabs++;
        if (_grabs >= _targetGrabs) {
          _gameWon = true;
          _ticker.stop();
        } else {
          _resetRound();
        }
      }
    } else {
      if (dt > 0 && dt < 0.1) {  // ignore huge spikes / first frame
        final center = _gameWidth / 2 - _handWidth / 2;
        final left = center - _amplitude;
        final right = center + _amplitude;
        _handX += _handVelocity * _handDirection * dt;
        if (_handX >= right) { _handX = right; _handDirection = -1; }
        if (_handX <= left) { _handX = left; _handDirection = 1; }
      }
    }

    if (mounted) setState(() {});
  }

  void _onTap() {
    if (_gameWon || _gameOver || _isGrabbing) return;

    final handCenter = _handX + _handWidth / 2;
    final objectCenter = _objectX + _objectSize / 2;
    final aligned = (handCenter - objectCenter).abs() < _tolerance;

    setState(() {
      if (aligned) {
        _isGrabbing = true;
        _grabProgress = 0;
      } else {
        _misses++;
        if (_misses > _maxMisses) {
          _gameOver = true;
          _ticker.stop();
        } else {
          _resetRound();
        }
      }
    });
  }

  @override
  void dispose() {
    _ticker.stop();
    _ticker.dispose();
    super.dispose();
  }

  void _resetGame() {
    setState(() {
      _lastTick = Duration.zero;
      _gameWon = false;
      _gameOver = false;
      _grabs = 0;
      _misses = 0;
    });
    _resetRound();
    _ticker.start();
  }

  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('GOT IT!', Icons.back_hand, _resetGame);
    }
    if (_gameOver) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.touch_app, size: 80, color: AppColors.danger),
            const SizedBox(height: 24),
            const Text(
              'CAUGHT!',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: AppColors.danger,
              ),
            ),
            Text(
              'Grabbed $_grabs / $_targetGrabs',
              style: const TextStyle(fontSize: 18, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 40),
            ElevatedButton.icon(
              onPressed: _resetGame,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.bgSecondary,
                foregroundColor: AppColors.textPrimary,
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                textStyle: const TextStyle(fontSize: 18),
              ),
            ),
          ],
        ),
      );
    }

    return GestureDetector(
      onTap: _onTap,
      child: Column(
        children: [
          buildStatsBar(
            'Grabs: $_grabs / $_targetGrabs',
            'Misses: $_misses / $_maxMisses',
          ),
          const SizedBox(height: 8),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 20),
            child: Text(
              'Tap when the hand lines up with the object',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: AppColors.textSecondary),
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: Center(
              child: Container(
                width: _gameWidth,
                height: _gameHeight,
                decoration: BoxDecoration(
                  color: AppColors.bgSecondary,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.borderSubtle, width: 2),
                ),
                clipBehavior: Clip.hardEdge,
                child: Stack(
                  children: [
                    // Pocket area (bottom)
                    Positioned(
                      left: 0,
                      right: 0,
                      bottom: 0,
                      height: 180,
                      child: Container(
                        decoration: BoxDecoration(
                          color: AppColors.bgTertiary,
                          border: Border(
                            top: BorderSide(color: AppColors.borderSubtle, width: 2),
                          ),
                        ),
                        child: Stack(
                          children: [
                            Center(
                              child: Text(
                                'POCKET',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: AppColors.textSecondary.withValues(alpha: 0.5),
                                ),
                              ),
                            ),
                            // Object in pocket
                            if (!_isGrabbing || _grabProgress < 0.5)
                              Positioned(
                                left: _objectX,
                                bottom: 70,
                                child: Container(
                                  width: _objectSize,
                                  height: _objectSize,
                                  decoration: BoxDecoration(
                                    color: AppColors.accentPrimary.withValues(alpha: 0.9),
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(color: AppColors.accentLight, width: 2),
                                  ),
                                  child: const Icon(Icons.credit_card, color: Colors.white, size: 24),
                                ),
                              ),
                          ],
                        ),
                      ),
                    ),
                    // Hand (moving or grabbing)
                    Positioned(
                      left: _handX,
                      top: _isGrabbing
                          ? 30 + _grabProgress * 200
                          : 20,
                      child: Container(
                        width: _handWidth,
                        height: _handHeight,
                        decoration: BoxDecoration(
                          color: Colors.brown.shade700,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.brown.shade900, width: 2),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.4),
                              blurRadius: 6,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Icon(
                          _isGrabbing ? Icons.front_hand : Icons.back_hand,
                          color: Colors.brown.shade200,
                          size: 28,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
