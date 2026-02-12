/// Global app configuration
/// Set debugMode to true for development features:
/// - Prepopulated player names
/// - Fit score badges on quick responses
/// - Debug logging
class AppConfig {
  /// Enable debug features (prepopulated names, fit scores, etc.)
  static const bool debugMode = true;

  /// Default player names in debug mode
  static const String debugMastermindName = 'Mike MM';
  static const String debugSafeCrackerName = 'Sally SC';
  
  /// Backend URL for HTTP requests
  /// Note: WebSocket URL is managed separately in WebSocketService
  static const String backendUrl = 'http://localhost:8000';
}
