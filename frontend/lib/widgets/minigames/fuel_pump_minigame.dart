import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

/// Hold button to fill tank. Release when full—overflow = fail.
class FuelPumpMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;
  final VoidCallback? onSuccess;

  const FuelPumpMinigame({super.key, required this.difficulty, this.onSuccess});

  @override
  State<FuelPumpMinigame> createState() => _FuelPumpMinigameState();
}

class _FuelPumpMinigameState extends State<FuelPumpMinigame>
    with SingleTickerProviderStateMixin {
  late Ticker _ticker;
  Duration _lastTick = Duration.zero;

  late double _fillRate;   // per second
  late double _zoneMin;    // target zone (e.g. 0.85 = 85%)
  late double _zoneMax;    // 1.0 = 100%, don't overflow

  double _fillLevel = 0;
  bool _isHolding = false;
  bool _gameWon = false;
  bool _gameOver = false;
  late int _timeLimit;
  int _timeLeft = 0;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _fillRate = 0.4;
        _zoneMin = 0.80;
        _zoneMax = 0.95;
        _timeLimit = 12;
        break;
      case MinigameDifficulty.medium:
        _fillRate = 0.55;
        _zoneMin = 0.85;
        _zoneMax = 0.97;
        _timeLimit = 10;
        break;
      case MinigameDifficulty.hard:
        _fillRate = 0.7;
        _zoneMin = 0.90;
        _zoneMax = 0.98;
        _timeLimit = 8;
        break;
    }
    _timeLeft = _timeLimit;
    _ticker = createTicker(_onTick);
    _ticker.start();
    _startTimer();
  }

  void _onTick(Duration elapsed) {
    if (_gameWon || _gameOver || !mounted) return;

    final dt = (elapsed.inMilliseconds - _lastTick.inMilliseconds) / 1000.0;
    _lastTick = elapsed;

    if (_isHolding) {
      _fillLevel += _fillRate * dt;
      if (_fillLevel >= 1.0) {
        _fillLevel = 1.0;
        _gameOver = true;
        _ticker.stop();
      }
    }

    if (mounted) setState(() {});
  }

  void _onPointerDown(PointerDownEvent _) {
    if (_gameWon || _gameOver) return;
    setState(() => _isHolding = true);
  }

  void _startTimer() {
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) return;
      setState(() {
        _timeLeft--;
        if (_timeLeft <= 0) {
          _gameOver = true;
          _timer?.cancel();
          _ticker.stop();
        }
      });
    });
  }

  void _onPointerUp(PointerUpEvent _) {
    if (!_isHolding) return;
    setState(() {
      _isHolding = false;
      if (_fillLevel >= _zoneMin && _fillLevel <= _zoneMax) {
        _gameWon = true;
        _timer?.cancel();
        _ticker.stop();
      }
    });
  }

  void _onPointerCancel(PointerCancelEvent _) {
    setState(() => _isHolding = false);
  }

  void _resetGame() {
    setState(() {
      _lastTick = Duration.zero;
      _fillLevel = 0;
      _isHolding = false;
      _gameWon = false;
      _gameOver = false;
      _timeLeft = _timeLimit;
    });
    _ticker.start();
    _startTimer();
  }

  @override
  void dispose() {
    _timer?.cancel();
    _ticker.stop();
    _ticker.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return PopScope(
        canPop: widget.onSuccess == null,
        child: buildWinScreen('FILLED!', Icons.local_gas_station, _resetGame, onSuccess: widget.onSuccess),
      );
    }
    if (_gameOver) {
      return buildFailScreen(_resetGame);
    }

      return Listener(
      onPointerDown: _onPointerDown,
      onPointerUp: _onPointerUp,
      onPointerCancel: _onPointerCancel,
      child: Column(
        children: [
          buildStatsBar(
            '${(_fillLevel * 100).round()}%',
            'Time: ${_timeLeft}s',
          ),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Text(
              'HOLD to fill • Release in green zone • Don\'t overflow',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                color: AppColors.textSecondary,
              ),
            ),
          ),
          const SizedBox(height: 32),
          // Tank
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 60),
            child: Column(
              children: [
                Container(
                  width: 120,
                  height: 220,
                  decoration: BoxDecoration(
                    color: AppColors.bgSecondary,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: AppColors.borderSubtle,
                      width: 2,
                    ),
                  ),
                  child: Stack(
                    alignment: Alignment.bottomCenter,
                    children: [
                      // Target zone (green) - safe "full" band
                      Positioned(
                        left: 4,
                        right: 4,
                        bottom: 4 + 200 * (1 - _zoneMax),
                        height: 200 * (_zoneMax - _zoneMin),
                        child: Container(
                          decoration: BoxDecoration(
                            color: AppColors.success.withValues(alpha: 0.25),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(
                              color: AppColors.success.withValues(alpha: 0.6),
                              width: 1,
                            ),
                          ),
                        ),
                      ),
                      // Fill level
                      Positioned(
                        left: 6,
                        right: 6,
                        bottom: 6,
                        height: 200 * _fillLevel.clamp(0.0, 1.0),
                        child: Container(
                          decoration: BoxDecoration(
                            color: _fillLevel >= _zoneMin && _fillLevel <= _zoneMax
                                ? AppColors.success
                                : AppColors.accentPrimary,
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '${(_fillLevel * 100).round()}%',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
              ],
            ),
          ),
          const Spacer(),
          // Pump button
          Padding(
            padding: const EdgeInsets.only(bottom: 40),
            child: Material(
              color: _isHolding ? AppColors.accentPrimary : AppColors.bgSecondary,
              borderRadius: BorderRadius.circular(16),
              child: InkWell(
                onTap: () {}, // Handled by Listener
                borderRadius: BorderRadius.circular(16),
                child: Container(
                  width: 160,
                  height: 80,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: _isHolding
                          ? AppColors.accentPrimary
                          : AppColors.borderSubtle,
                      width: 2,
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.local_gas_station,
                        size: 32,
                        color: _isHolding
                            ? AppColors.bgPrimary
                            : AppColors.textSecondary,
                      ),
                      const SizedBox(width: 12),
                      Text(
                        _isHolding ? 'PUMPING...' : 'HOLD TO FILL',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: _isHolding
                              ? AppColors.bgPrimary
                              : AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
