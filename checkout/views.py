from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from store.cart_utils import build_cart_items, clear_cart
from store.models import Order, OrderProduct


def send_order_email(order):
    customer_email = order.customer.get("email")
    if not customer_email:
        return

    order_products = OrderProduct.objects.select_related("product").filter(order=order)
    msg_html = render_to_string(
        "emails/order.html",
        {
            "order": order,
            "order_products": order_products,
            "customer": order.customer,
        },
    )
    subject = f"Order #{order.pk} completed successfully"
    message = "Your order has been completed successfully."

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [customer_email],
        html_message=msg_html,
        fail_silently=False,
    )


def checkout(request):
    items, total = build_cart_items(request)
    return render(request, 'checkout.html', {'cart_items': items, 'cart_total': total})


def checkout_complete(request):
    if request.method == "POST":
        items, total = build_cart_items(request)
        if not items:
            return redirect("cart")

        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip()

        if not first_name or not last_name or not email:
            return redirect("checkout")

        try:
            validate_email(email)
        except ValidationError:
            return redirect("checkout")

        customer = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        }

        with transaction.atomic():
            order = Order.objects.create(customer=customer, total=total)
            for item in items:
                for _ in range(item["quantity"]):
                    OrderProduct.objects.create(
                        order=order,
                        product=item["product"],
                        price=item["product"].price,
                    )

        send_order_email(order)

        clear_cart(request)
        request.session["last_order_id"] = order.pk
        return redirect("checkout_complete")

    latest_order = None
    order_id = request.session.get("last_order_id")
    if order_id:
        latest_order = Order.objects.filter(pk=order_id).first()
    return render(request, 'checkout-complete.html', {'latest_order': latest_order})
