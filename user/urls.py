from django.urls import path
from .views import index,kyc_verification

app_name = 'customer'

urlpatterns = [
    
    path('index/', index, name='index'),
    path('kyc-verification/', kyc_verification, name='kyc_verification'),

]
