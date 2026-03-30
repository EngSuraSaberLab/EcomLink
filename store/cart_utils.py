from .models import Product


def _to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_cart(raw_cart):
    quantities = {}

    if isinstance(raw_cart, dict):
        for key, value in raw_cart.items():
            try:
                product_id = int(key)
                qty = int(value)
            except (TypeError, ValueError):
                continue
            if qty > 0:
                quantities[product_id] = qty
    elif isinstance(raw_cart, list):
        for value in raw_cart:
            try:
                product_id = int(value)
            except (TypeError, ValueError):
                continue
            quantities[product_id] = quantities.get(product_id, 0) + 1

    return quantities


def get_cart_quantities(request):
    return _normalize_cart(request.session.get("cart", {}))


def save_cart_quantities(request, quantities):
    request.session["cart"] = {str(k): int(v) for k, v in quantities.items() if int(v) > 0}
    request.session.modified = True


def get_cart_item_count(request):
    return sum(get_cart_quantities(request).values())


def add_to_cart(request, product_id, quantity=1):
    quantities = get_cart_quantities(request)
    quantity = max(_to_int(quantity, 1), 1)
    quantities[product_id] = quantities.get(product_id, 0) + quantity
    save_cart_quantities(request, quantities)


def update_cart_item(request, product_id, quantity):
    quantities = get_cart_quantities(request)
    quantity = _to_int(quantity, 0)
    if quantity <= 0:
        quantities.pop(product_id, None)
    else:
        quantities[product_id] = quantity
    save_cart_quantities(request, quantities)


def remove_from_cart(request, product_id):
    quantities = get_cart_quantities(request)
    quantities.pop(product_id, None)
    save_cart_quantities(request, quantities)


def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True


def build_cart_items(request):
    quantities = get_cart_quantities(request)
    products = Product.objects.filter(pk__in=quantities.keys()).select_related("author", "category")
    products_by_id = {product.pk: product for product in products}

    items = []
    total = 0
    for product_id, qty in quantities.items():
        product = products_by_id.get(product_id)
        if not product:
            continue
        line_total = product.price * qty
        total += line_total
        items.append(
            {
                "product": product,
                "quantity": qty,
                "line_total": line_total,
            }
        )

    return items, total
