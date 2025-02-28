from django.urls import path
from .views import *

app_name = 'dashboard'

urlpatterns = [
    path('', vendor_dashboard, name='vendor_dashboard'),
    path('profile/', profile, name = 'vendor-profile' ),
    path('profile/edit/',profile_edit, name='profile_edit'),
    path('profile/change-password/', change_password, name='change_password'),
]
