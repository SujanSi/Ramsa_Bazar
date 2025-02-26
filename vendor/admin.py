from django.contrib import admin
from .models import Product

# Register Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'created_at', 'updated_at')
    search_fields = ('name', 'vendor__username', 'description')
    list_filter = ('vendor', 'created_at', 'price')
    ordering = ('-created_at',)

