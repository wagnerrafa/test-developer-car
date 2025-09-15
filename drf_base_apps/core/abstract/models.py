"""
Abstract models for the DRF base applications.

This module provides abstract model classes that can be extended by other applications
to provide common functionality, audit trails, and change tracking.
"""

import uuid

from crum import get_current_request
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import (
    DataError as DateErr,
    models,
)
from django.db.models import Q
from django.db.models.signals import pre_delete, pre_save
from django.db.transaction import TransactionManagementError
from django.db.utils import DataError, ProgrammingError
from django.forms import model_to_dict

from drf_base_apps.utils import _

AUTH_USER_MODEL = settings.AUTH_USER_MODEL


class ActiveManager(models.Manager):
    """Manager that returns only active objects."""

    def get_queryset(self):
        """Return only active objects."""
        return super().get_queryset().filter(is_active=True)


class AbstractModel(models.Model):
    """Abstraction of common fields in all models."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(_("Creation date"), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(_("Last update date"), auto_now=True, editable=False)
    create_user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        blank=True,
        related_name="%(class)s_created",
    )
    update_user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        blank=True,
        related_name="%(class)s_updated",
    )
    is_active = models.BooleanField(_("Is Active"), default=True, editable=False)

    # Managers
    all_objects = models.Manager()  # Para acesso completo (sem filtro)
    objects = ActiveManager()  # Retorna apenas registros com is_active=True

    class Meta:
        """Meta options for AbstractModel."""

        abstract = True
        ordering = ("-created_at", "-updated_at")

    def __init__(self, *args, **kwargs):
        """Initialize the AbstractModel with initial state tracking."""
        super().__init__(*args, **kwargs)
        self.__initial = self._dict
        self._validate_unique_called = False

    def save(self, *args, **kwargs):
        """Save model and set initial state."""
        if not self._validate_unique_called:
            self.validate_unique()

        self._validate_unique_called = False
        super().save(*args, **kwargs)
        self.__initial = self._dict

    def validate_unique(self, exclude=None):
        """Validate unique constraints."""
        self._validate_unique_called = True  # Marca a validação como chamada
        return super().validate_unique(exclude=exclude)

    @property
    def diff(self):
        """Get differences between current and initial state."""
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        """Check if the model has changed."""
        return bool(self.diff)

    @property
    def changed_fields(self):
        """Get changed fields."""
        return self.diff.items()

    def get_field_diff(self, field_name):
        """Return a diff for field if it's changed and None otherwise."""
        return self.diff.get(field_name, None)

    @property
    def _dict(self):
        """Convert model to dictionary."""
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])

    def dict_update(self, commit=True, *args, **kwargs):
        """Update fields through a dictionary."""
        for name, values in kwargs.items():
            try:
                attr_value = getattr(self, name)
                if attr_value != values:
                    setattr(self, name, values)
            except KeyError:
                pass
        if commit:
            self.save()
        return self

    def get_historical(self):
        """Get historical changes for this model."""
        return list(
            UpdateUser.objects.filter(object_id=self.id)
            .exclude(Q(field_changed="update_user") | Q(current_value__regex=r"^[\w-]{36}$"))
            .order_by("-created_at")
        )


class UpdateUser(models.Model):
    """Model template to catch all updates made to the model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(_("Creation date"), auto_now_add=True, editable=False)
    field_changed = models.CharField(_("Changed field"), max_length=100, blank=True, default="", editable=False)
    field_changed_display = models.CharField(
        _("Changed field display"), max_length=100, blank=True, default="", editable=False
    )
    current_value = models.TextField(_("Current value"), max_length=4000, blank=True, editable=False, default="")
    previous_value = models.TextField(_("Previous value"), max_length=4000, blank=True, editable=False, default="")

    create_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False)

    object_id = models.UUIDField(editable=False)  # uuid AbstractModel
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, editable=False)
    content_object = GenericForeignKey()

    class Meta:
        """Meta options for UpdateUser model."""

        verbose_name = _("Registro de Alteração")
        verbose_name_plural = _("Registros de Alteração")
        ordering = ("-created_at",)

    def __str__(self):
        """Return string representation of the model."""
        return str(self.field_changed)


def save_obj(sender, **kwargs):
    """Get User on request and track changes."""
    instance = kwargs.get("instance")
    requests_ = get_current_request()
    user_id = requests_.user.id if requests_ else None
    has_instance_user = hasattr(instance, "create_user")

    if user_id and has_instance_user:
        if not instance.create_user:
            instance.create_user_id = user_id
        instance.update_user_id = user_id
    if hasattr(instance, "changed_fields") and hasattr(instance, "id"):
        for field, values in instance.changed_fields:
            previous_value = values[0] or ""
            current_value = values[1] or ""
            new_field = instance._meta.get_field(field)
            if hasattr(new_field, "choices") and getattr(instance, f"get_{field}_display", None):
                choices = dict(new_field.choices)
                previous_value = choices.get(previous_value, previous_value)
                current_value = choices.get(current_value, current_value)
            try:
                if current_value:
                    current_value = str(current_value)[:3999]
                if previous_value:
                    previous_value = str(previous_value)[:3999]

                if current_value == previous_value:
                    return

                UpdateUser.objects.create(
                    field_changed=field,
                    field_changed_display=new_field.verbose_name,
                    previous_value=previous_value,
                    current_value=current_value,
                    create_user_id=user_id,
                    object_id=instance.id,
                    content_object=instance,
                )
            except (ValueError, DataError, TransactionManagementError, AttributeError, DateErr, ProgrammingError):
                pass


pre_save.connect(save_obj, dispatch_uid=AbstractModel)


def delete_obj(sender, **kwargs):
    """Get User on request for deletion tracking."""
    instance = kwargs.get("instance")
    requests_ = get_current_request()
    user_id = requests_.user.id if requests_ else None
    has_instance_user = hasattr(instance, "create_user")
    if user_id and has_instance_user:
        if not instance.create_user:
            instance.create_user_id = user_id
        instance.update_user_id = user_id
    if hasattr(instance, "id") and isinstance(instance.id, uuid.UUID):
        previous_value = instance.__str__()
        current_value = "deleted"
        try:
            if current_value:
                current_value = str(current_value)[:3999]
            if previous_value:
                previous_value = str(previous_value)[:3999]

            if current_value == previous_value:
                return
            UpdateUser.objects.create(
                field_changed="object",
                field_changed_display="object",
                previous_value=previous_value,
                current_value=current_value,
                create_user_id=user_id,
                object_id=instance.id,
                content_object=instance,
            )
        except (ValueError, DataError, TransactionManagementError, AttributeError, DateErr, ProgrammingError):
            pass


class ProtectedFK(models.ForeignKey):
    """
    Campo ForeignKey com proteção automática contra exclusão.

    Configura automaticamente on_delete=models.PROTECT para
    evitar exclusão acidental de registros relacionados.
    """

    def __init__(self, *args, **kwargs):
        """
        Inicializa o campo ForeignKey com proteção automática.

        Args:
            *args: Argumentos posicionais para ForeignKey.
            **kwargs: Argumentos nomeados para ForeignKey.

        """
        kwargs.setdefault("on_delete", models.PROTECT)
        super().__init__(*args, **kwargs)


pre_delete.connect(delete_obj, dispatch_uid=AbstractModel)
