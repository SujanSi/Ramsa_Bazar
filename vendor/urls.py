from django.urls import path
from .views import *

app_name = 'vendor'

urlpatterns = [
    path('',home, name='home'),
    path('products/', product_list, name='product_list'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('products/add/', add_product, name='add_product'),
    path('products/edit/<int:product_id>/', update_product, name='update_product'),
    path('products/delete/<int:product_id>/', delete_product, name='delete_product'),

    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('cart/', view_cart, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),

]
