import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

/// Tag all evidence markers at the crime scene before time runs out.
/// Watch out for decoys - wrong taps cost time!
class TagEvidenceMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;

  const TagEvidenceMinigame({super.key, required this.difficulty});

  @override
  State<TagEvidenceMinigame> createState() => _TagEvidenceMinigameState();
}

class _SceneItem {
  final double x;
  final double y;
  final int id;
  final bool isEvidence;
  final int evidenceNumber; // 1-based for display, 0 for decoys
  _SceneItem(this.x, this.y, this.id, this.isEvidence, this.evidenceNumber);
}

class _TagEvidenceMinigameState extends State<TagEvidenceMinigame> {
  static const double _sceneWidth = 320;
  static const double _sceneHeight = 400;
  static const double _itemSize = 48;

  final List<_SceneItem> _items = [];
  final Set<int> _taggedEvidence = {};
  int _nextExpected = 1; // Must tag in order 1, 2, 3...
  late int _totalEvidence;
  late int _timeLeft;
  late int _startTime;
  late int _decoyPenalty;
  Timer? _timer;
  bool _gameWon = false;
  bool _gameOver = false;
  bool _wrongOrder = false; // Failed due to wrong sequence
  String _feedback = '';
  late Random _random;

  @override
  void initState() {
    super.initState();
    _random = Random();
    _setupDifficulty();
  }

