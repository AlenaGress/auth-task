from django.db import models
from django.utils import timezone

class AccessToken(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=128, unique=True)  # sha256(hex)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)

    def is_valid(self) -> bool:
        return (not self.revoked) and (self.expires_at > timezone.now())

# ---- RBAC ----
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self): return self.name

class Permission(models.Model):
    resource = models.CharField(max_length=50)   # напр. "projects" или "acl"
    action   = models.CharField(max_length=20)   # "read" | "create" | "update" | "delete"

    class Meta:
        unique_together = ('resource','action')

    def __str__(self): return f"{self.resource}:{self.action}"

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    effect = models.CharField(max_length=10, default='allow')  # 'allow' | 'deny'

class UserRole(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user','role')
