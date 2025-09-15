"""
Management command to test group-based permissions.

This module provides a Django management command that tests the functionality
of group-based permissions in the system.
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from drf_base_apps.core.abstract.constants import GroupChoices
from drf_base_apps.utils import get_user_model

User = get_user_model()


class Command(BaseCommand):
    """Management command to test group-based permissions."""

    help = "Testa a funcionalidade de permissões baseadas em grupos"

    def handle(self, *args, **options):
        """Handle the command execution."""
        self.stdout.write(f"{'-' * 50}")
        self.stdout.write("Testando sistema de permissões baseadas em grupos")
        self.stdout.write(f"{'-' * 50}")

        self.create_test_groups()

        test_user = self.create_test_user()

        self.test_permissions(test_user)

        self.cleanup_test_data(test_user)

    def create_test_groups(self):
        """Create test groups."""
        self.stdout.write("Criando grupos de teste...")

        for choice in GroupChoices:
            group_name = choice.value
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f"  - Grupo '{group_name}' criado")
            else:
                self.stdout.write(f"  - Grupo '{group_name}' já existe")

    def create_test_user(self):
        """Create a test user."""
        self.stdout.write("\nCriando usuário de teste...")

        username = "test_permission_user"

        User.objects.filter(username=username).delete()

        user = User.objects.create(
            username=username, first_name="Test", last_name="User", email="test@example.com", is_active=True
        )

        self.stdout.write(f"  - Usuário '{username}' criado")
        return user

    def test_permissions(self, user):
        """Test group-based permissions."""
        self.stdout.write("\nTestando permissões baseadas em grupos...")

        self.stdout.write("\n1. Sem grupos:")
        self.print_permissions(user)

        rh_group = Group.objects.get(name=GroupChoices.RH.value)
        user.groups.add(rh_group)
        user.save()

        self.stdout.write("\n2. Com grupo RH:")
        self.print_permissions(user)

        user.groups.remove(rh_group)
        clb_group = Group.objects.get(name=GroupChoices.CLB.value)
        user.groups.add(clb_group)
        user.save()

        self.stdout.write("\n3. Com grupo CLB:")
        self.print_permissions(user)

        intra_group = Group.objects.get(name=GroupChoices.INTRA.value)
        user.groups.add(intra_group)
        user.save()

        self.stdout.write("\n4. Com grupos CLB e INTRA:")
        self.print_permissions(user)

        user.groups.clear()
        integrator_group = Group.objects.get(name=GroupChoices.INTEGRATOR.value)
        user.groups.add(integrator_group)
        user.save()

        self.stdout.write("\n5. Com grupo INTEGRATOR:")
        self.print_permissions(user)

    def print_permissions(self, user):
        """Print user permissions."""
        user.refresh_from_db()

        self.stdout.write(f"  - has_rh_perm (campo): {user.has_rh_perm}")
        self.stdout.write(f"  - has_clb_perm (campo): {user.has_clb_perm}")
        self.stdout.write(f"  - has_rh_perm_group (property): {user.has_rh_perm_group}")
        self.stdout.write(f"  - has_clb_perm_group (property): {user.has_clb_perm_group}")
        self.stdout.write(f"  - has_intra_perm (property): {user.has_intra_perm}")
        self.stdout.write(f"  - has_integrator_perm (property): {user.has_integrator_perm}")

        self.stdout.write(f"  - Grupos: {', '.join([g.name for g in user.groups.all()])}")

    def cleanup_test_data(self, user):
        """Clean up test data."""
        self.stdout.write("\nLimpando dados de teste...")

        user.delete()
        self.stdout.write("  - Usuário de teste removido")

        self.stdout.write(f"\n{'-' * 50}")
        self.stdout.write("Teste concluído!")
        self.stdout.write(f"{'-' * 50}")
