from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import KYCForm
from .models import KYCVerification
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def index(request):
    return render(request, 'user/index.html')


@login_required
def kyc_verification(request):
    # Check if the user has already submitted the KYC form
    kyc_exists = KYCVerification.objects.filter(user=request.user).exists()

    if kyc_exists:
        return redirect('vendor:vendor_dashboard') # Redirect to the homepage if KYC already submitted

    if request.method == 'POST':
        form = KYCForm(request.POST, request.FILES)
        if form.is_valid():
            kyc = form.save(commit=False)
            kyc.user = request.user
            kyc.status = 'pending'  # Set status to pending
            kyc.save()
            messages.success(request, "KYC submitted successfully. You can now access the platform.")
            return redirect('vendor:vendor_dashboard')
    else:
        form = KYCForm()

    return render(request, 'user/kyc_verification.html', {'form': form})




    
