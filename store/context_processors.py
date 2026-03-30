from .models import Category
from .cart_utils import get_cart_item_count


def navbar_categories(request):
    categories = Category.objects.order_by("order", "name")
    return {
        "navbar_categories": categories,
        "cart_item_count": get_cart_item_count(request),
    }
