/// Model for an inventory item
class Item {
  final String id;
  final String name;
  final String description;
  final String? location;
  final String? requiredFor;
  final bool hidden;
  final int quantity;
  final bool transferable;

  const Item({
    required this.id,
    required this.name,
    required this.description,
    this.location,
    this.requiredFor,
    this.hidden = false,
    this.quantity = 1,
    this.transferable = true,
  });

  factory Item.fromJson(Map<String, dynamic> json) {
    return Item(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      location: json['location'] as String?,
      requiredFor: json['required_for'] as String?,
      hidden: json['hidden'] as bool? ?? false,
      quantity: json['quantity'] as int? ?? 1,
      transferable: json['transferable'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      if (location != null) 'location': location,
      if (requiredFor != null) 'required_for': requiredFor,
      'hidden': hidden,
      'quantity': quantity,
      'transferable': transferable,
    };
  }

  @override
  String toString() => 'Item($name)';
}
