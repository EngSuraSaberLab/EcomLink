from django.contrib import admin
from .models import Product,Author,Order,OrderProduct ,Category, Slider

admin.site.register(Product)
admin.site.register(Author)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Category)
admin.site.register(Slider)


