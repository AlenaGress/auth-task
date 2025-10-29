# adminapi/viewsets.py
from rest_framework import viewsets
from access.permissions import HasPermission
from access.models import Role, Permission, RolePermission, UserRole
from .serializers import (
    RoleSerializer, PermissionSerializer, RolePermissionSerializer, UserRoleSerializer
)
from rest_framework.permissions import IsAuthenticated

class ACLBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasPermission]  
    required_resource = "acl"

class RoleViewSet(ACLBaseViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    required_action = "read"   # по умолчанию (GET list/detail)
    def get_permissions(self):
        # Меняем action в зависимости от метода
        method = self.request.method
        self.required_action = "read" if method in ("GET", "HEAD", "OPTIONS") else \
                               "create" if method == "POST" else \
                               "update" if method in ("PUT","PATCH") else \
                               "delete"
        return super().get_permissions()

class PermissionViewSet(RoleViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

class RolePermissionViewSet(RoleViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer

class UserRoleViewSet(RoleViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
