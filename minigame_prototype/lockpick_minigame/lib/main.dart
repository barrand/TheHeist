import 'package:flutter/material.dart';
import 'dart:math';
import 'dart:async';

void main() {
  runApp(const MinigamePrototypeApp());
}

class MinigamePrototypeApp extends StatelessWidget {
  const MinigamePrototypeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Minigame Prototypes',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF1a1a2e),
        primaryColor: const Color(0xFF16213e),
      ),
      home: const MinigameHub(),
    );
  }
}

class MinigameHub extends StatelessWidget {
  const MinigameHub({super.key});
  
  // Map of implemented minigames: id -> widget
  static const Map<String, Widget> _implementedMinigames = {
    'lockpick_timing': LockpickMinigame(),
    'dial_rotation': DialSafeMinigame(),
    'simon_says_sequence': SimonSaysMinigame(),
    'wire_connecting': WireConnectMinigame(),
    'badge_swipe': CardSwipeMinigame(),
    'timing_tap': TimingTapMinigame(),
    'button_mash_barrier': ButtonMashMinigame(),
    'climbing_rhythm': RhythmClimbMinigame(),
    'logic_clues': LogicCluesMinigame(),
  };
  
  // All roles and their minigames from roles.json
  static final List<RoleMinigames> _roles = [
    RoleMinigames('Mastermind', [
      MinigameInfo('logic_clues', 'Logic Clues', 'Arrange boxes using clues', Icons.psychology),
    ]),
    RoleMinigames('Hacker', [
      MinigameInfo('wire_connecting', 'Wire Connect', 'Match wires by color or symbol', Icons.cable),
      MinigameInfo('simon_says_sequence', 'Simon Says', 'Memorize and repeat pattern', Icons.grid_view),
      MinigameInfo('cipher_wheel_alignment', 'Cipher Wheel', 'Align spinning symbols', Icons.track_changes),
      MinigameInfo('card_swipe', 'Card Swipe', 'Swipe keycard at right speed', Icons.credit_card),
    ]),
    RoleMinigames('Safe Cracker', [
      MinigameInfo('dial_rotation', 'Dial Safe', 'Rotate dial to target numbers', Icons.lock),
      MinigameInfo('lockpick_timing', 'Lockpick', 'Position pins correctly', Icons.lock_open),
      MinigameInfo('listen_for_clicks', 'Listen for Clicks', 'Audio-based safecracking', Icons.hearing),
    ]),
    RoleMinigames('Driver', [
      MinigameInfo('steering_obstacle_course', 'Obstacle Course', 'Avoid obstacles while driving', Icons.sports_motorsports),
      MinigameInfo('fuel_pump', 'Fuel Pump', 'Fill tank without overflow', Icons.local_gas_station),
      MinigameInfo('parking_precision', 'Precision Park', 'Brake at perfect moment', Icons.local_parking),
    ]),
    RoleMinigames('Insider', [
      MinigameInfo('badge_swipe', 'Badge Swipe', 'Swipe at correct speed', Icons.badge),
      MinigameInfo('memory_matching', 'Memory Match', 'Remember access codes', Icons.memory),
      MinigameInfo('inventory_check', 'Inventory Check', 'Find items before timeout', Icons.inventory),
    ]),
    RoleMinigames('Grifter', [
      MinigameInfo('timed_dialogue_choices', 'Dialogue Choice', 'Pick response before timeout', Icons.chat_bubble),
      MinigameInfo('emotion_matching', 'Emotion Match', 'Match facial expression', Icons.emoji_emotions),
      MinigameInfo('convincing_sequence', 'Be Convincing', 'Tap in rhythm to persuade', Icons.favorite),
    ]),
    RoleMinigames('Muscle', [
      MinigameInfo('takedown_timing', 'Stealth Takedown', 'Tap at perfect moment', Icons.sports_martial_arts),
      MinigameInfo('button_mash_barrier', 'Button Mash', 'Tap rapidly to break through', Icons.fitness_center),
      MinigameInfo('reaction_time', 'Quick React', 'Tap immediately when prompted', Icons.flash_on),
    ]),
    RoleMinigames('Lookout', [
      MinigameInfo('spot_the_difference', 'Spot Difference', 'Find anomalies in feeds', Icons.compare),
      MinigameInfo('whack_a_mole_threats', 'Whack-a-Threat', 'Tap threats on camera feeds', Icons.videocam),
      MinigameInfo('pattern_memorization', 'Guard Pattern', 'Memorize patrol routes', Icons.route),
    ]),
    RoleMinigames('Fence', [
      MinigameInfo('item_matching', 'Item Match', 'Match items to buyers', Icons.handshake),
      MinigameInfo('haggling_slider', 'Haggle', 'Stop slider at best price', Icons.attach_money),
      MinigameInfo('quality_inspection', 'Quality Check', 'Find defects in forgery', Icons.search),
    ]),
    RoleMinigames('Cat Burglar', [
      MinigameInfo('climbing_rhythm', 'Rhythm Climb', 'Tap when note hits target', Icons.stairs),
      MinigameInfo('laser_maze_timing', 'Laser Maze', 'Time movement through lasers', Icons.blur_on),
      MinigameInfo('balance_meter', 'Balance', 'Keep meter centered', Icons.balance),
    ]),
    RoleMinigames('Cleaner', [
      MinigameInfo('swipe_fingerprints', 'Wipe Prints', 'Swipe over fingerprints', Icons.cleaning_services),
      MinigameInfo('tap_evidence_markers', 'Tag Evidence', 'Tap all markers before timeout', Icons.label),
      MinigameInfo('trash_disposal', 'Dispose', 'Drag items to trash quickly', Icons.delete),
    ]),
    RoleMinigames('Pickpocket', [
      MinigameInfo('timing_tap', 'Timing Tap', 'Tap when circle hits zone', Icons.touch_app),
      MinigameInfo('quick_pocket_search', 'Pocket Search', 'Drag items from pocket fast', Icons.backpack),
      MinigameInfo('distraction_meter', 'Distraction', 'Steal when target looks away', Icons.visibility_off),
    ]),
  ];
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1a1a2e),
      appBar: AppBar(
        backgroundColor: const Color(0xFF16213e),
        title: const Text('Minigame Prototypes'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: _roles.length,
          itemBuilder: (context, index) {
            return _buildRoleSection(context, _roles[index]);
          },
        ),
      ),
    );
  }
  
  Widget _buildRoleSection(BuildContext context, RoleMinigames role) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Role header
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
          child: Text(
            role.name.toUpperCase(),
            style: const TextStyle(
              color: Color(0xFF0ea5e9),
              fontSize: 14,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
        ),
        // Minigames for this role
        ...role.minigames.map((minigame) => _buildMinigameRow(context, minigame)),
        const SizedBox(height: 8),
      ],
    );
  }
  
  Widget _buildMinigameRow(BuildContext context, MinigameInfo minigame) {
    final isImplemented = _implementedMinigames.containsKey(minigame.id);
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: GestureDetector(
        onTap: isImplemented ? () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => MinigameScreen(
                title: minigame.name,
                child: _implementedMinigames[minigame.id]!,
              ),
            ),
          );
        } : null,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          decoration: BoxDecoration(
            color: isImplemented 
                ? const Color(0xFF16213e)
                : const Color(0xFF16213e).withOpacity(0.3),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: isImplemented 
                  ? const Color(0xFF0ea5e9).withOpacity(0.3)
                  : Colors.white.withOpacity(0.1),
              width: 1,
            ),
          ),
          child: Row(
            children: [
              Icon(
                minigame.icon,
                size: 20,
                color: isImplemented ? const Color(0xFF0ea5e9) : Colors.white30,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      minigame.name,
                      style: TextStyle(
                        color: isImplemented ? Colors.white : Colors.white38,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      minigame.description,
                      style: TextStyle(
                        color: isImplemented ? Colors.white60 : Colors.white24,
                        fontSize: 11,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              if (isImplemented)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: Colors.green, width: 1),
                  ),
                  child: const Text(
                    '✓',
                    style: TextStyle(
                      color: Colors.green,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                )
              else
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text(
                    'TODO',
                    style: TextStyle(
                      color: Colors.white30,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// Data models for organization
class RoleMinigames {
  final String name;
  final List<MinigameInfo> minigames;
  
  RoleMinigames(this.name, this.minigames);
}

class MinigameInfo {
  final String id;
  final String name;
  final String description;
  final IconData icon;
  
  MinigameInfo(this.id, this.name, this.description, this.icon);
}

// Wrapper screen for individual minigames with back button
class MinigameScreen extends StatelessWidget {
  final String title;
  final Widget child;
  
  const MinigameScreen({
    super.key,
    required this.title,
    required this.child,
  });
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1a1a2e),
      appBar: AppBar(
        backgroundColor: const Color(0xFF16213e),
        title: Text(title),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: child,
    );
  }
}

// ============================================
// 1. LOCKPICK MINIGAME (Safe Cracker)
// ============================================
class LockpickMinigame extends StatefulWidget {
  const LockpickMinigame({super.key});

  @override
  State<LockpickMinigame> createState() => _LockpickMinigameState();
}

class _LockpickMinigameState extends State<LockpickMinigame> {
  final int _pinCount = 5;
  late List<double> _pinPositions;
  late List<double> _targetPositions;
  late List<bool> _pinsSolved;
  int _attempts = 0;
  bool _gameWon = false;
  
  @override
  void initState() {
    super.initState();
    _initializeGame();
  }
  
  void _initializeGame() {
    final random = Random();
    _pinPositions = List.generate(_pinCount, (_) => 0.0);
    _targetPositions = List.generate(_pinCount, (_) => random.nextDouble());
    _pinsSolved = List.generate(_pinCount, (_) => false);
    _attempts = 0;
    _gameWon = false;
  }
  
  void _resetGame() {
    setState(() {
      _initializeGame();
    });
  }
  
  double _getProximity(int pinIndex) {
    final diff = (_pinPositions[pinIndex] - _targetPositions[pinIndex]).abs();
    return 1.0 - diff;
  }
  
  Color _getProximityColor(int pinIndex) {
    if (_pinsSolved[pinIndex]) return Colors.green;
    final proximity = _getProximity(pinIndex);
    if (proximity > 0.95) return Colors.green.shade300;
    if (proximity > 0.85) return Colors.yellow.shade300;
    if (proximity > 0.70) return Colors.orange.shade300;
    return Colors.red.shade300;
  }
  
  void _onPinDragged(int pinIndex, double delta) {
    setState(() {
      _pinPositions[pinIndex] = (_pinPositions[pinIndex] + delta).clamp(0.0, 1.0);
      _pinsSolved[pinIndex] = _getProximity(pinIndex) > 0.95;
      if (_pinsSolved.every((solved) => solved)) {
        _gameWon = true;
      }
    });
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return _buildWinScreen('UNLOCKED!', Icons.lock_open, _resetGame);
    }
    
    return Column(
      children: [
        _buildStatsBar(
          'Attempts: $_attempts',
          'Solved: ${_pinsSolved.where((s) => s).length}/$_pinCount',
        ),
        const SizedBox(height: 20),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'Drag each pin to find the correct position.\nGreen = locked!',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, color: Colors.white60, height: 1.5),
          ),
        ),
        const SizedBox(height: 20),
        Expanded(
          child: Center(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(_pinCount, (index) {
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: _buildPin(index),
                );
              }),
            ),
          ),
        ),
      ],
    );
  }
  
  Widget _buildPin(int index) {
    final color = _getProximityColor(index);
    final isSolved = _pinsSolved[index];
    
    return GestureDetector(
      onVerticalDragUpdate: (details) {
        _onPinDragged(index, -details.delta.dy / 300);
        _attempts++;
      },
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 40,
            height: 300,
            decoration: BoxDecoration(
              color: const Color(0xFF2a2a3e),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.white24, width: 2),
            ),
            child: Stack(
              children: [
                Positioned(
                  bottom: _pinPositions[index] * 260 + 20,
                  left: 0,
                  right: 0,
                  child: Container(
                    height: 20,
                    margin: const EdgeInsets.symmetric(horizontal: 8),
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(10),
                      boxShadow: [
                        BoxShadow(
                          color: color.withOpacity(0.5),
                          blurRadius: isSolved ? 15 : 5,
                          spreadRadius: isSolved ? 2 : 0,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: isSolved ? Colors.green : Colors.grey.shade800,
              shape: BoxShape.circle,
              border: Border.all(
                color: isSolved ? Colors.green.shade300 : Colors.grey.shade600,
                width: 2,
              ),
            ),
            child: Icon(
              isSolved ? Icons.check : Icons.lock,
              color: Colors.white,
              size: 20,
            ),
          ),
        ],
      ),
    );
  }
}

