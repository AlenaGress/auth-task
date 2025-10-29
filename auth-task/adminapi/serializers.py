# adminapi/serializers.py
from rest_framework import serializers
from access.models import Role, Permission, RolePermission, UserRole

class RoleSerializer(serializers.ModelSerializer):
    class Meta: model = Role; fields = "__all__"

class PermissionSerializer(serializers.ModelSerializer):
    class Meta: model = Permission; fields = "__all__"

class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta: model = RolePermission; fields = "__all__"

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta: model = UserRole; fields = "__all__"
