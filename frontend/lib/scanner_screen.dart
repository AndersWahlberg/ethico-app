import 'dart:async';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'scanner_session.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen>
    with WidgetsBindingObserver {
  final _controller = MobileScannerController(
    autoStart: false,
    formats: [BarcodeFormat.ean8, BarcodeFormat.ean13],
    detectionSpeed: DetectionSpeed.noDuplicates,
    returnImage: false,
  );
  late final ScannerSession _session;
  StreamSubscription<BarcodeCapture>? _subscription;
  MobileScannerException? _error;
  bool _leaving = false;

  @override
  void initState() {
    super.initState();
    _session = ScannerSession(_controller, onError: _onError);
    WidgetsBinding.instance.addObserver(this);
    _subscription = _controller.barcodes.listen(
      _onDetect,
      onError: (Object error, StackTrace stack) {
        if (error is MobileScannerBarcodeException) {
          unawaited(
            _session.fail(
              const MobileScannerException(
                errorCode: MobileScannerErrorCode.genericError,
              ),
            ),
          );
        } else if (error is MobileScannerException) {
          unawaited(_session.fail(error));
        } else {
          Error.throwWithStackTrace(error, stack);
        }
      },
    );
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted && !_leaving) {
        unawaited(_session.open(WidgetsBinding.instance.lifecycleState));
      }
    });
  }

  void _onError(MobileScannerException error) {
    if (mounted && !_leaving) setState(() => _error = error);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    unawaited(_session.lifecycle(state));
  }

  void _onDetect(BarcodeCapture capture) {
    if (_leaving || !mounted) return;
    for (final barcode in capture.barcodes) {
      if (_session.accept(barcode.rawValue)) {
        unawaited(_finish(barcode.rawValue));
        return;
      }
    }
  }

  Future<void> _finish(String? ean) async {
    if (_leaving) return;
    setState(() => _leaving = true);
    // close latches synchronously, before cancelling capture delivery.
    final closing = _session.close();
    unawaited(_subscription?.cancel());
    await closing;
    if (mounted) Navigator.of(context).pop(ean);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    unawaited(_subscription?.cancel());
    unawaited(_session.close());
    super.dispose();
  }

  Widget _errorBody(MobileScannerException error) => Center(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Text(scannerErrorMessage(error)),
    ),
  );

  @override
  Widget build(BuildContext context) => PopScope<String>(
    canPop: false,
    onPopInvokedWithResult: (didPop, result) {
      if (!didPop) unawaited(_finish(null));
    },
    child: Scaffold(
      appBar: AppBar(title: const Text('Scan EAN barcode')),
      body: Column(
        children: [
          Expanded(
            child:
                _leaving
                    ? const SizedBox.shrink()
                    : _error != null
                    ? _errorBody(_error!)
                    : MobileScanner(
                      controller: _controller,
                      errorBuilder:
                          (context, error, child) => _errorBody(error),
                    ),
          ),
          const SafeArea(
            top: false,
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Text('Point the camera at an EAN-8 or EAN-13 barcode.'),
            ),
          ),
        ],
      ),
    ),
  );
}
