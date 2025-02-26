from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product
from .forms import ProductForm
from .models import Cart, CartItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def vendor_dashboard(request):
    return render(request, 'vendor/dashboard.html')


@login_required
def product_list(request):
    # Fetch only the products for the logged-in vendor
    products = Product.objects.filter(vendor=request.user)
    
    return render(request, 'vendor/product_list.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'vendor/product_detail.html', {'product': product})


@login_required
def add_product(request):
    if not request.user.kyc_verified:
        messages.error(request, "Your KYC is not approved. You cannot add products.")
        return redirect('vendor:vendor_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('vendor:product_list')
    else:
        form = ProductForm()

    return render(request, 'vendor/add_product.html', {'form': form})

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)

    if not request.user.kyc_verified:
        messages.error(request, "Your KYC is not approved. You cannot edit products.")
        return redirect('vendor:vendor_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('vendor:product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'vendor/update_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)

    if not request.user.kyc_verified:
        messages.error(request, "Your KYC is not approved. You cannot delete products.")
        return redirect('vendor:vendor_dashboard')

    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('vendor:product_list')

    return render(request, 'vendor/delete_product.html', {'product': product})


def home(request):
    producted = Product.objects.all()  # Fetch all vendor products
    return render(request, 'home.html', {'producted': producted})



def get_cart(user):
    """Retrieve or create a cart for the user."""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        print(f"Adding quantity: {quantity} for product {product.name}")

        # Get or create a cart for the user
        cart = get_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            # Update the existing cart item’s quantity
            cart_item.quantity += quantity
        else:
            # If new item, set the quantity to the passed value
            cart_item.quantity = quantity
        cart_item.save()

        # After adding the item to the cart, redirect to the cart page
        return redirect('vendor:cart')  # Redirect to the cart page

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@login_required
def view_cart(request):
    """Display cart items."""
    cart = get_cart(request.user)  # Assuming this function fetches the user's cart
    cart_items = CartItem.objects.filter(cart=cart)

    # Calculate total price for each cart item
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