"""
Registers the custom User model and Permission model to the Django admin site and defines a custom admin interface for the User model using the built-in UserAdmin class.

Modules:
- django.contrib.admin: Django's built-in administration interface.
- django.contrib.auth.admin: Built-in admin interface for the User model.
- django.utils.translation: Tools for internationalization and localization.
- .models: Custom User model.
- .forms: Custom UserCreationForm.
- django.contrib.auth.models: Built-in Permission model.
"""

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

from drf_base_config.settings import ENABLE_PW

from .forms import UserCreationForm
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin interface for the User model."""

    add_form = UserCreationForm
    user_fields = (None, {"fields": ("username",)})

    if ENABLE_PW:
        user_fields = (None, {"fields": ("username", "password")})
    fieldsets = (
        user_fields,
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": ("is_active", "is_staff", "groups", "user_permissions"),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Additional info"), {"fields": ("cpf", "rg", "phone", "birth_date", "image", "has_changed_password")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "first_name", "last_name", "email"),
            },
        ),
    )
    readonly_fields = ("has_changed_password",)
    list_filter = ("is_staff", "is_active", "groups")
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "has_changed_password",
        "login_date",
    )

    actions = ["mark_has_changed_password_true", "mark_has_changed_password_false"]

    @admin.action(description="Ativar has_changed_password")
    def mark_has_changed_password_true(self, request, queryset):
        """Ativa o campo has_changed_password para os usuários selecionados."""
        updated = queryset.update(has_changed_password=True)
        self.message_user(
            request, f"{updated} usuário(s) atualizado(s) com has_changed_password=True.", messages.SUCCESS
        )

    @admin.action(description="Inativar has_changed_password")
    def mark_has_changed_password_false(self, request, queryset):
        """Inativa o campo has_changed_password para os usuários selecionados."""
        updated = queryset.update(has_changed_password=False)
        self.message_user(
            request, f"{updated} usuário(s) atualizado(s) com has_changed_password=False.", messages.SUCCESS
        )


admin.site.register(Permission)
