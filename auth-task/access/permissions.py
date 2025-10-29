from rest_framework.permissions import BasePermission
from .models import Permission, UserRole, RolePermission

class HasPermission(BasePermission):
    def has_permission(self, request, view):
        # если пользователь не аутентифицирован — сразу нет
        if not getattr(request.user, "is_authenticated", False):
            return False

        resource = getattr(view, 'required_resource', None)
        action   = getattr(view, 'required_action', None)
        if not resource or not action:
            return True

        perm = Permission.objects.filter(resource=resource, action=action).first()
        if not perm:
            return False

        role_ids = UserRole.objects.filter(user=request.user).values_list('role_id', flat=True)

        # deny имеет приоритет
        if RolePermission.objects.filter(role_id__in=role_ids, permission=perm, effect='deny').exists():
            return False

        return RolePermission.objects.filter(role_id__in=role_ids, permission=perm, effect='allow').exists()
