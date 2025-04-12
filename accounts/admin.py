from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin

from .models import User, Department, UserHistory

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'id_number', 'phone_number', 'department', 'role', 'profile_picture')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'id_number', 'phone_number', 'department', 'role'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'id_number', 'role', 'department', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'department')
    search_fields = ('email', 'first_name', 'last_name', 'id_number')
    ordering = ('email',)

@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'description')
    ordering = ('-timestamp',)
