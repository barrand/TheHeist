import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/lockpick_minigame.dart';
import 'package:the_heist/widgets/minigames/simon_says_minigame.dart';
import 'package:the_heist/widgets/minigames/dial_safe_minigame.dart';
import 'package:the_heist/widgets/minigames/button_mash_minigame.dart';
import 'package:the_heist/widgets/minigames/timing_tap_minigame.dart';
import 'package:the_heist/widgets/minigames/wire_connect_minigame.dart';
import 'package:the_heist/widgets/minigames/card_swipe_minigame.dart';
import 'package:the_heist/widgets/minigames/rhythm_climb_minigame.dart';
import 'package:the_heist/widgets/minigames/logic_clues_minigame.dart';
import 'package:the_heist/widgets/minigames/doodle_climb_minigame.dart';
import 'package:the_heist/widgets/minigames/tag_evidence_minigame.dart';
import 'package:the_heist/widgets/minigames/item_matching_minigame.dart';
import 'package:the_heist/widgets/minigames/steering_obstacle_minigame.dart';
import 'package:the_heist/widgets/minigames/whack_a_threat_minigame.dart';
import 'package:the_heist/widgets/minigames/emotion_matching_minigame.dart';
/// Hub screen showing all minigames organized by role
class MinigameHubScreen extends StatefulWidget {
  const MinigameHubScreen({super.key});

  @override
  State<MinigameHubScreen> createState() => _MinigameHubScreenState();
}

class _MinigameHubScreenState extends State<MinigameHubScreen> {
  MinigameDifficulty _selectedDifficulty = MinigameDifficulty.medium;
  
  // Map of implemented minigames: id -> builder function
  Map<String, Widget Function(MinigameDifficulty)> get _implementedMinigames => {
    'lockpick_timing': (diff) => LockpickMinigame(difficulty: diff),
    'dial_rotation': (diff) => DialSafeMinigame(difficulty: diff),
    'simon_says_sequence': (diff) => SimonSaysMinigame(difficulty: diff),
    'wire_connecting': (diff) => WireConnectMinigame(difficulty: diff),
    'badge_swipe': (diff) => CardSwipeMinigame(difficulty: diff),
    'timing_tap': (diff) => TimingTapMinigame(difficulty: diff),
    'button_mash_barrier': (diff) => ButtonMashMinigame(difficulty: diff),
    'climbing_rhythm': (diff) => RhythmClimbMinigame(difficulty: diff),
    'logic_clues': (diff) => LogicCluesMinigame(difficulty: diff),
    'doodle_climb': (diff) => DoodleClimbMinigame(difficulty: diff),
    'tap_evidence_markers': (diff) => TagEvidenceMinigame(difficulty: diff),
    'item_matching': (diff) => ItemMatchingMinigame(difficulty: diff),
    'steering_obstacle_course': (diff) => SteeringObstacleMinigame(difficulty: diff),
    'whack_a_mole_threats': (diff) => WhackAThreatMinigame(difficulty: diff),
    'emotion_matching': (diff) => EmotionMatchingMinigame(difficulty: diff),
  };
  
  // All roles and their minigames from roles.json
  static const List<RoleMinigames> _roles = [
    RoleMinigames(
      roleId: 'mastermind',
      name: 'Mastermind',
      minigames: [
        MinigameInfo(
          id: 'logic_clues',
          name: 'Logic Clues',
          description: 'Arrange boxes using clues',
          roleId: 'mastermind',
          isImplemented: true,
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
          isImplemented: true,
        ),
        MinigameInfo(
          id: 'simon_says_sequence',
          name: 'Simon Says',
          description: 'Memorize and repeat pattern',
          roleId: 'hacker',
          isImplemented: true,
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
          isImplemented: true,
        ),
        MinigameInfo(
          id: 'lockpick_timing',
          name: 'Lockpick',
          description: 'Position pins correctly',
          roleId: 'safe_cracker',
          isImplemented: true,
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
          isImplemented: true,
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
          isImplemented: true,
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
          isImplemented: true,
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
          isImplemented: true,
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
          isImplemented: true,
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
          isImplemented: true,
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
          isImplemented: true,
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
          isImplemented: true,
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
          isImplemented: true,
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
          isImplemented: true,
        ),
        MinigameInfo(
          id: 'quick_pocket_search',
          name: 'Pocket Search',
          description: 'Drag items from pocket fast',
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
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        backgroundColor: AppColors.bgSecondary,
        title: const Text('Minigame Prototypes'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Difficulty selector
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.bgSecondary,
                border: Border(
                  bottom: BorderSide(color: AppColors.borderSubtle),
                ),
              ),
              child: Column(
                children: [
                  const Text(
                    'Difficulty',
                    style: TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: MinigameDifficulty.values.map((diff) {
                      final isSelected = _selectedDifficulty == diff;
                      return Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 4),
                        child: GestureDetector(
                          onTap: () {
                            setState(() {
                              _selectedDifficulty = diff;
                            });
                          },
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                            decoration: BoxDecoration(
                              color: isSelected ? AppColors.accentPrimary : Colors.transparent,
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(
                                color: isSelected ? AppColors.accentPrimary : AppColors.borderSubtle,
                                width: 1.5,
                              ),
                            ),
                            child: Text(
                              diff.displayName,
                              style: TextStyle(
                                color: isSelected ? AppColors.bgPrimary : AppColors.textSecondary,
                                fontSize: 14,
                                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                              ),
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
            // Minigames list
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _roles.length,
                itemBuilder: (context, index) {
                  return _buildRoleSection(context, _roles[index]);
                },
              ),
            ),
          ],
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
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 4),
          child: Text(
            role.name.toUpperCase(),
            style: TextStyle(
              color: AppColors.accentPrimary,
              fontSize: 13,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.0,
            ),
          ),
        ),
        // Minigames for this role
        ...role.minigames.map((minigame) => _buildMinigameRow(context, minigame)),
        const SizedBox(height: 12),
      ],
    );
  }
  
  Widget _buildMinigameRow(BuildContext context, MinigameInfo minigame) {
    final isImplemented = _implementedMinigames.containsKey(minigame.id);
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: GestureDetector(
        onTap: isImplemented ? () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => MinigameScreen(
                title: minigame.name,
                child: _implementedMinigames[minigame.id]!(_selectedDifficulty),
              ),
            ),
          );
        } : null,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: isImplemented 
                ? AppColors.bgSecondary
                : AppColors.bgSecondary.withOpacity(0.3),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: isImplemented 
                  ? AppColors.borderSubtle
                  : AppColors.borderSubtle.withOpacity(0.3),
              width: 1,
            ),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      minigame.name,
                      style: TextStyle(
                        color: isImplemented ? AppColors.textPrimary : AppColors.textSecondary.withOpacity(0.5),
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      minigame.description,
                      style: TextStyle(
                        color: isImplemented ? AppColors.textSecondary : AppColors.textSecondary.withOpacity(0.4),
                        fontSize: 11,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              if (isImplemented)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    color: AppColors.success.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: AppColors.success, width: 1),
                  ),
                  child: const Text(
                    '✓',
                    style: TextStyle(
                      color: AppColors.success,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                )
              else
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'TODO',
                    style: TextStyle(
                      color: AppColors.textSecondary.withOpacity(0.5),
                      fontSize: 9,
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

/// Wrapper screen for individual minigames with back button
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
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        backgroundColor: AppColors.bgSecondary,
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
