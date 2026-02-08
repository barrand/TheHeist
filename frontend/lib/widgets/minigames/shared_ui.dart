import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';

Widget buildStatsBar(String left, String right) {
  return Container(
    padding: const EdgeInsets.all(16),
    color: AppColors.bgSecondary,
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(left, style: const TextStyle(fontSize: 18, color: AppColors.textSecondary)),
        Text(right, style: const TextStyle(fontSize: 18, color: AppColors.textSecondary)),
      ],
    ),
  );
}

Widget buildWinScreen(String message, IconData icon, VoidCallback onReset) {
  return Center(
    child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, size: 120, color: AppColors.success),
        const SizedBox(height: 24),
        Text(
          message,
          style: const TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.bold,
            color: AppColors.success,
          ),
        ),
        const SizedBox(height: 40),
        ElevatedButton.icon(
          onPressed: onReset,
          icon: const Icon(Icons.refresh),
          label: const Text('Play Again'),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.bgSecondary,
            foregroundColor: AppColors.textPrimary,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            textStyle: const TextStyle(fontSize: 18),
          ),
        ),
      ],
    ),
  );
}

Widget buildFailScreen(VoidCallback onReset) {
  return Center(
    child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Icon(Icons.error_outline, size: 120, color: AppColors.danger),
        const SizedBox(height: 24),
        const Text(
          'FAILED!',
          style: TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.bold,
            color: AppColors.danger,
          ),
        ),
        const SizedBox(height: 16),
        const Text(
          'Try again!',
          style: TextStyle(fontSize: 18, color: AppColors.textSecondary),
        ),
        const SizedBox(height: 40),
        ElevatedButton.icon(
          onPressed: onReset,
          icon: const Icon(Icons.refresh),
          label: const Text('Retry'),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.bgSecondary,
            foregroundColor: AppColors.textPrimary,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            textStyle: const TextStyle(fontSize: 18),
          ),
        ),
      ],
    ),
  );
}
