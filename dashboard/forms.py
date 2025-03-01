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
            # Text Inputs
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name',
                'maxlength': '255'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter SKU number'
            }),
            'size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product dimensions/size'
            }),

            # Number Inputs
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price in USD',
                'step': '0.01'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Discount percentage (0-100)',
                'min': '0',
                'max': '100'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Available quantity',
                'min': '0'
            }),

            # Text Areas
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed product description...'
            }),
            'additional_information': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Warranty info, care instructions...'
            }),
            'features': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Key features & benefits...'
            }),

            # Select Boxes
            'brand': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Select brand'
            }),
            'product_type': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Select product type'
            }),

            # Multiple Select
            'categories': forms.Select(attrs={
                'class': 'form-select',
                'size': '5',
                'aria-label': 'Select categories'
            }),

            # File Input
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),

            # Checkbox
            'availability': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty labels for select fields
        self.fields['brand'].empty_label = '-- Select Brand --'
        self.fields['product_type'].empty_label = '-- Select Type --'