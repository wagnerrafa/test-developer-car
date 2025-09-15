"""
Admin configuration for abstract models.

This file facilitates the registration of the UpdateUser models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the core.abstract.models
module, this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(UpdateUser)

"""

from dalf.admin import DALFChoicesField, DALFModelAdmin, DALFRelatedField, DALFRelatedFieldAjax, DALFRelatedOnlyField
from django.contrib import admin
from django.db import models

from drf_base_apps.core.abstract.models import UpdateUser
from drf_base_apps.utils import _


class AbstractModelAdmin(admin.ModelAdmin):
    """Abstract model admin with readonly fields."""

    readonly_fields = (
        "created_at",
        "field_changed",
        "field_changed_display",
        "current_value",
        "previous_value",
        "create_user",
        "object_id",
        "content_type",
        "content_object",
    )

    def has_delete_permission(self, request, obj=None) -> bool:
        """Check if user has delete permission."""
        return False


class AbstractAdmin(DALFModelAdmin):
    """
    A custom Django admin.ModelAdmin class that provides functionality for filtering objects based on user groups.

    Now enhanced with DALF autocomplete capabilities.

    This class allows filtering objects in the admin interface based on the user's group membership and superuser
    status. It provides a custom queryset that includes filtering by user groups if the user has superuser permission
    and if the 'custom_filter' attribute is set to True.

    Methods:
        get_queryset(request: HttpRequest) -> QuerySet:
            Returns a filtered queryset based on user groups if custom filtering is enabled and the user has superuser
            permission.

        get_user_groups(user: User) -> QuerySet:
            Returns the user's groups filtered by group types specified in 'group_type'.

        get_dict_filter(user: User) -> dict:
            Returns a dictionary filter based on the user's groups to use in queryset filtering.

        has_super_permission(user: User) -> bool:
            Checks if the user has superuser permission.

    Usage Example:
        class MyModelAdmin(AbstractAdmin):
            group_type = ['A']  # Filter by group type 'A' in addition to superusers.
            custom_filter = True

    Note:
        To use this custom admin.ModelAdmin class, subclass it in your admin.py file and configure it as needed.

    """

    gen_autocomplete_fields = True
    gen_list_display = True
    gen_readonly_fields = True
    gen_search_fields = True
    gen_list_filter = True
    gen_raw_id_fields = True

    # Novas configurações para DALF
    gen_dalf_filters = True  # Habilitar filtros DALF automaticamente
    dalf_ajax_enabled = True  # Habilitar AJAX por padrão
    dalf_minimum_input_length = 2
    dalf_maximum_results = 20

    @admin.display(ordering="created_at")
    @admin.display(description=_("Creation date"))
    def get_created_at(self, obj):
        """Get creation date with user information."""
        return f'{obj.created_at} - {obj.create_user or "anônimo"}'

    @admin.display(ordering="updated_at")
    @admin.display(description=_("Last update date"))
    def get_updated_at(self, obj):
        """Get update date with user information."""
        return f'{obj.updated_at} - {obj.update_user or "anônimo"}'

    def get_queryset(self, request):
        """
        Get queryset with all objects support.

        This method ensures that all objects (including inactive ones) are available
        in the admin interface, which is important for:
        - Showing all related objects in detail views
        - Allowing selection of inactive objects in forms
        - Maintaining data integrity in the admin
        """
        objects = getattr(self.model, "all_objects", self.model.objects)
        return objects.all()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Override formfield_for_foreignkey to use all_objects for related fields.

        This ensures that all related objects (including inactive ones) are available
        in dropdowns and forms, which is crucial for maintaining data relationships.
        """
        if hasattr(db_field.remote_field.model, "all_objects"):
            kwargs["queryset"] = db_field.remote_field.model.all_objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Override formfield_for_manytomany to use all_objects for related fields.

        This ensures that all related objects (including inactive ones) are available
        in many-to-many fields.
        """
        if hasattr(db_field.remote_field.model, "all_objects"):
            kwargs["queryset"] = db_field.remote_field.model.all_objects.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_dalf_config(self):
        """Return custom DALF configurations."""
        return {
            "minimum_input_length": self.dalf_minimum_input_length,
            "maximum_results": self.dalf_maximum_results,
        }

    def __init__(self, model, admin_site):
        """Initialize the admin with automatic field generation."""
        super().__init__(model, admin_site)

        non_models = ["AbstractAdmin", "CustomUserAdmin", "CustomGroupAdmin"]
        non_model = False
        for non in non_models:
            if str(self.__class__.__name__).endswith(non):
                non_model = True
                break
        if not non_model:
            search_fields = get_fields(model)
            new_list_display = ["__str__"]
            new_readonly_fields = []

            if "id" in search_fields:
                new_list_display += ["id"]

            if "is_active" in search_fields:
                new_list_display += ["is_active"]

            if str(self.__class__.__name__).endswith("TokenAdmin"):
                new_list_display = ["__str__"]

            if "created_at" in search_fields:
                new_list_display += ["__str__", "get_created_at"]
                new_readonly_fields += ["id", "created_at", "create_user"]

            if "updated_at" in search_fields:
                new_list_display += ["get_updated_at"]
                new_readonly_fields += ["updated_at", "update_user"]

            if self.gen_list_display:
                self.list_display = list(dict.fromkeys(new_list_display + list(self.list_display)))

            if self.gen_readonly_fields:
                self.readonly_fields = list(set(new_readonly_fields + list(self.readonly_fields)))

            if self.gen_search_fields:
                self.search_fields = list(set(get_fields(model) + list(self.search_fields)))

            # Nova lógica para filtros DALF
            if self.gen_list_filter and self.gen_dalf_filters:
                self.list_filter = self._generate_dalf_filters(model)

            if self.search_fields and self.gen_autocomplete_fields:
                relation_fields = get_relation_fields(model)
                self.autocomplete_fields = relation_fields

    def _generate_dalf_filters(self, model):
        """Generate DALF filters automatically based on model fields."""
        filters = []
        relation_fields = get_relation_fields(model)
        choice_fields = get_choice_fields(model)
        boolean_fields = get_boolean_fields(model)
        datetime_fields = get_datetime_fields(model)

        for field_name in relation_fields:
            field = model._meta.get_field(field_name)

            if isinstance(field, models.ForeignKey):
                if self.dalf_ajax_enabled:
                    filters.append((field_name, DALFRelatedFieldAjax))
                else:
                    filters.append((field_name, DALFRelatedField))

            elif isinstance(field, models.ManyToManyField):
                filters.append((field_name, DALFRelatedOnlyField))

        # Adicionar filtros para campos de escolha
        for field_name in choice_fields:
            filters.append((field_name, DALFChoicesField))

        # Adicionar filtros para campos boolean
        for field_name in boolean_fields:
            filters.append(field_name)

        # Adicionar filtros para campos datetime
        for field_name in datetime_fields:
            filters.append(field_name)

        return filters


