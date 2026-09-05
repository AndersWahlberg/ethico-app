import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'product_api.dart';

class ProductDetails extends StatelessWidget {
  const ProductDetails({super.key, required this.product, this.openLink});

  final Product product;
  // Tests supply a callback so they never open a real browser.
  final Future<bool> Function(Uri)? openLink;

  Future<void> _openSource(BuildContext context, String url) async {
    try {
      final uri = Uri.tryParse(url);
      if (uri == null ||
          !['https', 'http'].contains(uri.scheme) ||
          uri.host.isEmpty) {
        throw const FormatException('Invalid source URL');
      }
      final opened =
          await (openLink != null
              ? openLink!(uri)
              : launchUrl(uri, mode: LaunchMode.externalApplication));
      if (opened) return;
    } catch (_) {
      // Keep the product visible even when a browser cannot open the source.
    }
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Could not open the source. You can copy its URL below.',
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(product.name, style: Theme.of(context).textTheme.titleLarge),
          Text('Brand: ${product.brand}'),
          Text('Company: ${product.company}'),
          Text(
            'Company role: ${product.companyRole == 'manufacturer' ? 'Manufacturer' : product.companyRole ?? 'Not specified'}',
          ),
          Text('EAN: ${product.ean}'),
          const SizedBox(height: 12),
          if (product.isDemo)
            const Text(
              'Fictional demo product. No verified company information.',
            )
          else ...[
            const Text(
              'Sources',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            if (product.sources.isEmpty)
              const Text('No sources recorded for this product.'),
            for (final source in product.sources) ...[
              const SizedBox(height: 12),
              Text(
                source.title,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(source.supports),
              Text('Source checked: ${source.checkedOn}'),
              TextButton.icon(
                onPressed: () => _openSource(context, source.url),
                icon: const Icon(Icons.open_in_new),
                label: const Text('Open source'),
              ),
              SelectableText(source.url),
            ],
            const SizedBox(height: 12),
            const Text(
              'Sources support the stated product facts, not an ethical rating.',
            ),
          ],
        ],
      ),
    ),
  );
}
