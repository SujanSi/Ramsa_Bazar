from django import forms
from core.models import CustomUser

class VendorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),  # Email should not be changed
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