// ============================================
// 2. SIMON SAYS MINIGAME (Hacker)
// ============================================
class SimonSaysMinigame extends StatefulWidget {
  const SimonSaysMinigame({super.key});

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
  int _tappedButton = -1; // Track player taps for visual feedback
  int _round = 1;
  
  final List<Color> _buttonColors = [
    Colors.red,
    Colors.blue,
    Colors.green,
    Colors.yellow,
  ];
  
  @override
  void initState() {
    super.initState();
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
      await Future.delayed(const Duration(milliseconds: 600));
      if (!mounted) return;
      setState(() {
        _flashingButton = -1;
      });
      await Future.delayed(const Duration(milliseconds: 200));
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
      _tappedButton = index; // Show visual feedback
      _playerInput.add(index);
      
      if (_playerInput[_currentIndex] != _sequence[_currentIndex]) {
        _gameFailed = true;
      } else {
        _currentIndex++;
        if (_currentIndex == _sequence.length) {
          if (_round >= 5) {
            _gameWon = true;
          } else {
            _round++;
            Future.delayed(const Duration(milliseconds: 500), _startNewRound);
          }
        }
      }
    });
    
    // Clear tap feedback after a brief moment
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
      return _buildWinScreen('HACKED!', Icons.check_circle, _resetGame);
    }
    
    if (_gameFailed) {
      return _buildFailScreen(_resetGame);
    }
    
    return Column(
      children: [
        _buildStatsBar(
          'Round: $_round / 5',
          'Sequence: ${_sequence.length}',
        ),
        const SizedBox(height: 20),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            _showingSequence ? 'Watch the sequence...' : 'Repeat the pattern!',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 18, color: Colors.white70, fontWeight: FontWeight.bold),
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

// ============================================
// 3. DIAL SAFE MINIGAME (Safe Cracker)
// ============================================
class DialSafeMinigame extends StatefulWidget {
  const DialSafeMinigame({super.key});

  @override
  State<DialSafeMinigame> createState() => _DialSafeMinigameState();
}

class _DialSafeMinigameState extends State<DialSafeMinigame> {
  double _rotation = 0.0;
  final List<int> _combination = [15, 73, 42];
  final List<int> _userInput = [];
  int _currentStep = 0;
  bool _gameWon = false;
  
  int get _currentNumber => ((_rotation % 360) / 3.6).round() % 100;
  
  void _onDragUpdate(DragUpdateDetails details) {
    setState(() {
      _rotation += details.delta.dx * 0.5;
      _rotation = _rotation % 360;
    });
  }
  
  void _submitNumber() {
    if (_currentStep >= _combination.length) return;
    
    setState(() {
      _userInput.add(_currentNumber);
      
      // Check if correct
      if (_userInput[_currentStep] >= _combination[_currentStep] - 2 &&
          _userInput[_currentStep] <= _combination[_currentStep] + 2) {
        _currentStep++;
        if (_currentStep == _combination.length) {
          _gameWon = true;
        }
      } else {
        // Reset on wrong input
        _userInput.clear();
        _currentStep = 0;
      }
    });
  }
  
  void _resetGame() {
    setState(() {
      _rotation = 0.0;
      _userInput.clear();
      _currentStep = 0;
      _gameWon = false;
    });
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return _buildWinScreen('CRACKED!', Icons.lock_open, _resetGame);
    }
    
    return Column(
      children: [
        _buildStatsBar(
          'Step: ${_currentStep + 1} / ${_combination.length}',
          'Target: ${_currentStep < _combination.length ? _combination[_currentStep] : "—"}',
        ),
        const SizedBox(height: 20),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'Drag the dial to the target number, then tap Submit',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, color: Colors.white60, height: 1.5),
          ),
        ),
        const SizedBox(height: 40),
        Expanded(
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Current number display
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 20),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2a2a3e),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.white24, width: 2),
                  ),
                  child: Text(
                    _currentNumber.toString().padLeft(2, '0'),
                    style: const TextStyle(
                      fontSize: 60,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
                const SizedBox(height: 40),
                // Dial
                GestureDetector(
                  onPanUpdate: _onDragUpdate,
                  child: Transform.rotate(
                    angle: _rotation * pi / 180,
                    child: Container(
                      width: 200,
                      height: 200,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xFF2a2a3e),
                        border: Border.all(color: Colors.white24, width: 4),
                      ),
                      child: Stack(
                        children: [
                          Center(
                            child: Container(
                              width: 20,
                              height: 20,
                              decoration: const BoxDecoration(
                                color: Colors.white,
                                shape: BoxShape.circle,
                              ),
                            ),
                          ),
                          Positioned(
                            top: 10,
                            left: 90,
                            child: Container(
                              width: 20,
                              height: 60,
                              decoration: BoxDecoration(
                                color: Colors.cyan,
                                borderRadius: BorderRadius.circular(10),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 40),
                // Submit button
                ElevatedButton(
                  onPressed: _submitNumber,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF16213e),
                    padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
                  ),
                  child: const Text('Submit', style: TextStyle(fontSize: 18)),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

// ============================================
// 4. BUTTON MASH MINIGAME (Muscle)
// ============================================
class ButtonMashMinigame extends StatefulWidget {
  const ButtonMashMinigame({super.key});

  @override
  State<ButtonMashMinigame> createState() => _ButtonMashMinigameState();
}

class _ButtonMashMinigameState extends State<ButtonMashMinigame> {
  int _taps = 0;
  final int _targetTaps = 50;
  bool _gameWon = false;
  Timer? _timer;
  int _timeLeft = 10;
  
  @override
  void initState() {
    super.initState();
    _startTimer();
  }
  
  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
  
  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        _timeLeft--;
        if (_timeLeft <= 0) {
          timer.cancel();
        }
      });
    });
  }
  
  void _onTap() {
    if (_gameWon || _timeLeft <= 0) return;
    
    setState(() {
      _taps++;
      if (_taps >= _targetTaps) {
        _gameWon = true;
        _timer?.cancel();
      }
    });
  }
  
  void _resetGame() {
    setState(() {
      _taps = 0;
      _gameWon = false;
      _timeLeft = 10;
    });
    _timer?.cancel();
    _startTimer();
  }
  
  @override
  Widget build(BuildContext context) {
    final progress = _taps / _targetTaps;
    
    if (_gameWon) {
      return _buildWinScreen('SMASHED!', Icons.fitness_center, _resetGame);
    }
    
    if (_timeLeft <= 0 && !_gameWon) {
      return _buildFailScreen(_resetGame);
    }
    
    return Column(
      children: [
        _buildStatsBar(
          'Taps: $_taps / $_targetTaps',
          'Time: ${_timeLeft}s',
        ),
        const SizedBox(height: 20),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'TAP AS FAST AS YOU CAN!',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 20,
              color: Colors.white,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
            ),
          ),
        ),
        const SizedBox(height: 40),
        // Progress bar
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 40),
          child: Column(
            children: [
              LinearProgressIndicator(
                value: progress,
                minHeight: 20,
                backgroundColor: Colors.grey.shade800,
                valueColor: AlwaysStoppedAnimation<Color>(
                  progress > 0.7 ? Colors.green : Colors.orange,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${(progress * 100).toInt()}%',
                style: const TextStyle(fontSize: 18, color: Colors.white70),
              ),
            ],
          ),
        ),
        const SizedBox(height: 60),
        // Big tap button
        Expanded(
          child: Center(
            child: GestureDetector(
              onTap: _onTap,
              child: Container(
                width: 250,
                height: 250,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.red.withOpacity(0.3),
                  border: Border.all(color: Colors.red, width: 5),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.red.withOpacity(0.5),
                      blurRadius: 30,
                      spreadRadius: 10,
                    ),
                  ],
                ),
                child: const Center(
                  child: Text(
                    'TAP!',
                    style: TextStyle(
                      fontSize: 48,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

// ============================================
// 5. TIMING TAP MINIGAME (Pickpocket)
// ============================================
class TimingTapMinigame extends StatefulWidget {
  const TimingTapMinigame({super.key});

  @override
  State<TimingTapMinigame> createState() => _TimingTapMinigameState();
}

class _TimingTapMinigameState extends State<TimingTapMinigame> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  bool _gameWon = false;
  int _attempts = 0;
  int _successes = 0;
  String _feedback = '';
  
  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2500), // Slower for easier timing
    )..repeat(reverse: true);
  }
  
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
  
  void _onTap() {
    setState(() {
      _attempts++;
      final value = _controller.value;
      // Challenging success zone: 0.40 to 0.60 (20% range)
      if (value >= 0.40 && value <= 0.60) {
        _successes++;
        _feedback = 'PERFECT! ✓';
        if (_successes >= 5) {
          _gameWon = true;
          _controller.stop();
        }
      } else {
        _feedback = 'Too early/late ✗';
      }
      
      // Clear feedback after a moment
      Future.delayed(const Duration(milliseconds: 500), () {
        if (mounted) {
          setState(() {
            _feedback = '';
          });
        }
      });
    });
  }
  
  void _resetGame() {
    setState(() {
      _gameWon = false;
      _attempts = 0;
      _successes = 0;
    });
    _controller.repeat(reverse: true);
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return _buildWinScreen('PERFECT STEAL!', Icons.check_circle, _resetGame);
    }
    
    return Column(
      children: [
        _buildStatsBar(
          'Successes: $_successes / 5',
          'Attempts: $_attempts',
        ),
        const SizedBox(height: 20),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            children: [
              const Text(
                'Tap when the circle enters the GREEN ZONE!\nGet 5 perfect taps to win.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.white60, height: 1.5),
              ),
              const SizedBox(height: 8),
              if (_feedback.isNotEmpty)
                Text(
                  _feedback,
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: _feedback.contains('PERFECT') ? Colors.green : Colors.red,
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: 40),
        Expanded(
          child: Center(
            child: AnimatedBuilder(
              animation: _controller,
              builder: (context, child) {
                final value = _controller.value;
                final inGoodZone = value >= 0.40 && value <= 0.60;
                
                return Stack(
                  alignment: Alignment.center,
                  children: [
                    // Outer boundary
                    Container(
                      width: 300,
                      height: 300,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white24, width: 3),
                        color: Colors.transparent,
                      ),
                    ),
                    // Success zone indicator (green donut)
                    // Outer edge: 300*(1-0.40) = 180
                    Container(
                      width: 180,
                      height: 180,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.green.withOpacity(0.2),
                        border: Border.all(color: Colors.green.withOpacity(0.6), width: 2),
                      ),
                    ),
                    // Inner cutout (to make it a ring)
                    // Inner edge: 300*(1-0.60) = 120
                    Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xFF1a1a2e), // Match background
                        border: Border.all(color: Colors.green.withOpacity(0.6), width: 2),
                      ),
                    ),
                    // Shrinking circle
                    Container(
                      width: 300 * (1 - value),
                      height: 300 * (1 - value),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: inGoodZone 
                            ? Colors.green.withOpacity(0.4)
                            : Colors.cyan.withOpacity(0.3),
                        border: Border.all(
                          color: inGoodZone ? Colors.green : Colors.cyan,
                          width: 4,
                        ),
                        boxShadow: inGoodZone ? [
                          BoxShadow(
                            color: Colors.green.withOpacity(0.6),
                            blurRadius: 20,
                            spreadRadius: 5,
                          ),
                        ] : [],
                      ),
                    ),
                    // Center dot
                    Container(
                      width: 20,
                      height: 20,
                      decoration: const BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(40),
          child: ElevatedButton(
            onPressed: _onTap,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF16213e),
              padding: const EdgeInsets.symmetric(horizontal: 60, vertical: 20),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(30),
              ),
            ),
            child: const Text(
              'TAP NOW!',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
          ),
        ),
      ],
    );
  }
}

