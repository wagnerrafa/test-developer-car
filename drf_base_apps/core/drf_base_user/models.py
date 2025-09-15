"""User models for the application."""

import itertools
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from drf_base_apps.core.abstract.constants import GroupChoices
from drf_base_apps.core.abstract.models import AbstractModel
from drf_base_config.settings import ENABLE_PW

STATUS_CHOICES = (
    ("A", _("Ativo")),
    ("I", _("Inativo")),
    ("P", _("Pendente")),
    ("R", _("Rejeitado")),
)


def user_image_path(instance, filename):
    """Generate a random filename while keeping the original extension."""
    # Gera um nome de arquivo aleatório mantendo a extensão original
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    # Retorna o caminho: users/user_id/filename
    return f"users/{instance.id}/{filename}"


class BaseUser(AbstractUser, AbstractModel):
    """Base user model with extended functionality."""

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")
    login_date = models.DateField(_("Login today"), null=True, blank=True, editable=False)
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]
    status = models.CharField("status", default="P", max_length=1, choices=STATUS_CHOICES)
    email = models.EmailField(_("email address"), null=True, blank=True, unique=True, default=None)

    cpf = models.CharField(_("CPF"), max_length=14, unique=True, blank=True, default="")
    rg = models.CharField(_("RG"), max_length=20, blank=True, default="")
    phone = models.TextField(_("Phone"), blank=True, default="")
    birth_date = models.DateField(_("Birth Date"), blank=True, null=True)

    image = models.ImageField(_("Image"), upload_to=user_image_path, null=True, blank=True)
    has_changed_password = models.BooleanField(_("Has Changed Password"), default=False, editable=False)

    @property
    def has_rh_perm_group(self):
        """Verifica se o usuário pertence ao grupo RH."""
        return self.groups.filter(name=GroupChoices.RH.value).exists()

    @property
    def has_clb_perm_group(self):
        """Verifica se o usuário pertence ao grupo CLB."""
        return self.groups.filter(name=GroupChoices.CLB.value).exists()

    @property
    def has_intra_perm(self):
        """Verifica se o usuário pertence ao grupo INTRA."""
        return self.groups.filter(name=GroupChoices.INTRA.value).exists()

    @property
    def has_integrator_perm(self):
        """Verifica se o usuário pertence ao grupo INTEGRATOR."""
        return self.groups.filter(name=GroupChoices.INTEGRATOR.value).exists()

    def has_permission(self, perms: list or str, obj=None):
        """
        Return True if the user has the specified permission in individual or group.

        Query all available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        if isinstance(perms, str):
            perms = [perms]
        has_perm = False

        if self.is_active and self.is_superuser:
            return True

        for perm in perms:
            has_perm = any(
                [
                    self.groups.filter(permissions__codename=perm).exists(),
                    self.user_permissions.filter(codename=perm).exists(),
                ]
            )
            if has_perm is False:
                break
        return has_perm

    def get_list_permissions(self):
        """Return the list permissions for the user."""
        user_permissions = list(self.user_permissions.all().values("name", "codename"))
        group_permissions = (group.permissions.all().values("name", "codename") for group in self.groups.all())
        return list(itertools.chain(user_permissions, *group_permissions))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Save the user with password handling."""
        if not ENABLE_PW:
            self.set_unusable_password()
        return super().save(force_insert, force_update, using, update_fields)

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() or self.username

    @property
    def full_name(self):
        """Return the full name of the user."""
        return self.get_full_name()

    class Meta:
        """Meta options for BaseUser model."""

        abstract = True

    def __str__(self):
        """Return string representation of the user."""
        return self.full_name


class User(BaseUser):
    """Concrete user model for the application."""

    class Meta(AbstractUser.Meta):
        """Meta options for User model."""

        swappable = "AUTH_USER_MODEL"