  void _setupDifficulty() {
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _totalEvidence = 6;
        _startTime = 12;
        _decoyPenalty = 2;
        break;
      case MinigameDifficulty.medium:
        _totalEvidence = 9;
        _startTime = 10;
        _decoyPenalty = 3;
        break;
      case MinigameDifficulty.hard:
        _totalEvidence = 12;
        _startTime = 11;
        _decoyPenalty = 4;
        break;
    }
    _timeLeft = _startTime;
    _nextExpected = 1;
    _generateScene();
    _startTimer();
  }

  void _generateScene() {
    _items.clear();
    _taggedEvidence.clear();
    final usedPositions = <String>{};

    int id = 0;
    for (int i = 0; i < _totalEvidence; i++) {
      final pos = _randomPosition(usedPositions);
      _items.add(_SceneItem(
        double.parse(pos.split(',')[0]),
        double.parse(pos.split(',')[1]),
        id++,
        true,
        i + 1,
      ));
    }

    final decoyCount = widget.difficulty == MinigameDifficulty.easy ? 2
        : widget.difficulty == MinigameDifficulty.medium ? 4 : 6;
    for (int i = 0; i < decoyCount; i++) {
      final pos = _randomPosition(usedPositions);
      _items.add(_SceneItem(
        double.parse(pos.split(',')[0]),
        double.parse(pos.split(',')[1]),
        id++,
        false,
        0,
      ));
    }
    _items.shuffle(_random);
  }

  String _randomPosition(Set<String> used) {
    const padding = 20.0;
    const grid = 18.0;
    for (int attempt = 0; attempt < 80; attempt++) {
      final x = padding + _random.nextDouble() * (_sceneWidth - padding * 2 - _itemSize);
      final y = padding + _random.nextDouble() * (_sceneHeight - padding * 2 - _itemSize);
      final gx = (x / grid).floor();
      final gy = (y / grid).floor();
      final key = '$gx,$gy';
      if (!used.contains(key)) {
        used.add(key);
        return '$x,$y';
      }
    }
    used.add('0,0');
    return '${padding},${padding}';
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

  void _onItemTap(_SceneItem item) {
    if (_gameWon || _gameOver) return;

    setState(() {
      if (item.isEvidence) {
        if (item.evidenceNumber != _nextExpected) {
          _wrongOrder = true;
          _gameOver = true;
          _timer?.cancel();
          _feedback = 'Wrong order!';
          return;
        }
        if (!_taggedEvidence.contains(item.id)) {
          _taggedEvidence.add(item.id);
          _nextExpected++;
          _feedback = 'TAGGED! ✓';
          if (_taggedEvidence.length >= _totalEvidence) {
            _gameWon = true;
            _timer?.cancel();
          }
        }
      } else {
        _timeLeft = (_timeLeft - _decoyPenalty).clamp(0, 999);
        _feedback = '-${_decoyPenalty}s!';
        if (_timeLeft <= 0) {
          _gameOver = true;
          _timer?.cancel();
        }
      }
      Future.delayed(const Duration(milliseconds: 400), () {
        if (mounted) setState(() => _feedback = '');
      });
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _resetGame() {
    setState(() {
      _gameWon = false;
      _gameOver = false;
      _wrongOrder = false;
      _feedback = '';
      _nextExpected = 1;
    });
    _setupDifficulty();
  }

  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('SCENE CLEAN!', Icons.verified_user, _resetGame);
    }
    if (_gameOver) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(_wrongOrder ? Icons.schedule : Icons.timer_off, size: 80, color: AppColors.danger),
            const SizedBox(height: 24),
            Text(
              _wrongOrder ? 'WRONG ORDER!' : 'TIME UP!',
              style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: AppColors.danger),
            ),
            Text(
              _wrongOrder ? 'Tag evidence 1→2→3 in sequence!' : 'Tagged ${_taggedEvidence.length} / $_totalEvidence',
              style: const TextStyle(fontSize: 18, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 40),
            ElevatedButton.icon(onPressed: _resetGame, icon: const Icon(Icons.refresh), label: const Text('Retry'), style: ElevatedButton.styleFrom(backgroundColor: AppColors.bgSecondary, foregroundColor: AppColors.textPrimary, padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16), textStyle: const TextStyle(fontSize: 18))),
          ],
        ),
      );
    }

    return Column(
      children: [
        buildStatsBar(
          'Tagged: ${_taggedEvidence.length} / $_totalEvidence',
          'Time: ${_timeLeft}s',
        ),
        const SizedBox(height: 12),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'Tag in order 1→2→3... Decoys cost $_decoyPenalty sec',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 14, color: AppColors.warning, height: 1.4),
          ),
        ),
        SizedBox(
          height: 32,
          child: Center(
            child: _feedback.isNotEmpty
                ? Text(
                    _feedback,
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: _feedback.contains('✓') ? AppColors.success : AppColors.danger),
                  )
                : const SizedBox.shrink(),
          ),
        ),
        const SizedBox(height: 16),
        Expanded(
          child: Center(
            child: Container(
              width: _sceneWidth,
              height: _sceneHeight,
              decoration: BoxDecoration(
                color: AppColors.bgSecondary,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.borderSubtle, width: 2),
                boxShadow: [BoxShadow(color: Colors.black54, blurRadius: 20, spreadRadius: 2)],
              ),
              child: Stack(
                children: [
                  Positioned.fill(
                    child: CustomPaint(
                      painter: _CrimeScenePainter(),
                    ),
                  ),
                  ..._items.map((item) {
                    if (item.isEvidence && _taggedEvidence.contains(item.id)) {
                      return Positioned(
                        left: item.x,
                        top: item.y,
                        child: Container(
                          width: _itemSize,
                          height: _itemSize,
                          decoration: BoxDecoration(
                            color: AppColors.success.withOpacity(0.3),
                            shape: BoxShape.circle,
                            border: Border.all(color: AppColors.success, width: 3),
                          ),
                          child: const Icon(Icons.check, color: AppColors.success, size: 28),
                        ),
                      );
                    }
                    return Positioned(
                      left: item.x,
                      top: item.y,
                      child: GestureDetector(
                        onTap: () => _onItemTap(item),
                        child: AnimatedScale(
                          scale: _feedback.isNotEmpty && _feedback.contains('✓') ? 1.0 : 1.0,
                          duration: const Duration(milliseconds: 100),
                          child: Container(
                            width: _itemSize,
                            height: _itemSize,
                            decoration: BoxDecoration(
                              color: AppColors.accentPrimary.withOpacity(0.9),
                              shape: BoxShape.circle,
                              border: Border.all(color: AppColors.accentLight, width: 2),
                              boxShadow: [
                                BoxShadow(
                                  color: AppColors.accentPrimary.withOpacity(0.5),
                                  blurRadius: 8,
                                  spreadRadius: 1,
                                ),
                              ],
                            ),
                            child: Center(
                              child: item.isEvidence
                                  ? Text(
                                      '${item.evidenceNumber}',
                                      style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
                                    )
                                  : const SizedBox.shrink(),
                            ),
                          ),
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 24),
      ],
    );
  }
}

class _CrimeScenePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.borderSubtle.withOpacity(0.3)
      ..strokeWidth = 1
      ..style = PaintingStyle.stroke;
    for (double x = 0; x < size.width; x += 40) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (double y = 0; y < size.height; y += 40) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
