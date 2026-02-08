import 'dart:math';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

class SimonSaysMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;
  
  const SimonSaysMinigame({super.key, required this.difficulty});

  @override
  State<SimonSaysMinigame> createState() => _SimonSaysMinigameState();
}

class _SimonSaysMinigameState extends State<SimonSaysMinigame> {
  final List<int> _sequence = [];
  final List<int> _playerInput = [];
  int _currentIndex = 0;
  bool _showingSequence = false;
  bool _gameFailed = false;
  bool _gameWon = false;
  int _flashingButton = -1;
  int _tappedButton = -1;
  int _round = 1;
  late int _targetRounds;
  late int _flashDuration;
  late int _pauseDuration;
  
  final List<Color> _buttonColors = [
    Colors.red,
    Colors.blue,
    Colors.green,
    Colors.yellow,
  ];
  
  @override
  void initState() {
    super.initState();
    // Difficulty: number of rounds and speed
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _targetRounds = 4;
        _flashDuration = 700;
        _pauseDuration = 300;
        break;
      case MinigameDifficulty.medium:
        _targetRounds = 5;
        _flashDuration = 600;
        _pauseDuration = 200;
        break;
      case MinigameDifficulty.hard:
        _targetRounds = 7;
        _flashDuration = 400;
        _pauseDuration = 150;
        break;
    }
    _startNewRound();
  }
  
  void _startNewRound() {
    setState(() {
      final random = Random();
      _sequence.add(random.nextInt(4));
      _playerInput.clear();
      _currentIndex = 0;
      _gameFailed = false;
    });
    _showSequence();
  }
  
  Future<void> _showSequence() async {
    if (!mounted) return;
    setState(() {
      _showingSequence = true;
    });
    
    await Future.delayed(const Duration(milliseconds: 500));
    if (!mounted) return;
    
    for (int i = 0; i < _sequence.length; i++) {
      if (!mounted) return;
      setState(() {
        _flashingButton = _sequence[i];
      });
      await Future.delayed(Duration(milliseconds: _flashDuration));
      if (!mounted) return;
      setState(() {
        _flashingButton = -1;
      });
      await Future.delayed(Duration(milliseconds: _pauseDuration));
      if (!mounted) return;
    }
    
    if (!mounted) return;
    setState(() {
      _showingSequence = false;
    });
  }
  
  void _onButtonPressed(int index) {
    if (_showingSequence || _gameFailed || _gameWon) return;
    
    setState(() {
      _tappedButton = index;
      _playerInput.add(index);
      
      if (_playerInput[_currentIndex] != _sequence[_currentIndex]) {
        _gameFailed = true;
      } else {
        _currentIndex++;
        if (_currentIndex == _sequence.length) {
          if (_round >= _targetRounds) {
            _gameWon = true;
          } else {
            _round++;
            Future.delayed(const Duration(milliseconds: 500), _startNewRound);
          }
        }
      }
    });
    
    Future.delayed(const Duration(milliseconds: 200), () {
      if (mounted) {
        setState(() {
          _tappedButton = -1;
        });
      }
    });
  }
  
  void _resetGame() {
    setState(() {
      _sequence.clear();
      _playerInput.clear();
      _currentIndex = 0;
      _showingSequence = false;
      _gameFailed = false;
      _gameWon = false;
      _flashingButton = -1;
      _round = 1;
    });
    _startNewRound();
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('HACKED!', Icons.check_circle, _resetGame);
    }
    
    if (_gameFailed) {
      return buildFailScreen(_resetGame);
    }
    
    return Column(
      children: [
        buildStatsBar(
          'Round: $_round / $_targetRounds',
          'Sequence: ${_sequence.length}',
        ),
        const SizedBox(height: 20),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            _showingSequence ? 'Watch the sequence...' : 'Repeat the pattern!',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 18, color: AppColors.textSecondary, fontWeight: FontWeight.bold),
          ),
        ),
        const SizedBox(height: 40),
        Expanded(
          child: Center(
            child: Wrap(
              spacing: 20,
              runSpacing: 20,
              alignment: WrapAlignment.center,
              children: List.generate(4, (index) {
                final isFlashing = _flashingButton == index;
                final isTapped = _tappedButton == index;
                final isHighlighted = isFlashing || isTapped;
                
                return GestureDetector(
                  onTap: () => _onButtonPressed(index),
                  child: AnimatedScale(
                    scale: isTapped ? 0.95 : 1.0,
                    duration: const Duration(milliseconds: 100),
                    child: Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        color: isHighlighted 
                            ? _buttonColors[index] 
                            : _buttonColors[index].withOpacity(0.3),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: _buttonColors[index],
                          width: isTapped ? 5 : 3,
                        ),
                        boxShadow: isHighlighted ? [
                          BoxShadow(
                            color: _buttonColors[index].withOpacity(0.6),
                            blurRadius: 20,
                            spreadRadius: 5,
                          ),
                        ] : [],
                      ),
                    ),
                  ),
                );
              }),
            ),
          ),
        ),
      ],
    );
  }
}
