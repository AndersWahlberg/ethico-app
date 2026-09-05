import 'dart:convert';
import 'package:ethico/product_api.dart';
import 'package:ethico/product_details.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

const source = ProductSource(
  title: 'Kespro product listing',
  url: 'https://www.kespro.com/tuotteet/example',
  checkedOn: '2026-09-05',
  supports: 'Identifies the EAN and manufacturer.',
);

const product = Product(
  '6430051512933',
  'Leader creatine',
  'Leader',
  'Leader Foods Oy',
  companyRole: 'manufacturer',
  sources: [source],
);

Widget screen(Product product, Future<bool> Function(Uri) openLink) =>
    MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(
          child: ProductDetails(product: product, openLink: openLink),
        ),
      ),
    );

void main() {
  test('parses source metadata from an API response', () async {
    final api = ProductApi(
      MockClient(
        (_) async => http.Response(
          jsonEncode({
            'ean': '6430051512933',
            'product_name': 'Leader creatine',
            'brand': 'Leader',
            'company': 'Leader Foods Oy',
            'company_role': 'manufacturer',
            'is_demo': false,
            'sources': [
              {
                'title': source.title,
                'url': source.url,
                'checked_on': source.checkedOn,
                'supports': source.supports,
              },
            ],
          }),
          200,
        ),
      ),
    );
    final result = await api.lookup('6430051512933');
    expect(result.companyRole, 'manufacturer');
    expect(result.isDemo, isFalse);
    expect(result.sources.single.url, source.url);
    expect(result.sources.single.checkedOn, '2026-09-05');
    expect(result.sources.single.supports, source.supports);
  });

  testWidgets('shows source scope and date and opens the matching URL', (
    tester,
  ) async {
    Uri? opened;
    await tester.pumpWidget(
      screen(product, (uri) async {
        opened = uri;
        return true;
      }),
    );
    expect(find.text('Company role: Manufacturer'), findsOneWidget);
    expect(find.text(source.supports), findsOneWidget);
    expect(find.text('Source checked: 2026-09-05'), findsOneWidget);
    await tester.tap(find.text('Open source'));
    await tester.pumpAndSettle();
    expect(opened.toString(), source.url);
  });

  testWidgets(
    'failed browser launch leaves the product and copyable URL visible',
    (tester) async {
      await tester.pumpWidget(screen(product, (_) async => false));
      await tester.tap(find.text('Open source'));
      await tester.pumpAndSettle();
      expect(
        find.text('Could not open the source. You can copy its URL below.'),
        findsOneWidget,
      );
      expect(find.text('Leader creatine'), findsOneWidget);
      expect(find.byType(SelectableText), findsOneWidget);
    },
  );

  testWidgets('demo products are labelled and do not show source claims', (
    tester,
  ) async {
    await tester.pumpWidget(
      screen(
        const Product(
          '2000000000015',
          'Demo',
          'Demo',
          'Fictional',
          isDemo: true,
        ),
        (_) async => throw StateError('Must not open'),
      ),
    );
    expect(
      find.text('Fictional demo product. No verified company information.'),
      findsOneWidget,
    );
    expect(find.text('Sources'), findsNothing);
  });

  testWidgets('missing evidence is explicit', (tester) async {
    await tester.pumpWidget(
      screen(
        const Product('2000000000039', 'Local', 'Local', 'Local'),
        (_) async => true,
      ),
    );
    expect(find.text('No sources recorded for this product.'), findsOneWidget);
    expect(find.text('Company role: Not specified'), findsOneWidget);
  });

  testWidgets('non-web source URLs are never launched', (tester) async {
    await tester.pumpWidget(
      screen(
        const Product(
          '2000000000039',
          'Local',
          'Local',
          'Local',
          sources: [
            ProductSource(
              title: 'Invalid',
              url: 'file:///private',
              checkedOn: '2026-09-05',
              supports: 'Invalid',
            ),
          ],
        ),
        (_) async => throw StateError('Must not open'),
      ),
    );
    await tester.tap(find.text('Open source'));
    await tester.pumpAndSettle();
    expect(
      find.text('Could not open the source. You can copy its URL below.'),
      findsOneWidget,
    );
  });
}
