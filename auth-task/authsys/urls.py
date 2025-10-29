from django.contrib import admin
from django.urls import path, include
from users.views import RegisterView, LoginView, LogoutView, MeView
from mock.views import ProjectsList, ProjectsCreate
from rest_framework.routers import DefaultRouter
from adminapi.viewsets import RoleViewSet, PermissionViewSet, RolePermissionViewSet, UserRoleViewSet

router = DefaultRouter()
router.register(r'admin/roles', RoleViewSet, basename='roles')
router.register(r'admin/permissions', PermissionViewSet, basename='permissions')
router.register(r'admin/role-permissions', RolePermissionViewSet, basename='role-permissions')
router.register(r'admin/user-roles', UserRoleViewSet, basename='user-roles')

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/register", RegisterView.as_view()),
    path("api/auth/login",    LoginView.as_view()),
    path("api/auth/logout",   LogoutView.as_view()),
    path("api/users/me",      MeView.as_view()),

    path("api/projects",      ProjectsList.as_view()),
    path("api/projects/create", ProjectsCreate.as_view()),

    path("api/", include(router.urls)),
]
