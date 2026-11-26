import 'package:flutter_test/flutter_test.dart';
import 'package:hamrah_dana/main.dart';

void main() {
  testWidgets('Hamrah Dana chat screen renders', (WidgetTester tester) async {
    await tester.pumpWidget(const HamrahDanaApp());

    expect(find.text('همراه دانا'), findsOneWidget);
    expect(find.text('دستیار آموزشی برق و الکترونیک'), findsOneWidget);
    expect(
      find.text('سلام! من همراه دانا هستم. چه کمکی از دستم برمیاد؟'),
      findsOneWidget,
    );
    expect(find.text('پیامت رو بنویس...'), findsOneWidget);
  });
}
