import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

class CardSwipeMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;
  
  const CardSwipeMinigame({super.key, required this.difficulty});

  @override
  State<CardSwipeMinigame> createState() => _CardSwipeMinigameState();
}

class _CardSwipeMinigameState extends State<CardSwipeMinigame> with TickerProviderStateMixin {
  late AnimationController _speedIndicator;
  late AnimationController _cardAnimation;
  double _swipeSpeed = 0.0;
  int _attempts = 0;
  int _successes = 0;
  bool _gameWon = false;
  String _feedback = '';
  double _cardOffset = -150.0;
  bool _isSwiping = false;
  late double _minSpeed;
  late double _maxSpeed;
  late int _targetSuccesses;
  
  @override
  void initState() {
    super.initState();
    // Difficulty: speed range and successes needed
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _minSpeed = 150;
        _maxSpeed = 700;
        _targetSuccesses = 2;
        break;
      case MinigameDifficulty.medium:
        _minSpeed = 200;
        _maxSpeed = 600;
        _targetSuccesses = 3;
        break;
      case MinigameDifficulty.hard:
        _minSpeed = 300;
        _maxSpeed = 500;
        _targetSuccesses = 5;
        break;
    }
    
    _speedIndicator = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);
    
    _cardAnimation = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
  }
  
  @override
  void dispose() {
    _speedIndicator.dispose();
    _cardAnimation.dispose();
    super.dispose();
  }
  
  void _onSwipeStart(DragStartDetails details) {
    setState(() {
      _isSwiping = true;
      _cardOffset = -150.0;
    });
  }
  
  void _onSwipeUpdate(DragUpdateDetails details) {
    setState(() {
      if (details.delta.dx > 0) {
        _cardOffset += details.delta.dx;
        _cardOffset = _cardOffset.clamp(-150.0, 150.0);
      }
    });
  }
  
  void _onSwipeEnd(DragEndDetails details) {
    final velocityX = details.velocity.pixelsPerSecond.dx;
    
    if (velocityX < 0) {
      setState(() {
        _isSwiping = false;
        _feedback = 'SWIPE RIGHT! →';
        _cardOffset = -150.0;
      });
      
      Future.delayed(const Duration(milliseconds: 1000), () {
        if (mounted) {
          setState(() {
            _feedback = '';
          });
        }
      });
      return;
    }
    
    final velocity = velocityX.abs();
    setState(() {
      _isSwiping = false;
      _attempts++;
      _swipeSpeed = velocity;
      
      if (velocity >= _minSpeed && velocity <= _maxSpeed) {
        _successes++;
        _feedback = 'PERFECT SWIPE! ✓';
        if (_successes >= _targetSuccesses) {
          _gameWon = true;
          _speedIndicator.stop();
        }
      } else if (velocity < _minSpeed) {
        _feedback = 'TOO SLOW ✗';
      } else {
        _feedback = 'TOO FAST ✗';
      }
      
      _cardAnimation.forward(from: 0.0).then((_) {
        setState(() {
          _cardOffset = -150.0;
        });
      });
      
      Future.delayed(const Duration(milliseconds: 1000), () {
        if (mounted) {
          setState(() {
            _feedback = '';
            _swipeSpeed = 0.0;
          });
        }
      });
    });
  }
  
  void _resetGame() {
    setState(() {
      _attempts = 0;
      _successes = 0;
      _gameWon = false;
      _feedback = '';
      _swipeSpeed = 0.0;
      _cardOffset = -150.0;
    });
    _speedIndicator.repeat(reverse: true);
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('ACCESS GRANTED!', Icons.check_circle, _resetGame);
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
                'Swipe the card RIGHT at the right speed!\nNot too fast, not too slow.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: AppColors.textSecondary, height: 1.5),
              ),
              const SizedBox(height: 12),
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
        // Speed meter
        AnimatedBuilder(
          animation: _speedIndicator,
          builder: (context, child) {
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 40),
              child: Column(
                children: [
                  const Text(
                    'Target Speed Zone',
                    style: TextStyle(color: AppColors.success, fontSize: 14),
                  ),
                  const SizedBox(height: 8),
                  Stack(
                    children: [
                      Container(
                        height: 40,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [
                              Colors.red,
                              Colors.orange,
                              Colors.green,
                              Colors.orange,
                              Colors.red,
                            ],
                            stops: [0.0, 0.25, 0.5, 0.75, 1.0],
                          ),
                          borderRadius: BorderRadius.circular(20),
                        ),
                      ),
                      if (_swipeSpeed > 0)
                        Positioned(
                          left: (_swipeSpeed / 1000 * MediaQuery.of(context).size.width * 0.8).clamp(0, MediaQuery.of(context).size.width * 0.8),
                          child: Container(
                            width: 4,
                            height: 40,
                            color: Colors.white,
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: 40),
        // Card reader terminal
        Expanded(
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: 320,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.black,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.grey.shade700, width: 2),
                  ),
                  child: Column(
                    children: [
                      Text(
                        _isSwiping ? 'READING...' : 'READY',
                        style: TextStyle(
                          color: _isSwiping ? Colors.yellow : AppColors.success,
                          fontSize: 16,
                          fontFamily: 'monospace',
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        height: 160,
                        width: double.infinity,
                        decoration: BoxDecoration(
                          color: Colors.grey.shade900,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Stack(
                          alignment: Alignment.center,
                          children: [
                            Positioned(
                              top: 75,
                              left: 0,
                              right: 0,
                              child: Container(
                                height: 10,
                                decoration: BoxDecoration(
                                  border: Border(
                                    top: BorderSide(color: Colors.grey.shade600, width: 2),
                                    bottom: BorderSide(color: Colors.grey.shade600, width: 2),
                                  ),
                                ),
                              ),
                            ),
                            AnimatedBuilder(
                              animation: _cardAnimation,
                              builder: (context, child) {
                                final animOffset = _cardAnimation.isAnimating 
                                    ? _cardOffset * (1 - _cardAnimation.value)
                                    : _cardOffset;
                                return Transform.translate(
                                  offset: Offset(animOffset, 0),
                                  child: GestureDetector(
                                    onHorizontalDragStart: _onSwipeStart,
                                    onHorizontalDragUpdate: _onSwipeUpdate,
                                    onHorizontalDragEnd: _onSwipeEnd,
                                    child: Container(
                                      width: 200,
                                      height: 120,
                                      decoration: BoxDecoration(
                                        gradient: LinearGradient(
                                          colors: [
                                            Colors.cyan.shade700,
                                            Colors.blue.shade900,
                                          ],
                                        ),
                                        borderRadius: BorderRadius.circular(8),
                                        border: Border.all(color: Colors.cyan, width: 2),
                                        boxShadow: [
                                          BoxShadow(
                                            color: Colors.cyan.withOpacity(0.5),
                                            blurRadius: _isSwiping ? 20 : 10,
                                            spreadRadius: _isSwiping ? 3 : 0,
                                          ),
                                        ],
                                      ),
                                      child: const Column(
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        children: [
                                          Icon(Icons.credit_card, size: 40, color: Colors.white),
                                          SizedBox(height: 8),
                                          Text(
                                            'ACCESS CARD',
                                            style: TextStyle(
                                              color: Colors.white70,
                                              fontSize: 12,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                );
                              },
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.arrow_forward, color: AppColors.accentPrimary, size: 20),
                    SizedBox(width: 8),
                    Text(
                      'Swipe card RIGHT through reader',
                      style: TextStyle(
                        color: AppColors.textSecondary,
                        fontSize: 14,
                      ),
                    ),
                    SizedBox(width: 8),
                    Icon(Icons.arrow_forward, color: AppColors.accentPrimary, size: 20),
                  ],
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
