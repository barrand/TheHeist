import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'screens/landing_page.dart';

void main() {
  runApp(const TheHeistApp());
}

class TheHeistApp extends StatelessWidget {
  const TheHeistApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'The Heist',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const LandingPage(),
    );
  }
}
