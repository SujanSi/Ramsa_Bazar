from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from .forms import *
from django.db.models import Q
from django.db.models import Count

# Create your views here.
now = timezone.now()

def home(request):
    categories = Category.objects.all().order_by('name')

    # Get products added in the last 30 days
    time_threshold = now - timedelta(days=30)
    new_arrival = Product.objects.filter(created_at__gte=time_threshold)

    # Get only selling products
    selling_products = Product.objects.filter(product_type='selling')
    initial_products = selling_products[:5]
    
    featured_products = Product.objects.filter(features=True)[:5]
    brand=Brand.objects.all() 

    products_with_comment_count = Product.objects.annotate(comment_count=Count('reviews'))


    context = {
        'categories': categories,
        'selling_products': selling_products,
        'initial_products': initial_products,
        'new_arrival': new_arrival,
        'featured_products': featured_products,
        'brand': brand,
        'products_with_comment_count': products_with_comment_count,
    }

    return render(request, "home.html", context)

def search_view(request):
    query = request.POST.get('query', '') if request.method == 'POST' else request.GET.get('query', '')
    category_id = request.POST.get('category_id', '') if request.method == 'POST' else request.GET.get('category_id', '')
    
    products = Product.objects.all().select_related('categories')  # Optimize query with select_related
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(additional_information__icontains=query) |
            Q(categories__name__icontains=query)
        )
    
    category = None
    if category_id:
        products = products.filter(categories__id=category_id)
        category = get_object_or_404(Category, id=category_id)
    
    # Group products by category
    products_by_category = {}
    for product in products:
        category_name = product.categories.name if product.categories else "Uncategorized"
        if category_name not in products_by_category:
            products_by_category[category_name] = []
        products_by_category[category_name].append(product)
    
    categories = Category.objects.all()
    
    context = {
        'products_by_category': products_by_category,  # Dictionary of category: products
        'query': query,
        'category_id': category_id,
        'categories': categories,
        'category': category,
    }
    return render(request, 'shop/search.html', context)



def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Reviews.objects.filter(product=product).order_by('-created_at')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Save the new review
            review = form.save(commit=False)
            review.product = product  # Associate the review with the product
            review.save()
            return redirect('shop:product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'shop/product-detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        })


@login_required
def chat_with_vendor(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user == product.vendor:
        return redirect('shop:product_detail', product_id=product.id)  # Vendors can't chat with themselves
    
    # Corrected filter syntax
    chat_messages = ChatMessage.objects.filter(
        product=product
    ).filter(
        Q(sender=request.user, receiver=product.vendor) | Q(sender=product.vendor, receiver=request.user)
    ).order_by('created_at')

    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            ChatMessage.objects.create(
                sender=request.user,
                receiver=product.vendor,
                product=product,
                message=message_content
            )
            return redirect('shop:chat_with_vendor', product_id=product.id)

    return render(request, 'shop/chat_with_vendor.html', {
        'product': product,
        'chat_messages': chat_messages,
    })


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(categories=category)
    categories = Category.objects.all().order_by('name')
    
    print(f"Category ID: {category_id}")
    print(f"Category Name: {category.name}")
    print(f"Number of Products: {products.count()}")
    
    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'shop/category_products.html', context)


