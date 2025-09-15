"""
Serializes the fields of the Statement model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Statement` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.

Usage example:
serializer = StatementSchema()

"""

from django.contrib.auth.models import Permission
from rest_framework import serializers

from drf_base_apps.core.abstract.schemas import AbstractDescriptionSchema
from drf_base_apps.utils import get_user_model
from drf_base_config.settings import PROJECT_INSTALLED_APPS

User = get_user_model()


class PermissionSchema(AbstractDescriptionSchema):
    """Provide a serializer to serialize the Permission model fields."""

    content_type = serializers.StringRelatedField()
    app_label = serializers.CharField(source="content_type.app_label", read_only=True)
    display = serializers.SerializerMethodField(read_only=True)

    def get_display(self, obj):
        """Get a user-friendly display name for the permission."""
        model = obj.content_type.model_class()
        if not model:
            return obj.content_type.model

        # Mapeia o codename para um texto mais amigável
        action_map = {
            "add": "Pode adicionar",
            "change": "Pode editar",
            "delete": "Pode deletar",
            "view": "Pode visualizar",
        }

        # Extrai a ação do codename (primeira parte antes do underscore)
        action = obj.codename.split("_")[0] if "_" in obj.codename else obj.codename
        action_text = action_map.get(action, action)

        return f"{action_text} {model._meta.verbose_name}"

    class Meta:
        """Meta options for PermissionSchema."""

        model = Permission
        fields = ["id", "name", "codename", "content_type", "app_label", "display"]


class UserSchema(serializers.ModelSerializer):
    """Serializer for User model fields."""

    full_name = serializers.ReadOnlyField(source="get_full_name")
    user_permissions_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Lista de IDs de permissões Django a serem atribuídas ao usuário",
        read_only=True,
    )

    user_permissions = PermissionSchema(many=True, read_only=True)

    class Meta:
        """Meta options for UserSchema."""

        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "cpf",
            "rg",
            "phone",
            "birth_date",
            "status",
            "login_date",
            "is_active",
            "image",
            "has_changed_password",
            "user_permissions_ids",
            "user_permissions",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the serializer with optional field exclusion."""
        fields = kwargs.pop("exclude", [])
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            set(self.fields)
            for field_name in allowed:
                try:
                    self.fields.pop(field_name)
                except KeyError:
                    continue


class UserEditSchema(UserSchema):
    """Serializer for User model fields."""

    user_permissions_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Lista de IDs de permissões Django a serem atribuídas ao usuário",
    )

    class Meta:
        """Meta options for UserSchema."""

        model = User
        fields = [
            "id",
            "email",
            "cpf",
            "rg",
            "phone",
            "birth_date",
            "is_active",
            "image",
            "user_permissions_ids",
        ]
        non_required_fields = "__all__"

    def _assign_permissions(self, user, permission_ids):
        """Atribui permissões individuais ao usuário."""
        project_app_labels = []
        for app in PROJECT_INSTALLED_APPS:
            if app.startswith("apps."):
                if "." in app[5:]:  # Se tem ponto após "apps."
                    base_app = app.split(".")[1]
                    project_app_labels.append(f"{base_app}_apps")
                else:
                    project_app_labels.append(app[5:])
            else:
                project_app_labels.append(app)

        valid_permissions = Permission.objects.filter(
            id__in=permission_ids, content_type__app_label__in=project_app_labels
        )

        user.user_permissions.set(valid_permissions)

    def update(self, instance, validated_data):
        """Update user object with validated data."""
        user_permissions_ids = validated_data.pop("user_permissions_ids", [])
        user = super().update(instance, validated_data)

        if user_permissions_ids:
            self._assign_permissions(user, user_permissions_ids)

        return user
