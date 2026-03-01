import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter/services.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

/// Crossy Road–style driving: dodge obstacles by switching lanes.
class SteeringObstacleMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;

  const SteeringObstacleMinigame({super.key, required this.difficulty});

  @override
  State<SteeringObstacleMinigame> createState() => _SteeringObstacleMinigameState();
}

class _Obstacle {
  final double x;
  final double y;
  final int type; // 0=car, 1=barrier, 2=cone
  _Obstacle(this.x, this.y, this.type);
}

class _SteeringObstacleMinigameState extends State<SteeringObstacleMinigame>
    with SingleTickerProviderStateMixin {
  static const double _gameWidth = 300;
  static const double _gameHeight = 420;
  static const double _carWidth = 40;
  static const double _carHeight = 24;
  static const double _obstacleWidth = 42;
  static const double _obstacleHeight = 26;
  static const double _graceDistance = 120; // No obstacles for first ~1 sec

  final FocusNode _focusNode = FocusNode();
  late Ticker _ticker;
  double _playerX = 0; // Free movement 0 to _gameWidth - _carWidth
  late double _baseScrollSpeed;
  late double _speedRampPer400; // extra speed per 400 distance
  late double _spawnInterval;
  late int _targetDistance;
  double _distance = 0;
  final List<_Obstacle> _obstacles = [];
  double _nextSpawnDistance = 0;
  double _health = 100;
  late double _maxHealth;
  late Random _random;
  bool _gameWon = false;
  bool _gameOver = false;

  static double _damageForType(int type) {
    switch (type) {
      case 0: return 40; // car - most damage
      case 1: return 25; // barrier
      case 2: return 15; // cone - least
      default: return 20;
    }
  }
  double _lastTime = 0;

  @override
  void initState() {
    super.initState();
    _random = Random();
    _playerX = _gameWidth / 2 - _carWidth / 2; // center

    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _baseScrollSpeed = 165;
        _speedRampPer400 = 12;
        _spawnInterval = 150;
        _targetDistance = 4000;
        _maxHealth = 100;
        break;
      case MinigameDifficulty.medium:
        _baseScrollSpeed = 210;
        _speedRampPer400 = 15;
        _spawnInterval = 120;
        _targetDistance = 6000;
        _maxHealth = 100;
        break;
      case MinigameDifficulty.hard:
        _baseScrollSpeed = 260;
        _speedRampPer400 = 18;
        _spawnInterval = 95;
        _targetDistance = 8000;
        _maxHealth = 100;
        break;
    }

    _initObstacles();
    _ticker = createTicker(_onTick);
    _ticker.start();
    _lastTime = DateTime.now().millisecondsSinceEpoch / 1000.0;
  }

  void _initObstacles() {
    _obstacles.clear();
    _distance = 0;
    _nextSpawnDistance = _graceDistance;
    _health = _maxHealth;
  }

  void _onTick(Duration elapsed) {
    if (_gameWon || _gameOver || !mounted) return;

    final now = DateTime.now().millisecondsSinceEpoch / 1000.0;
    final dt = (now - _lastTime).clamp(0.01, 0.05);
    _lastTime = now;

    // Speed increases with distance (car goes faster as you go)
    final scrollSpeed = _baseScrollSpeed + (_distance / 400) * _speedRampPer400;
    final move = scrollSpeed * dt;
    _distance += move;

    for (int i = _obstacles.length - 1; i >= 0; i--) {
      final o = _obstacles[i];
      final newY = o.y + move;

      // Remove past bottom
      if (newY > _gameHeight + 50) {
        _obstacles.removeAt(i);
        continue;
      }
      _obstacles[i] = _Obstacle(o.x, newY, o.type);

      // Collision: only when rectangles actually overlap (touch-based)
      final playerLeft = _playerX + 4;
      final playerRight = _playerX + _carWidth - 4;
      final playerTop = _gameHeight - 40 - _carHeight;
      final playerBottom = _gameHeight - 40;
      final obsLeft = o.x + 4;
      final obsRight = o.x + _obstacleWidth - 4;
      final obsTop = newY;
      final obsBottom = newY + _obstacleHeight;

      if (playerRight > obsLeft && playerLeft < obsRight &&
          playerBottom > obsTop && playerTop < obsBottom) {
        _health = (_health - _damageForType(o.type)).clamp(0.0, _maxHealth);
        _obstacles.removeAt(i);
        if (_health <= 0) {
          _gameOver = true;
          _ticker.stop();
        }
        if (mounted) setState(() {});
        return;
      }
    }

    // Spawn obstacles from the top (only after grace period) - one at a time, always off-screen above
    if (_distance >= _nextSpawnDistance && _distance > _graceDistance) {
      final spawnY = -_obstacleHeight - 20; // well above the visible area
      final x = 20.0 + _random.nextDouble() * (_gameWidth - _obstacleWidth - 40);
      final type = _random.nextInt(3);
      _obstacles.add(_Obstacle(x, spawnY, type));
      _nextSpawnDistance = _distance + _spawnInterval + _random.nextDouble() * 60;
    }

    if (_distance >= _targetDistance) {
      _gameWon = true;
      _ticker.stop();
    }

    if (mounted) setState(() {});
  }

  void _setPlayerX(double x) {
    if (_gameOver || _gameWon) return;
    _playerX = x.clamp(0.0, _gameWidth - _carWidth);
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
      _health = _maxHealth;
      _playerX = _gameWidth / 2 - _carWidth / 2;
    });
    _initObstacles();
    _lastTime = DateTime.now().millisecondsSinceEpoch / 1000.0;
    _ticker.start();
  }

  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('CLEAR!', Icons.directions_car, _resetGame);
    }
    if (_gameOver) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.car_crash, size: 80, color: AppColors.danger),
            const SizedBox(height: 24),
            const Text(
              'CRASHED!',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: AppColors.danger,
              ),
            ),
            Text(
              '${_distance.round()} / $_targetDistance',
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

    return Focus(
      focusNode: _focusNode,
      autofocus: true,
      onKeyEvent: (node, event) {
        if (event is! KeyDownEvent) return KeyEventResult.ignored;
        const step = 20.0;
        if (event.logicalKey == LogicalKeyboardKey.arrowLeft) {
          _setPlayerX(_playerX - step);
          return KeyEventResult.handled;
        }
        if (event.logicalKey == LogicalKeyboardKey.arrowRight) {
          _setPlayerX(_playerX + step);
          return KeyEventResult.handled;
        }
        return KeyEventResult.ignored;
      },
      child: Listener(
        onPointerDown: (_) => _focusNode.requestFocus(),
        child: Column(
          children: [
            buildStatsBar(
              'Distance: ${_distance.round()} / $_targetDistance',
              'HP: ${_health.round()}',
            ),
            const SizedBox(height: 4),
            _buildHealthBar(),
            const SizedBox(height: 12),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 20),
              child: Text(
                'Drag or use arrows to move',
                style: TextStyle(fontSize: 14, color: AppColors.textSecondary),
              ),
            ),
            const SizedBox(height: 12),
            Center(child: _buildGameArea()),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthBar() {
    final pct = (_health / _maxHealth).clamp(0.0, 1.0);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.favorite, size: 16, color: AppColors.danger),
              const SizedBox(width: 6),
              Text(
                'Health',
                style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
              ),
            ],
          ),
          const SizedBox(height: 4),
          LayoutBuilder(
            builder: (context, constraints) {
              return Container(
                height: 10,
                decoration: BoxDecoration(
                  color: AppColors.bgTertiary,
                  borderRadius: BorderRadius.circular(5),
                ),
                clipBehavior: Clip.hardEdge,
                child: Row(
                  children: [
                    Container(
                      width: constraints.maxWidth * pct,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: pct > 0.5
                              ? [AppColors.success, AppColors.success.withValues(alpha: 0.8)]
                              : [AppColors.warning, pct > 0.25 ? AppColors.warning.withValues(alpha: 0.8) : AppColors.danger],
                          begin: Alignment.centerLeft,
                          end: Alignment.centerRight,
                        ),
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildGameArea() {
    return Listener(
      behavior: HitTestBehavior.opaque,
      onPointerMove: (e) => _setPlayerX(e.localPosition.dx - _carWidth / 2),
      onPointerDown: (e) => _setPlayerX(e.localPosition.dx - _carWidth / 2),
      child: Container(
        width: _gameWidth,
        height: _gameHeight,
        decoration: BoxDecoration(
          color: AppColors.bgSecondary,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.borderSubtle, width: 2),
          boxShadow: [
            BoxShadow(
              color: AppColors.borderSubtle.withValues(alpha: 0.3),
              blurRadius: 12,
              spreadRadius: 1,
            ),
          ],
        ),
        clipBehavior: Clip.hardEdge,
        child: Stack(
          children: [
            // Subtle road
            CustomPaint(
              size: Size(_gameWidth, _gameHeight),
              painter: _RoadPainter(),
            ),
            // Obstacles
            for (final o in _obstacles)
              if (o.y > -60 && o.y < _gameHeight + 60)
                Positioned(
                  left: o.x,
                  top: o.y,
                  child: _buildObstacle(o),
                ),
            // Player car
            Positioned(
              left: _playerX,
              bottom: 40,
              child: Container(
                width: _carWidth,
                height: _carHeight,
                decoration: BoxDecoration(
                  color: AppColors.accentPrimary,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppColors.accentLight, width: 1.5),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.accentPrimary.withValues(alpha: 0.4),
                      blurRadius: 12,
                      spreadRadius: 0,
                    ),
                  ],
                ),
                child: const Icon(Icons.directions_car, color: Colors.white, size: 22),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildObstacle(_Obstacle o) {
    Color color;
    IconData icon;
    switch (o.type) {
      case 0:
        color = Colors.red.shade700;
        icon = Icons.directions_car;
        break;
      case 1:
        color = Colors.grey.shade600;
        icon = Icons.warning_amber_rounded;
        break;
      case 2:
        color = Colors.orange.shade700;
        icon = Icons.warning_rounded;
        break;
      default:
        color = Colors.grey;
        icon = Icons.warning;
    }
    return Container(
      width: _obstacleWidth,
      height: _obstacleHeight,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.white24, width: 1),
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.4),
            blurRadius: 6,
            spreadRadius: 0,
          ),
        ],
      ),
      child: Icon(icon, color: Colors.white, size: 20),
    );
  }
}

class _RoadPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // Subtle center dashed line
    final paint = Paint()
      ..color = AppColors.borderSubtle.withValues(alpha: 0.25)
      ..strokeWidth = 1
      ..style = PaintingStyle.stroke;

    for (double y = 0; y < size.height; y += 24) {
      canvas.drawLine(
        Offset(size.width / 2, y),
        Offset(size.width / 2, (y + 12).clamp(0, size.height)),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
