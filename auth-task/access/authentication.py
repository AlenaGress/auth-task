from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from hashlib import sha256
from .models import AccessToken

class TokenAuth(BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth:  # нет заголовка
            # 401 NotAuthenticated
            raise exceptions.NotAuthenticated('Authentication credentials were not provided.')

        if not auth.startswith(self.keyword + ' '):
            # 401 неверный формат
            raise exceptions.AuthenticationFailed('Invalid Authorization header')

        raw = auth.split(' ', 1)[1].strip()
        token_hash = sha256(raw.encode('utf-8')).hexdigest()
        try:
            at = AccessToken.objects.select_related('user').get(token_hash=token_hash)
        except AccessToken.DoesNotExist:
            # 401 токен не найден
            raise exceptions.AuthenticationFailed('Invalid token')

        if not at.user.is_active:
            raise exceptions.AuthenticationFailed('Inactive user')
        if not at.is_valid():
            raise exceptions.AuthenticationFailed('Token expired or revoked')

        return (at.user, None)

    # важно: чтобы DRF отдавал 401, нужен WWW-Authenticate
    def authenticate_header(self, request):
        return self.keyword