def get_cart(user):
    """Retrieve or create a cart for the user."""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Prevent vendors from adding their own products to the cart
    if request.user == product.vendor:
        messages.error(request, "You cannot purchase your own product.")
        return redirect('shop:product_detail', product_id=product.id)
    
    
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
import json

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
                'product_id': item.product.id,
                'product_name': item.product.name,
                'price': float(item.product.price),
                'quantity': item.quantity,
                'total_price': float(item.product.price * item.quantity)
            } for item in cart_items
        ]
        logger.info("Session data stored: grand_total and cart_items")

        if payment_method == 'Khalti':
            # Directly initiate Khalti payment
            logger.info("Initiating Khalti payment directly")
            transaction_uuid = uuid.uuid4()
            amount = int(grand_total * 100)  # Convert to paisa

            payload = {
                "return_url": request.build_absolute_uri('/khalti_verify'),
                "website_url": "http://localhost:8000",  # Replace with your actual website URL
                "amount": amount,
                "purchase_order_id": str(transaction_uuid),
                "purchase_order_name": "Order Payment",
                "customer_info": {
                    "name": request.user.full_name,
                    "email": request.user.email,
                    "phone": "9800000001"  # Replace with actual user phone
                }
            }

            headers = {
                'Authorization': 'Key 28808af5b2f74228b7da6ba0a27b1e7e',  # Replace with your Khalti secret key
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
        else:
            try:
                with transaction.atomic():
                    for item in cart_items:
                        Order.objects.create(
                            user=request.user,
                            product=item.product,
                            price=item.product.price,
                            quantity=item.quantity,
                            total_price=item.product.price * item.quantity,
                            payment_method=payment_method,
                            status="pending",
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

from django.core.mail import send_mail
@login_required
def khalti_verify(request):
    if request.method == 'GET':
        pidx = request.GET.get('pidx')
        if not pidx:
            logger.error("No pidx provided for Khalti verification")
            return redirect('shop:cart')

        # Verify payment with Khalti
        headers = {
            'Authorization': 'Key 28808af5b2f74228b7da6ba0a27b1e7e',  # Replace with your Khalti secret key
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
                order_list = []

                try:
                    with transaction.atomic():
                        for item in cart_items:
                            product = Product.objects.get(id=item['product_id'])  # Fetch product using ID
                            Order.objects.create(
                                user=request.user,
                                product=product,
                                price=Decimal(item['price']),
                                quantity=item['quantity'],
                                total_price=Decimal(item['total_price']),
                                payment_method='khalti',
                                status="pending",
                            )
                            order_list.append(f"- {product.name} x {item['quantity']} (${item['total_price']})")
                        # Clear cart (assuming cart_items.delete() clears the cart in DB)
                        CartItem.objects.filter(cart=get_cart(request.user)).delete()
                        logger.info("Cart cleared successfully after Khalti payment.")

                        # Clean up session
                        del request.session['cart_items']
                        del request.session['grand_total']


                        # **Send Order Confirmation Email**
                    # Send Order Confirmation Email
                    user_email = request.user.email
                    if not user_email:
                        logger.error("User email is not set.")
                        messages.warning(request, "Order placed, but email confirmation failed due to missing email.")
                    else:
                        total_paid = round(grand_total, 2)
                        subject = "Order Confirmation - Payment Successful"
                        message = f"""
                        Dear {request.user.full_name},

                        Your payment via Khalti was successful!

                        **Order Details:**
                        {chr(10).join(order_list)}

                        **Total Paid:** ${total_paid}

                        Your order is now being processed. Thank you for shopping with us!

                        Regards, 
                        Your Store Team
                        """
                        try:
                            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
                            logger.info(f"Order confirmation email sent to {user_email}")
                        except Exception as e:
                            logger.error(f"Failed to send email: {str(e)}")
                            messages.warning(request, "Order placed, but email confirmation failed.")

                    messages.success(request, 'Order has been placed successfully via Khalti!')
                    return redirect('shop:order_list')
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


def about(request):
    return render(request, 'about.html')

def contact(request):
     form = ContactForm()
     if request.method == "POST":
            form = ContactForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your message has been sent successfully!")
                return redirect("shop:home")  
     return render(request, 'contact.html',{"form": form})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_list.html', {'orders': orders})


# View to list all active auction products
def auction_list(request):
    auctions = Auction.objects.filter(
        is_active=True,
        end_time__gt=timezone.now()
    ).select_related('product').order_by('end_time')
    
    context = {
        'auctions': auctions,
    }
    return render(request, 'shop/auction_list.html', context)

# View to view details and place a bid on an auction
@login_required
def auction_detail(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    product = auction.product
    
    if not auction.is_active or timezone.now() >= auction.end_time:
        auction.is_active = False
        auction.save()
        messages.info(request, "This auction has ended.")
        return redirect('shop:auction_list')

    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['amount']
            # Check if bid is higher than current highest bid or starting bid
            if (auction.highest_bid and bid_amount <= auction.highest_bid) or bid_amount <= auction.starting_bid:
                messages.error(request, "Your bid must be higher than the current highest bid or starting bid.")
            elif request.user == product.vendor:
                messages.error(request, "You cannot bid on your own auction.")
            else:
                bid = Bid(
                    auction=auction,
                    bidder=request.user,
                    amount=bid_amount
                )
                bid.save()  # This triggers update_highest_bid via Bid.save()
                messages.success(request, "Your bid has been placed successfully!")
                return redirect('shop:auction_detail', auction_id=auction.id)
        else:
            messages.error(request, "Invalid bid amount.")
    else:
        form = BidForm()

    context = {
        'auction': auction,
        'product': product,
        'form': form,
        'bids': auction.bids.order_by('-amount')[:5],  # Show top 5 bids
    }
    return render(request, 'shop/auction_detail.html', context)