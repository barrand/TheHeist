import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/core/theme/app_dimensions.dart';
import 'package:the_heist/models/role.dart';

/// Modal for selecting a role from all available options
class RoleSelectionModal extends StatefulWidget {
  final List<Role> availableRoles;
  final String? currentRole;
  final List<Map<String, dynamic>> players;
  final Function(String roleId) onSelectRole;
  final String initialGender; // Initial gender preference
  
  const RoleSelectionModal({
    super.key,
    required this.availableRoles,
    required this.currentRole,
    required this.players,
    required this.onSelectRole,
    required this.initialGender,
  });

  @override
  State<RoleSelectionModal> createState() => _RoleSelectionModalState();
}

class _RoleSelectionModalState extends State<RoleSelectionModal> {
  late String _selectedGender;

  @override
  void initState() {
    super.initState();
    _selectedGender = widget.initialGender; // Start with player's chosen gender
  }
  
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
            
            SizedBox(height: AppDimensions.spaceMD),
            
            // Gender toggle
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'Show as: ',
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 14,
                  ),
                ),
                SizedBox(width: 8),
                GestureDetector(
                  onTap: () => setState(() => _selectedGender = 'female'),
                  child: Container(
                    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: _selectedGender == 'female'
                          ? AppColors.accentPrimary
                          : AppColors.bgTertiary,
                      borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
                      border: Border.all(
                        color: _selectedGender == 'female'
                            ? AppColors.accentPrimary
                            : AppColors.borderSubtle,
                        width: 2,
                      ),
                    ),
                    child: Text(
                      'Female',
                      style: TextStyle(
                        color: _selectedGender == 'female'
                            ? AppColors.textPrimary
                            : AppColors.textSecondary,
                        fontSize: 13,
                        fontWeight: _selectedGender == 'female'
                            ? FontWeight.w600
                            : FontWeight.normal,
                      ),
                    ),
                  ),
                ),
                SizedBox(width: 8),
                GestureDetector(
                  onTap: () => setState(() => _selectedGender = 'male'),
                  child: Container(
                    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: _selectedGender == 'male'
                          ? AppColors.accentPrimary
                          : AppColors.bgTertiary,
                      borderRadius: BorderRadius.circular(AppDimensions.radiusSM),
                      border: Border.all(
                        color: _selectedGender == 'male'
                            ? AppColors.accentPrimary
                            : AppColors.borderSubtle,
                        width: 2,
                      ),
                    ),
                    child: Text(
                      'Male',
                      style: TextStyle(
                        color: _selectedGender == 'male'
                            ? AppColors.textPrimary
                            : AppColors.textSecondary,
                        fontSize: 13,
                        fontWeight: _selectedGender == 'male'
                            ? FontWeight.w600
                            : FontWeight.normal,
                      ),
                    ),
                  ),
                ),
              ],
            ),
            
            SizedBox(height: AppDimensions.spaceLG),
            
            // Roles list
            Flexible(
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: widget.availableRoles.length,
                itemBuilder: (context, index) {
                  final role = widget.availableRoles[index];
                  final roleId = role.roleId;
                  final isSelected = widget.currentRole == roleId;
                  final takenByPlayer = widget.players.firstWhere(
                    (p) => p['role'] == roleId,
                    orElse: () => <String, dynamic>{},
                  );
                  final isTaken = takenByPlayer.isNotEmpty;
                  final takenByName = isTaken ? takenByPlayer['name'] : null;
                  final isAvailable = !isTaken || isSelected;
                  
                  return Container(
                    margin: EdgeInsets.only(bottom: AppDimensions.spaceMD),
                    child: Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: isAvailable
                            ? () {
                                widget.onSelectRole(roleId);
                                Navigator.of(context).pop();
                              }
                            : null,
                        borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                        child: Container(
                          padding: EdgeInsets.all(AppDimensions.spaceLG),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? AppColors.accentPrimary.withAlpha(51)
                                : isTaken
                                    ? AppColors.bgTertiary.withAlpha(128)
                                    : AppColors.bgSecondary,
                            borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                            border: Border.all(
                              color: isSelected
                                  ? AppColors.accentPrimary
                                  : isTaken
                                      ? AppColors.danger.withAlpha(128)
                                      : AppColors.borderSubtle,
                              width: isSelected ? 2 : 1,
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  // Character portrait - 200px!
                                  ClipRRect(
                                    borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
                                    child: Image.asset(
                                      'assets/static/${roleId}_$_selectedGender.png',
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
                                            role.icon,
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
                                        Text(
                                          role.name,
                                          style: TextStyle(
                                            color: isSelected
                                                ? AppColors.textPrimary
                                                : isTaken
                                                    ? AppColors.textTertiary
                                                    : AppColors.textPrimary,
                                            fontSize: 18,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        SizedBox(height: 4),
                                        Text(
                                          role.description,
                                          style: TextStyle(
                                            color: isSelected
                                                ? AppColors.textSecondary
                                                : isTaken
                                                    ? AppColors.textTertiary
                                                    : AppColors.textSecondary,
                                            fontSize: 13,
                                            height: 1.3,
                                          ),
                                          maxLines: 2,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                        if (isTaken && !isSelected) ...[
                                          SizedBox(height: 4),
                                          Text(
                                            'Taken by $takenByName',
                                            style: TextStyle(
                                              color: AppColors.danger,
                                              fontSize: 12,
                                              fontWeight: FontWeight.w600,
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
                                      size: 28,
                                    ),
                                ],
                              ),
                              // Minigames section
                              if (role.minigames.isNotEmpty) ...[
                                SizedBox(height: AppDimensions.spaceSM),
                                Padding(
                                  padding: EdgeInsets.only(left: 216), // Align with text above (200px image + 16px spacing)
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Minigames:',
                                        style: TextStyle(
                                          color: AppColors.textTertiary,
                                          fontSize: 11,
                                          fontWeight: FontWeight.w600,
                                          letterSpacing: 0.5,
                                        ),
                                      ),
                                      SizedBox(height: 4),
                                      ...role.minigames.take(3).map((minigame) => Padding(
                                        padding: EdgeInsets.only(bottom: 2),
                                        child: Row(
                                          children: [
                                            Text(
                                              '•',
                                              style: TextStyle(
                                                color: AppColors.accentPrimary,
                                                fontSize: 12,
                                              ),
                                            ),
                                            SizedBox(width: 6),
                                            Expanded(
                                              child: Text(
                                                minigame.displayName,
                                                style: TextStyle(
                                                  color: isSelected
                                                      ? AppColors.textSecondary
                                                      : isTaken
                                                          ? AppColors.textTertiary
                                                          : AppColors.textSecondary,
                                                  fontSize: 12,
                                                ),
                                                maxLines: 1,
                                                overflow: TextOverflow.ellipsis,
                                              ),
                                            ),
                                          ],
                                        ),
                                      )),
                                    ],
                                  ),
                                ),
                              ],
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
