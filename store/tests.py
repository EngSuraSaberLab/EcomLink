from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class TestCartRedirectSecurity(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Security")
        self.product = Product.objects.create(
            name="Safe Book",
            short_description="Short",
            description="Desc",
            image=SimpleUploadedFile("book.jpg", b"fake-image-bytes", content_type="image/jpeg"),
            price="10.00",
            category=self.category,
        )

    def test_cart_add_blocks_external_next_redirect(self):
        response = self.client.post(
            reverse("cart_add", kwargs={"slug": self.product.slug}),
            {"quantity": "1", "next": "https://evil.example"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("cart"))
