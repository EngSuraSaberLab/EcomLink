from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from store.models import Category, Order, Product


class TestCheckoutValidation(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Checkout")
        self.product = Product.objects.create(
            name="Checkout Book",
            short_description="Short",
            description="Desc",
            image=SimpleUploadedFile("checkout.jpg", b"fake-image-bytes", content_type="image/jpeg"),
            price="15.00",
            category=self.category,
        )

    def _add_item_to_session_cart(self):
        session = self.client.session
        session["cart"] = {str(self.product.pk): 1}
        session.save()

    def test_checkout_complete_rejects_empty_customer_fields(self):
        self._add_item_to_session_cart()
        before = Order.objects.count()

        response = self.client.post(
            reverse("checkout_complete"),
            {"first_name": "", "last_name": "", "email": ""},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("checkout"))
        self.assertEqual(Order.objects.count(), before)

    def test_checkout_complete_rejects_invalid_email(self):
        self._add_item_to_session_cart()
        before = Order.objects.count()

        response = self.client.post(
            reverse("checkout_complete"),
            {"first_name": "A", "last_name": "B", "email": "invalid-email"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("checkout"))
        self.assertEqual(Order.objects.count(), before)
