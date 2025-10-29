from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from access.permissions import HasPermission

class ProjectsList(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_resource = "projects"
    required_action   = "read"

    def get(self, request):
        return Response([
            {"id": 1, "name": "Demo Project"},
            {"id": 2, "name": "Secret Project"},
        ])

class ProjectsCreate(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_resource = "projects"
    required_action   = "create"

    def post(self, request):
        return Response({"id": 3, "name": request.data.get("name","New Project")}, status=201)
