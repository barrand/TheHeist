import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

/// Tap threats on camera feeds. Avoid decoys (civilians). Missed threats or wrong taps = fail.
class WhackAThreatMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;

  const WhackAThreatMinigame({super.key, required this.difficulty});

  @override
  State<WhackAThreatMinigame> createState() => _WhackAThreatMinigameState();
}

class _Threat {
  final int slotIndex;
  final bool isThreat; // true = tap it, false = decoy, don't tap
  final int id;
  final int iconType; // 0=guard, 1=alarm for threats; 0=civilian for decoy
  _Threat(this.slotIndex, this.isThreat, this.id, this.iconType);
}

class _WhackAThreatMinigameState extends State<WhackAThreatMinigame>
    with SingleTickerProviderStateMixin {
  late int _gridCols;
  late int _gridRows;
  late int _totalSlots;
  late int _targetThreats;
  late int _maxMisses;
  late int _maxWrongTaps;
  late double _spawnInterval;
  late double _stayDuration;

  int _threatsHit = 0;
  int _misses = 0;
  int _wrongTaps = 0;
  final Map<int, _Threat> _activeThreats = {};
  int _nextId = 0;
  Timer? _spawnTimer;
  Ticker? _ticker;
  late Random _random;
  bool _gameWon = false;
  bool _gameOver = false;
  String _gameOverReason = '';

  @override
  void initState() {
    super.initState();
    _random = Random();

    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _gridCols = 2;
        _gridRows = 2;
        _targetThreats = 8;
        _maxMisses = 3;
        _maxWrongTaps = 2;
        _spawnInterval = 0.9;
        _stayDuration = 1.2;
        break;
      case MinigameDifficulty.medium:
        _gridCols = 3;
        _gridRows = 2;
        _targetThreats = 12;
        _maxMisses = 3;
        _maxWrongTaps = 2;
        _spawnInterval = 0.7;
        _stayDuration = 1.0;
        break;
      case MinigameDifficulty.hard:
        _gridCols = 3;
        _gridRows = 3;
        _targetThreats = 18;
        _maxMisses = 2;
        _maxWrongTaps = 1;
        _spawnInterval = 0.5;
        _stayDuration = 0.8;
        break;
    }
    _totalSlots = _gridCols * _gridRows;

    _startGame();
  }

  void _startGame() {
    _spawnTimer?.cancel();
    _ticker?.stop();
    _ticker?.dispose();
    _ticker = null;
    _threatsHit = 0;
    _misses = 0;
    _wrongTaps = 0;
    _activeThreats.clear();
    _nextId = 0;
    final ticker = createTicker(_onTick);
    ticker.start();
    _ticker = ticker;
    _scheduleSpawn();
    if (mounted) setState(() {});
  }

  void _scheduleSpawn() {
    _spawnTimer?.cancel();
    if (_gameWon || _gameOver) return;
    _spawnTimer = Timer(Duration(milliseconds: (_spawnInterval * 1000).round()), () {
      if (!mounted || _gameWon || _gameOver) return;
      _spawnThreat();
      if (!_gameWon && !_gameOver) _scheduleSpawn();
    });
  }

  void _spawnThreat() {
    if (_threatsHit >= _targetThreats) return;

    final occupied = _activeThreats.values.map((t) => t.slotIndex).toSet();
    final available = <int>[];
    for (int i = 0; i < _totalSlots; i++) {
      if (!occupied.contains(i)) available.add(i);
    }
    if (available.isEmpty) return;

    final slot = available[_random.nextInt(available.length)];
    final isThreat = _random.nextDouble() < 0.7;
    final iconType = isThreat ? _random.nextInt(2) : 0;
    final t = _Threat(slot, isThreat, _nextId++, iconType);
    _activeThreats[t.id] = t;

    Timer(Duration(milliseconds: (_stayDuration * 1000).round()), () {
      if (!mounted) return;
      if (_activeThreats.containsKey(t.id)) {
        _activeThreats.remove(t.id);
        if (t.isThreat) {
          setState(() {
            _misses++;
            if (_misses > _maxMisses) {
              _gameOver = true;
              _gameOverReason = 'Too many missed!';
              _ticker?.stop();
              _spawnTimer?.cancel();
            }
          });
        }
      }
    });

    setState(() {});
  }

  void _onTick(Duration elapsed) {
    if (_gameWon || _gameOver || !mounted) return;
    setState(() {});
  }

  void _onSlotTap(int slotIndex) {
    if (_gameWon || _gameOver) return;

    _Threat? found;
    for (final t in _activeThreats.values) {
      if (t.slotIndex == slotIndex) {
        found = t;
        break;
      }
    }

    if (found == null) return;

    _activeThreats.remove(found.id);

    setState(() {
      if (found!.isThreat) {
        _threatsHit++;
        if (_threatsHit >= _targetThreats) {
          _gameWon = true;
          _ticker?.stop();
          _spawnTimer?.cancel();
        }
      } else {
        _wrongTaps++;
        if (_wrongTaps > _maxWrongTaps) {
          _gameOver = true;
          _gameOverReason = 'Wrong tap!';
          _ticker?.stop();
          _spawnTimer?.cancel();
        }
      }
    });
  }

  @override
  void dispose() {
    _spawnTimer?.cancel();
    _ticker?.stop();
    _ticker?.dispose();
    super.dispose();
  }

  void _resetGame() {
    setState(() {
      _gameWon = false;
      _gameOver = false;
      _gameOverReason = '';
    });
    _startGame();
  }

  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('CLEAR!', Icons.visibility, _resetGame);
    }
    if (_gameOver) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.warning_amber_rounded, size: 80, color: AppColors.danger),
            const SizedBox(height: 24),
            const Text(
              'FAILED!',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: AppColors.danger,
              ),
            ),
            Text(
              _gameOverReason,
              style: const TextStyle(fontSize: 18, color: AppColors.textSecondary),
            ),
            Text(
              'Hit $_threatsHit / $_targetThreats',
              style: const TextStyle(fontSize: 16, color: AppColors.textSecondary),
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

    return Column(
      children: [
        buildStatsBar(
          'Threats: $_threatsHit / $_targetThreats',
          'Miss: $_misses | Wrong: $_wrongTaps',
        ),
        const SizedBox(height: 8),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'Tap threats (guard, alarm). Avoid decoys.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 14, color: AppColors.textSecondary),
          ),
        ),
        const SizedBox(height: 16),
        Expanded(
          child: Center(
            child: Container(
              padding: const EdgeInsets.all(16),
              margin: const EdgeInsets.symmetric(horizontal: 12),
              constraints: const BoxConstraints(maxWidth: 400, maxHeight: 420),
              decoration: BoxDecoration(
                color: AppColors.bgSecondary,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.borderSubtle, width: 2),
              ),
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final w = constraints.maxWidth;
                  final h = constraints.maxHeight;
                  return SizedBox(
                    width: w,
                    height: h,
                    child: GridView.builder(
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: _gridCols,
                    crossAxisSpacing: 8,
                    mainAxisSpacing: 8,
                    childAspectRatio: 1,
                  ),
                  itemCount: _totalSlots,
                  itemBuilder: (context, index) => _buildCameraFeed(index),
                ),
                  );
                },
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCameraFeed(int slotIndex) {
    _Threat? threat;
    for (final t in _activeThreats.values) {
      if (t.slotIndex == slotIndex) {
        threat = t;
        break;
      }
    }

    return GestureDetector(
      onTap: () => _onSlotTap(slotIndex),
      child: Container(
        decoration: BoxDecoration(
          color: const Color(0xFF1a1625),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: AppColors.borderSubtle, width: 2),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.5),
              blurRadius: 4,
              spreadRadius: 0,
            ),
          ],
        ),
        child: Stack(
          fit: StackFit.expand,
          children: [
            // Camera feed background - subtle grid
            CustomPaint(
              painter: _CameraFeedPainter(),
            ),
            if (threat != null)
              _buildThreat(threat)
            else
              Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.videocam_off,
                      size: 40,
                      color: AppColors.textSecondary.withValues(alpha: 0.5),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Cam ${slotIndex + 1}',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary.withValues(alpha: 0.5),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildThreat(_Threat t) {
    final IconData icon = t.isThreat
        ? (t.iconType == 0 ? Icons.security : Icons.warning_amber_rounded)
        : Icons.person_outline;
    final color = t.isThreat ? AppColors.danger : Colors.blueGrey;
    final label = t.isThreat ? 'TAP!' : 'NO';

    return Container(
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.25),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color, width: 3),
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.4),
            blurRadius: 12,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 48, color: color),
            const SizedBox(height: 6),
            Text(
              label,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CameraFeedPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.borderSubtle.withValues(alpha: 0.15)
      ..strokeWidth = 1
      ..style = PaintingStyle.stroke;
    for (double x = 0; x < size.width; x += 16) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (double y = 0; y < size.height; y += 16) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
