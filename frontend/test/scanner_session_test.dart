import 'dart:async';
import 'package:ethico/scanner_session.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

// Only public controller state/operations are substituted. No camera is tested.
class ControlledCamera extends MobileScannerController {
  ControlledCamera() : super(autoStart: false);
  final operations = <String>[];
  Completer<void>? starting;
  Completer<void>? stopping;
  MobileScannerException? startupError;
  Object? thrownStartError;
  MobileScannerException? stopError;

  @override
  Future<void> start({CameraFacing? cameraDirection}) async {
    operations.add('start');
    await starting?.future;
    if (thrownStartError != null) throw thrownStartError!;
    value = value.copyWith(
      isInitialized: true,
      isRunning: startupError == null,
      error: startupError,
    );
  }

  @override
  Future<void> stop() async {
    operations.add('stop');
    value = value.copyWith(isRunning: false);
    await stopping?.future;
    if (stopError != null) throw stopError!;
  }

  @override
  // Deliberately substitute native disposal in this controlled camera.
  // ignore: must_call_super
  Future<void> dispose() async {
    operations.add('dispose');
  }
}

void main() {
  late ControlledCamera camera;
  late ScannerSession session;
  late List<MobileScannerException> errors;
  setUp(() {
    camera = ControlledCamera();
    errors = [];
    session = ScannerSession(camera, onError: errors.add);
  });

  for (final value in [
    null,
    '',
    'hello',
    '1234567',
    '123456789',
    '123456789012',
    '12345678901234',
    '１２３４５６７８',
    '12345678\n',
    ' 12345678',
    'https://example.org',
  ]) {
    test(
      'ignores invalid barcode shape ${value == null ? "null" : value.length}',
      () async {
        await session.open(AppLifecycleState.resumed);
        expect(session.accept(value), isFalse);
        expect(session.accept('12345678'), isTrue);
        await session.close();
      },
    );
  }
  for (final ean in ['00000000', '0000000000017']) {
    test(
      'accepts first $ean shape without duplicating backend checksum rules',
      () async {
        await session.open(AppLifecycleState.resumed);
        expect(session.accept(ean), isTrue);
        expect(session.accept(ean), isFalse);
        expect(session.accept('12345678'), isFalse);
        await session.lifecycle(AppLifecycleState.resumed);
        await session.close();
        expect(camera.operations, ['start', 'stop', 'dispose']);
      },
    );
  }
  test('no camera work before open or while initially backgrounded', () async {
    await session.lifecycle(AppLifecycleState.resumed);
    await session.lifecycle(AppLifecycleState.inactive);
    expect(camera.operations, isEmpty);
    expect(session.accept('12345678'), isFalse);
    await session.open(AppLifecycleState.paused);
    expect(camera.operations, isEmpty);
    await session.lifecycle(AppLifecycleState.resumed);
    expect(camera.operations, ['start']);
    await session.close();
  });
  test('permission dialog transitions wait for initial startup', () async {
    camera.starting = Completer<void>();
    final opening = session.open(AppLifecycleState.resumed);
    await Future<void>.delayed(Duration.zero);
    final inactive = session.lifecycle(AppLifecycleState.inactive);
    final resumed = session.lifecycle(AppLifecycleState.resumed);
    final repeated = session.lifecycle(AppLifecycleState.resumed);
    expect(camera.operations, ['start']);
    camera.starting!.complete();
    await Future.wait([opening, inactive, resumed, repeated]);
    expect(camera.operations, ['start']);
    await session.close();
  });
  test('background during startup stops only after camera is ready', () async {
    camera.starting = Completer<void>();
    final opening = session.open(AppLifecycleState.resumed);
    await Future<void>.delayed(Duration.zero);
    final pausing = session.lifecycle(AppLifecycleState.paused);
    expect(camera.operations, ['start']);
    camera.starting!.complete();
    await Future.wait([opening, pausing]);
    expect(camera.operations, ['start', 'stop']);
    await session.close();
  });
  test(
    'all non-resumed states stop once; resume waits for stop completion',
    () async {
      await session.open(AppLifecycleState.resumed);
      for (final state in [
        AppLifecycleState.inactive,
        AppLifecycleState.hidden,
        AppLifecycleState.paused,
        AppLifecycleState.detached,
      ]) {
        await session.lifecycle(state);
        expect(session.accept('12345678'), isFalse);
      }
      expect(camera.operations, ['start', 'stop']);
      await session.lifecycle(AppLifecycleState.resumed);
      camera.stopping = Completer<void>();
      final stopping = session.lifecycle(AppLifecycleState.inactive);
      await Future<void>.delayed(Duration.zero);
      final resume = session.lifecycle(AppLifecycleState.resumed);
      await Future<void>.delayed(Duration.zero);
      expect(camera.operations, ['start', 'stop', 'start', 'stop']);
      camera.stopping!.complete();
      await Future.wait([stopping, resume]);
      expect(camera.operations.last, 'start');
      await session.close();
    },
  );
  test(
    'close during startup waits, stops, disposes once and never restarts',
    () async {
      camera.starting = Completer<void>();
      final opening = session.open(AppLifecycleState.resumed);
      await Future<void>.delayed(Duration.zero);
      final closing = session.close();
      expect(identical(closing, session.close()), isTrue);
      expect(session.accept('12345678'), isFalse);
      final resume = session.lifecycle(AppLifecycleState.resumed);
      camera.starting!.complete();
      await Future.wait([opening, closing, resume]);
      await session.open(AppLifecycleState.resumed);
      await session.lifecycle(AppLifecycleState.inactive);
      expect(camera.operations, ['start', 'stop', 'dispose']);
    },
  );
  test('close before open disposes without starting', () async {
    await session.close();
    await session.open(AppLifecycleState.resumed);
    expect(camera.operations, ['dispose']);
  });
  for (final code in [
    MobileScannerErrorCode.permissionDenied,
    MobileScannerErrorCode.genericError,
  ]) {
    test('controller error $code blocks automatic retry', () async {
      camera.startupError = MobileScannerException(errorCode: code);
      await session.open(AppLifecycleState.resumed);
      await session.lifecycle(AppLifecycleState.inactive);
      await session.lifecycle(AppLifecycleState.resumed);
      expect(session.accept('12345678'), isFalse);
      expect(camera.operations, ['start']);
      await session.close();
      expect(camera.operations, ['start', 'dispose']);
    });
  }
  test('thrown plugin failures are surfaced and prevent restarts', () async {
    camera.thrownStartError = const MobileScannerException(
      errorCode: MobileScannerErrorCode.genericError,
    );
    await session.open(AppLifecycleState.resumed);
    expect(errors, hasLength(1));
    await session.lifecycle(AppLifecycleState.resumed);
    expect(camera.operations, ['start']);
    await session.close();
  });
  test('stop failure is surfaced and disposal still runs', () async {
    await session.open(AppLifecycleState.resumed);
    camera.stopError = const MobileScannerException(
      errorCode: MobileScannerErrorCode.genericError,
    );
    await session.close();
    expect(errors, hasLength(1));
    expect(camera.operations, ['start', 'stop', 'dispose']);
  });
  test('unrelated failures propagate, while close still disposes', () async {
    camera.thrownStartError = StateError('unexpected');
    await expectLater(
      session.open(AppLifecycleState.resumed),
      throwsStateError,
    );
    await expectLater(session.close(), throwsStateError);
    expect(errors, isEmpty);
    expect(camera.operations, ['start', 'dispose']);
  });
  test(
    'permission and generic messages differ and exclude private details',
    () {
      String message(MobileScannerErrorCode code) => scannerErrorMessage(
        MobileScannerException(
          errorCode: code,
          errorDetails: const MobileScannerErrorDetails(
            message: 'private raw details',
          ),
        ),
      );
      final permission = message(MobileScannerErrorCode.permissionDenied);
      final generic = message(MobileScannerErrorCode.genericError);
      expect(permission, contains('device settings'));
      expect(generic, isNot(contains('device settings')));
      for (final text in [permission, generic]) {
        expect(text, contains('enter the EAN manually'));
        expect(text, isNot(contains('private raw details')));
        expect(text, isNot(contains('Exception')));
      }
    },
  );
}
