import 'package:flutter/material.dart';

void main() => runApp(const BWaveApp());

class BWaveApp extends StatelessWidget {
  const BWaveApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'B-Wave Scanner',
      theme: ThemeData.dark(useMaterial3: true),
      home: const Scaffold(
        body: Center(
          child: Text('B-Wave Scanner'),
        ),
      ),
    );
  }
}
