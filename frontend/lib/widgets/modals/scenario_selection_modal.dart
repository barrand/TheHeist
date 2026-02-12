import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';
import 'package:the_heist/models/scenario.dart';
import 'package:the_heist/models/role.dart';

/// Modal for selecting a scenario from all available options
class ScenarioSelectionModal extends StatelessWidget {
  final List<Scenario> availableScenarios;
  final String currentScenarioId;
  final List<Role> availableRoles;
  final Function(String scenarioId) onSelectScenario;
  
  const ScenarioSelectionModal({
    super.key,
    required this.availableScenarios,
    required this.currentScenarioId,
    required this.availableRoles,
    required this.onSelectScenario,
  });
  
  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppColors.bgPrimary,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppDimensions.radiusXL),
        side: BorderSide(color: AppColors.borderSubtle, width: 1),
      ),
      child: Container(
        constraints: BoxConstraints(
          maxWidth: 600,
          maxHeight: MediaQuery.of(context).size.height * 0.85,
        ),
        padding: EdgeInsets.all(AppDimensions.space2XL),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Row(
              children: [
                Text(
                  'SELECT SCENARIO',
                  style: TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                  ),
                ),
                Spacer(),
                IconButton(
                  icon: Icon(Icons.close, color: AppColors.textSecondary),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
            
            SizedBox(height: AppDimensions.spaceLG),
            
            // Scenarios list
            Flexible(
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: availableScenarios.length,
                itemBuilder: (context, index) {
                  final scenario = availableScenarios[index];
                  final isSelected = currentScenarioId == scenario.scenarioId;
                  
                  return Container(
                    margin: EdgeInsets.only(bottom: AppDimensions.spaceMD),
                    child: Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: () {
                          onSelectScenario(scenario.scenarioId);
                          Navigator.of(context).pop();
                        },
                        borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                        child: Container(
                          padding: EdgeInsets.all(AppDimensions.spaceLG),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? AppColors.accentPrimary.withAlpha(51)
                                : AppColors.bgSecondary,
                            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                            border: Border.all(
                              color: isSelected
                                  ? AppColors.accentPrimary
                                  : AppColors.borderSubtle,
                              width: isSelected ? 2 : 1,
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Scenario image - 200px!
                                  ClipRRect(
                                    borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                                    child: Image.asset(
                                      'assets/static/${scenario.scenarioId}.png',
                                      width: 200,
                                      height: 200,
                                      fit: BoxFit.cover,
                                      errorBuilder: (context, error, stackTrace) {
                                        // Fallback to emoji icon if image not found
                                        return Container(
                                          width: 200,
                                          height: 200,
                                          alignment: Alignment.center,
                                          decoration: BoxDecoration(
                                            color: AppColors.bgTertiary,
                                            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                                          ),
                                          child: Text(
                                            scenario.themeIcon,
                                            style: TextStyle(fontSize: 80),
                                          ),
                                        );
                                      },
                                    ),
                                  ),
                                  SizedBox(width: AppDimensions.spaceLG),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          children: [
                                            Expanded(
                                              child: Text(
                                                scenario.name,
                                                style: TextStyle(
                                                  color: AppColors.textPrimary,
                                                  fontSize: 18,
                                                  fontWeight: FontWeight.w600,
                                                ),
                                              ),
                                            ),
                                            if (isSelected)
                                              Icon(
                                                Icons.check_circle,
                                                color: AppColors.success,
                                                size: 28,
                                              ),
                                          ],
                                        ),
                                        SizedBox(height: 8),
                                        Text(
                                          scenario.summary,
                                          style: TextStyle(
                                            color: AppColors.textSecondary,
                                            fontSize: 14,
                                            height: 1.4,
                                          ),
                                          maxLines: 4,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                        SizedBox(height: 12),
                                        Text(
                                          'Required Roles:',
                                          style: TextStyle(
                                            color: AppColors.textTertiary,
                                            fontSize: 11,
                                            fontWeight: FontWeight.w600,
                                            letterSpacing: 0.5,
                                          ),
                                        ),
                                        SizedBox(height: 6),
                                        Wrap(
                                          spacing: 6,
                                          runSpacing: 4,
                                          children: scenario.rolesRequired.map((roleId) {
                                            final role = availableRoles.firstWhere(
                                              (r) => r.roleId == roleId,
                                              orElse: () => Role(
                                                roleId: roleId,
                                                name: roleId,
                                                description: '',
                                                minigames: [],
                                                icon: '❓',
                                              ),
                                            );
                                            return Container(
                                              padding: EdgeInsets.symmetric(
                                                horizontal: 8,
                                                vertical: 4,
                                              ),
                                              decoration: BoxDecoration(
                                                color: AppColors.accentPrimary.withAlpha(51),
                                                borderRadius: BorderRadius.circular(4),
                                                border: Border.all(
                                                  color: AppColors.accentPrimary,
                                                  width: 1,
                                                ),
                                              ),
                                              child: Text(
                                                role.name,
                                                style: TextStyle(
                                                  color: AppColors.accentPrimary,
                                                  fontSize: 11,
                                                  fontWeight: FontWeight.w600,
                                                ),
                                              ),
                                            );
                                          }).toList(),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
