from datetime import timedelta
from hashlib import sha256
from django.utils import timezone
from rest_framework.test import APITestCase
from users.models import User
from access.models import Role, Permission, RolePermission, UserRole, AccessToken

def issue_token(user):
    raw = "tkn-"+str(user.id)
    th = sha256(raw.encode()).hexdigest()
    AccessToken.objects.create(
        user=user, token_hash=th,
        expires_at=timezone.now() + timedelta(hours=1),
        revoked=False,
    )
    return raw

class RBACProjectsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # ресурсы/права
        cls.p_read = Permission.objects.create(resource="projects", action="read")
        cls.p_create = Permission.objects.create(resource="projects", action="create")

        # роль manager с allow: read
        cls.role_mgr = Role.objects.create(name="manager", description="can read projects")
        RolePermission.objects.create(role=cls.role_mgr, permission=cls.p_read, effect="allow")

        # пользователи
        cls.u_no = User.objects.create(email="noaccess@example.com", password_hash="x")
        cls.u_mgr = User.objects.create(email="mgr@example.com", password_hash="x")
        UserRole.objects.create(user=cls.u_mgr, role=cls.role_mgr)

    def test_401_without_token(self):
        r = self.client.get("/api/projects")
        self.assertEqual(r.status_code, 401)

    def test_403_without_permission(self):
        token = issue_token(self.u_no)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        r = self.client.get("/api/projects")
        self.assertEqual(r.status_code, 403)

    def test_200_with_read_permission(self):
        token = issue_token(self.u_mgr)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        r = self.client.get("/api/projects")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.data, list)

    def test_201_requires_create_permission(self):
        # manager сейчас имеет только read -> POST вернёт 403
        token = issue_token(self.u_mgr)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        r_forbidden = self.client.post("/api/projects/create", {"name":"X"}, format="json")
        self.assertEqual(r_forbidden.status_code, 403)

        # добавим allow create
        RolePermission.objects.create(role=self.role_mgr, permission=self.p_create, effect="allow")

        r_created = self.client.post("/api/projects/create", {"name":"X"}, format="json")
        self.assertEqual(r_created.status_code, 201)
        self.assertEqual(r_created.data["name"], "X")