// ============================================
// 6. WIRE CONNECT MINIGAME (Hacker)
// ============================================
class WireConnectMinigame extends StatefulWidget {
  const WireConnectMinigame({super.key});

  @override
  State<WireConnectMinigame> createState() => _WireConnectMinigameState();
}

class _WireConnectMinigameState extends State<WireConnectMinigame> {
  // Left wires: Each has BOTH color and symbol
  final List<WireFull> _leftWires = [
    WireFull(Colors.red, Icons.star, 'Red Star'),
    WireFull(Colors.blue, Icons.circle, 'Blue Circle'),
    WireFull(Colors.green, Icons.square, 'Green Square'),
    WireFull(Colors.purple, Icons.favorite, 'Purple Heart'),
    WireFull(Colors.orange, Icons.hexagon, 'Orange Hex'),
  ];
  
  // Right ports: Each shows EITHER color or symbol (not both)
  // matchType: 'color' or 'symbol' - determines what matches
  late List<PortType> _rightPorts;
  
  final Map<int, int> _connections = {}; // left wire index -> right port index
  final Map<int, bool> _wrongAttempts = {}; // Track wrong connections to show visual feedback
  bool _gameWon = false;
  int? _selectedLeftWire;
  String _feedback = '';
  
  @override
  void initState() {
    super.initState();
    _resetGame();
  }
  
