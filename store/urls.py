from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category/', views.category, name='category'),
    path('category/<slug:slug>/', views.category, name='category_detail'),
    path('category/<int:pk>/', views.category, name='category_detail'),
    path('product/', views.product, name='product'),
    path('product/<slug:slug>/', views.product, name='product_detail'),
    path('product/<int:pk>/', views.product, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<slug:slug>/', views.cart_add, name='cart_add'),
    path('cart/update/<slug:slug>/', views.cart_update, name='cart_update'),
    path('cart/remove/<slug:slug>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('contact/', views.contact, name='contact'),
]
