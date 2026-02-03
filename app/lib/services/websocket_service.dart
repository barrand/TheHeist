import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter/foundation.dart';

/// WebSocket service for real-time multiplayer communication
class WebSocketService {
  WebSocketChannel? _channel;
  final String baseUrl;
  String? _roomCode;
  String? _playerId;
  
  // Message handlers
  final _messageController = StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get messages => _messageController.stream;
  
  // Connection state
  bool _isConnected = false;
  bool get isConnected => _isConnected;
  
  // Specific message type streams
  final _roomStateController = StreamController<Map<String, dynamic>>.broadcast();
  final _playerJoinedController = StreamController<Map<String, dynamic>>.broadcast();
  final _roleSelectedController = StreamController<Map<String, dynamic>>.broadcast();
  final _gameStartedController = StreamController<Map<String, dynamic>>.broadcast();
  final _taskCompletedController = StreamController<Map<String, dynamic>>.broadcast();
  final _taskUnlockedController = StreamController<Map<String, dynamic>>.broadcast();
  final _errorController = StreamController<Map<String, dynamic>>.broadcast();
  
  // Store the latest room state for late subscribers
  Map<String, dynamic>? _latestRoomState;
  
  Stream<Map<String, dynamic>> get roomState => _roomStateController.stream;
  Stream<Map<String, dynamic>> get playerJoined => _playerJoinedController.stream;
  Stream<Map<String, dynamic>> get roleSelected => _roleSelectedController.stream;
  Stream<Map<String, dynamic>> get gameStarted => _gameStartedController.stream;
  Stream<Map<String, dynamic>> get taskCompleted => _taskCompletedController.stream;
  Stream<Map<String, dynamic>> get taskUnlocked => _taskUnlockedController.stream;
  Stream<Map<String, dynamic>> get errors => _errorController.stream;
  
  // Get the latest room state (useful for late subscribers)
  Map<String, dynamic>? get latestRoomState => _latestRoomState;
  
  WebSocketService({this.baseUrl = 'ws://localhost:8000'});
  
  /// Connect to a room's WebSocket
  Future<void> connect(String roomCode, String playerName) async {
    if (_isConnected) {
      await disconnect();
    }
    
    try {
      _roomCode = roomCode;
      final wsUrl = '$baseUrl/ws/$roomCode';
      
      debugPrint('🔌 Connecting to WebSocket: $wsUrl');
      
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _isConnected = true;
      
      // Listen to messages
      _channel!.stream.listen(
        (message) {
          _handleMessage(message);
        },
        onError: (error) {
          debugPrint('❌ WebSocket error: $error');
          _isConnected = false;
        },
        onDone: () {
          debugPrint('🔌 WebSocket disconnected');
          _isConnected = false;
        },
      );
      
      // Send join message
      await Future.delayed(const Duration(milliseconds: 100));
      send({
        'type': 'join_room',
        'room_code': roomCode,
        'player_name': playerName,
      });
      
      debugPrint('✅ WebSocket connected');
    } catch (e) {
      debugPrint('❌ Failed to connect: $e');
      _isConnected = false;
      rethrow;
    }
  }
  
  /// Disconnect from WebSocket
  Future<void> disconnect() async {
    if (_channel != null) {
      await _channel!.sink.close();
      _channel = null;
      _isConnected = false;
      _roomCode = null;
      _playerId = null;
      debugPrint('🔌 WebSocket disconnected');
    }
  }
  
  /// Send a message to the server
  void send(Map<String, dynamic> message) {
    if (!_isConnected || _channel == null) {
      debugPrint('❌ Cannot send - not connected');
      return;
    }
    
    try {
      _channel!.sink.add(json.encode(message));
      debugPrint('📤 Sent: ${message['type']}');
    } catch (e) {
      debugPrint('❌ Error sending message: $e');
    }
  }
  
  /// Select a role in lobby
  void selectRole(String role) {
    debugPrint('🎭 WS: Sending select_role with role: $role');
    send({
      'type': 'select_role',
      'role': role,
    });
  }
  
  /// Start game (host only)
  void startGame(String scenario) {
    send({
      'type': 'start_game',
      'scenario': scenario,
    });
  }
  
  /// Complete a task
  void completeTask(String taskId) {
    send({
      'type': 'complete_task',
      'task_id': taskId,
    });
  }
  
  /// Send NPC message
  void sendNPCMessage(String taskId, String npcId, String message) {
    send({
      'type': 'npc_message',
      'task_id': taskId,
      'npc_id': npcId,
      'message': message,
    });
  }
  
  /// Move to new location
  void moveLocation(String location) {
    send({
      'type': 'move_location',
      'location': location,
    });
  }
  
  /// Hand off item to another player
  void handoffItem(String itemId, String toPlayerId) {
    send({
      'type': 'handoff_item',
      'item_id': itemId,
      'to_player_id': toPlayerId,
    });
  }
  
  /// Handle incoming messages
  void _handleMessage(dynamic rawMessage) {
    try {
      final Map<String, dynamic> message = json.decode(rawMessage);
      final String type = message['type'] ?? 'unknown';
      
      debugPrint('📥 WS: Received message type: $type');
      if (type == 'role_selected') {
        debugPrint('📥 WS: role_selected full message: $message');
      }
      
      // Emit to general stream
      _messageController.add(message);
      
      // Route to specific streams
      switch (type) {
        case 'room_state':
          _playerId = message['your_player_id'];
          _latestRoomState = message; // Store for late subscribers
          debugPrint('📥 WS: Room state received, my player ID: $_playerId');
          debugPrint('📥 WS: is_host value: ${message['is_host']}');
          _roomStateController.add(message);
          break;
        case 'player_joined':
          debugPrint('📥 WS: Player joined: ${message['player']}');
          _playerJoinedController.add(message);
          break;
        case 'role_selected':
          debugPrint('📥 WS: Emitting to roleSelectedController stream');
          _roleSelectedController.add(message);
          debugPrint('📥 WS: role_selected emitted to stream');
          break;
        case 'game_started':
          _gameStartedController.add(message);
          break;
        case 'task_completed':
          _taskCompletedController.add(message);
          break;
        case 'task_unlocked':
          _taskUnlockedController.add(message);
          break;
        case 'error':
          _errorController.add(message);
          debugPrint('❌ Error from server: ${message['message']}');
          break;
        default:
          debugPrint('⚠️ Unknown message type: $type');
      }
    } catch (e) {
      debugPrint('❌ Error handling message: $e');
    }
  }
  
  /// Get current player ID
  String? get playerId => _playerId;
  
  /// Get current room code
  String? get roomCode => _roomCode;
  
  /// Dispose and clean up
  void dispose() {
    disconnect();
    _messageController.close();
    _roomStateController.close();
    _playerJoinedController.close();
    _roleSelectedController.close();
    _gameStartedController.close();
    _taskCompletedController.close();
    _taskUnlockedController.close();
    _errorController.close();
  }
}
