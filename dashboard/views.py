from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileEditForm,CustomPasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from shop.models import Product
from .forms import ProductForm
from django.urls import reverse


# Create your views here.
@login_required
def vendor_dashboard(request):
    return render(request, 'dashboard/home.html')


@login_required
def profile(request):
    user = request.user
    return render(request, 'dashboard/profile.html', {'user': user})


@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:vendor-profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileEditForm(instance=user)
    return render(request, 'dashboard/profile_edit.html', {'form': form})

from django.contrib.auth import logout
@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            logout(request)  # Log out the user
            messages.success(request, 'Your password was successfully updated! Please log in again.')
            return redirect('core:login')  # Redirect to core:login
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'dashboard/change_password.html', {'form': form})


@login_required
def vendor_products(request):
    # Check if user is a vendor and KYC verified
    if request.user.role != 'vendor' or not request.user.kyc_verified:
        return render(request, 'dashboard/access_denied.html', {
            'message': 'Only KYC-verified vendors can access this section.'
        })

    product_type = request.GET.get('type', 'selling')
    if product_type not in ['selling', 'auction', 'renting']:
        product_type = 'selling'

    products = Product.objects.filter(
        vendor=request.user,
        product_type=product_type
    ).select_related('categories', 'brand', 'size').order_by('-created_at')

    context = {
        'vendor': request.user,
        'product_type': product_type,
        'products': products,
    }
    return render(request, 'dashboard/vendor_products.html', context)


@login_required
def add_product(request):
    # Check if user is a vendor and KYC verified
    if request.user.role != 'vendor' or not request.user.kyc_verified:
        return render(request, 'dashboard/access_denied.html', {
            'message': 'Only KYC-verified vendors can add products.'
        })

    product_type = request.GET.get('type', 'selling')
    print(f"Add Product - product_type: {product_type}")  # Debug
    if product_type not in ['selling', 'auction', 'renting']:
        product_type = 'selling'

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user
            product.save()
            return redirect(f"{reverse('dashboard:vendor_products')}?type={product_type}")
    else:
        form = ProductForm(initial={'product_type': product_type})

    context = {
        'form': form,
        'vendor': request.user,
        'product_type': product_type,
    }
    return render(request, 'dashboard/add_product.html', context)


@login_required
def edit_product(request, product_id):
    # Check if user is a vendor and KYC verified
    if request.user.role != 'vendor' or not request.user.kyc_verified:
        return render(request, 'dashboard/access_denied.html', {
            'message': 'Only KYC-verified vendors can edit products.'
        })

    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    product_type = request.GET.get('type', 'selling')
    if product_type not in ['selling', 'auction', 'renting']:
        product_type = 'selling'

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('dashboard:vendor_products')}?type={product_type}")
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'vendor': request.user,
        'product': product,
        'product_type': product_type,
    }
    return render(request, 'dashboard/edit_product.html', context)


@login_required
def remove_product(request, product_id):
    # Check if user is a vendor and KYC verified
    if request.user.role != 'vendor' or not request.user.kyc_verified:
        return render(request, 'dashboard/access_denied.html', {
            'message': 'Only KYC-verified vendors can remove products.'
        })

    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    product_type = request.GET.get('type', 'selling')
    if product_type not in ['selling', 'auction', 'renting']:
        product_type = 'selling'

    if request.method == 'POST':
        product.delete()
        return redirect(f"{reverse('dashboard:vendor_products')}?type={product_type}")
    return redirect(f"{reverse('dashboard:vendor_products')}?type={product_type}")



from shop.models import Order
from django.http import HttpResponse
import logging
from django.core.paginator import Paginator
logger = logging.getLogger(__name__)

@login_required
def vendor_orders(request):
    """
    Display orders for products uploaded by the logged-in vendor
    """
    if not hasattr(request.user, 'role') or request.user.role != 'vendor':
        logger.error(f"Non-vendor {request.user} attempted to access vendor orders")
        return HttpResponse("Unauthorized", status=403)

    try:
        # Get all products uploaded by this vendor
        vendor_products = Product.objects.filter(vendor=request.user)
        
        # Get all orders for these products (compatible with existing Order model)
        orders = Order.objects.filter(
            product__in=vendor_products
        ).select_related(
            'user', 'product'
        ).order_by('-created_at')

        # Status filter
        status_filter = request.GET.get('status', '')
        if status_filter:
            orders = orders.filter(status=status_filter)

        # Pagination
        paginator = Paginator(orders, 10)  # 10 orders per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'status_choices': Order.STATUS_CHOICES,
            'current_status': status_filter,
        }
        
        logger.info(f"Vendor {request.user} viewed their orders")
        return render(request, 'shop/vendor_orders.html', context)

    except Exception as e:
        logger.error(f"Error loading vendor orders for {request.user}: {str(e)}")
        return render(request, 'shop/vendor_orders.html', {
            'error': 'Unable to load orders at this time'
        })