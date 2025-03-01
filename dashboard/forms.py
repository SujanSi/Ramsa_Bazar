from django import forms
from core.models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
from shop.models import Product

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),  # Email should not be changed
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Custom Password Change Form with Bootstrap styling
class CustomPasswordChangeForm(BasePasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password',
        })
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
        })
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
        })

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'additional_information', 'price', 'discount',
            'availability', 'sku', 'size', 'image', 'features', 'categories',
            'stock', 'brand', 'product_type'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'additional_information': forms.Textarea(attrs={'rows': 3}),
            'features': forms.Textarea(attrs={'rows': 3}),
        }