from django.core.management.base import BaseCommand
from users.models import User
from access.models import Role, Permission, RolePermission, UserRole

class Command(BaseCommand):
    help = "Initialize default roles and permissions for RBAC"

    def handle(self, *args, **options):
        admin_role, _ = Role.objects.get_or_create(name="admin", defaults={"description": "Administrator"})

        specs = [
            ("projects", "read"),
            ("projects", "create"),
            ("acl", "read"),
            ("acl", "create"),
            ("acl", "update"),
            ("acl", "delete"),
        ]

        perms = [Permission.objects.get_or_create(resource=r, action=a)[0] for r, a in specs]

        for p in perms:
            RolePermission.objects.get_or_create(role=admin_role, permission=p, defaults={"effect": "allow"})

        u = User.objects.filter(email="user1@example.com").first()
        if u:
            UserRole.objects.get_or_create(user=u, role=admin_role)
            self.stdout.write(self.style.SUCCESS(f"✅ Bootstrap complete for: {u.email}"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ User user1@example.com not found."))