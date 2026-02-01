import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_dimensions.dart';
import '../models/npc.dart';
import '../widgets/common/section_header.dart';
import 'npc_conversation_screen.dart';

/// Test harness for NPC conversation screen
/// Allows testing with different scenarios
class NPCTestScreen extends StatelessWidget {
  const NPCTestScreen({Key? key}) : super(key: key);

  // Test NPCs
  static final List<NPC> testNPCs = [
    NPC(
      id: '1',
      name: 'Sophia Castellano',
      role: 'Museum Night Guard',
      personality: 'Professional, takes job seriously, 15 years experience',
      location: 'Museum East Wing',
      imageUrl: null, // TODO: Add asset when available
    ),
    NPC(
      id: '2',
      name: 'Marcus Romano',
      role: 'Bank Security Chief',
      personality: 'Friendly but alert, protective of protocols',
      location: 'Security Office',
      imageUrl: null,
    ),
    NPC(
      id: '3',
      name: 'Dr. Elena Vasquez',
      role: 'Museum Curator',
      personality: 'Sophisticated, protective of art',
      location: 'Gallery 3',
      imageUrl: null,
    ),
  ];

  // Test scenarios with objectives
  List<Objective> _getObjectivesForNPC(String npcId) {
    switch (npcId) {
      case '1': // Sophia
        return [
          Objective(
            id: 'obj1',
            description: 'Camera offline schedule',
            confidence: ConfidenceLevel.high,
          ),
          Objective(
            id: 'obj2',
            description: 'Guard rotation times',
            confidence: ConfidenceLevel.medium,
          ),
        ];
      case '2': // Marcus
        return [
          Objective(
            id: 'obj1',
            description: 'Night shift rotation',
            confidence: ConfidenceLevel.high,
          ),
        ];
      case '3': // Elena
        return [
          Objective(
            id: 'obj1',
            description: 'Which painting is fake',
            confidence: ConfidenceLevel.high,
          ),
          Objective(
            id: 'obj2',
            description: 'Vault access code',
            confidence: ConfidenceLevel.low,
          ),
        ];
      default:
        return [];
    }
  }

  void _launchNPCConversation(BuildContext context, NPC npc) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => NPCConversationScreen(
          npc: npc,
          objectives: _getObjectivesForNPC(npc.id),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        backgroundColor: AppColors.bgPrimary,
        elevation: 0,
        title: Text(
          'NPC Conversation Test',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: AppColors.textPrimary,
          ),
        ),
      ),
      body: SafeArea(
        child: Container(
          padding: EdgeInsets.all(AppDimensions.containerPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Info card
              Container(
                padding: EdgeInsets.all(AppDimensions.cardPadding),
                decoration: BoxDecoration(
                  color: AppColors.bgSecondary,
                  border: Border.all(color: AppColors.borderSubtle),
                  borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'NPC CONVERSATION TEST',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textTertiary,
                        letterSpacing: 1,
                      ),
                    ),
                    SizedBox(height: AppDimensions.spaceSM),
                    Text(
                      'Test the production NPC conversation UI with Flutter widgets',
                      style: TextStyle(
                        fontSize: 14,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
              
              SectionHeader(text: 'Select NPC to Test'),
              
              // NPC selection list
              Expanded(
                child: ListView.builder(
                  itemCount: testNPCs.length,
                  itemBuilder: (context, index) {
                    final npc = testNPCs[index];
                    final objectives = _getObjectivesForNPC(npc.id);
                    
                    return Container(
                      margin: EdgeInsets.only(bottom: AppDimensions.spaceMD),
                      decoration: BoxDecoration(
                        color: AppColors.bgSecondary,
                        border: Border.all(color: AppColors.borderSubtle),
                        borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
                      ),
                      child: Material(
                        color: Colors.transparent,
                        child: InkWell(
                          onTap: () => _launchNPCConversation(context, npc),
                          borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
                          child: Padding(
                            padding: EdgeInsets.all(AppDimensions.cardPadding),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Text(
                                      '🎭',
                                      style: TextStyle(fontSize: 24),
                                    ),
                                    SizedBox(width: AppDimensions.spaceMD),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            npc.name,
                                            style: TextStyle(
                                              fontSize: 16,
                                              fontWeight: FontWeight.w600,
                                              color: AppColors.textPrimary,
                                            ),
                                          ),
                                          Text(
                                            npc.role,
                                            style: TextStyle(
                                              fontSize: 12,
                                              color: AppColors.textSecondary,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    Icon(
                                      Icons.chevron_right,
                                      color: AppColors.textSecondary,
                                    ),
                                  ],
                                ),
                                
                                SizedBox(height: AppDimensions.spaceSM),
                                
                                // Objectives preview
                                ...objectives.take(2).map((obj) {
                                  return Padding(
                                    padding: EdgeInsets.only(top: AppDimensions.spaceXS),
                                    child: Text(
                                      '• ${obj.description}',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: AppColors.textTertiary,
                                      ),
                                    ),
                                  );
                                }).toList(),
                              ],
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
              
              // Note
              Container(
                padding: EdgeInsets.all(AppDimensions.spaceMD),
                child: Text(
                  'Note: LLM integration coming soon. Currently shows UI structure.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textTertiary,
                    fontStyle: FontStyle.italic,
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
