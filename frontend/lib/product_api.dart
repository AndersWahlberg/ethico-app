import 'dart:convert';
import 'package:http/http.dart' as http;

class Product {
  const Product(
    this.ean,
    this.name,
    this.brand,
    this.company, {
    this.companyRole,
    this.isDemo = false,
    this.sources = const [],
  });
  final String ean;
  final String name;
  final String? brand;
  final String? company;
  final String? companyRole;
  final bool isDemo;
  final List<ProductSource> sources;
}

class ProductSource {
  const ProductSource({
    required this.title,
    required this.url,
    this.checkedOn,
    required this.supports,
    this.provider,
    this.retrievedOn,
    this.license,
  });

  final String title;
  final String url;
  final String? checkedOn;
  final String supports;
  final String? provider;
  final String? retrievedOn;
  final String? license;

  factory ProductSource.fromJson(Map<String, dynamic> json) => ProductSource(
    title: json['title'] as String,
    url: json['url'] as String,
    checkedOn: json['checked_on'] as String?,
    supports: json['supports'] as String,
    provider: json['provider'] as String?,
    retrievedOn: json['retrieved_on'] as String?,
    license: json['license'] as String?,
  );
}

class LookupException implements Exception {
  const LookupException(this.message);
  final String message;
}

class ProductApi {
  ProductApi(
    this.client, {
    this.baseUrl = const String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://10.0.2.2:8000',
    ),
  });
  final http.Client client;
  final String baseUrl;

  Future<Product> lookup(String ean) async {
    final response = await client
        .get(Uri.parse('$baseUrl/products/${Uri.encodeComponent(ean)}'))
        .timeout(const Duration(seconds: 10));
    if (response.statusCode == 404) {
      throw const LookupException('Product not found.');
    }
    if (response.statusCode == 422) {
      throw const LookupException(
        'Enter a valid EAN-8 or EAN-13, including its check digit.',
      );
    }
    if (response.statusCode == 503) {
      throw const LookupException(
        'Product information could not be checked right now. Please try again.',
      );
    }
    if (response.statusCode != 200) {
      throw const LookupException(
        'The server could not complete the lookup. Please retry.',
      );
    }
    final json =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    return Product(
      json['ean'] as String,
      json['product_name'] as String,
      json['brand'] as String?,
      json['company'] as String?,
      companyRole: json['company_role'] as String?,
      isDemo: json['is_demo'] as bool? ?? false,
      sources:
          (json['sources'] as List<dynamic>? ?? [])
              .map(
                (source) =>
                    ProductSource.fromJson(source as Map<String, dynamic>),
              )
              .toList(),
    );
  }
}
