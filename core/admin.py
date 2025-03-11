from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Define the fields to display in the admin list view
    list_display = ('email', 'full_name', 'phone', 'role', 'is_active', 'is_staff','is_blacklisted')
    list_filter = ('role', 'is_blacklisted')
    ordering = ('email',)
    search_fields = ('email', 'full_name', 'phone')
    actions = ['blacklist_users', 'unblacklist_users']

    def blacklist_users(self, request, queryset):
        queryset.update(is_blacklisted=True)
    blacklist_users.short_description = "Blacklist selected users"

    def unblacklist_users(self, request, queryset):
        queryset.update(is_blacklisted=False)
    unblacklist_users.short_description = "Unblacklist selected users"
    # Override fieldsets to exclude 'username' and include your custom fields
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions', 'is_blacklisted')}),
        ('KYC', {'fields': ('kyc_verified',)}),
    )

    # Override add_fieldsets for the "Add" form in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone', 'password1', 'password2', 'role', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # Specify the filter options
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')

admin.site.register(CustomUser, CustomUserAdmin)