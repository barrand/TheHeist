import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

/// Service for room-related REST API calls
class RoomService {
  final String baseUrl;
  
  RoomService({this.baseUrl = 'http://localhost:8000'});
  
  /// Create a new room
  Future<Map<String, dynamic>> createRoom(String hostName) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/rooms/create'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'host_name': hostName}),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        debugPrint('✅ Room created: ${data['room_code']}');
        return data;
      } else {
        debugPrint('❌ Failed to create room: ${response.statusCode}');
        throw Exception('Failed to create room: ${response.body}');
      }
    } catch (e) {
      debugPrint('❌ Error creating room: $e');
      rethrow;
    }
  }
  
  /// Get room information
  Future<Map<String, dynamic>> getRoomInfo(String roomCode) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/rooms/$roomCode'),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        debugPrint('✅ Got room info: $roomCode');
        return data;
      } else if (response.statusCode == 404) {
        throw Exception('Room not found');
      } else {
        throw Exception('Failed to get room info: ${response.body}');
      }
    } catch (e) {
      debugPrint('❌ Error getting room info: $e');
      rethrow;
    }
  }
  
  /// Check if room exists and is joinable
  Future<bool> canJoinRoom(String roomCode) async {
    try {
      final roomInfo = await getRoomInfo(roomCode);
      return roomInfo['is_joinable'] == true;
    } catch (e) {
      return false;
    }
  }
}