  void _resetGame() {
    setState(() {
      _connections.clear();
      _wrongAttempts.clear();
      _gameWon = false;
      _selectedLeftWire = null;
      _feedback = '';
      
      // Create right ports - each wire can match by color OR symbol
      // Randomly decide which attribute each port shows
      final decisions = [0, 1, 2, 3, 4]; // Which wires
      decisions.shuffle();
      
      _rightPorts = [];
      for (int i = 0; i < 5; i++) {
        final wireIndex = decisions[i];
        final wire = _leftWires[wireIndex];
        final matchByColor = Random().nextBool(); // 50/50 color or symbol
        
        _rightPorts.add(PortType(
          wireIndex: wireIndex,
          color: matchByColor ? wire.color : Colors.grey.shade700,
          icon: matchByColor ? null : wire.icon,
          matchType: matchByColor ? 'color' : 'symbol',
        ));
      }
      // Shuffle right ports
      _rightPorts.shuffle();
    });
  }
  
  void _selectLeftWire(int wireIndex) {
    setState(() {
      _selectedLeftWire = wireIndex;
    });
  }
  
  void _selectRightPort(int portIndex) {
    if (_selectedLeftWire == null) return;
    
    final leftWire = _leftWires[_selectedLeftWire!];
    final rightPort = _rightPorts[portIndex];
    
    setState(() {
      // Check if this wire matches this port
      if (rightPort.wireIndex == _selectedLeftWire) {
        // Correct match! Remove any existing connection to this port
        _connections.removeWhere((key, value) => value == portIndex);
        // Add new connection
        _connections[_selectedLeftWire!] = portIndex;
        _feedback = '✓ Connected!';
        
        Future.delayed(const Duration(milliseconds: 800), () {
          if (mounted) {
            setState(() {
              _feedback = '';
            });
          }
        });
        
        // Check if all connected correctly
        if (_connections.length == 5) {
          _gameWon = true;
        }
      } else {
        // Wrong match - show feedback
        _feedback = '✗ No match! Try another.';
        _wrongAttempts[portIndex] = true;
        
        // Clear wrong attempt marker after a moment
        Future.delayed(const Duration(milliseconds: 1500), () {
          if (mounted) {
            setState(() {
              _feedback = '';
              _wrongAttempts.remove(portIndex);
            });
          }
        });
      }
      
      _selectedLeftWire = null;
    });
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return _buildWinScreen('CONNECTED!', Icons.check_circle, _resetGame);
    }
    
