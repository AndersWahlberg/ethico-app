import 'package:flutter/widgets.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

/// Serializes this route's camera work; camera state stays in the controller.
class ScannerSession {
  ScannerSession(this.controller, {required this.onError});

  final MobileScannerController controller;
  final void Function(MobileScannerException) onError;
  Future<void> _pending = Future<void>.value();
  Future<void>? _closing;
  bool _ready = false;
  bool _resumed = false;
  bool _finished = false;
  bool _failed = false;

  Future<void> open(AppLifecycleState? state) {
    if (_finished) return _pending;
    _ready = true;
    _resumed = state == null || state == AppLifecycleState.resumed;
    return _schedule();
  }

  Future<void> lifecycle(AppLifecycleState state) {
    if (_finished) return _pending;
    _resumed = state == AppLifecycleState.resumed;
    return _schedule();
  }

  Future<void> fail(MobileScannerException error) {
    if (_finished) return _pending;
    _failed = true;
    onError(error);
    return _schedule();
  }

  bool accept(String? value) {
    if (_finished ||
        !_ready ||
        !_resumed ||
        _failed ||
        controller.value.error != null ||
        value == null ||
        !RegExp(r'^(?:[0-9]{8}|[0-9]{13})$').hasMatch(value)) {
      return false;
    }
    _finished = true;
    return true;
  }

  Future<void> _schedule() =>
      _pending = _pending.then((_) async {
        if (!_ready || _closing != null) return;
        try {
          final state = controller.value;
          if (_finished || !_resumed || _failed) {
            if (state.isInitialized && state.isRunning) await controller.stop();
          } else if (!state.isRunning &&
              state.error == null &&
              (!state.isInitialized || state.hasCameraPermission)) {
            // The first start requests permission. Further events wait for it,
            // then inspect actual controller state, including permission errors.
            await controller.start();
          }
        } on MobileScannerException catch (error) {
          // Surface plugin failures safely, and never retry a failed session.
          // Programming/unrelated errors deliberately propagate to the caller.
          _failed = true;
          onError(error);
        }
      });

  Future<void> close() {
    _finished = true; // Synchronous: frames/resume cannot race with cleanup.
    return _closing ??= _pending
        .then((_) async {
          try {
            if (controller.value.isInitialized && controller.value.isRunning) {
              await controller.stop();
            }
          } on MobileScannerException catch (error) {
            onError(error);
          }
        })
        .whenComplete(() async {
          try {
            await controller.dispose();
          } on MobileScannerException catch (error) {
            onError(error);
          }
        });
  }
}

String scannerErrorMessage(MobileScannerException error) =>
    error.errorCode == MobileScannerErrorCode.permissionDenied
        ? 'Camera permission denied. Allow camera access in device settings, or go back and enter the EAN manually.'
        : 'Camera unavailable. Go back and enter the EAN manually.';
