import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

/// Swipe over fingerprints to wipe them clean.
class WipePrintsMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;

  const WipePrintsMinigame({super.key, required this.difficulty});

  @override
  State<WipePrintsMinigame> createState() => _WipePrintsMinigameState();
}

class _Fingerprint {
  final double x;
  final double y;
  final double radius;
  final int id;
  bool wiped;
  _Fingerprint(this.x, this.y, this.radius, this.id) : wiped = false;
}

class _DoNotClean {
  final double x;
  final double y;
  final double radius;
  final int id;
  _DoNotClean(this.x, this.y, this.radius, this.id);
}

class _WipePrintsMinigameState extends State<WipePrintsMinigame> {
  static const double _sceneWidth = 320;
  static const double _sceneHeight = 360;
  static const double _fingerprintRadius = 28;
  static const double _wipeTouchRadius = 40; // how close swipe must be to count

  final List<_Fingerprint> _prints = [];
  final List<_DoNotClean> _doNotClean = [];
  final List<Offset> _swipePath = [];
  late int _totalPrints;
  late int _decoyCount;
  late int _timeLeft;
  late int _startTime;
  Timer? _timer;
  bool _gameWon = false;
  bool _gameOver = false;
  late Random _random;
  final GlobalKey _sceneKey = GlobalKey();

  @override
  void initState() {
    super.initState();
    _random = Random();
    _setupDifficulty();
  }

