from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *


# Create your views here.
def home(request):
    return render(request, "home.html") 

@login_required
def product_list(request):
    products = Product.objects.filter(vendor=request.user)
    return render(request, 'vendor/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'vendor/product_detail.html', {'product': product})

def get_cart(user):
    """Retrieve or create a cart for the user."""
    cart, created = CartItem.objects.get_or_create(user=user)
    return cart

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        print(f"Adding quantity: {quantity} for product {product.name}")

        cart = get_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return redirect('vendor:cart') 

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@login_required
def view_cart(request):
    """Display cart items."""
    cart = get_cart(request.user)  
    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        item.total_price = item.product.price * item.quantity

    cart_total = sum(item.total_price for item in cart_items)


    return render(request, "vendor/cart.html", {"cart_items": cart_items, "cart_total": cart_total})

@login_required
def remove_from_cart(request, item_id):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('vendor:cart')