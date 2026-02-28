import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

class LogicCluesMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;
  
  const LogicCluesMinigame({super.key, required this.difficulty});

  @override
  State<LogicCluesMinigame> createState() => _LogicCluesMinigameState();
}

class _LogicCluesMinigameState extends State<LogicCluesMinigame> {
  late List<String> _currentOrder;
  late List<String> _correctOrder;
  late List<String> _clues;
  bool _gameWon = false;
  int _attempts = 0;
  
  late Map<String, Color> _itemColors;
  late int _itemCount;
  
  @override
  void initState() {
    super.initState();
    _resetGame();
  }
  
  void _resetGame() {
    setState(() {
      // Difficulty: number of items and complexity
      switch (widget.difficulty) {
        case MinigameDifficulty.easy:
          _itemCount = 3;
          _itemColors = {
            'Red': Colors.red,
            'Blue': Colors.blue,
            'Green': Colors.green,
          };
          _correctOrder = ['Red', 'Blue', 'Green'];
          _clues = [
            'Red is left of Blue',
            'Green is at the far right',
          ];
          break;
        case MinigameDifficulty.medium:
          _itemCount = 4;
          _itemColors = {
            'Red': Colors.red,
            'Blue': Colors.blue,
            'Yellow': Colors.yellow,
            'Green': Colors.green,
          };
          _correctOrder = ['Red', 'Blue', 'Yellow', 'Green'];
          _clues = [
            'Red is left of Blue',
            'Yellow is between Blue and Green',
            'Green is at the far right',
          ];
          break;
        case MinigameDifficulty.hard:
          _itemCount = 6;
          _itemColors = {
            'Red': Colors.red,
            'Blue': Colors.blue,
            'Yellow': Colors.yellow,
            'Green': Colors.green,
            'Purple': Colors.purple,
            'Orange': Colors.orange,
          };
          // Order: Yellow, Purple, Red, Blue, Green, Orange
          // No direct position clues - requires chaining deductions
          _correctOrder = ['Yellow', 'Purple', 'Red', 'Blue', 'Green', 'Orange'];
          _clues = [
            'Yellow is left of Purple',
            'Purple is between Yellow and Red',
            'Blue is between Red and Green',
            'Green is left of Orange',
            'Red is left of Blue',
          ];
          break;
      }
      
      _currentOrder = List.from(_correctOrder)..shuffle();
      _gameWon = false;
      _attempts = 0;
    });
  }
  
  void _checkSolution() {
    setState(() {
      _attempts++;
      if (_listEquals(_currentOrder, _correctOrder)) {
        _gameWon = true;
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Failed attempt'),
            backgroundColor: Colors.red,
          ),
        );
      }
    });
  }
  
  bool _listEquals(List<String> a, List<String> b) {
    if (a.length != b.length) return false;
    for (int i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('SOLVED!', Icons.psychology, _resetGame);
    }
    
    return Column(
      children: [
        buildStatsBar(
          'Attempts: $_attempts',
          'Arrange $_itemCount boxes',
        ),
        const SizedBox(height: 20),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'Use the clues to arrange the boxes in correct order',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, color: AppColors.textSecondary, height: 1.5),
          ),
        ),
        const SizedBox(height: 20),
        // Clues section
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 20),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.bgSecondary,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.accentPrimary.withOpacity(0.3), width: 2),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.lightbulb_outline, color: AppColors.accentPrimary, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'CLUES:',
                    style: TextStyle(
                      color: AppColors.accentPrimary,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              ..._clues.map((clue) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    const Text('• ', style: TextStyle(color: AppColors.textSecondary, fontSize: 16)),
                    Expanded(
                      child: Text(
                        clue,
                        style: const TextStyle(color: AppColors.textSecondary, fontSize: 14),
                      ),
                    ),
                  ],
                ),
              )),
            ],
          ),
        ),
        const SizedBox(height: 40),
        // Draggable boxes
        Expanded(
          child: Center(
            child: ReorderableListView(
              buildDefaultDragHandles: false,
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 40),
              onReorder: (oldIndex, newIndex) {
                setState(() {
                  if (newIndex > oldIndex) {
                    newIndex -= 1;
                  }
                  final item = _currentOrder.removeAt(oldIndex);
                  _currentOrder.insert(newIndex, item);
                });
              },
              children: _currentOrder.asMap().entries.map<Widget>((entry) {
                final index = entry.key;
                final item = entry.value;
                return ReorderableDragStartListener(
                  key: ValueKey(item),
                  index: index,
                  child: Container(
                  width: 80,
                  height: 80,
                  margin: const EdgeInsets.symmetric(horizontal: 8),
                  decoration: BoxDecoration(
                    color: _itemColors[item],
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.white, width: 3),
                    boxShadow: [
                      BoxShadow(
                        color: _itemColors[item]!.withOpacity(0.5),
                        blurRadius: 10,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: Center(
                    child: Text(
                      item,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                );
              }).toList(),
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(40),
          child: ElevatedButton.icon(
            onPressed: _checkSolution,
            icon: const Icon(Icons.check_circle_outline),
            label: const Text('Check Solution'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.bgSecondary,
              foregroundColor: AppColors.textPrimary,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              textStyle: const TextStyle(fontSize: 18),
            ),
          ),
        ),
      ],
    );
  }
}
