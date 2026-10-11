import 'dart:async';
import 'package:ethico/main.dart';
import 'package:ethico/product_api.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
// Types used by the package's public platform-interface start signature.
import 'package:mobile_scanner/src/mobile_scanner_view_attributes.dart';
import 'package:mobile_scanner/src/objects/start_options.dart';

class CameraPlatform extends MobileScannerPlatform {
  final captures = StreamController<BarcodeCapture?>.broadcast();
  final operations = <String>[];
  MobileScannerException? error;
  Completer<void>? starting;
  Completer<void>? stopping;

  @override
  Stream<BarcodeCapture?> get barcodesStream => captures.stream;
  @override
  Stream<TorchState> get torchStateStream => const Stream.empty();
  @override
  Stream<double> get zoomScaleStateStream => const Stream.empty();
  @override
  Widget buildCameraView() => const SizedBox();
  @override
  Future<MobileScannerViewAttributes> start(StartOptions options) async {
    operations.add('start');
    expect(options.formats, [BarcodeFormat.ean8, BarcodeFormat.ean13]);
    expect(options.returnImage, isFalse);
    await starting?.future;
    if (error != null) throw error!;
    return const MobileScannerViewAttributes(
      currentTorchMode: TorchState.unavailable,
      size: Size(640, 480),
    );
  }

  @override
  Future<void> stop() async {
    operations.add('stop');
    await stopping?.future;
  }

  @override
  Future<void> dispose() async {
    operations.add('dispose');
  }

  @override
  Future<void> updateScanWindow(Rect? window) async {}
}

void main() {
  late CameraPlatform camera;
  late MobileScannerPlatform original;
  late int requests;
  setUp(() {
    original = MobileScannerPlatform.instance;
    camera = CameraPlatform();
    MobileScannerPlatform.instance = camera;
    requests = 0;
  });
  tearDown(() async {
    MobileScannerPlatform.instance = original;
    await camera.captures.close();
  });
  Future<void> open(WidgetTester tester) async {
    final client = MockClient((request) async {
      requests++;
      return http.Response(
        '{"ean":"0000000000017","product_name":"Demo Tea","brand":"Demo","company":"Fictional"}',
        200,
      );
    });
    addTearDown(client.close);
    await tester.pumpWidget(EthicoApp(api: ProductApi(client)));
    await tester.enterText(find.byType(TextField), '2000000000015');
    await tester.tap(find.text('Scan barcode'));
    await tester.pumpAndSettle();
  }

  testWidgets(
    'real route Back waits for cleanup, returns null and can reopen',
    (tester) async {
      await open(tester);
      camera.stopping = Completer<void>();
      await tester.binding.handlePopRoute();
      await tester.pump();
      expect(camera.operations, ['start', 'stop']);
      expect(find.text('Scan EAN barcode'), findsOneWidget);
      camera.captures.add(
        BarcodeCapture(barcodes: [Barcode(rawValue: '0000000000017')]),
      );
      camera.stopping!.complete();
      await tester.pumpAndSettle();
      expect(requests, 0);
      expect(camera.operations, ['start', 'stop', 'dispose']);
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller!.text,
        '2000000000015',
      );
      await tester.tap(find.text('Scan barcode'));
      await tester.pumpAndSettle();
      expect(camera.operations.last, 'start');
      await tester.tap(find.byType(BackButton));
      await tester.pumpAndSettle();
      expect(requests, 0);
    },
  );

  testWidgets('multiple frames navigate and lookup once after camera cleanup', (
    tester,
  ) async {
    await open(tester);
    camera.stopping = Completer<void>();
    for (var i = 0; i < 3; i++) {
      camera.captures.add(
        BarcodeCapture(
          barcodes: [
            Barcode(rawValue: 'not an EAN'),
            Barcode(rawValue: '0000000000017'),
            Barcode(rawValue: '12345678'),
          ],
        ),
      );
    }
    await tester.pump();
    expect(requests, 0);
    await tester.binding.handlePopRoute();
    camera.stopping!.complete();
    await tester.pumpAndSettle();
    expect(requests, 1);
    expect(camera.operations, ['start', 'stop', 'dispose']);
    expect(find.text('Demo Tea'), findsOneWidget);
    await tester.tap(find.text('Scan barcode'));
    await tester.pumpAndSettle();
    camera.captures.add(
      BarcodeCapture(barcodes: [Barcode(rawValue: '0000000000017')]),
    );
    await tester.pumpAndSettle();
    expect(requests, 2);
  });

  for (final code in [
    MobileScannerErrorCode.permissionDenied,
    MobileScannerErrorCode.genericError,
  ]) {
    testWidgets('$code shows safe fallback and permits Back/manual lookup', (
      tester,
    ) async {
      camera.error = MobileScannerException(
        errorCode: code,
        errorDetails: const MobileScannerErrorDetails(
          message: 'private native error',
        ),
      );
      await open(tester);
      expect(find.textContaining('enter the EAN manually'), findsOneWidget);
      expect(
        find.textContaining('device settings'),
        code == MobileScannerErrorCode.permissionDenied
            ? findsOneWidget
            : findsNothing,
      );
      expect(find.textContaining('private native error'), findsNothing);
      await tester.tap(find.byType(BackButton));
      await tester.pumpAndSettle();
      expect(requests, 0);
      await tester.tap(find.text('Look up product'));
      await tester.pumpAndSettle();
      expect(requests, 1);
      expect(find.text('Demo Tea'), findsOneWidget);
    });
  }
  testWidgets(
    'capture failure stops scanning and offers safe manual fallback',
    (tester) async {
      await open(tester);
      camera.captures.addError(
        const MobileScannerBarcodeException('private decode error'),
      );
      await tester.pumpAndSettle();
      expect(
        find.text('Camera unavailable. Go back and enter the EAN manually.'),
        findsOneWidget,
      );
      expect(find.textContaining('private decode error'), findsNothing);
      expect(camera.operations, ['start', 'stop']);
      await tester.tap(find.byType(BackButton));
      await tester.pumpAndSettle();
      expect(requests, 0);
    },
  );
}
