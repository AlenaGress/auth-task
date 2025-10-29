from datetime import timedelta
from hashlib import sha256
from django.utils import timezone
from rest_framework.test import APITestCase
from users.models import User
from access.models import AccessToken

API = "http://testserver"  # APITestCase сам подменяет хост

def issue_token(user):
    raw = "testtoken123"
    th = sha256(raw.encode()).hexdigest()
    AccessToken.objects.create(
        user=user, token_hash=th,
        expires_at=timezone.now() + timedelta(hours=1),
        revoked=False,
    )
    return raw

class AuthFlowTests(APITestCase):
    def test_register_201_and_unique_email_400(self):
        # 201
        r = self.client.post("/api/auth/register", {
            "email": "u1@example.com", "password": "Pass1234!", "confirm_password": "Pass1234!",
            "first_name": "Alena"
        }, format="json")
        self.assertEqual(r.status_code, 201)

        # 400 при повторе email
        r2 = self.client.post("/api/auth/register", {
            "email": "u1@example.com", "password": "Pass1234!", "confirm_password": "Pass1234!"
        }, format="json")
        self.assertEqual(r2.status_code, 400)

    def test_login_200_and_me_200_vs_401(self):
        u = User(email="u2@example.com"); u.set_password("Pass1234!"); u.save()

        # 401 на /me без токена
        r0 = self.client.get("/api/users/me")
        self.assertEqual(r0.status_code, 401)

        # login -> 200 и токен
        r = self.client.post("/api/auth/login", {
            "email":"u2@example.com", "password":"Pass1234!"
        }, format="json")
        self.assertEqual(r.status_code, 200)
        token = r.data["access_token"]

        # /me с токеном -> 200
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        r2 = self.client.get("/api/users/me")
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.data["email"], "u2@example.com")

    def test_logout_204_then_401(self):
        u = User(email="u3@example.com"); u.set_password("Pass1234!"); u.save()
        token = issue_token(u)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        r = self.client.post("/api/auth/logout")
        self.assertEqual(r.status_code, 204)

        # тем же токеном запрос теперь 401
        r2 = self.client.get("/api/users/me")
        self.assertEqual(r2.status_code, 401)