    return Column(
      children: [
        _buildStatsBar(
          'Connected: ${_connections.length} / 5',
          'Colors + Symbols',
        ),
        const SizedBox(height: 20),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            children: [
              const Text(
                '🧩 Figure out the pattern!\nLeft: Color + Symbol | Right: Color OR Symbol',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 14, color: Colors.white60, height: 1.5),
              ),
              const SizedBox(height: 8),
              if (_selectedLeftWire != null)
                Text(
                  'Selected: ${_leftWires[_selectedLeftWire!].name}',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: _leftWires[_selectedLeftWire!].color,
                  ),
                ),
              if (_feedback.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text(
                    _feedback,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: _feedback.contains('✓') ? Colors.green : Colors.red,
                    ),
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: 40),
        Expanded(
          child: Center(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                // Left wires (color + symbol)
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(5, (wireIndex) {
                    return _buildLeftWire(wireIndex);
                  }),
                ),
                // Wires visualization
                Expanded(
                  child: CustomPaint(
                    painter: WireConnectPainter(_connections, _leftWires, _rightPorts, _selectedLeftWire),
                    child: Container(),
                  ),
                ),
                // Right ports (color OR symbol)
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(_rightPorts.length, (portIndex) {
                    return _buildRightPort(portIndex);
                  }),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
  
  Widget _buildLeftWire(int wireIndex) {
    final wire = _leftWires[wireIndex];
    final isConnected = _connections.containsKey(wireIndex);
    final isSelected = _selectedLeftWire == wireIndex;
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: GestureDetector(
        onTap: () => _selectLeftWire(wireIndex),
        child: Container(
          width: 70,
          height: 70,
          decoration: BoxDecoration(
            color: isConnected 
                ? wire.color 
                : (isSelected 
                    ? wire.color.withOpacity(0.6) 
                    : wire.color.withOpacity(0.3)),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: wire.color, 
              width: isSelected ? 5 : 3,
            ),
            boxShadow: (isConnected || isSelected) ? [
              BoxShadow(
                color: wire.color.withOpacity(0.6),
                blurRadius: 15,
                spreadRadius: isSelected ? 5 : 3,
              ),
            ] : [],
          ),
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  wire.icon,
                  color: Colors.white,
                  size: 24,
                ),
                const SizedBox(height: 2),
                Container(
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    color: wire.color.withOpacity(0.8),
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 2),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildRightPort(int portIndex) {
    final port = _rightPorts[portIndex];
    final isConnected = _connections.values.contains(portIndex);
    final isWrongAttempt = _wrongAttempts[portIndex] == true;
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: GestureDetector(
        onTap: () => _selectRightPort(portIndex),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: 70,
          height: 70,
          decoration: BoxDecoration(
            color: isWrongAttempt
                ? Colors.red.withOpacity(0.3)
                : (isConnected 
                    ? port.color 
                    : port.color.withOpacity(0.3)),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isWrongAttempt ? Colors.red : port.color,
              width: isWrongAttempt ? 3 : 3,
            ),
            boxShadow: isConnected ? [
              BoxShadow(
                color: port.color.withOpacity(0.6),
                blurRadius: 15,
                spreadRadius: 3,
              ),
            ] : [],
          ),
          child: Center(
            child: port.icon != null
                ? Icon(
                    port.icon,
                    color: Colors.white,
                    size: 32,
                  )
                : (isConnected
                    ? const Icon(Icons.check, color: Colors.white, size: 30)
                    : Container(
                        width: 30,
                        height: 30,
                        decoration: BoxDecoration(
                          color: port.color,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 2),
                        ),
                      )),
          ),
        ),
      ),
    );
  }
}

