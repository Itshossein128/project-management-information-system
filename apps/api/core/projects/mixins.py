from rest_framework.permissions import IsAuthenticated

from projects.permissions import IsProjectMember

PROJECT_MEMBER_PERMISSIONS = [IsAuthenticated, IsProjectMember]
