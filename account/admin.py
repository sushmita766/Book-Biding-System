from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserBase

class CustomUserAdmin(UserAdmin):
    model = UserBase
    list_display = ['username', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'username', 'role', 'is_active', 'pan_number', 'citizenship', 'firstname', 'phone_number', 'address', 'collateral')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'is_active', 'pan_number', 'citizenship', 'firstname', 'phone_number', 'address', 'collateral', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

admin.site.register(UserBase, CustomUserAdmin)
