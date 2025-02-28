from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileEditForm,CustomPasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

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