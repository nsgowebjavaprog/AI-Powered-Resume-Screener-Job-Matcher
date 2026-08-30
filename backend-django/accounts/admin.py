"""
accounts/admin.py
------------------
Registering a model here gives you a full CRUD UI for it at /admin/ with
ZERO extra code - one of Django's biggest productivity wins.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Extend Django's built-in UserAdmin to also show our custom fields
    list_display = ("username", "email", "role", "is_staff", "created_at")
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Info", {"fields": ("full_name", "role")}),
    )
