from django.contrib import admin
from .models import LoginOTP

@admin.register(LoginOTP)
class LoginOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'expires_at', 'attempts', 'used')
    # Le mot de passe à usage unique n'est jamais stocké en clair.
    exclude = ('code_hash',)
