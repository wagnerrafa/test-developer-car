"""Models for login record."""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from drf_base_apps.utils import get_user_model

User = get_user_model()


class LoginRecord(models.Model):
    """Model to track user login records."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_date = models.DateField(auto_now_add=True)
    login_tm = models.TimeField()
    campo_teste = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        """Meta options for LoginRecord model."""

        verbose_name = _("Registro de Login")
        verbose_name_plural = _("Registros de Login")
        unique_together = [["user", "login_date"]]

    def __str__(self):
        """Return string representation of the login record."""
        return f"{self.user.username} {self.login_date}:{self.login_tm}"

    def save(self, *args, **kwargs):
        """Save the login record with automatic time setting."""
        if not self.login_tm:  # Verifica se é uma inserção (não atualização)
            self.login_tm = timezone.localtime().time()

        super().save(*args, **kwargs)
