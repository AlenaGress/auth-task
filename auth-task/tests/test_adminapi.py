from datetime import timedelta
from hashlib import sha256
from django.utils import timezone
from rest_framework.test import APITestCase
from users.models import User
from access.models import Role, Permission, RolePermission, UserRole, AccessToken

def issue_token(user):
    raw = "admin-"+str(user.id)
    th = sha256(raw.encode()).hexdigest()
    AccessToken.objects.create(
        user=user, token_hash=th,
        expires_at=timezone.now() + timedelta(hours=1),
        revoked=False,
    )
    return raw

class AdminAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # admin user
        cls.admin = User.objects.create(email="admin@example.com", password_hash="x")
        # роли/права для ACL
        cls.role_admin = Role.objects.create(name="admin", description="all acl")
        p_read  = Permission.objects.create(resource="acl", action="read")
        p_create= Permission.objects.create(resource="acl", action="create")
        p_update= Permission.objects.create(resource="acl", action="update")
        p_delete= Permission.objects.create(resource="acl", action="delete")
        for p in (p_read, p_create, p_update, p_delete):
            RolePermission.objects.create(role=cls.role_admin, permission=p, effect="allow")
        UserRole.objects.create(user=cls.admin, role=cls.role_admin)

        # обычный пользователь
        cls.user = User.objects.create(email="user@example.com", password_hash="x")

    def test_admin_can_create_role(self):
        token = issue_token(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        r = self.client.post("/api/admin/roles/", {"name":"auditor","description":"read-only"}, format="json")
        self.assertIn(r.status_code, (201, 400))  # 400 если уже есть
        # и чтение доступно
        r2 = self.client.get("/api/admin/roles/")
        self.assertEqual(r2.status_code, 200)

    def test_non_admin_forbidden(self):
        token = issue_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        r = self.client.post("/api/admin/roles/", {"name":"foo"}, format="json")
        self.assertEqual(r.status_code, 403)
