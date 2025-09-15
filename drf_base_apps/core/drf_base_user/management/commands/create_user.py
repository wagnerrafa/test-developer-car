"""Management command to create development users."""

from django.core.management.base import BaseCommand

from drf_base_apps.utils import get_user_model
from drf_base_config.settings import ENV_DEV, PASSWD_DEV, USER_ADM_DEV, USER_DEV

User = get_user_model()


class Command(BaseCommand):
    """Command to create development users."""

    help = "Run create user dev and admin"

    def write_msg(self, msg):
        """Write a warning message to stdout."""
        self.stdout.write(self.style.WARNING(msg))

    def create_user(self):
        """Create User dev and admin to local or dev mode."""
        try:

            return []

            if not ENV_DEV:
                return

            user, created = User.objects.update_or_create(
                username=USER_ADM_DEV,
                defaults={
                    "first_name": "admin",
                    "last_name": "dev",
                    "is_staff": True,
                    "is_active": True,
                    "email": "dev_admin@base_django.com",
                    "is_superuser": True,
                },
            )
            user.set_password(PASSWD_DEV)
            user.save()

            self.write_msg(f'User Admin {"created" if created else "altered"}')

            user, created = User.objects.update_or_create(
                username=USER_DEV,
                defaults={
                    "first_name": "user",
                    "last_name": "dev",
                    "is_staff": False,
                    "is_active": True,
                    "email": "user_admin@base_django.com",
                    "is_superuser": False,
                },
            )
            user.set_password(PASSWD_DEV)
            user.save()

            self.write_msg(f'User Dev {"created" if created else "altered"}')

        except Exception as e:
            self.write_msg(e)

    def delete_user(self):
        """Delete users with empty email addresses."""
        user = User.objects.filter(email__icontains="").first()
        if user:
            user.projectuser_set.all().delete()
            user.loginrecord_set.all().delete()
            user.delete()

    def handle(self, *args, **options):
        """Handle the command execution."""
        self.create_user()