// Left wire: has BOTH color and symbol
class WireFull {
  final Color color;
  final IconData icon;
  final String name;
  
  WireFull(this.color, this.icon, this.name);
}

// Right port: shows EITHER color or symbol
class PortType {
  final int wireIndex; // Which left wire this matches
  final Color color;
  final IconData? icon;
  final String matchType; // 'color' or 'symbol'
  
  PortType({
    required this.wireIndex,
    required this.color,
    this.icon,
    required this.matchType,
  });
}

class WireConnectPainter extends CustomPainter {
  final Map<int, int> connections;
  final List<WireFull> leftWires;
  final List<PortType> rightPorts;
  final int? selectedLeftWire;
  
  WireConnectPainter(this.connections, this.leftWires, this.rightPorts, this.selectedLeftWire);
  
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..strokeWidth = 4
      ..style = PaintingStyle.stroke;
    
    // Draw connected wires
    connections.forEach((leftIndex, rightPortIndex) {
      paint.color = leftWires[leftIndex].color;
      final startY = 100.0 + (leftIndex * 94);
      final endY = 100.0 + (rightPortIndex * 94);
      
      final path = Path();
      path.moveTo(0, startY);
      // Curved wire
      path.cubicTo(
        size.width * 0.3, startY,
        size.width * 0.7, endY,
        size.width, endY,
      );
      canvas.drawPath(path, paint);
    });
    
    // Draw selection indicator
    if (selectedLeftWire != null) {
      paint.color = leftWires[selectedLeftWire!].color.withOpacity(0.5);
      paint.strokeWidth = 2;
      paint.style = PaintingStyle.stroke;
      final startY = 100.0 + (selectedLeftWire! * 94);
      canvas.drawLine(
        Offset(0, startY),
        Offset(size.width, startY),
        paint,
      );
    }
  }
  
  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

// ============================================
// 7. CARD SWIPE MINIGAME (Insider)
// ============================================
class CardSwipeMinigame extends StatefulWidget {
  const CardSwipeMinigame({super.key});

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
  double _cardOffset = -150.0; // Start on the left
  bool _isSwiping = false;
  
