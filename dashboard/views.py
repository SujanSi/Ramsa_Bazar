from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .forms import VendorProfileUpdateForm
from django.contrib import messages

# Create your views here.
@login_required
def vendor_dashboard(request):
    return render(request, 'dashboard/home.html')

@login_required
def vendor_profile_view(request):
    user = request.user  # Get the logged-in user (vendor)

    if user.role != "vendor":  
        messages.error(request, "You are not authorized to view this page.")
        return redirect("dashboard:home")  # Redirect non-vendors

    if request.method == 'POST':
        form = VendorProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard:vendor-profile')
    else:
        form = VendorProfileUpdateForm(instance=user)

    return render(request, 'dashboard/profile.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'dashboard/profile.html')