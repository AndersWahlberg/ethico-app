import 'dart:async';
import 'dart:convert';
import 'package:ethico/main.dart';
import 'package:ethico/product_api.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  http.Response product(String ean, String name) => http.Response(
    jsonEncode({
      'ean': ean,
      'product_name': name,
      'brand': 'Demo',
      'company': 'Fictional',
    }),
    200,
  );

  String input(WidgetTester tester) =>
      tester.widget<TextField>(find.byType(TextField)).controller!.text;

  testWidgets('cancel preserves input, makes zero requests and can reopen', (
    tester,
  ) async {
    var requests = 0;
    var scans = 0;
    final client = MockClient((request) async {
      requests++;
      expect(request.url.path, '/products/0000000000017');
      return product('0000000000017', 'Demo Tea');
    });
    addTearDown(client.close);
    await tester.pumpWidget(
      MaterialApp(
        home: LookupScreen(
          api: ProductApi(client),
          scannerLauncher: (_) async => ++scans == 1 ? null : '0000000000017',
        ),
      ),
    );
    await tester.enterText(find.byType(TextField), '2000000000015');
    await tester.tap(find.text('Scan barcode'));
    await tester.pumpAndSettle();
    expect(requests, 0);
    expect(input(tester), '2000000000015');
    expect(find.textContaining('retry'), findsNothing);
    expect(
      tester
          .widget<FilledButton>(
            find.widgetWithText(FilledButton, 'Look up product'),
          )
          .onPressed,
      isNotNull,
    );
    await tester.tap(find.text('Scan barcode'));
    await tester.pumpAndSettle();
    expect(scans, 2);
    expect(requests, 1);
    expect(input(tester), '0000000000017');
    expect(find.text('Demo Tea'), findsOneWidget);
  });

  testWidgets(
    'scan succeeds once, clears stale facts on failure and retries without rescanning',
    (tester) async {
      final requested = <String>[];
      var scans = 0;
      final failure = Completer<http.Response>();
      final client = MockClient((request) async {
        requested.add(request.url.path);
        if (requested.length == 2) return failure.future;
        return product(
          request.url.pathSegments.last,
          requested.length == 1 ? 'Old product' : 'New product',
        );
      });
      addTearDown(client.close);
      await tester.pumpWidget(
        MaterialApp(
          home: LookupScreen(
            api: ProductApi(client),
            scannerLauncher:
                (_) async => ++scans == 1 ? '2000000000015' : '0000000000017',
          ),
        ),
      );
      await tester.tap(find.text('Scan barcode'));
      await tester.pumpAndSettle();
      expect(requested, ['/products/2000000000015']);
      expect(input(tester), '2000000000015');
      expect(find.text('Old product'), findsOneWidget);
      await tester.tap(find.text('Scan barcode'));
      await tester.pump();
      expect(find.text('Old product'), findsNothing);
      expect(input(tester), '0000000000017');
      failure.complete(
        http.Response('{"detail":"private provider details"}', 503),
      );
      await tester.pumpAndSettle();
      expect(
        find.text(
          'Product information could not be checked right now. Please try again.',
        ),
        findsOneWidget,
      );
      expect(find.textContaining('private provider details'), findsNothing);
      expect(input(tester), '0000000000017');
      await tester.tap(find.text('Look up product'));
      await tester.pumpAndSettle();
      expect(scans, 2);
      expect(requested, [
        '/products/2000000000015',
        '/products/0000000000017',
        '/products/0000000000017',
      ]);
      expect(find.text('New product'), findsOneWidget);
      expect(find.textContaining('Please try again.'), findsNothing);
      await tester.tap(find.text('Scan barcode'));
      await tester.pumpAndSettle();
      expect(scans, 3);
      expect(requested.length, 4);
      expect(find.text('New product'), findsOneWidget);
    },
  );

  testWidgets(
    'rapid taps launch once and lookup once, then cancellation preserves product',
    (tester) async {
      var scans = 0;
      var requests = 0;
      final result = Completer<String?>();
      final client = MockClient((_) async {
        requests++;
        return product('0000000000017', 'Demo Tea');
      });
      addTearDown(client.close);
      await tester.pumpWidget(
        MaterialApp(
          home: LookupScreen(
            api: ProductApi(client),
            scannerLauncher:
                (_) => ++scans == 1 ? result.future : Future.value(null),
          ),
        ),
      );
      await tester.tap(find.text('Scan barcode'));
      await tester.tap(find.text('Scan barcode'));
      expect(scans, 1);
      expect(requests, 0);
      result.complete('0000000000017');
      await tester.pumpAndSettle();
      expect(requests, 1);
      await tester.tap(find.text('Scan barcode'));
      await tester.pumpAndSettle();
      expect(scans, 2);
      expect(requests, 1);
      expect(input(tester), '0000000000017');
      expect(find.text('Demo Tea'), findsOneWidget);
    },
  );

  testWidgets(
    'scanner completion after lookup screen disposal makes no request',
    (tester) async {
      var requests = 0;
      final result = Completer<String?>();
      final client = MockClient((_) async {
        requests++;
        return product('0000000000017', 'Demo Tea');
      });
      addTearDown(client.close);
      await tester.pumpWidget(
        MaterialApp(
          home: LookupScreen(
            api: ProductApi(client),
            scannerLauncher: (_) => result.future,
          ),
        ),
      );
      await tester.tap(find.text('Scan barcode'));
      await tester.pumpWidget(const SizedBox());
      result.complete('0000000000017');
      await tester.pumpAndSettle();
      expect(requests, 0);
      expect(tester.takeException(), isNull);
    },
  );
}