def get_choice_fields(model):
    """Get choice fields from model."""
    choice_fields = []
    for field in model._meta.fields:
        if hasattr(field, "choices") and field.choices:
            choice_fields.append(field.name)
    return choice_fields


def get_boolean_fields(model):
    """Get boolean fields from model."""
    boolean_fields = []
    for field in model._meta.fields:
        if isinstance(field, models.BooleanField):
            boolean_fields.append(field.name)
    return boolean_fields


def get_datetime_fields(model):
    """Get datetime fields from model."""
    datetime_fields = []
    for field in model._meta.fields:
        if isinstance(field, (models.DateTimeField, models.DateField)):
            datetime_fields.append(field.name)
    return datetime_fields


def get_field_type(field):
    """
    Mapeia o tipo do campo Django para o tipo correspondente no Swagger.

    Args:
        field: O campo do modelo Django.

    Returns:
        str: O tipo do campo no formato Swagger.

    """
    field_types = {
        models.DateField: "date",
        models.DateTimeField: "datetime",
        models.IntegerField: "integer",
        models.FloatField: "float",
        models.BooleanField: "boolean",
        models.EmailField: "string",
        models.URLField: "string",
        models.UUIDField: "uuid",
        models.FileField: "string",
        models.ImageField: "string",
        models.JSONField: "object",
        models.ForeignKey: "uuid",
        models.OneToOneField: "integer",
        models.ManyToManyField: "array",
    }

    for field_class, swagger_type in field_types.items():
        if isinstance(field, field_class):
            if isinstance(field, models.ForeignKey):
                # Verifica se o campo relacionado é do tipo UUID
                if isinstance(field.remote_field.model._meta.pk, models.UUIDField):
                    return "uuid"  # UUID é representado como string no Swagger
                return "integer"  # Chave estrangeira padrão é inteiro
            return swagger_type
    return "string"


def get_fields(model, recursive=True):
    """
    Retrieve a list of field names for a given Django model, excluding sensitive and file-related fields.

    Args:
        model: The Django model for which to retrieve field names.
        recursive: Whether to include fields from related models.

    Returns:
        list: A list of field names for the provided model, including both direct fields and related fields
              from related models, while excluding sensitive and file-related fields.

    """
    fields = []
    text_sensitive = [
        "password",
        "last_login",
        "is_superuser",
        "token",
        "user_permissions",
        "auth_token",
        "logentry__id",
    ]

    def valid_field(fi):
        if fi.name in text_sensitive:
            return False

        return not isinstance(fi, (models.ImageField, models.FileField))

    for field in model._meta.get_fields():
        if field.is_relation:
            related_model = field.related_model

            if related_model and recursive:
                for sub_field in related_model._meta.get_fields():
                    if not valid_field(sub_field):
                        continue
                    if not sub_field.is_relation:
                        field_type = get_field_type(sub_field)

                        if field_type == "string":
                            fields.append(f"{field.name}__{sub_field.name}__icontains")
                        else:
                            fields.append(f"{field.name}__{sub_field.name}")
        else:
            if not valid_field(field):
                continue
            fields.append(field.name)
    return fields


def valid_field(fi):
    """Check if field is valid for admin."""
    return not fi.is_relation or fi.many_to_one or fi.one_to_one or (fi.many_to_many and fi.blank)


def get_fields_filter(model, recursive=True):
    """Get filterable fields from model."""
    fields = []
    for field in model._meta.fields:
        if valid_field_filter(field):
            fields.append(field.name)
    if recursive:
        for field in model._meta.fields:
            if valid_field_filter(field) and hasattr(field, "related_model") and field.related_model:
                fields.extend(get_fields_filter(field.related_model, recursive=False))
    return fields


def valid_field_filter(fi):
    """Check if field is valid for filtering."""
    return not fi.is_relation or fi.many_to_one or fi.one_to_one or (fi.many_to_many and fi.blank)


def get_relation_fields(model):
    """Get relation fields from model."""
    relation_fields = []
    for field in model._meta.fields:
        if valid_field(field) and field.is_relation and isinstance(field, (models.ForeignKey, models.ManyToManyField)):
            relation_fields.append(field.name)
    return relation_fields


@admin.register(UpdateUser)
class UpdateUserAdmin(AbstractModelAdmin):
    """Admin configuration for UpdateUser model."""

    list_display = ["field_changed", "created_at", "create_user"]
    list_filter = ["field_changed", "created_at"]
    search_fields = ["field_changed", "current_value", "previous_value"]
    readonly_fields = AbstractModelAdmin.readonly_fields