  @override
  void initState() {
    super.initState();
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
      _cardOffset = -150.0; // Reset to left
    });
  }
  
  void _onSwipeUpdate(DragUpdateDetails details) {
    setState(() {
      // Only allow rightward movement
      if (details.delta.dx > 0) {
        _cardOffset += details.delta.dx;
        _cardOffset = _cardOffset.clamp(-150.0, 150.0);
      }
    });
  }
  
  void _onSwipeEnd(DragEndDetails details) {
    final velocityX = details.velocity.pixelsPerSecond.dx;
    
    // Only count rightward swipes
    if (velocityX < 0) {
      setState(() {
        _isSwiping = false;
        _feedback = 'SWIPE RIGHT! →';
        _cardOffset = -150.0; // Reset immediately
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
      
      // Target speed: 200-600 pixels/second
      if (velocity >= 200 && velocity <= 600) {
        _successes++;
        _feedback = 'PERFECT SWIPE! ✓';
        if (_successes >= 3) {
          _gameWon = true;
          _speedIndicator.stop();
        }
      } else if (velocity < 200) {
        _feedback = 'TOO SLOW ✗';
      } else {
        _feedback = 'TOO FAST ✗';
      }
      
      // Animate card back to left
      _cardAnimation.forward(from: 0.0).then((_) {
        setState(() {
          _cardOffset = -150.0; // Back to left
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
      _cardOffset = -150.0; // Reset to left
    });
    _speedIndicator.repeat(reverse: true);
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return _buildWinScreen('ACCESS GRANTED!', Icons.check_circle, _resetGame);
    }
    
    return Column(
      children: [
        _buildStatsBar(
          'Successes: $_successes / 3',
          'Attempts: $_attempts',
        ),
        const SizedBox(height: 20),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            children: [
              const Text(
                'Swipe the card at the right speed!\nNot too fast, not too slow.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.white60, height: 1.5),
              ),
              const SizedBox(height: 12),
              if (_feedback.isNotEmpty)
                Text(
                  _feedback,
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: _feedback.contains('PERFECT') ? Colors.green : Colors.red,
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
                    style: TextStyle(color: Colors.green, fontSize: 14),
                  ),
                  const SizedBox(height: 8),
                  Stack(
                    children: [
                      Container(
                        height: 40,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [
                              Colors.red,
                              Colors.orange,
                              Colors.green,
                              Colors.orange,
                              Colors.red,
                            ],
                            stops: const [0.0, 0.25, 0.5, 0.75, 1.0],
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
                // Terminal display
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
                          color: _isSwiping ? Colors.yellow : Colors.green,
                          fontSize: 16,
                          fontFamily: 'monospace',
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      // Card slot visualization
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
                            // Slot lines
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
                            // Moving card
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    Icon(Icons.arrow_forward, color: Colors.cyan, size: 20),
                    SizedBox(width: 8),
                    Text(
                      'Swipe card RIGHT through reader',
                      style: TextStyle(
                        color: Colors.white60,
                        fontSize: 14,
                      ),
                    ),
                    SizedBox(width: 8),
                    Icon(Icons.arrow_forward, color: Colors.cyan, size: 20),
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

// ============================================
// 8. RHYTHM CLIMB MINIGAME (Cat Burglar)
// ============================================
class RhythmClimbMinigame extends StatefulWidget {
  const RhythmClimbMinigame({super.key});

  @override
  State<RhythmClimbMinigame> createState() => _RhythmClimbMinigameState();
}

class _RhythmClimbMinigameState extends State<RhythmClimbMinigame> with SingleTickerProviderStateMixin {
  late AnimationController _noteController;
  int _height = 0;
  final int _targetHeight = 10;
  bool _gameWon = false;
  String _feedback = '';
  int _consecutiveMisses = 0;
  double _targetLinePosition = 0.7; // Where notes should be hit - changes after each tap!
  final List<double> _possiblePositions = [0.3, 0.5, 0.7, 0.85]; // Different target positions
  
  @override
  void initState() {
    super.initState();
    _noteController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000), // Time for note to travel
    )..repeat();
  }
  
  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }
  
  void _onTap() {
    final noteValue = _noteController.value;
    // Success zone: when note is near the target line (±0.08 range)
    final onBeat = (noteValue >= _targetLinePosition - 0.08 && noteValue <= _targetLinePosition + 0.08);
    
    setState(() {
      if (onBeat) {
        _height++;
        _consecutiveMisses = 0;
        _feedback = 'PERFECT! ✓';
        
        // Move target to a new position after successful hit
        final currentIndex = _possiblePositions.indexOf(_targetLinePosition);
        final availablePositions = List<double>.from(_possiblePositions);
        if (currentIndex != -1) {
          availablePositions.removeAt(currentIndex); // Don't stay in same spot
        }
        _targetLinePosition = availablePositions[Random().nextInt(availablePositions.length)];
        
        if (_height >= _targetHeight) {
          _gameWon = true;
          _noteController.stop();
        }
      } else {
        _consecutiveMisses++;
        _feedback = 'MISSED ✗';
        if (_consecutiveMisses >= 2 && _height > 0) {
          _height--;
        }
      }
      
      Future.delayed(const Duration(milliseconds: 400), () {
        if (mounted) {
          setState(() {
            _feedback = '';
          });
        }
      });
    });
  }
  
  void _resetGame() {
    setState(() {
      _height = 0;
      _gameWon = false;
      _feedback = '';
      _consecutiveMisses = 0;
    });
    _noteController.repeat();
  }
  
  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return _buildWinScreen('REACHED THE TOP!', Icons.check_circle, _resetGame);
    }
    
    return Column(
      children: [
        _buildStatsBar(
          'Height: $_height / $_targetHeight',
          'Miss Streak: $_consecutiveMisses',
        ),
        const SizedBox(height: 20),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            children: [
              const Text(
                'Tap when the note hits the target line!\n⚠️ Target moves after each hit!',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.white60, height: 1.5),
              ),
              const SizedBox(height: 8),
              if (_feedback.isNotEmpty)
                Text(
                  _feedback,
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: _feedback.contains('PERFECT') ? Colors.green : Colors.red,
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        // Guitar Hero style note highway
        Expanded(
          child: Container(
            width: 120,
            margin: const EdgeInsets.symmetric(horizontal: 40),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.5),
              border: Border.all(color: Colors.white24, width: 2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Stack(
              children: [
                // Target line (where to hit)
                Positioned(
                  top: MediaQuery.of(context).size.height * 0.4 * _targetLinePosition,
                  left: 0,
                  right: 0,
                  child: Container(
                    height: 60,
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.3),
                      border: Border.all(color: Colors.green, width: 3),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Center(
                      child: Text(
                        'TAP HERE',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ),
                // Moving note
                AnimatedBuilder(
                  animation: _noteController,
                  builder: (context, child) {
                    return Positioned(
                      top: MediaQuery.of(context).size.height * 0.4 * _noteController.value,
                      left: 0,
                      right: 0,
                      child: Center(
                        child: Container(
                          width: 50,
                          height: 50,
                          decoration: BoxDecoration(
                            color: Colors.cyan,
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.white, width: 2),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.cyan.withOpacity(0.6),
                                blurRadius: 15,
                                spreadRadius: 3,
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.music_note,
                            color: Colors.white,
                            size: 24,
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        // Height indicator
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.stairs, color: Colors.white70),
            const SizedBox(width: 8),
            Text(
              'Height: $_height / $_targetHeight',
              style: const TextStyle(
                fontSize: 18,
                color: Colors.white70,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        // Progress bar
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 40),
          child: LinearProgressIndicator(
            value: _height / _targetHeight,
            minHeight: 10,
            backgroundColor: Colors.grey.shade800,
            valueColor: AlwaysStoppedAnimation<Color>(
              _height >= _targetHeight * 0.7 ? Colors.green : Colors.cyan,
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(30),
          child: GestureDetector(
            onTap: _onTap,
            child: Container(
              width: 200,
              height: 80,
              decoration: BoxDecoration(
                color: const Color(0xFF16213e),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.cyan, width: 2),
                boxShadow: [
                  BoxShadow(
                    color: Colors.cyan.withOpacity(0.3),
                    blurRadius: 15,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: const Center(
                child: Text(
                  'TAP!',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

// ============================================
// 9. LOGIC CLUES MINIGAME (Mastermind)
// ============================================
class LogicCluesMinigame extends StatefulWidget {
  const LogicCluesMinigame({super.key});

  @override
  State<LogicCluesMinigame> createState() => _LogicCluesMinigameState();
}

class _LogicCluesMinigameState extends State<LogicCluesMinigame> {
  late List<String> _currentOrder; // Current arrangement
  late List<String> _correctOrder; // Correct arrangement
  late List<String> _clues; // Clues to show
  bool _gameWon = false;
  int _attempts = 0;
  
  final Map<String, Color> _itemColors = {
    'Red': Colors.red,
    'Blue': Colors.blue,
    'Green': Colors.green,
    'Yellow': Colors.yellow,
  };
  
  @override
  void initState() {
    super.initState();
    _resetGame();
  }
  
  void _resetGame() {
    setState(() {
      // Set correct order
      _correctOrder = ['Red', 'Blue', 'Yellow', 'Green'];
      // Randomize starting order
      _currentOrder = List.from(_correctOrder)..shuffle();
      _gameWon = false;
      _attempts = 0;
      
      // Generate clues based on correct order
      _clues = [
        'Red is left of Blue',
        'Yellow is between Blue and Green',
        'Green is at the far right',
      ];
    });
  }
  
  void _checkSolution() {
    setState(() {
      _attempts++;
      if (_listEquals(_currentOrder, _correctOrder)) {
        _gameWon = true;
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
      return _buildWinScreen('SOLVED!', Icons.psychology, _resetGame);
    }
    
    return Column(
      children: [
        _buildStatsBar(
          'Attempts: $_attempts',
          'Arrange 4 boxes',
        ),
        const SizedBox(height: 20),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'Use the clues to arrange the boxes in correct order',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, color: Colors.white60, height: 1.5),
          ),
        ),
        const SizedBox(height: 20),
        // Clues section
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 20),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF2a2a3e),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.cyan.withOpacity(0.3), width: 2),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.lightbulb_outline, color: Colors.cyan, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'CLUES:',
                    style: TextStyle(
                      color: Colors.cyan,
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
                    const Text('• ', style: TextStyle(color: Colors.white70, fontSize: 16)),
                    Expanded(
                      child: Text(
                        clue,
                        style: const TextStyle(color: Colors.white70, fontSize: 14),
                      ),
                    ),
                  ],
                ),
              )).toList(),
            ],
          ),
        ),
        const SizedBox(height: 40),
        // Draggable boxes
        Expanded(
          child: Center(
            child: ReorderableListView(
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
              children: _currentOrder.map((item) {
                return Container(
                  key: ValueKey(item),
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
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.drag_handle, color: Colors.white, size: 24),
                        const SizedBox(height: 4),
                        Text(
                          item,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
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
              backgroundColor: const Color(0xFF16213e),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              textStyle: const TextStyle(fontSize: 18),
            ),
          ),
        ),
      ],
    );
  }
}

// ============================================
// SHARED UI COMPONENTS
// ============================================

Widget _buildStatsBar(String left, String right) {
  return Container(
    padding: const EdgeInsets.all(16),
    color: const Color(0xFF16213e),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(left, style: const TextStyle(fontSize: 18, color: Colors.white70)),
        Text(right, style: const TextStyle(fontSize: 18, color: Colors.white70)),
      ],
    ),
  );
}

Widget _buildWinScreen(String message, IconData icon, VoidCallback onReset) {
  return Center(
    child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, size: 120, color: Colors.green),
        const SizedBox(height: 24),
        Text(
          message,
          style: const TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.bold,
            color: Colors.green,
          ),
        ),
        const SizedBox(height: 40),
        ElevatedButton.icon(
          onPressed: onReset,
          icon: const Icon(Icons.refresh),
          label: const Text('Play Again'),
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF16213e),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            textStyle: const TextStyle(fontSize: 18),
          ),
        ),
      ],
    ),
  );
}

Widget _buildFailScreen(VoidCallback onReset) {
  return Center(
    child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Icon(Icons.error_outline, size: 120, color: Colors.red),
        const SizedBox(height: 24),
        const Text(
          'FAILED!',
          style: TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.bold,
            color: Colors.red,
          ),
        ),
        const SizedBox(height: 16),
        const Text(
          'Try again!',
          style: TextStyle(fontSize: 18, color: Colors.white70),
        ),
        const SizedBox(height: 40),
        ElevatedButton.icon(
          onPressed: onReset,
          icon: const Icon(Icons.refresh),
          label: const Text('Retry'),
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF16213e),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            textStyle: const TextStyle(fontSize: 18),
          ),
        ),
      ],
    ),
  );
}
