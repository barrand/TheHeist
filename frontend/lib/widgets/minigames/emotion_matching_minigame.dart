import 'dart:math';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

/// Tap the facial expression that matches the situation. Read the room!
class EmotionMatchingMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;

  const EmotionMatchingMinigame({super.key, required this.difficulty});

  @override
  State<EmotionMatchingMinigame> createState() => _EmotionMatchingMinigameState();
}

class _Situation {
  final String text;
  final int correctIndex; // index into emotion list
  _Situation(this.text, this.correctIndex);
}

class _EmotionMatchingMinigameState extends State<EmotionMatchingMinigame> {
  static const List<String> _emotions = ['😊', '😠', '😟', '😎', '🤔', '😬', '🙄', '😇'];

  late int _targetRounds;
  late int _maxStrikes;
  late int _optionsCount;
  int _round = 0;
  int _strikes = 0;
  late List<_Situation> _situations;
  late _Situation _current;
  late List<String> _choices;
  late Random _random;
  bool _gameWon = false;
  bool _gameOver = false;

  static final List<_Situation> _allSituations = [
    _Situation('The guard looks suspicious of you.', 3),  // confident
    _Situation('They seem flattered by a compliment.', 0), // happy
    _Situation('The host is clearly bored.', 4),  // thoughtful
    _Situation('They\'re about to call security.', 2),  // worried/apologetic
    _Situation('They want to be impressed.', 3),  // confident
    _Situation('Someone just insulted them.', 6),  // eye roll / dismiss
    _Situation('They\'re looking for an excuse to help.', 7),  // friendly
    _Situation('The bribe offer made them angry.', 1),  // angry
    _Situation('They need to trust you quickly.', 0),  // warm/happy
    _Situation('They\'re sizing you up.', 3),  // confident
    _Situation('Your story has a hole in it.', 2),  // worried
    _Situation('They love attention.', 0),  // happy
    _Situation('They\'re tired and want to go home.', 5),  // sympathetic
    _Situation('They caught you in a lie.', 2),  // worried/guilty
    _Situation('They think they\'re smarter than you.', 6),  // play along
  ];

  @override
  void initState() {
    super.initState();
    _random = Random();
    switch (widget.difficulty) {
      case MinigameDifficulty.easy:
        _targetRounds = 4;
        _maxStrikes = 4;
        _optionsCount = 3;
        break;
      case MinigameDifficulty.medium:
        _targetRounds = 6;
        _maxStrikes = 3;
        _optionsCount = 4;
        break;
      case MinigameDifficulty.hard:
        _targetRounds = 8;
        _maxStrikes = 2;
        _optionsCount = 5;
        break;
    }
    _resetGame();
  }

  void _resetGame() {
    setState(() {
      _gameWon = false;
      _gameOver = false;
      _round = 0;
      _strikes = 0;
      _situations = List.from(_allSituations)..shuffle(_random);
      _nextRound();
    });
  }

  void _nextRound() {
    if (_round >= _targetRounds) {
      _gameWon = true;
      return;
    }
    _current = _situations[_round];
    final correct = _emotions[_current.correctIndex];
    final wrongPool = _emotions.where((e) => e != correct).toList();
    wrongPool.shuffle(_random);
    _choices = [correct, ...wrongPool.take(_optionsCount - 1)];
    _choices.shuffle(_random);
  }

  void _onTap(int index) {
    if (_gameWon || _gameOver) return;

    final picked = _choices[index];
    final correct = _emotions[_current.correctIndex];

    setState(() {
      if (picked == correct) {
        _round++;
        if (_round >= _targetRounds) {
          _gameWon = true;
        } else {
          _nextRound();
        }
      } else {
        _strikes++;
        if (_strikes > _maxStrikes) {
          _gameOver = true;
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('CONVINCED!', Icons.face, _resetGame);
    }
    if (_gameOver) {
      return buildFailScreen(_resetGame);
    }

    return Column(
      children: [
        buildStatsBar(
          'Round ${_round + 1} / $_targetRounds',
          _maxStrikes > 0 ? 'Strikes: $_strikes / $_maxStrikes' : 'No mistakes!',
        ),
        const SizedBox(height: 24),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.bgSecondary,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.borderSubtle, width: 2),
            ),
            child: Column(
              children: [
                const Text(
                  'Read the room:',
                  style: TextStyle(
                    fontSize: 14,
                    color: AppColors.textSecondary,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  _current.text,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 20,
                    color: AppColors.textPrimary,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 32),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'Tap the expression that fits',
            style: TextStyle(fontSize: 14, color: AppColors.textSecondary),
          ),
        ),
        const SizedBox(height: 24),
        Wrap(
          alignment: WrapAlignment.center,
          spacing: 16,
          runSpacing: 16,
          children: List.generate(_choices.length, (i) => _buildEmotionOption(i)),
        ),
      ],
    );
  }

  Widget _buildEmotionOption(int index) {
    final emoji = _choices[index];
    return GestureDetector(
      onTap: () => _onTap(index),
      child: Container(
        width: 72,
        height: 72,
        decoration: BoxDecoration(
          color: AppColors.bgSecondary,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.borderSubtle, width: 2),
          boxShadow: [
            BoxShadow(
              color: AppColors.accentPrimary.withValues(alpha: 0.2),
              blurRadius: 8,
              spreadRadius: 0,
            ),
          ],
        ),
        child: Center(
          child: Text(
            emoji,
            style: const TextStyle(fontSize: 40),
          ),
        ),
      ),
    );
  }
}
