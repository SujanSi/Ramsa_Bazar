from django.urls import path
from .views import *

app_name = 'dashboard'

urlpatterns = [
    path('', vendor_dashboard, name='vendor_dashboard'),
    path('profile/', profile, name='profile'),
]
