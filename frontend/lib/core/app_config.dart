/// Global app configuration
/// Set debugMode to true for development features:
/// - Prepopulated player names
/// - Fit score badges on quick responses
/// - Debug logging
class AppConfig {
  /// Enable debug features (prepopulated names, fit scores, etc.)
  static const bool debugMode = false;

  /// Default player names in debug mode
  static const String debugMastermindName = 'Mike MM';
  static const String debugSafeCrackerName = 'Sally SC';
}
