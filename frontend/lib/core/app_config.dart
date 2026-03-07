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

  /// Backend URL for HTTP requests.
  /// Set at build time via --dart-define=BACKEND_URL=https://...
  /// Falls back to localhost for local development.
  static const String backendUrl = String.fromEnvironment(
    'BACKEND_URL',
    defaultValue: 'http://localhost:8000',
  );

  /// WebSocket URL derived from backendUrl (http->ws, https->wss).
  static String get wsUrl {
    if (backendUrl.startsWith('https://')) {
      return backendUrl.replaceFirst('https://', 'wss://');
    }
    return backendUrl.replaceFirst('http://', 'ws://');
  }
}
