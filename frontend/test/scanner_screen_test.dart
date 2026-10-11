import 'dart:async';
import 'package:ethico/main.dart';
import 'package:ethico/product_api.dart';
import 'package:ethico/scanner_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

// Substitutes only the exported controller operations and capture stream.
// The real ScannerScreen and ScannerSession still own navigation and cleanup.
class CameraController extends MobileScannerController {
  CameraController({this.error}) : super(autoStart: false);

  final captures = StreamController<BarcodeCapture>.broadcast();
  final operations = <String>[];
  final MobileScannerException? error;
  Completer<void>? stopping;

  @override
  Stream<BarcodeCapture> get barcodes => captures.stream;

  @override
  Future<void> start({CameraFacing? cameraDirection}) async {
    operations.add('start');
    value = value.copyWith(
      isInitialized: true,
      isRunning: error == null,
      error: error,
    );
  }

  @override
  Future<void> stop() async {
    operations.add('stop');
    value = value.copyWith(isRunning: false);
    await stopping?.future;
  }

  @override
  // Native disposal is deliberately substituted, as in the session unit tests.
  // ignore: must_call_super
  Future<void> dispose() async {
    operations.add('dispose');
  }
}

// Exercise Ethico's actual error builder with public controller state, without
// mounting a native camera preview or simulating the plugin's platform adapter.
Widget cameraPreview(MobileScanner scanner) =>
    ValueListenableBuilder<MobileScannerState>(
      valueListenable: scanner.controller!,
      builder:
          (context, state, child) =>
              state.error == null
                  ? const SizedBox()
                  : scanner.errorBuilder!(context, state.error!, child),
    );
void main() {
  late CameraController camera;
  final cameras = <CameraController>[];
  MobileScannerException? startupError;
  late int requests;
  setUp(() {
    startupError = null;
    requests = 0;
    cameras.clear();
  });
  tearDown(() async {
    for (final controller in cameras) {
      await controller.captures.close();
    }
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
    await tester.pumpWidget(
      MaterialApp(
        home: LookupScreen(
          api: ProductApi(client),
          scannerLauncher: (context) {
            camera = CameraController(error: startupError);
            cameras.add(camera);
            return Navigator.of(context).push<String>(
              MaterialPageRoute(
                builder:
                    (_) => ScannerScreen(
                      controller: camera,
                      previewBuilder: cameraPreview,
                    ),
              ),
            );
          },
        ),
      ),
    );
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
      startupError = MobileScannerException(
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
