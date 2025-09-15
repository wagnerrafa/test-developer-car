"""Token authentication for the application."""

import logging
from typing import Any

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_base_apps.core.drf_base_user.schemas import UserSchema


def get_theme_color(user):
    """Função para obter a cor do tema para o usuário."""
    theme_color = "#3498db"  # Cor padrão

    try:
        from apps.company_settings.models import CompanyColorSettings, UserColorPreference

        try:
            preference = UserColorPreference.objects.get(user=user)
            theme_color = preference.preferred_color
        except UserColorPreference.DoesNotExist:
            try:
                if hasattr(user, "company") and user.company:
                    company_settings = CompanyColorSettings.objects.get(company=user.company)
                    theme_color = company_settings.primary_color
                else:
                    from apps.employee.models import Employee

                    employee = Employee.objects.filter(user=user).first()
                    if employee and employee.company:
                        company_settings = CompanyColorSettings.objects.get(company=employee.company)
                        theme_color = company_settings.primary_color
            except Exception as e:
                logging.debug(e, exc_info=True)  # Usa a cor padrão
    except ImportError as import_error:
        logging.debug(import_error, exc_info=True)  # Usa a cor padrão se os modelos não estiverem disponíveis

    return theme_color


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes theme color and user data."""

    @classmethod
    def get_token(cls, user):
        """Adiciona a cor do tema ao payload do token JWT."""
        token = super().get_token(user)

        theme_color = get_theme_color(user)

        token["theme_color"] = theme_color

        return token

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        """Validate credentials and return token with user data and theme color."""
        data = super().validate(attrs)
        user_serializer = UserSchema(self.user).data

        theme_color = get_theme_color(self.user)

        data["theme_color"] = theme_color

        data.update(user_serializer)

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that uses the custom serializer."""

    serializer_class = CustomTokenObtainPairSerializer
