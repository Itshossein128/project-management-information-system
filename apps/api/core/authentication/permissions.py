"""
Role-based permission classes (SOLID: one concern per class).
Use Django's Group model; role names match group names (e.g. visitor, manager, commentor, human-resource).
Designed so you can apply these per route/endpoint/operation later.
"""
from rest_framework import permissions


# Class representing IsInGroup
class IsInGroup(permissions.BasePermission):
    """
    Allow only if the user belongs to the given Django group (role).
    Use for role-based access; add more roles by creating new group and
    using IsInGroup('role_name') or a dedicated permission class.
    """
    role_name: str = ""

    # Function to handle   init
    def __init__(self, role_name: str = "", **kwargs):
        super().__init__(**kwargs)
        self.role_name = role_name or getattr(self.__class__, "role_name", "")

    # Function to handle has permission
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if not self.role_name:
            return True
        return request.user.groups.filter(name=self.role_name).exists()


# Class representing IsVisitor
class IsVisitor(IsInGroup):
    """Allow only users in the 'visitor' group."""
    role_name = "visitor"


# Class representing IsManager
class IsManager(IsInGroup):
    """Allow only users in the 'manager' group."""
    role_name = "manager"


# Class representing IsCommentor
class IsCommentor(IsInGroup):
    """Allow only users in the 'commentor' group."""
    role_name = "commentor"

# Class representing IsHumanResource
class IsHumanResource(IsInGroup):
    """Allow only users in the 'hr' group."""
    role_name = "hr"


# Class representing IsBusinessSetup
class IsBusinessSetup(IsInGroup):
    """
    Allow only users in the 'business-setup' group.
    Can add businesses and control features of each business.
    Assign only to support users (e.g. via Django admin).
    """
    role_name = "business-setup"


# Class representing IsManagerOrHR
class IsManagerOrHR(permissions.BasePermission):
    """
    Allow authenticated users for safe methods (GET, HEAD, OPTIONS).
    For unsafe methods, require Django group 'manager' or 'hr'.
    """
    # Function to handle has permission
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name__in=("manager", "hr")).exists()


# Class representing IsHrOrAdmin
class IsHrOrAdmin(permissions.BasePermission):
    """
    HR / admin user listing: Django groups `admin` or `hr`, or staff / superuser.
    Matches the HR users area in the frontend.
    """
    # Function to handle has permission
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        u = request.user
        if u.is_superuser or u.is_staff:
            return True
        return u.groups.filter(name__in=("admin", "hr")).exists()


# Apply per view when you add route/endpoint/operation checks, e.g.:
#   permission_classes = [IsAuthenticated, IsManager]
#   permission_classes = [IsAuthenticated, (IsManager | IsCommentor)]
#   permission_classes = [IsAuthenticated, IsVisitor]  # any authenticated user with visitor role
