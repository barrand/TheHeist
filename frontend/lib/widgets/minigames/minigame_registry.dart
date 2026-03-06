import 'package:flutter/material.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/lockpick_minigame.dart';
import 'package:the_heist/widgets/minigames/dial_safe_minigame.dart';
import 'package:the_heist/widgets/minigames/simon_says_minigame.dart';
import 'package:the_heist/widgets/minigames/wire_connect_minigame.dart';
import 'package:the_heist/widgets/minigames/card_swipe_minigame.dart';
import 'package:the_heist/widgets/minigames/button_mash_minigame.dart';
import 'package:the_heist/widgets/minigames/timing_tap_minigame.dart';
import 'package:the_heist/widgets/minigames/rhythm_climb_minigame.dart';
import 'package:the_heist/widgets/minigames/logic_clues_minigame.dart';
import 'package:the_heist/widgets/minigames/doodle_climb_minigame.dart';
import 'package:the_heist/widgets/minigames/tag_evidence_minigame.dart';
import 'package:the_heist/widgets/minigames/wipe_prints_minigame.dart';
import 'package:the_heist/widgets/minigames/item_matching_minigame.dart';
import 'package:the_heist/widgets/minigames/steering_obstacle_minigame.dart';
import 'package:the_heist/widgets/minigames/fuel_pump_minigame.dart';
import 'package:the_heist/widgets/minigames/whack_a_threat_minigame.dart';
import 'package:the_heist/widgets/minigames/emotion_matching_minigame.dart';
import 'package:the_heist/widgets/minigames/pocket_grab_minigame.dart';

/// Single source of truth for all minigame metadata and widget builders.
///
/// Two responsibilities:
///   1. [builders] — maps every implemented minigame ID to a builder function.
///      Used by the game screen to launch a real minigame, and by the hub to
///      know which entries are playable.
///   2. [allByRole] — full metadata list including un-implemented games.
///      Used by the hub to display TODO badges for future games.
class MinigameRegistry {
  MinigameRegistry._();

  // ---------------------------------------------------------------------------
  // Builder map — only implemented games
  // ---------------------------------------------------------------------------

  static final Map<String, Widget Function(MinigameDifficulty, {VoidCallback? onSuccess})>
      builders = {
    'lockpick_timing': (d, {onSuccess}) =>
        LockpickMinigame(difficulty: d, onSuccess: onSuccess),
    'dial_rotation': (d, {onSuccess}) =>
        DialSafeMinigame(difficulty: d, onSuccess: onSuccess),
    'simon_says_sequence': (d, {onSuccess}) =>
        SimonSaysMinigame(difficulty: d, onSuccess: onSuccess),
    'wire_connecting': (d, {onSuccess}) =>
        WireConnectMinigame(difficulty: d, onSuccess: onSuccess),
    'badge_swipe': (d, {onSuccess}) =>
        CardSwipeMinigame(difficulty: d, onSuccess: onSuccess),
    'button_mash_barrier': (d, {onSuccess}) =>
        ButtonMashMinigame(difficulty: d, onSuccess: onSuccess),
    'timing_tap': (d, {onSuccess}) =>
        TimingTapMinigame(difficulty: d, onSuccess: onSuccess),
    'climbing_rhythm': (d, {onSuccess}) =>
        RhythmClimbMinigame(difficulty: d, onSuccess: onSuccess),
    'logic_clues': (d, {onSuccess}) =>
        LogicCluesMinigame(difficulty: d, onSuccess: onSuccess),
    'doodle_climb': (d, {onSuccess}) =>
        DoodleClimbMinigame(difficulty: d, onSuccess: onSuccess),
    'tap_evidence_markers': (d, {onSuccess}) =>
        TagEvidenceMinigame(difficulty: d, onSuccess: onSuccess),
    'swipe_fingerprints': (d, {onSuccess}) =>
        WipePrintsMinigame(difficulty: d, onSuccess: onSuccess),
    'item_matching': (d, {onSuccess}) =>
        ItemMatchingMinigame(difficulty: d, onSuccess: onSuccess),
    'steering_obstacle_course': (d, {onSuccess}) =>
        SteeringObstacleMinigame(difficulty: d, onSuccess: onSuccess),
    'fuel_pump': (d, {onSuccess}) =>
        FuelPumpMinigame(difficulty: d, onSuccess: onSuccess),
    'whack_a_mole_threats': (d, {onSuccess}) =>
        WhackAThreatMinigame(difficulty: d, onSuccess: onSuccess),
    'emotion_matching': (d, {onSuccess}) =>
        EmotionMatchingMinigame(difficulty: d, onSuccess: onSuccess),
    'pocket_grab': (d, {onSuccess}) =>
        PocketGrabMinigame(difficulty: d, onSuccess: onSuccess),
  };

