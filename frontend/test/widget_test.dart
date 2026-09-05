import 'dart:async';
import 'package:ethico/main.dart';
import 'package:ethico/product_api.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  testWidgets('manual lookup sends EAN and displays the response', (
    tester,
  ) async {
    final pending = Completer<http.Response>();
    final client = MockClient((request) {
      expect(request.url.path, '/products/0000000000017');
      return pending.future;
    });
    await tester.pumpWidget(EthicoApp(api: ProductApi(client)));
    await tester.enterText(find.byType(TextField), '0000000000017');
    await tester.tap(find.text('Look up product'));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    pending.complete(
      http.Response(
        '{"ean":"0000000000017","product_name":"Demo Tea","brand":"Demo Leaf","company":"Fictional Leaf Foods"}',
        200,
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Demo Tea'), findsOneWidget);
    expect(find.text('Company: Fictional Leaf Foods'), findsOneWidget);
  });

  testWidgets('invalid input does not send a request', (tester) async {
    final client = MockClient((_) async => throw StateError('Must not send'));
    await tester.pumpWidget(EthicoApp(api: ProductApi(client)));
    await tester.enterText(find.byType(TextField), '123');
    await tester.tap(find.text('Look up product'));
    await tester.pump();
    expect(find.text('Enter 8 or 13 digits.'), findsOneWidget);
  });

  testWidgets('not found clears the previous product and permits retry', (
    tester,
  ) async {
    var calls = 0;
    final client = MockClient(
      (_) async =>
          ++calls == 1
              ? http.Response(
                '{"ean":"2000000000015","product_name":"Demo Drink","brand":"Demo","company":"Fictional"}',
                200,
              )
              : http.Response('{"detail":"not found"}', 404),
    );
    await tester.pumpWidget(EthicoApp(api: ProductApi(client)));
    await tester.enterText(find.byType(TextField), '2000000000015');
    await tester.tap(find.text('Look up product'));
    await tester.pumpAndSettle();
    expect(find.text('Demo Drink'), findsOneWidget);
    await tester.enterText(find.byType(TextField), '2000000000039');
    await tester.tap(find.text('Look up product'));
    await tester.pumpAndSettle();
    expect(find.text('Demo Drink'), findsNothing);
    expect(find.text('Product not found in the demo dataset.'), findsOneWidget);
  });

  test(
    'API distinguishes invalid codes, server failures, and malformed responses',
    () async {
      for (final status in [422, 500]) {
        final api = ProductApi(
          MockClient((_) async => http.Response('{}', status)),
        );
        await expectLater(
          api.lookup('2000000000015'),
          throwsA(isA<LookupException>()),
        );
      }
      final api = ProductApi(
        MockClient((_) async => http.Response('not json', 200)),
      );
      await expectLater(api.lookup('2000000000015'), throwsFormatException);
    },
  );

  testWidgets('network failure shows a retryable error', (tester) async {
    final api = ProductApi(
      MockClient((_) async => throw http.ClientException('offline')),
    );
    await tester.pumpWidget(EthicoApp(api: api));
    await tester.enterText(find.byType(TextField), '2000000000015');
    await tester.tap(find.text('Look up product'));
    await tester.pumpAndSettle();
    expect(
      find.text('Could not load the product. Check your connection and retry.'),
      findsOneWidget,
    );
  });
}
