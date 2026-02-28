import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter/services.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

/// Doodle Jump-style climbing minigame. Bounce off ledges to scale the building.
class DoodleClimbMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;

  const DoodleClimbMinigame({super.key, required this.difficulty});

  @override
  State<DoodleClimbMinigame> createState() => _DoodleClimbMinigameState();
}

class _Platform {
  final double x;
  final double y;
  final double width;
  final int type; // 0=ledge, 1=ac, 2=window, 3=breakable

  _Platform(this.x, this.y, this.width, this.type);

  bool get isBreakable => type == 3;
}

class _DoodleClimbMinigameState extends State<DoodleClimbMinigame>
    with SingleTickerProviderStateMixin {
  final FocusNode _focusNode = FocusNode();
  static const double _gameWidth = 300;
  static const double _gameHeight = 450;
  static const double _playerWidth = 28;
  static const double _playerHeight = 36;

  late Ticker _ticker;
  double _playerX = 0;
  double _playerY = 0;
  double _velocityX = 0;
  double _velocityY = 0;
  double _cameraY = 0;
  final List<_Platform> _platforms = [];
  final Set<_Platform> _platformsToRemove = {};
  double _highestPlatformY = 0;
  int _heightReached = 0;
  late int _targetHeight;
  late double _gravity;
  late double _jumpForce;
  late double _moveSpeed;
  late double _platformWidth;
  late double _platformSpacing;
  late Random _random;
  bool _gameWon = false;
  bool _gameOver = false;
  int _moveDir = 0; // -1 left, 0 none, 1 right
  double _lastTime = 0;

  @override
  void initState() {
    super.initState();
    _random = Random();
    // Slower physics, dense platforms especially near start
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _targetHeight = 2000;
        _gravity = 0.28;
        _jumpForce = 10.5 * 1.1;
        _moveSpeed = 5;
        _platformWidth = 85;
        _platformSpacing = 48;
        break;
      case MinigameDifficulty.medium:
        _targetHeight = 4000;
        _gravity = 0.32;
        _jumpForce = 9.8 * 1.1;
        _moveSpeed = 6;
        _platformWidth = 75;
        _platformSpacing = 52;
        break;
      case MinigameDifficulty.hard:
        _targetHeight = 6000;
        _gravity = 0.38;
        _jumpForce = 9.0 * 1.1;
        _moveSpeed = 7;
        _platformWidth = 60;
        _platformSpacing = 55;
        break;
    }
    _initGame();
    _ticker = createTicker(_onTick);
    _ticker.start();
    _lastTime = DateTime.now().millisecondsSinceEpoch / 1000.0;
  }

  void _initGame() {
    _playerX = _gameWidth / 2 - _playerWidth / 2;
    _velocityX = 0;
    _velocityY = 0;
    _platforms.clear();
    _highestPlatformY = 0;

    // Start platform centered vertically so player appears in middle of screen
    const startPlatY = 243.0;
    final startPlat = _Platform(
      _gameWidth / 2 - _platformWidth / 2,
      startPlatY,
      _platformWidth,
      0,
    );
    _platforms.add(startPlat);
    _highestPlatformY = startPlat.y;

    // Player standing on start platform (feet on platform top)
    _playerY = startPlatY - _playerHeight;

    // Camera so player is vertically centered
    _cameraY = _playerY + _playerHeight / 2 - _gameHeight / 2;

    _generatePlatformsWithDenseStart();
  }

  void _generatePlatformsWithDenseStart() {
    // Dense platforms near start (first 250 units) - tight spacing for easy jumps
    const denseSpacing = 42.0;
    const denseEndY = 50.0;  // Generate dense platforms from start down to y=50
    double y = _highestPlatformY - denseSpacing;
    while (y > denseEndY) {
      final maxX = _gameWidth - _platformWidth - 20;
      final x = 10.0 + _random.nextDouble() * maxX;
      final type = _random.nextDouble() < 0.15 ? 3 : _random.nextInt(3); // 15% breakable
      _platforms.add(_Platform(x, y, _platformWidth, type));
      _highestPlatformY = y;
      y -= denseSpacing;
    }
    _generatePlatformsUntil(-150);
  }

  void _generatePlatformsUntil(double targetY) {
    while (_highestPlatformY > targetY - _platformSpacing) {
      _highestPlatformY -= _platformSpacing;
      final maxX = _gameWidth - _platformWidth - 20;
      final x = 10.0 + _random.nextDouble() * maxX;
      final type = _random.nextDouble() < 0.15 ? 3 : _random.nextInt(3); // 15% breakable
      _platforms.add(_Platform(x, _highestPlatformY, _platformWidth, type));
    }
  }

  void _generateMorePlatformsIfNeeded() {
    // Dense spacing for lower altitude (closer to camera top)
    final useDense = _cameraY > -150;
    final spacing = useDense ? 45.0 : _platformSpacing;
    while (_highestPlatformY > _cameraY - 120) {
      _highestPlatformY -= spacing;
      final maxX = _gameWidth - _platformWidth - 20;
      final x = 10.0 + _random.nextDouble() * maxX;
      final type = _random.nextDouble() < 0.15 ? 3 : _random.nextInt(3); // 15% breakable
      _platforms.add(_Platform(x, _highestPlatformY, _platformWidth, type));
    }
  }

  void _onTick(Duration elapsed) {
    if (_gameWon || _gameOver || !mounted) return;

    final now = DateTime.now().millisecondsSinceEpoch / 1000.0;
    final dt = (now - _lastTime).clamp(0.01, 0.05);
    _lastTime = now;

    _velocityY += _gravity * 60 * dt;
    _velocityX = _moveDir * _moveSpeed;
    _playerX += _velocityX * 60 * dt;
    _playerY += _velocityY * 60 * dt;

    // Wrap horizontally
    if (_playerX < -_playerWidth / 2) _playerX = _gameWidth - _playerWidth / 2;
    if (_playerX > _gameWidth - _playerWidth / 2) _playerX = -_playerWidth / 2;

    // Check platform collisions only when FALLING (moving down)
    // Pass through platforms when jumping up
    if (_velocityY > 0) {
      final feetY = _playerY + _playerHeight;
      final left = _playerX + 4;
      final right = _playerX + _playerWidth - 4;

      for (final p in _platforms) {
        // Only bounce on platforms in the visible area
        if (p.y >= _cameraY + _gameHeight) continue;

        final platTop = p.y;
        final platBottom = p.y + 14;
        final platLeft = p.x;
        final platRight = p.x + p.width;

        if (feetY >= platTop &&
            feetY <= platBottom + 8 &&
            right > platLeft &&
            left < platRight) {
          if (p.isBreakable) {
            _platformsToRemove.add(p);
            // Don't bounce - fall through
          } else {
            _velocityY = -_jumpForce;
            _playerY = platTop - _playerHeight;
          }
          break;
        }
      }
    }

    // Update height and camera
    if (_playerY < _cameraY + _gameHeight * 0.6) {
      _cameraY = _playerY - _gameHeight * 0.6;
    }
    _heightReached = (-_cameraY).round().clamp(0, 9999);
    if (_heightReached >= _targetHeight) {
      _gameWon = true;
      _ticker.stop();
    }

    // Fail when character falls out of visible area (below bottom of screen)
    if (_playerY + _playerHeight > _cameraY + _gameHeight) {
      _gameOver = true;
      _ticker.stop();
    }

    _generateMorePlatformsIfNeeded();
    _platforms.removeWhere((p) => p.y > _cameraY + _gameHeight + 50);
    _platforms.removeWhere(_platformsToRemove.contains);
    _platformsToRemove.clear();

    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    _focusNode.dispose();
    _ticker.stop();
    _ticker.dispose();
    super.dispose();
  }

  void _resetGame() {
    setState(() {
      _gameWon = false;
      _gameOver = false;
    });
    _initGame();
    _lastTime = DateTime.now().millisecondsSinceEpoch / 1000.0;
    _ticker.start();
  }

  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('ROOFTOP!', Icons.roofing, _resetGame);
    }
    if (_gameOver) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.trending_down, size: 80, color: AppColors.danger),
            const SizedBox(height: 24),
            const Text(
              'FELL!',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: AppColors.danger,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Height: $_heightReached / $_targetHeight',
              style: const TextStyle(fontSize: 18, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 40),
            ElevatedButton.icon(
              onPressed: _resetGame,
              icon: const Icon(Icons.refresh),
              label: const Text('Try Again'),
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
          'Height: $_heightReached / $_targetHeight',
          'Reach the rooftop',
        ),
        const SizedBox(height: 12),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'Tap LEFT / RIGHT to move. Bounce off ledges!',
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 14,
              color: AppColors.textSecondary,
              height: 1.4,
            ),
          ),
        ),
        const SizedBox(height: 16),
        Expanded(
          child: Focus(
            focusNode: _focusNode,
            autofocus: true,
            onKeyEvent: (node, event) {
              if (event is KeyDownEvent) {
                if (event.logicalKey.keyLabel == 'Arrow Left') {
                  setState(() => _moveDir = -1);
                  return KeyEventResult.handled;
                }
                if (event.logicalKey.keyLabel == 'Arrow Right') {
                  setState(() => _moveDir = 1);
                  return KeyEventResult.handled;
                }
              } else if (event is KeyUpEvent) {
                if (event.logicalKey.keyLabel == 'Arrow Left' ||
                    event.logicalKey.keyLabel == 'Arrow Right') {
                  setState(() => _moveDir = 0);
                  return KeyEventResult.handled;
                }
              }
              return KeyEventResult.ignored;
            },
            child: Center(
            child: Container(
              width: _gameWidth,
              height: _gameHeight,
              decoration: BoxDecoration(
                color: AppColors.bgSecondary,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.borderSubtle, width: 2),
              ),
              clipBehavior: Clip.hardEdge,
              child: Stack(
                children: [
                  // Platforms
                  ..._platforms.map((p) {
                    final screenY = p.y - _cameraY;
                    if (screenY < -20 || screenY > _gameHeight + 20) {
                      return const SizedBox.shrink();
                    }
                    return Positioned(
                      left: p.x,
                      top: screenY,
                      child: _buildPlatform(p.type),
                    );
                  }),
                  // Player
                  Positioned(
                    left: _playerX,
                    top: _playerY - _cameraY,
                    child: Container(
                      width: _playerWidth,
                      height: _playerHeight,
                      decoration: BoxDecoration(
                        color: AppColors.accentPrimary,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: Colors.white, width: 2),
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.accentPrimary.withOpacity(0.5),
                            blurRadius: 8,
                            spreadRadius: 1,
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.person,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'or use arrow keys',
          style: TextStyle(fontSize: 12, color: AppColors.textSecondary.withOpacity(0.8)),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildMoveButton(Icons.arrow_back, -1),
            const SizedBox(width: 40),
            _buildMoveButton(Icons.arrow_forward, 1),
          ],
        ),
        const SizedBox(height: 24),
      ],
    );
  }

  Widget _buildPlatform(int type) {
    final color = type == 0
        ? Colors.brown.shade700
        : type == 1
            ? Colors.grey.shade600
            : type == 2
                ? Colors.blueGrey.shade700
                : Colors.orange.shade800; // breakable
    return Container(
      width: _platformWidth,
      height: 14,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(type == 1 ? 6 : 2),
        border: Border.all(
          color: type == 3 ? Colors.orange.shade300 : Colors.white24,
          width: type == 3 ? 1.5 : 1,
        ),
      ),
      child: type == 3
          ? CustomPaint(
              painter: _CrackPainter(),
              size: Size(_platformWidth, 14),
            )
          : null,
    );
  }

  Widget _buildMoveButton(IconData icon, int dir) {
    final isPressed = _moveDir == dir;
    return Listener(
      onPointerDown: (_) {
        if (mounted) setState(() => _moveDir = dir);
      },
      onPointerUp: (_) {
        if (mounted) setState(() => _moveDir = 0);
      },
      onPointerCancel: (_) {
        if (mounted) setState(() => _moveDir = 0);
      },
      child: Container(
        width: 80,
        height: 60,
        decoration: BoxDecoration(
          color: isPressed
              ? AppColors.accentPrimary.withOpacity(0.8)
              : AppColors.bgSecondary,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: AppColors.accentPrimary,
            width: 2,
          ),
        ),
        child: Icon(icon, color: Colors.white, size: 36),
      ),
    );
  }
}

class _CrackPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.brown.shade900.withOpacity(0.6)
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;
    // Crack lines to show it's fragile
    final path = Path();
    path.moveTo(size.width * 0.2, 2);
    path.lineTo(size.width * 0.35, size.height * 0.5);
    path.lineTo(size.width * 0.5, size.height - 2);
    path.moveTo(size.width * 0.6, 4);
    path.lineTo(size.width * 0.75, size.height * 0.4);
    path.moveTo(size.width * 0.85, size.height * 0.3);
    path.lineTo(size.width - 2, size.height * 0.8);
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
