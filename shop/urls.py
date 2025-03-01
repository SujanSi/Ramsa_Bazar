from django.urls import path
from .views import *

app_name = 'shop'

urlpatterns = [
    path('', home, name='home'),
    path('product/<int:product_id>/',product_detail, name='product_detail'),
    path('category/<int:category_id>/', category_products, name='category_products'),
    path('cart/', view_cart, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('order-confirmation/', order_confirmation, name='order_confirmation'),
    path('place-order/', place_order, name='place_order'),
    path('khalti_verify', khalti_verify, name='khalti_verify'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),

    path('orders/', order_list, name='order_list'),


]
