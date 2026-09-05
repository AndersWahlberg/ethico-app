import 'dart:async';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'product_api.dart';
import 'scanner_screen.dart';

void main() => runApp(const EthicoApp());

class EthicoApp extends StatelessWidget {
  const EthicoApp({super.key, this.api});
  final ProductApi? api;

  @override
  Widget build(BuildContext context) =>
      MaterialApp(title: 'Ethico', home: LookupScreen(api: api));
}

class LookupScreen extends StatefulWidget {
  const LookupScreen({super.key, this.api});
  final ProductApi? api;

  @override
  State<LookupScreen> createState() => _LookupScreenState();
}

class _LookupScreenState extends State<LookupScreen> {
  final _ean = TextEditingController();
  http.Client? _ownedClient;
  late final ProductApi _api;
  Product? _product;
  String? _error;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _api = widget.api ?? ProductApi(_ownedClient = http.Client());
  }

  @override
  void dispose() {
    _ean.dispose();
    _ownedClient?.close();
    super.dispose();
  }

  Future<void> _lookup() async {
    if (_loading) return;
    final ean = _ean.text.trim();
    setState(() {
      _product = null;
      _error = null;
    });
    if (!RegExp(r'^(?:[0-9]{8}|[0-9]{13})$').hasMatch(ean)) {
      setState(() => _error = 'Enter 8 or 13 digits.');
      return;
    }
    setState(() => _loading = true);
    try {
      final product = await _api.lookup(ean);
      if (mounted) setState(() => _product = product);
    } on LookupException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } on TimeoutException {
      if (mounted) {
        setState(() => _error = 'The request timed out. Please retry.');
      }
    } catch (_) {
      if (mounted) {
        setState(
          () =>
              _error =
                  'Could not load the product. Check your connection and retry.',
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _scan() async {
    final ean = await Navigator.of(
      context,
    ).push<String>(MaterialPageRoute(builder: (_) => const ScannerScreen()));
    if (!mounted || ean == null) return;
    _ean.text = ean;
    await _lookup();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Ethico')),
    body: SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          const Text('Scan a product or enter its EAN.'),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: _loading ? null : _scan,
            icon: const Icon(Icons.qr_code_scanner),
            label: const Text('Scan barcode'),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _ean,
            enabled: !_loading,
            keyboardType: TextInputType.number,
            textInputAction: TextInputAction.search,
            onSubmitted: (_) => _lookup(),
            decoration: const InputDecoration(
              labelText: 'EAN code',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: _loading ? null : _lookup,
            child: const Text('Look up product'),
          ),
          const SizedBox(height: 16),
          const Text(
            'Demo dataset only. Products and companies are fictional.',
          ),
          const Text('Try: 2000000000015'),
          if (_loading)
            const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            ),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Text(_error!, semanticsLabel: _error),
            ),
          if (_product != null)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _product!.name,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    Text('Brand: ${_product!.brand}'),
                    Text('Company: ${_product!.company}'),
                    Text('EAN: ${_product!.ean}'),
                  ],
                ),
              ),
            ),
        ],
      ),
    ),
  );
}
