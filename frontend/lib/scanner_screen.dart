import 'dart:async';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen>
    with WidgetsBindingObserver {
  final _controller = MobileScannerController(
    formats: [BarcodeFormat.ean8, BarcodeFormat.ean13],
    detectionSpeed: DetectionSpeed.noDuplicates,
  );
  bool _returned = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (!_controller.value.hasCameraPermission || _returned) return;
    if (state == AppLifecycleState.resumed) {
      unawaited(_controller.start());
    } else if (state == AppLifecycleState.inactive) {
      unawaited(_controller.stop());
    }
  }

  void _onDetect(BarcodeCapture capture) {
    if (_returned || !mounted) return;
    for (final barcode in capture.barcodes) {
      final value = barcode.rawValue;
      if (value != null &&
          RegExp(r'^(?:[0-9]{8}|[0-9]{13})$').hasMatch(value)) {
        _returned = true;
        Navigator.of(context).pop(value);
        return;
      }
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    unawaited(_controller.dispose());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Scan EAN barcode')),
    body: Column(
      children: [
        Expanded(
          child: MobileScanner(
            controller: _controller,
            onDetect: _onDetect,
            errorBuilder:
                (context, error, child) => const Center(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Text(
                      'Camera unavailable. Allow camera access in device settings, or go back and enter the EAN manually.',
                    ),
                  ),
                ),
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
  );
}
