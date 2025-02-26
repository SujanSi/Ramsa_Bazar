from django.urls import path
from .views import *

app_name = 'core'

urlpatterns = [
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    # path('password-reset/', password_reset_request, name='password_reset'),
    # path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    # path('password-reset-done', password_reset_done, name='password_reset_done'),
    path('check_email/', check_email, name='check_email'),
    path('logout/', user_logout, name='logout'),
    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),
]