  /// Returns true if a widget exists for [id].
  static bool isImplemented(String id) => builders.containsKey(id);

  /// Builds the minigame widget for [id].
  /// Pass [onSuccess] to wire task-completion in the real game.
  /// In the standalone hub/prototype, omit [onSuccess] (defaults to null).
  static Widget build(
    String id,
    MinigameDifficulty difficulty, {
    VoidCallback? onSuccess,
  }) {
    final builder = builders[id];
    assert(builder != null, 'No builder registered for minigame id: $id');
    return builder!(difficulty, onSuccess: onSuccess);
  }

  // ---------------------------------------------------------------------------
  // Full metadata list — all roles including un-implemented games
  // Used by MinigameHubScreen to show TODO badges.
  // ---------------------------------------------------------------------------

  static const List<RoleMinigames> allByRole = [
    RoleMinigames(
      roleId: 'mastermind',
      name: 'Mastermind',
      minigames: [
        MinigameInfo(
          id: 'logic_clues',
          name: 'Logic Clues',
          description: 'Arrange boxes using clues',
          roleId: 'mastermind',
        ),
      ],
    ),
    RoleMinigames(
      roleId: 'hacker',
      name: 'Hacker',
      minigames: [
        MinigameInfo(
          id: 'wire_connecting',
          name: 'Wire Connect',
          description: 'Match wires by color or symbol',
          roleId: 'hacker',
        ),
        MinigameInfo(
          id: 'simon_says_sequence',
          name: 'Simon Says',
          description: 'Memorize and repeat pattern',
          roleId: 'hacker',
        ),
        MinigameInfo(
          id: 'cipher_wheel_alignment',
          name: 'Cipher Wheel',
          description: 'Align spinning symbols',
          roleId: 'hacker',
        ),
        MinigameInfo(
          id: 'card_swipe',
          name: 'Card Swipe',
          description: 'Swipe keycard at right speed',
          roleId: 'hacker',
        ),
      ],
    ),
    RoleMinigames(
      roleId: 'safe_cracker',
      name: 'Safe Cracker',
      minigames: [
        MinigameInfo(
          id: 'dial_rotation',
          name: 'Dial Safe',
          description: 'Rotate dial to target numbers',
          roleId: 'safe_cracker',
        ),
        MinigameInfo(
          id: 'lockpick_timing',
          name: 'Lockpick',
          description: 'Position pins correctly',
          roleId: 'safe_cracker',
        ),
        MinigameInfo(
          id: 'listen_for_clicks',
          name: 'Listen for Clicks',
          description: 'Audio-based safecracking',
          roleId: 'safe_cracker',
        ),
      ],
    ),
    RoleMinigames(
      roleId: 'driver',
      name: 'Driver',
      minigames: [
        MinigameInfo(
          id: 'steering_obstacle_course',
          name: 'Obstacle Course',
          description: 'Avoid obstacles while driving',
          roleId: 'driver',
        ),
        MinigameInfo(
          id: 'fuel_pump',
          name: 'Fuel Pump',
          description: 'Fill tank without overflow',
          roleId: 'driver',
        ),
        MinigameInfo(
          id: 'parking_precision',
          name: 'Precision Park',
          description: 'Brake at perfect moment',
          roleId: 'driver',
        ),
      ],
    ),
    RoleMinigames(
      roleId: 'insider',
      name: 'Insider',
      minigames: [
        MinigameInfo(
          id: 'badge_swipe',
          name: 'Badge Swipe',
          description: 'Swipe at correct speed',
          roleId: 'insider',
        ),
        MinigameInfo(
          id: 'memory_matching',
          name: 'Memory Match',
          description: 'Remember access codes',
          roleId: 'insider',
        ),
        MinigameInfo(
          id: 'inventory_check',
          name: 'Inventory Check',
          description: 'Find items before timeout',
          roleId: 'insider',
        ),
      ],
    ),
    RoleMinigames(
      roleId: 'grifter',
      name: 'Grifter',
      minigames: [
        MinigameInfo(
          id: 'timed_dialogue_choices',
          name: 'Dialogue Choice',
          description: 'Pick response before timeout',
          roleId: 'grifter',
        ),
        MinigameInfo(
          id: 'emotion_matching',
          name: 'Emotion Match',
          description: 'Match facial expression',
          roleId: 'grifter',
        ),
        MinigameInfo(
          id: 'convincing_sequence',
          name: 'Be Convincing',
          description: 'Tap in rhythm to persuade',
          roleId: 'grifter',
        ),
      ],
    ),
    RoleMinigames(
      roleId: 'muscle',
      name: 'Muscle',
      minigames: [
        MinigameInfo(
          id: 'takedown_timing',
          name: 'Stealth Takedown',
          description: 'Tap at perfect moment',
          roleId: 'muscle',
        ),
        MinigameInfo(
          id: 'button_mash_barrier',
          name: 'Button Mash',
          description: 'Tap rapidly to break through',
          roleId: 'muscle',
        ),
        MinigameInfo(
          id: 'reaction_time',
          name: 'Quick React',
          description: 'Tap immediately when prompted',
          roleId: 'muscle',
        ),
      ],
    ),
    RoleMinigames(
      roleId: 'lookout',
      name: 'Lookout',
      minigames: [
        MinigameInfo(
          id: 'spot_the_difference',
          name: 'Spot Difference',
          description: 'Find anomalies in feeds',
          roleId: 'lookout',
        ),
        MinigameInfo(
          id: 'whack_a_mole_threats',
          name: 'Whack-a-Threat',
          description: 'Tap threats on camera feeds',
          roleId: 'lookout',
        ),
        MinigameInfo(
          id: 'pattern_memorization',
          name: 'Guard Pattern',
          description: 'Memorize patrol routes',
          roleId: 'lookout',
        ),
      ],
    ),
    RoleMinigames(
      roleId: 'fence',
      name: 'Fence',
      minigames: [
        MinigameInfo(
          id: 'item_matching',
          name: 'Item Match',
          description: 'Match items to buyers',
          roleId: 'fence',
        ),
        MinigameInfo(
          id: 'haggling_slider',
          name: 'Haggle',
          description: 'Stop slider at best price',
          roleId: 'fence',
        ),
        MinigameInfo(
          id: 'quality_inspection',
          name: 'Quality Check',
          description: 'Find defects in forgery',
          roleId: 'fence',
        ),
      ],
    ),
    RoleMinigames(
      roleId: 'cat_burglar',
      name: 'Cat Burglar',
      minigames: [
        MinigameInfo(
          id: 'climbing_rhythm',
          name: 'Rhythm Climb',
          description: 'Tap when note hits target',
          roleId: 'cat_burglar',
        ),
        MinigameInfo(
          id: 'laser_maze_timing',
          name: 'Laser Maze',
          description: 'Time movement through lasers',
          roleId: 'cat_burglar',
        ),
        MinigameInfo(
          id: 'balance_meter',
          name: 'Balance',
          description: 'Keep meter centered',
          roleId: 'cat_burglar',
        ),
        MinigameInfo(
          id: 'doodle_climb',
          name: 'Doodle Climb',
          description: 'Bounce off ledges to scale the building',
          roleId: 'cat_burglar',
        ),
      ],
    ),
    RoleMinigames(
      roleId: 'cleaner',
      name: 'Cleaner',
      minigames: [
        MinigameInfo(
          id: 'swipe_fingerprints',
          name: 'Wipe Prints',
          description: 'Swipe over fingerprints',
          roleId: 'cleaner',
        ),
        MinigameInfo(
          id: 'tap_evidence_markers',
          name: 'Tag Evidence',
          description: 'Tap all markers before timeout',
          roleId: 'cleaner',
        ),
        MinigameInfo(
          id: 'trash_disposal',
          name: 'Dispose',
          description: 'Drag items to trash quickly',
          roleId: 'cleaner',
        ),
      ],
    ),
    RoleMinigames(
      roleId: 'pickpocket',
      name: 'Pickpocket',
      minigames: [
        MinigameInfo(
          id: 'timing_tap',
          name: 'Timing Tap',
          description: 'Tap when circle hits zone',
          roleId: 'pickpocket',
        ),
        MinigameInfo(
          id: 'quick_pocket_search',
          name: 'Pocket Search',
          description: 'Drag items from pocket fast',
          roleId: 'pickpocket',
        ),
        MinigameInfo(
          id: 'pocket_grab',
          name: 'Pocket Grab',
          description: 'Tap when hand aligns with object',
          roleId: 'pickpocket',
        ),
        MinigameInfo(
          id: 'distraction_meter',
          name: 'Distraction',
          description: 'Steal when target looks away',
          roleId: 'pickpocket',
        ),
      ],
    ),
  ];
}
