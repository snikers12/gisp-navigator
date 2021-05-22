from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'date_joined')
    list_filter = ('is_superuser', 'groups')
    search_fields = ('username', 'email')
    ordering = ('email',)
