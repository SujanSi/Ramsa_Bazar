from django.urls import path
from .views import *

app_name = 'dashboard'

urlpatterns = [
    path('', vendor_dashboard, name='vendor_dashboard'),
    path('vendor/profile/', vendor_profile_view, name='vendor-profile'),
]
