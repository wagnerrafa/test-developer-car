"""Admin configuration for login record."""

from django.contrib import admin

from drf_base_apps.login_record.models import LoginRecord


@admin.register(LoginRecord)
class LoginRecordAdmin(admin.ModelAdmin):
    """Admin configuration for the LoginRecord model."""

    list_display = ("id", "user", "login_date", "login_tm")
    search_fields = ("user__first_name", "user__last_name", "user__username")
