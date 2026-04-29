import 'package:flutter_test/flutter_test.dart';
import 'package:bwave_mobile/main.dart';

void main() {
  testWidgets('App renders B-Wave Scanner text', (tester) async {
    await tester.pumpWidget(const BWaveApp());
    expect(find.text('B-Wave Scanner'), findsOneWidget);
  });
}
