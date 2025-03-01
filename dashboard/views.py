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



def vendor_products(request):
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


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user  # Set the current user as vendor
            product.save()
            return redirect('dashboard:vendor_products')  # Redirect back to products page
    else:
        form = ProductForm(initial={'product_type': 'selling'})  # Default to 'selling'

    context = {
        'form': form,
        'vendor': request.user,
    }
    return render(request, 'dashboard/add_product.html', context)



def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    product_type = request.GET.get('type', 'selling')  # Capture product_type from URL
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
        'product_type': product_type,  # Pass to template
    }
    return render(request, 'dashboard/edit_product.html', context)

def remove_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    product_type = request.GET.get('type', 'selling')  # Get the current product type
    if product_type not in ['selling', 'auction', 'renting']:
        product_type = 'selling'  # Fallback to 'selling' if invalid

    if request.method == 'POST':
        product.delete()
        # Redirect to the same product type page using reverse
        return redirect(f"{reverse('dashboard:vendor_products')}?type={product_type}")
    
    # If not POST, redirect back to the same product type page
    return redirect(f"{reverse('dashboard:vendor_products')}?type={product_type}")