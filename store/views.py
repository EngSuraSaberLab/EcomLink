from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.db.models import Q
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Category, Product, Slider
from .cart_utils import (
    add_to_cart,
    build_cart_items,
    clear_cart,
    get_cart_item_count,
    remove_from_cart,
    update_cart_item,
)

def index(request):
    products = Product.objects.select_related('author', 'category').order_by('-created_at')[:8]
    sliders = Slider.objects.order_by('order', '-created_at')
    return render(request, 'index.html', {'products': products, 'sliders': sliders})


def category(request, slug=None, pk=None):
    categories = Category.objects.order_by('order', 'name')
    products = Product.objects.select_related('author', 'category').order_by('-created_at')
    selected_category = None
    search_query = (request.GET.get('q') or '').strip()
    category_filter = (request.GET.get('category') or '').strip()

    if slug is not None:
        selected_category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=selected_category)
    elif pk is not None:
        selected_category = get_object_or_404(Category, pk=pk)
        products = products.filter(category=selected_category)
    elif category_filter:
        selected_category = get_object_or_404(Category, slug=category_filter)
        products = products.filter(category=selected_category)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(short_description__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(author__name__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    context = {
        'categories': categories,
        'products': products,
        'selected_category': selected_category,
        'search_query': search_query,
    }
    return render(request, 'category.html', context)


def product(request, slug=None, pk=None):
    if slug is not None:
        current_product = get_object_or_404(
            Product.objects.select_related('author', 'category'),
            slug=slug,
        )
    elif pk is not None:
        current_product = get_object_or_404(
            Product.objects.select_related('author', 'category'),
            pk=pk,
        )
    else:
        current_product = (
            Product.objects.select_related('author', 'category')
            .order_by('-created_at')
            .first()
        )

    related_products = Product.objects.none()
    if current_product:
        related_products = (
            Product.objects.select_related('author', 'category')
            .filter(category=current_product.category)
            .exclude(pk=current_product.pk)
            .order_by('-created_at')[:4]
        )

    return render(
        request,
        'product.html',
        {
            'product': current_product,
            'related_products': related_products,
        },
    )


def cart(request):
    items, total = build_cart_items(request)
    return render(request, 'cart.html', {'cart_items': items, 'cart_total': total})


def cart_add(request, slug):
    if request.method != "POST":
        return redirect("product_detail", slug=slug)
    product = get_object_or_404(Product, slug=slug)
    quantity = request.POST.get("quantity", 1)
    add_to_cart(request, product.pk, quantity)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "cart_count": get_cart_item_count(request)})
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    if next_url and not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = None
    return redirect(next_url or "cart")


def cart_update(request, slug):
    if request.method != "POST":
        return redirect("cart")
    product = get_object_or_404(Product, slug=slug)
    quantity = request.POST.get("quantity", 1)
    update_cart_item(request, product.pk, quantity)
    return redirect("cart")


def cart_remove(request, slug):
    if request.method != "POST":
        return redirect("cart")
    product = get_object_or_404(Product, slug=slug)
    remove_from_cart(request, product.pk)
    return redirect("cart")


def cart_clear(request):
    if request.method == "POST":
        clear_cart(request)
    return redirect("cart")


def contact(request):
    categories = Category.objects.order_by('order', 'name')[:6]
    featured_products = Product.objects.select_related('author').order_by('-created_at')[:3]
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'contact.html', context)
