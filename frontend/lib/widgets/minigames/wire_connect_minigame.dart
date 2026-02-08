import 'dart:math';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

class WireConnectMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;
  
  const WireConnectMinigame({super.key, required this.difficulty});

  @override
  State<WireConnectMinigame> createState() => _WireConnectMinigameState();
}

class _WireConnectMinigameState extends State<WireConnectMinigame> {
  late List<WireFull> _leftWires;
  late List<PortType> _rightPorts;
  late int _wireCount;
  
  final Map<int, int> _connections = {};
  final Map<int, bool> _wrongAttempts = {};
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
      
      // Difficulty: number of wires
      switch (widget.difficulty) {
        case MinigameDifficulty.easy:
          _wireCount = 3;
          break;
        case MinigameDifficulty.medium:
          _wireCount = 5;
          break;
        case MinigameDifficulty.hard:
          _wireCount = 7;
          break;
      }
      
      // Wire definitions
      final allWires = [
        WireFull(Colors.red, Icons.star, 'Red Star'),
        WireFull(Colors.blue, Icons.circle, 'Blue Circle'),
        WireFull(Colors.green, Icons.square, 'Green Square'),
        WireFull(Colors.purple, Icons.favorite, 'Purple Heart'),
        WireFull(Colors.orange, Icons.hexagon, 'Orange Hex'),
        WireFull(Colors.cyan, Icons.diamond, 'Cyan Diamond'),
        WireFull(Colors.yellow, Icons.change_history, 'Yellow Triangle'),
      ];
      
      _leftWires = allWires.sublist(0, _wireCount);
      
      // Create right ports
      final decisions = List.generate(_wireCount, (i) => i);
      decisions.shuffle();
      
      _rightPorts = [];
      for (int i = 0; i < _wireCount; i++) {
        final wireIndex = decisions[i];
        final wire = _leftWires[wireIndex];
        final matchByColor = Random().nextBool();
        
        _rightPorts.add(PortType(
          wireIndex: wireIndex,
          color: matchByColor ? wire.color : Colors.grey.shade700,
          icon: matchByColor ? null : wire.icon,
          matchType: matchByColor ? 'color' : 'symbol',
        ));
      }
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
    
    final rightPort = _rightPorts[portIndex];
    
    setState(() {
      if (rightPort.wireIndex == _selectedLeftWire) {
        _connections.removeWhere((key, value) => value == portIndex);
        _connections[_selectedLeftWire!] = portIndex;
        _feedback = '✓ Connected!';
        
        Future.delayed(const Duration(milliseconds: 800), () {
          if (mounted) {
            setState(() {
              _feedback = '';
            });
          }
        });
        
        if (_connections.length == _wireCount) {
          _gameWon = true;
        }
      } else {
        _feedback = '✗ No match! Try another.';
        _wrongAttempts[portIndex] = true;
        
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
      return buildWinScreen('CONNECTED!', Icons.check_circle, _resetGame);
    }
    
    return Column(
      children: [
        buildStatsBar(
          'Connected: ${_connections.length} / $_wireCount',
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
                style: TextStyle(fontSize: 14, color: AppColors.textSecondary, height: 1.5),
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
                      color: _feedback.contains('✓') ? AppColors.success : AppColors.danger,
                    ),
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: 40),
        Expanded(
          child: Center(
            child: SingleChildScrollView(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // Left wires
                  Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(_wireCount, (wireIndex) {
                      return _buildLeftWire(wireIndex);
                    }),
                  ),
                  // Wires visualization
                  SizedBox(
                    width: 100,
                    height: _wireCount * 94.0,
                    child: CustomPaint(
                      painter: WireConnectPainter(_connections, _leftWires, _rightPorts, _selectedLeftWire),
                    ),
                  ),
                  // Right ports
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
                ? AppColors.danger.withOpacity(0.3)
                : (isConnected 
                    ? port.color 
                    : port.color.withOpacity(0.3)),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isWrongAttempt ? AppColors.danger : port.color,
              width: 3,
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

// Data models
class WireFull {
  final Color color;
  final IconData icon;
  final String name;
  
  WireFull(this.color, this.icon, this.name);
}

class PortType {
  final int wireIndex;
  final Color color;
  final IconData? icon;
  final String matchType;
  
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
    
    connections.forEach((leftIndex, rightPortIndex) {
      paint.color = leftWires[leftIndex].color;
      final startY = 47.0 + (leftIndex * 94);
      final endY = 47.0 + (rightPortIndex * 94);
      
      final path = Path();
      path.moveTo(0, startY);
      path.cubicTo(
        size.width * 0.3, startY,
        size.width * 0.7, endY,
        size.width, endY,
      );
      canvas.drawPath(path, paint);
    });
    
    if (selectedLeftWire != null) {
      paint.color = leftWires[selectedLeftWire!].color.withOpacity(0.5);
      paint.strokeWidth = 2;
      final startY = 47.0 + (selectedLeftWire! * 94);
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
