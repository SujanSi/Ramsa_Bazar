from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import logout
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from user.forms import KYCForm
from user.models import KYCVerification


# Create your views here.

User = get_user_model()


def register(request):
    if request.method == 'POST':
        try:
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            password = request.POST.get('password', '')
            role = request.POST.get('role', 'user')

            print("-------------------")
            # Check if any required field is empty
            if not full_name or not email or not phone or not password:
                messages.error(request, "All fields are required.")
                return redirect('core:register')

            # Check if email or phone already exists
            # if User.objects.filter(email=email).exists():
            #     messages.error(request, "Email is already registered.")
            #     return redirect('register')

            if User.objects.filter(phone=phone).exists():
                messages.error(request, "Phone number is already registered.")
                return redirect('core:register')

            # Create user but keep inactive until email confirmation
            user = User.objects.create_user(email=email, full_name=full_name, phone=phone, password=password)
            user.role = role
            user.is_active = False
            user.save()

            # Generate Email Verification Link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = request.build_absolute_uri(reverse('core:activate', args=[uid, token]))

            # Email Content
            email_subject = 'Activate Your Account'
            email_body = f'Hi {full_name},\n\nClick the link to activate your account: {activation_link}\n\nThank you!'

            try:
                send_mail(
                    email_subject,
                    email_body,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,  # Change to True if you want to suppress email errors
                )
                messages.success(request, "Registration successful! Check your email to confirm your account.")
            except Exception as e:
                messages.error(request, f"Error sending email: {e}")
                return redirect('core:register')

            return redirect('core:check_email')  # Redirect to a 'Check Email' page

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('core:register')

    return render(request, 'core/signup.html')



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated. You can now login.")
        return redirect('core:login')
    else:
        messages.error(request, "Invalid activation link.")
        return redirect('core:register')
    



def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        remember = request.POST.get('remember')
        print('------------------------------')
        print("Attempting Login for:", email)
        user = authenticate(request, email=email, password=password)
        print("Authenticated User:", email)  # Debugging

        if user:
            login(request, user)
            request.session.set_expiry(0 if not remember else 604800)  # 7 days
            
            kyc_exists = KYCVerification.objects.filter(user=user).exists()
            print(f"KYC Exists for {user.email}: {kyc_exists}")  # Debugging

            # Check if the logged-in user is a vendor and has not completed KYC
            if user.role == 'vendor':
                kyc_exists = KYCVerification.objects.filter(user=user).exists()
                print(f"KYC Exists for {user.email}: {kyc_exists}")  # Debugging

                if not kyc_exists:
                    print(f"Redirecting {user.email} to KYC Page.")  # Debugging
                    messages.info(request, "Please complete KYC verification before proceeding.")
                    return redirect('customer:kyc_verification')  # Ensure the name matches the URL pattern

            # Redirect based on user role
            if user.role == 'vendor':
                return redirect('vendor:vendor_dashboard')  # Redirect to vendor dashboard
            elif user.role == 'superadmin':
                return redirect('admin:index')  # Redirect to superadmin dashboard
            else:
                return redirect('vendor:home')

        else:
            print(f"Invalid credentials for {email}")  # Debugging
            messages.error(request, "Invalid email or password.")
            return redirect('core:login')  # Redirect back to login page if authentication fails

    return render(request, 'core/signin.html')



# def password_reset_request(request):
#     if request.method == "POST":
#         form = PasswordResetForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data["email"]
#             user = get_user_model().objects.filter(email=email).first()
            
#             if user and user == request.user:  # Check if the email matches the logged-in user
#                 # Generate password reset token and send email
#                 token = default_token_generator.make_token(user)
#                 uid = urlsafe_base64_encode(str(user.pk).encode())
#                 reset_link = request.build_absolute_uri(
#                     f"/accounts/reset/{uid}/{token}/"  # Make sure this matches your URL pattern
#                 )
#                 subject = "Password Reset Request"
#                 message = f"Click the link to reset your password: {reset_link}"
#                 send_mail(subject, message, "admin@mywebsite.com", [email])
#                 messages.success(request, "Password reset email sent.")
#                 return redirect('user:password_reset_done')
            
#             else:
#                 messages.error(request, "This email is not associated with the logged-in user.")
#                 return redirect('login')  # Optional: you can return an error message
        
#     else:
#         form = PasswordResetForm()

#     return render(request, "user/lost-password.html", {"form": form})


# from django.contrib.auth.forms import SetPasswordForm
# from django.contrib.auth.tokens import default_token_generator

# def password_reset_confirm(request, uidb64, token):
#     try:
#         # Decode the UID
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = get_user_model().objects.get(pk=uid)

#         # Check the token
#         if default_token_generator.check_token(user, token):
#             if request.method == 'POST':
#                 form = SetPasswordForm(user, request.POST)
#                 if form.is_valid():
#                     form.save()
#                     messages.success(request, "Password has been reset successfully.")
#                     return redirect('user:login')
#             else:
#                 form = SetPasswordForm(user)
#             return render(request, 'user/password_reset_confirm.html', {'form': form})
#         else:
#             messages.error(request, "The password reset link is invalid or expired.")
#             return redirect('user:login')
#     except Exception as e:
#         messages.error(request, "The password reset link is invalid or expired.")
#         return redirect('user:login')


def check_email(request):
    return render(request, 'core/check_email.html')


# def password_reset_done(request):
#     return render(request, 'user/password_reset_done.html')

def user_logout(request):
    logout(request)
    return redirect('vendor:home')  # Redirect to login page after logout


@login_required
def dashboard_redirect(request):
    if request.user.role == 'superadmin':
        return redirect('supadmin:superadmin_dashboard')
    elif request.user.role == 'vendor':
        return redirect('vendor:vendor_dashboard')  
    else:
        return redirect('customer:customer_dashboard')