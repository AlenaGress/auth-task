import os, hashlib
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import User
from access.models import AccessToken
import os, hashlib
from datetime import timedelta


def _issue_token(user):
    raw = os.urandom(32).hex()  # 256 бит
    token_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    AccessToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=timezone.now() + timedelta(hours=24),
    )
    return raw

class RegisterView(APIView):
    authentication_classes = []                 
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        data = request.data
        required = ("email","password","confirm_password")
        if any(k not in data for k in required):
            return Response({"detail":"email, password, confirm_password required"}, status=400)
        if data["password"] != data["confirm_password"]:
            return Response({"detail":"Passwords do not match"}, status=400)
        if User.objects.filter(email=data["email"]).exists():
            return Response({"detail":"Email already used"}, status=400)

        u = User(
            email=data["email"],
            first_name=data.get("first_name",""),
            last_name=data.get("last_name",""),
            middle_name=data.get("middle_name",""),
        )
        u.set_password(data["password"])
        u.save()
        return Response({"id": u.id, "email": u.email}, status=201)

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get("email")
        pwd   = request.data.get("password")
        try:
            u = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail":"Invalid credentials"}, status=400)
        if not u.is_active or not u.check_password(pwd):
            return Response({"detail":"Invalid credentials"}, status=400)
        token_raw = _issue_token(u)
        return Response({"access_token": token_raw})

class LogoutView(APIView):
    def post(self, request):
        # revoke текущего токена из заголовка
        auth = request.META.get('HTTP_AUTHORIZATION','')
        if auth.startswith('Bearer '):
            raw = auth.split(' ',1)[1].strip()
            th = hashlib.sha256(raw.encode()).hexdigest()
            AccessToken.objects.filter(token_hash=th, revoked=False).update(revoked=True)
        return Response(status=204)

class MeView(APIView):
    def get(self, request):
        u = request.user
        return Response({
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "middle_name": u.middle_name,
            "is_active": u.is_active,
        })

    def patch(self, request):
        u = request.user
        for f in ["first_name","last_name","middle_name","email"]:
            if f in request.data:
                setattr(u, f, request.data[f])
        try:
            u.save()
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
        return Response({"detail": "updated"})

    def delete(self, request):
        u = request.user
        u.is_active = False
        u.save()
        AccessToken.objects.filter(user=u, revoked=False).update(revoked=True)
        return Response(status=204)
