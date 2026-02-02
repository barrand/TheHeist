import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_dimensions.dart';
import '../widgets/common/heist_primary_button.dart';
import '../widgets/common/heist_secondary_button.dart';
import '../widgets/common/heist_text_field.dart';
import '../services/room_service.dart';
import '../services/websocket_service.dart';
import 'npc_test_screen.dart';
import 'room_lobby_screen.dart';

/// Landing Page - First screen of the app
/// Users can create a new room or join an existing one
class LandingPage extends StatefulWidget {
  const LandingPage({Key? key}) : super(key: key);

  @override
  State<LandingPage> createState() => _LandingPageState();
}

class _LandingPageState extends State<LandingPage> {
  final RoomService _roomService = RoomService();
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _roomCodeController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _nameController.dispose();
    _roomCodeController.dispose();
    super.dispose();
  }

  Future<void> _onCreateRoom(BuildContext context) async {
    // Show dialog to enter name
    final name = await _showNameDialog(context, 'Create Room');
    if (name == null || name.isEmpty) return;

    setState(() => _isLoading = true);

    try {
      // Create room via REST API
      final roomData = await _roomService.createRoom(name);
      final roomCode = roomData['room_code'];
      final playerId = roomData['player_id'];

      // Connect to WebSocket
      final wsService = WebSocketService();
      await wsService.connect(roomCode, name);

      // Navigate to lobby
      if (context.mounted) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => RoomLobbyScreen(
              roomCode: roomCode,
              playerName: name,
              wsService: wsService,
            ),
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        _showError(context, 'Failed to create room: $e');
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _onJoinRoom(BuildContext context) async {
    // Show dialog to enter room code and name
    final result = await _showJoinDialog(context);
    if (result == null) return;

    final roomCode = result['roomCode'] as String;
    final name = result['name'] as String;

    setState(() => _isLoading = true);

    try {
      // Check if room exists and is joinable
      final canJoin = await _roomService.canJoinRoom(roomCode);
      if (!canJoin) {
        throw Exception('Room not found or already started');
      }

      // Connect to WebSocket
      final wsService = WebSocketService();
      await wsService.connect(roomCode, name);

      // Navigate to lobby
      if (context.mounted) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => RoomLobbyScreen(
              roomCode: roomCode,
              playerName: name,
              wsService: wsService,
            ),
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        _showError(context, 'Failed to join room: $e');
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<String?> _showNameDialog(BuildContext context, String title) async {
    final controller = TextEditingController();
    
    return showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.bgSecondary,
        title: Text(
          title,
          style: TextStyle(color: AppColors.textPrimary),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Enter your name:',
              style: TextStyle(color: AppColors.textSecondary),
            ),
            SizedBox(height: AppDimensions.spaceMD),
            HeistTextField(
              controller: controller,
              hintText: 'Your Name',
              maxLines: 1,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel', style: TextStyle(color: AppColors.textSecondary)),
          ),
          ElevatedButton(
            onPressed: () {
              final name = controller.text.trim();
              if (name.isNotEmpty) {
                Navigator.pop(context, name);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.accentPrimary,
            ),
            child: Text('Continue', style: TextStyle(color: AppColors.textPrimary)),
          ),
        ],
      ),
    );
  }

  Future<Map<String, String>?> _showJoinDialog(BuildContext context) async {
    final roomCodeController = TextEditingController();
    final nameController = TextEditingController();
    
    return showDialog<Map<String, String>>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.bgSecondary,
        title: Text(
          'Join Room',
          style: TextStyle(color: AppColors.textPrimary),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            HeistTextField(
              controller: roomCodeController,
              hintText: 'Room Code (e.g., 4S2X)',
              maxLines: 1,
            ),
            SizedBox(height: AppDimensions.spaceMD),
            HeistTextField(
              controller: nameController,
              hintText: 'Your Name',
              maxLines: 1,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel', style: TextStyle(color: AppColors.textSecondary)),
          ),
          ElevatedButton(
            onPressed: () {
              final roomCode = roomCodeController.text.trim().toUpperCase();
              final name = nameController.text.trim();
              if (roomCode.isNotEmpty && name.isNotEmpty) {
                Navigator.pop(context, {'roomCode': roomCode, 'name': name});
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.accentPrimary,
            ),
            child: Text('Join', style: TextStyle(color: AppColors.textPrimary)),
          ),
        ],
      ),
    );
  }

  void _showError(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.danger,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _onTestNPC(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => NPCTestScreen()),
    );
  }

  void _onHowToPlay(BuildContext context) {
    // TODO: Show How to Play modal
    print('How to Play tapped');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      body: _isLoading
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: AppColors.accentPrimary),
                  SizedBox(height: AppDimensions.spaceMD),
                  Text(
                    'Connecting...',
                    style: TextStyle(color: AppColors.textSecondary),
                  ),
                ],
              ),
            )
          : SafeArea(
        child: Container(
          constraints: BoxConstraints(
            maxWidth: AppDimensions.maxWidthMobile,
          ),
          margin: EdgeInsets.symmetric(
            horizontal: AppDimensions.containerPadding,
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Spacer(flex: 2),
              
              // App Title
              Text(
                'THE HEIST 🎭',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                  letterSpacing: 2,
                ),
              ),
              
              SizedBox(height: AppDimensions.spaceMD),
              
              // Tagline
              Text(
                'Collaborative Heist Game',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  color: AppColors.textSecondary,
                  letterSpacing: 0.5,
                ),
              ),
              
              SizedBox(height: AppDimensions.space3XL),
              
              // Create Room Button
              HeistPrimaryButton(
                text: 'CREATE ROOM',
                icon: Icons.add_circle_outline,
                onPressed: () => _onCreateRoom(context),
              ),
              
              SizedBox(height: AppDimensions.spaceLG),
              
              // Join Room Button
              HeistSecondaryButton(
                text: 'JOIN ROOM',
                icon: Icons.login,
                onPressed: () => _onJoinRoom(context),
              ),
              
              SizedBox(height: AppDimensions.spaceLG),
              
              // Test NPC Button (for development)
              HeistSecondaryButton(
                text: 'TEST NPC CONVERSATION',
                icon: Icons.chat_bubble_outline,
                onPressed: () => _onTestNPC(context),
              ),
              
              Spacer(flex: 3),
              
              // How to Play Link
              TextButton(
                onPressed: () => _onHowToPlay(context),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'How to Play',
                      style: TextStyle(
                        color: AppColors.textSecondary,
                        fontSize: 14,
                      ),
                    ),
                    SizedBox(width: AppDimensions.spaceXS),
                    Icon(
                      Icons.info_outline,
                      color: AppColors.textSecondary,
                      size: AppDimensions.iconMD,
                    ),
                  ],
                ),
              ),
              
              SizedBox(height: AppDimensions.spaceSM),
              
              // Version number
              Text(
                'v0.1.0',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 10,
                  color: AppColors.textTertiary,
                ),
              ),
              
              SizedBox(height: AppDimensions.spaceLG),
            ],
          ),
        ),
      ),
    );
  }
}
