from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms

from authentication.models import CustomUser

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email_name, domain_part = email.strip().rsplit('@', 1)
            email = email_name + '@' + domain_part.lower()
        return email

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email_name, domain_part = email.strip().rsplit('@', 1)
            email = email_name + '@' + domain_part.lower()
        return email

    def clean_username(self):
        email = self.cleaned_data.get('email')
        if email:
            return email.split('@')[0]
        return self.cleaned_data.get('username')

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Fields displayed in the user list
    list_display = (
        'email', 'username', 'first_name', 'last_name', 
        'role', 'is_staff', 'is_active', 'date_joined'
    )
    
    # Fields to filter users by
    list_filter = (
        'role', 'is_staff', 'is_active', 'date_joined'
    )
    
    # Search fields
    search_fields = (
        'email', 'username', 'first_name', 'last_name', 
        'npm', 'google_id'
    )
    
    # Default ordering
    ordering = ('email',)
    
    # Fields to display in the user detail form
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'role'
            )
        }),
        (_('Authentication Info'), {
            'fields': (
                'google_id', 'npm', 'angkatan'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Fields to display in the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name', 'password', 'password2',
                'role', 'is_staff', 'is_active'
            )
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')