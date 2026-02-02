import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';

/// Modal for selecting a role from all available options
class RoleSelectionModal extends StatelessWidget {
  final List<Map<String, String>> availableRoles;
  final String? currentRole;
  final List<Map<String, dynamic>> players;
  final Function(String roleId) onSelectRole;
  
  const RoleSelectionModal({
    super.key,
    required this.availableRoles,
    required this.currentRole,
    required this.players,
    required this.onSelectRole,
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
          maxWidth: 400,
          maxHeight: MediaQuery.of(context).size.height * 0.8,
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
                  'SELECT YOUR ROLE',
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
            
            // Roles list
            Flexible(
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: availableRoles.length,
                itemBuilder: (context, index) {
                  final role = availableRoles[index];
                  final roleId = role['id']!;
                  final isSelected = currentRole == roleId;
                  final takenByPlayer = players.firstWhere(
                    (p) => p['role'] == roleId,
                    orElse: () => <String, dynamic>{},
                  );
                  final isTaken = takenByPlayer.isNotEmpty;
                  final takenByName = isTaken ? takenByPlayer['name'] : null;
                  final isAvailable = !isTaken || isSelected;
                  
                  return Container(
                    margin: EdgeInsets.only(bottom: AppDimensions.spaceSM),
                    child: Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: isAvailable
                            ? () {
                                onSelectRole(roleId);
                                Navigator.of(context).pop();
                              }
                            : null,
                        borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                        child: Container(
                          padding: EdgeInsets.all(AppDimensions.spaceLG),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? AppColors.accentPrimary
                                : isTaken
                                    ? AppColors.bgTertiary.withAlpha(128)
                                    : AppColors.bgSecondary,
                            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                            border: Border.all(
                              color: isSelected
                                  ? AppColors.accentLight
                                  : isTaken
                                      ? AppColors.danger.withAlpha(128)
                                      : AppColors.borderSubtle,
                              width: isSelected ? 2 : 1,
                            ),
                          ),
                          child: Row(
                            children: [
                              Text(
                                role['icon']!,
                                style: TextStyle(fontSize: 24),
                              ),
                              SizedBox(width: AppDimensions.spaceMD),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      role['name']!,
                                      style: TextStyle(
                                        color: isSelected
                                            ? AppColors.textPrimary
                                            : isTaken
                                                ? AppColors.textTertiary
                                                : AppColors.textPrimary,
                                        fontSize: 16,
                                        fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                                      ),
                                    ),
                                    if (isTaken && !isSelected) ...[
                                      SizedBox(height: 2),
                                      Text(
                                        'Taken by $takenByName',
                                        style: TextStyle(
                                          color: AppColors.danger,
                                          fontSize: 12,
                                          fontStyle: FontStyle.italic,
                                        ),
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                              if (isSelected)
                                Icon(
                                  Icons.check_circle,
                                  color: AppColors.success,
                                  size: 24,
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
