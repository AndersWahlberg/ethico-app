import 'dart:convert';
import 'package:http/http.dart' as http;

class Product {
  const Product(this.ean, this.name, this.brand, this.company);
  final String ean;
  final String name;
  final String brand;
  final String company;
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
      throw const LookupException('Product not found in the demo dataset.');
    }
    if (response.statusCode == 422) {
      throw const LookupException(
        'Enter a valid EAN-8 or EAN-13, including its check digit.',
      );
    }
    if (response.statusCode != 200) {
      throw const LookupException(
        'The server could not complete the lookup. Please retry.',
      );
    }
    final json = jsonDecode(response.body) as Map<String, dynamic>;
    return Product(
      json['ean'] as String,
      json['product_name'] as String,
      json['brand'] as String,
      json['company'] as String,
    );
  }
}
