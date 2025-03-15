from django.urls import path
from .views import index,kyc_verification,profile,edit_profile

app_name = 'customer'

urlpatterns = [
    
    path('index/', index, name='index'),
    path('kyc-verification/', kyc_verification, name='kyc_verification'),
    path('profile/', profile, name='profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),

]
