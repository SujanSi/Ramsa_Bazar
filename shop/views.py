from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
import random


# Create your views here.
def home(request):
    categories = Category.objects.all().order_by('name')
    # Get all products
    products = Product.objects.all()
    
    # Select a random product for initial display (optional)
    initial_products = products[:8]

    context = {
        'categories': categories,
        'products': products,
        'initial_products': initial_products,
    }

    return render(request, "home.html", context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product-detail.html', {'product': product})

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

        cart = get_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return redirect('shop:cart') 

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@login_required
def view_cart(request):
    """Display cart items."""
    cart = get_cart(request.user)  
    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        item.total_price = item.product.price * item.quantity

    cart_total = sum(item.total_price for item in cart_items)


    return render(request, "shop/cart.html", {"cart_items": cart_items, "cart_total": cart_total})

@login_required
def update_cart(request, item_id):
    """Update the quantity of a cart item."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = min(quantity, cart_item.product.stock or 100)
            cart_item.save()
    return redirect('shop:cart')

@login_required
def remove_from_cart(request, item_id):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('shop:cart')

@login_required
def checkout(request):
    """Handle checkout process."""
    if request.method == "POST":
        cart = get_cart(request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items:
            return redirect('shop:cart')

        # Extract form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        country = request.POST.get('country', '').strip()
        state = request.POST.get('state', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()

        # Validate required fields
        if not first_name or not last_name or not country or not state or not postal_code:
            return redirect('shop:cart')  # Redirect back if validation fails

        # Create Checkout instance
        checkout = Checkout.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=request.user.email or "unknown@example.com",
            address=f"{country}, {state}",
            city=state,
            postal_code=postal_code,
            phone=request.user.profile.phone if hasattr(request.user, 'profile') else "N/A",
        )

        return redirect('shop:order_confirmation' )

    return redirect('shop:cart')


from decimal import Decimal
@login_required
def order_confirmation(request):
    # Get the user's cart
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        return redirect('shop:cart')

    # Get the latest checkout instance for the user
    try:
        checkout = Checkout.objects.filter(user=request.user).latest('created_at')
    except Checkout.DoesNotExist:
        return redirect('shop:cart')

    # Calculate subtotal (sum of Decimal values)
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    
    # Define shipping and tax as Decimal
    shipping = Decimal('4.00')  # Convert float to Decimal
    tax = Decimal('0.00')       # Convert float to Decimal
    grand_total = subtotal + shipping + tax

    # Context to pass to the template
    context = {
        'checkout': checkout,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
        'message': 'Please review your order before confirmation.',
    }

    return render(request, 'shop/checkout.html', context)


import logging
from django.db import transaction
from django.http import HttpResponse
import requests
import uuid

# Set up logging
logger = logging.getLogger(__name__)
@login_required
def place_order(request):
    if request.method == "POST":
        logger.info(f"Place order initiated for user: {request.user}")
        cart = get_cart(request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items:
            logger.warning("Cart is empty, redirecting to cart.")
            return redirect('shop:cart')

        try:
            checkout = Checkout.objects.filter(user=request.user).latest('created_at')
            logger.info(f"Checkout retrieved: {checkout}")
        except Checkout.DoesNotExist:
            logger.error("No checkout found, redirecting to cart.")
            return redirect('shop:cart')

        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        shipping = Decimal('4.00')
        grand_total = subtotal + shipping

        payment_method = request.POST.get('payment_method')
        logger.info(f"Payment method selected: {payment_method}")

        valid_payment_methods = [key for key, value in Order.Payment_Method]
        if payment_method not in valid_payment_methods:
            logger.error(f"Invalid payment method: {payment_method}. Valid options: {valid_payment_methods}")
            return redirect('shop:order_confirmation')

        # Store data in session
        request.session['grand_total'] = float(grand_total)
        request.session['cart_items'] = [
            {
                'product_name': item.product.name,
                'price': float(item.product.price),
                'quantity': item.quantity,
                'total_price': float(item.product.price * item.quantity)
            } for item in cart_items
        ]
        logger.info("Session data stored: grand_total and cart_items")

        if payment_method == 'Khalti':
            print("Redirecting to khalti_payment")
            return redirect('shop:khalti_payment')  # Ensure this matches your URL name
        else:
            try:
                with transaction.atomic():
                    for item in cart_items:
                        Order.objects.create(
                            product=item.product.name,
                            price=item.product.price,
                            quantity=item.quantity,
                            total_price=item.product.price * item.quantity,
                            payment_method=payment_method,
                            status="Pending",
                        )
                    cart_items.delete()
                    logger.info("Cart cleared successfully.")
            except Exception as e:
                logger.error(f"Failed to create orders: {str(e)}")
                return redirect('shop:order_confirmation')

            return render(request, 'shop/checkout.html', {
                'message': 'Order has been placed successfully!',
                'checkout': checkout,
                'grand_total': grand_total,
            })

    logger.warning("Non-POST request to place_order, redirecting to cart.")
    return redirect('shop:cart')

def khalti_payment(request):
    logger.info("Entered khalti_payment view")
    transaction_uuid = uuid.uuid4()
    print(transaction_uuid)
    grand_total = request.session.get('grand_total', 0)
    amount = int(grand_total * 100)  # Convert to paisa

    if grand_total == 0:
        logger.error("No grand_total found in session, redirecting to cart")
        return redirect('shop:cart')

    context = {
        'purchase_order_id': str(transaction_uuid),
        'amount': amount,
        'return_url': request.build_absolute_uri('/shop/khalti_verify/'),
    }
    logger.info(f"Khalti payment context prepared: {context}")
    return render(request, 'shop/khalti_payment.html', context)

import json

def submit_khalti_payment(request):
    logger.info("Entered submit_khalti_payment view")
    if request.method == 'POST':
        purchase_order_id = request.POST.get('purchase_order_id')
        amount = request.POST.get('amount')
        return_url = request.POST.get('return_url')

        logger.info(f"Received POST data: purchase_order_id={purchase_order_id}, amount={amount}, return_url={return_url}")

        if not all([purchase_order_id, amount, return_url]):
            logger.error("Missing required POST data")
            return HttpResponse("Missing payment data", status=400)

        payload = {
            "return_url": return_url,
            "website_url": "http://localhost:8000",  # Replace with your actual website URL
            "amount": amount,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "Order Payment",
            "customer_info": {
                "name": request.user.full_name,
                "email": request.user.email,
                "phone": "9800000001"  # Replace with actual user phone
            }
        }

        headers = {
            'Authorization': 'Key 133eff2bf18d4888a8e0e699ede0f774',  # Replace with your Khalti secret key
            'Content-Type': 'application/json',
        }

        url = "https://a.khalti.com/api/v2/epayment/initiate/"
        try:
            response = requests.post(url, headers=headers, json=payload)
            logger.info(f"Khalti API response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                new_res = json.loads(response.text)
                payment_url = new_res.get('payment_url')
                if payment_url:
                    logger.info(f"Redirecting to Khalti payment URL: {payment_url}")
                    return redirect(payment_url)
                else:
                    logger.error("No payment_url in Khalti response")
                    return redirect('shop:cart')
            else:
                logger.error(f"Khalti API failed with status {response.status_code}: {response.text}")
                return redirect('shop:cart')
        except Exception as e:
            logger.error(f"Error during Khalti API call: {str(e)}")
            return redirect('shop:cart')

    logger.warning("Non-POST request to submit_khalti_payment")
    return HttpResponse("Invalid Request", status=405)

@login_required
def khalti_verify(request):
    if request.method == 'GET':
        pidx = request.GET.get('pidx')
        if not pidx:
            logger.error("No pidx provided for Khalti verification")
            return redirect('shop:cart')

        # Verify payment with Khalti
        headers = {
            'Authorization': 'Key 133eff2bf18d4888a8e0e699ede0f774',  # Replace with your Khalti secret key
            'Content-Type': 'application/json',
        }
        url = "https://a.khalti.com/api/v2/epayment/lookup/"
        payload = {"pidx": pidx}
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            result = json.loads(response.text)
            if result.get('status') == 'Completed':
                # Payment successful, create orders
                cart_items = request.session.get('cart_items', [])
                grand_total = Decimal(request.session.get('grand_total', 0))

                try:
                    with transaction.atomic():
                        for item in cart_items:
                            Order.objects.create(
                                product=item['product_name'],
                                price=Decimal(item['price']),
                                quantity=item['quantity'],
                                total_price=Decimal(item['total_price']),
                                payment_method='khalti',
                                status="Pending",
                            )
                        # Clear cart (assuming cart_items.delete() clears the cart in DB)
                        CartItem.objects.filter(cart=get_cart(request.user)).delete()
                        logger.info("Cart cleared successfully after Khalti payment.")

                        # Clean up session
                        del request.session['cart_items']
                        del request.session['grand_total']

                    return render(request, 'shop/checkout.html', {
                        'message': 'Order has been placed successfully via Khalti!',
                        'grand_total': grand_total,
                    })
                except Exception as e:
                    logger.error(f"Failed to create orders after Khalti payment: {str(e)}")
                    return redirect('shop:order_confirmation')
            else:
                logger.error(f"Khalti payment not completed: {result}")
                return redirect('shop:cart')
        else:
            logger.error(f"Khalti verification failed: {response.text}")
            return redirect('shop:cart')

    return HttpResponse("Invalid Request")