  void _setupDifficulty() {
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _totalPrints = 5;
        _decoyCount = 2;
        _startTime = 6;
        break;
      case MinigameDifficulty.medium:
        _totalPrints = 8;
        _decoyCount = 4;
        _startTime = 5;
        break;
      case MinigameDifficulty.hard:
        _totalPrints = 12;
        _decoyCount = 6;
        _startTime = 4;
        break;
    }
    _timeLeft = _startTime;
    _generatePrints();
    _startTimer();
  }

  static const double _minSpacing = 72; // minimum distance between item centers

  bool _tooCloseToAny(double x, double y, List<({double x, double y})> existing) {
    final cx = x + _fingerprintRadius;
    final cy = y + _fingerprintRadius;
    for (final e in existing) {
      final ex = e.x + _fingerprintRadius;
      final ey = e.y + _fingerprintRadius;
      final dx = cx - ex;
      final dy = cy - ey;
      if (dx * dx + dy * dy < _minSpacing * _minSpacing) return true;
    }
    return false;
  }

  void _generatePrints() {
    _prints.clear();
    _doNotClean.clear();
    const padding = 25.0;
    final existing = <({double x, double y})>[];

    for (int i = 0; i < _totalPrints; i++) {
      for (int attempt = 0; attempt < 80; attempt++) {
        final x = padding +
            _random.nextDouble() * (_sceneWidth - padding * 2 - _fingerprintRadius * 2);
        final y = padding +
            _random.nextDouble() * (_sceneHeight - padding * 2 - _fingerprintRadius * 2);
        if (!_tooCloseToAny(x, y, existing)) {
          existing.add((x: x, y: y));
          _prints.add(_Fingerprint(x, y, _fingerprintRadius, i));
          break;
        }
      }
    }
    for (int i = 0; i < _decoyCount; i++) {
      for (int attempt = 0; attempt < 80; attempt++) {
        final x = padding +
            _random.nextDouble() * (_sceneWidth - padding * 2 - _fingerprintRadius * 2);
        final y = padding +
            _random.nextDouble() * (_sceneHeight - padding * 2 - _fingerprintRadius * 2);
        if (!_tooCloseToAny(x, y, existing)) {
          existing.add((x: x, y: y));
          _doNotClean.add(_DoNotClean(x, y, _fingerprintRadius, i + 1000));
          break;
        }
      }
    }
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
        }
      });
    });
  }

  void _onPanStart(DragStartDetails details) {
    if (_gameWon || _gameOver) return;
    final box = _sceneKey.currentContext?.findRenderObject() as RenderBox?;
    if (box == null || !box.hasSize) return;
    final local = box.globalToLocal(details.globalPosition);
    _swipePath.clear();
    _swipePath.add(local);
    _checkPathAgainstPrints();
  }

  void _onPanUpdate(DragUpdateDetails details) {
    if (_gameWon || _gameOver) return;
    final box = _sceneKey.currentContext?.findRenderObject() as RenderBox?;
    if (box == null || !box.hasSize) return;
    final local = box.globalToLocal(details.globalPosition);
    _swipePath.add(local);
    _checkPathAgainstPrints();
  }

  void _onPanEnd(DragEndDetails _) {
    _swipePath.clear();
  }

  void _checkPathAgainstPrints() {
    // Check decoys first—touching one = instant fail
    for (final d in _doNotClean) {
      for (final pt in _swipePath) {
        final dx = pt.dx - (d.x + d.radius);
        final dy = pt.dy - (d.y + d.radius);
        if (dx * dx + dy * dy <= _wipeTouchRadius * _wipeTouchRadius) {
          _gameOver = true;
          _timer?.cancel();
          setState(() {});
          return;
        }
      }
    }
    for (final p in _prints) {
      if (p.wiped) continue;
      for (final pt in _swipePath) {
        final dx = pt.dx - (p.x + p.radius);
        final dy = pt.dy - (p.y + p.radius);
        if (dx * dx + dy * dy <= _wipeTouchRadius * _wipeTouchRadius) {
          p.wiped = true;
          if (_prints.every((fp) => fp.wiped)) {
            _gameWon = true;
            _timer?.cancel();
          }
          break;
        }
      }
    }
    setState(() {});
  }

  void _resetGame() {
    setState(() {
      _gameWon = false;
      _gameOver = false;
      _timeLeft = _startTime;
    });
    _generatePrints();
    _startTimer();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('CLEAN!', Icons.cleaning_services, _resetGame);
    }
    if (_gameOver) {
      return buildFailScreen(_resetGame);
    }

    final wipedCount = _prints.where((p) => p.wiped).length;

    return GestureDetector(
      onPanStart: _onPanStart,
      onPanUpdate: _onPanUpdate,
      onPanEnd: _onPanEnd,
      child: Column(
        children: [
          buildStatsBar(
            'Prints: $wipedCount / $_totalPrints',
            'Time: ${_timeLeft}s',
          ),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Text(
              'Wipe fingerprints only—don\'t touch the ⛔ items',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                color: AppColors.textSecondary,
              ),
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: Center(
              child: Container(
                key: _sceneKey,
                width: _sceneWidth,
                height: _sceneHeight,
                decoration: BoxDecoration(
                  color: AppColors.bgSecondary,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.borderSubtle),
                ),
                child: Stack(
                  clipBehavior: Clip.none,
                  children: [
                    // Surface texture hint
                    Positioned.fill(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(10),
                        child: CustomPaint(
                          painter: _SurfacePainter(),
                        ),
                      ),
                    ),
                    ..._doNotClean.map((d) => _buildDoNotClean(d)),
                    ..._prints.map((fp) => _buildFingerprint(fp)),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFingerprint(_Fingerprint fp) {
    if (fp.wiped) return const SizedBox.shrink();
    return Positioned(
      left: fp.x,
      top: fp.y,
      width: fp.radius * 2,
      height: fp.radius * 2,
      child: Icon(
        Icons.fingerprint,
        size: fp.radius * 2,
        color: AppColors.textSecondary.withValues(alpha: 0.6),
      ),
    );
  }

  Widget _buildDoNotClean(_DoNotClean d) {
    return Positioned(
      left: d.x,
      top: d.y,
      width: d.radius * 2,
      height: d.radius * 2,
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.danger.withValues(alpha: 0.15),
          shape: BoxShape.circle,
          border: Border.all(color: AppColors.danger.withValues(alpha: 0.6), width: 2),
        ),
        child: Icon(
          Icons.do_not_disturb,
          size: d.radius * 1.4,
          color: AppColors.danger,
        ),
      ),
    );
  }
}

class _SurfacePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.bgSecondary
      ..style = PaintingStyle.fill;
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
