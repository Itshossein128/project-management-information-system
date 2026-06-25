"""
Authentication views following SOLID principles.
Views delegate business logic to services (Dependency Inversion Principle).
Uses phone_number as identifier (no username/email).
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from common.i18n import localize_api_payload

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserListSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from business_meta.serializers import ProjectMemberReadSerializer
from master_data.models import ProjectMember
from .permissions import IsHrOrAdmin
from .services import (
    UserRegistrationService,
    PasswordResetService,
    PasswordChangeService
)
from .utils import authenticate_user, get_tokens_for_user
from .throttles import LoginRateThrottle

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint.
    Single Responsibility: Handle user registration requests.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register a new user",
        description="""
        Create a new user account with phone number, first name, last name, and password.

        Password requirements:
        - Must be at least 8 characters long
        - Cannot be too similar to user information
        - Cannot be a commonly used password
        - Cannot be entirely numeric
        """,
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                description="User created and authenticated",
                response={
                    'type': 'object',
                    'properties': {
                        'access': {'type': 'string', 'description': 'JWT access token'},
                        'refresh': {'type': 'string', 'description': 'JWT refresh token'},
                        'user': {'type': 'object'},
                    },
                },
            ),
            400: OpenApiResponse(
                description="Validation error",
                response={
                    'type': 'object',
                    'properties': {
                        'field_name': {
                            'type': 'array',
                            'items': {'type': 'string'}
                        }
                    }
                }
            )
        },
        tags=['Authentication']
    )
    def create(self, request, *args, **kwargs):
        """Handle user registration."""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
                tokens = get_tokens_for_user(user)
                return Response(
                    {
                        'access': tokens['access'],
                        'refresh': tokens['refresh'],
                        'user': UserSerializer(user).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except ValidationError as e:
                return Response(
                    localize_api_payload(
                        e.message_dict if hasattr(e, 'message_dict') else {'error': e.messages}
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            localize_api_payload(serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    @extend_schema(
        summary="User login",
        description="""
        Authenticate user with phone number and return JWT access and refresh tokens.
        """,
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="Login successful",
                response={
                    'type': 'object',
                    'properties': {
                        'access': {'type': 'string', 'description': 'JWT access token'},
                        'refresh': {'type': 'string', 'description': 'JWT refresh token'},
                        'user': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'phone_number': {'type': 'string'},
                                'first_name': {'type': 'string'},
                                'last_name': {'type': 'string'},
                                'full_name': {'type': 'string'},
                                'roles': {'type': 'array', 'items': {'type': 'string'}}
                            }
                        }
                    }
                }
            ),
            401: OpenApiResponse(
                description="Invalid credentials",
                response={
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            )
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Handle user login."""
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                localize_api_payload(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )

        login = serializer.validated_data['login']
        password = serializer.validated_data['password']

        user = authenticate_user(login, password)

        if user is None:
            return Response(
                localize_api_payload(
                    {'error': _('Invalid credentials. Please check your phone number and password.')}
                ),
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                localize_api_payload({'error': _('User account is disabled.')}),
                status=status.HTTP_401_UNAUTHORIZED
            )

        tokens = get_tokens_for_user(user)
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class ChangePasswordView(generics.GenericAPIView):
    """
    Change password endpoint for authenticated users.
    Single Responsibility: Handle password change requests.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change password",
        description="""
        Change the password for the authenticated user.

        Requires:
        - Valid authentication token
        - Current password
        - New password (must meet Django's password validation requirements)
        """,
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="Password changed successfully",
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(
                description="Validation error",
                response={
                    'type': 'object',
                    'properties': {
                        'field_name': {
                            'type': 'array',
                            'items': {'type': 'string'}
                        }
                    }
                }
            ),
            401: OpenApiResponse(
                description="Unauthorized - Invalid or missing token"
            )
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Handle password change."""
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                localize_api_payload(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )

        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        try:
            service = PasswordChangeService()
            result = service.change_password(
                user=request.user,
                old_password=old_password,
                new_password=new_password
            )
            return Response(localize_api_payload(result), status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                localize_api_payload(
                    e.message_dict if hasattr(e, 'message_dict') else {'error': e.messages}
                ),
                status=status.HTTP_400_BAD_REQUEST
            )


class ForgotPasswordView(generics.GenericAPIView):
    """
    Forgot password endpoint.
    Single Responsibility: Handle password reset initiation.
    """
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Request password reset",
        description="""
        Request a password reset code via SMS.

        If an account exists with the provided phone number, a reset code will be sent.
        For security reasons, the response is the same whether the phone exists or not.
        """,
        request=ForgotPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="Password reset code sent (if account exists)",
                response={
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'message': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(
                description="Validation error",
                response={
                    'type': 'object',
                    'properties': {
                        'phone_number': {
                            'type': 'array',
                            'items': {'type': 'string'}
                        }
                    }
                }
            )
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Handle forgot password request."""
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                localize_api_payload(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )

        phone_number = serializer.validated_data['phone_number']

        service = PasswordResetService()
        result = service.initiate_password_reset(phone_number)

        return Response(localize_api_payload(result), status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    """
    Reset password endpoint with token.
    Single Responsibility: Handle password reset completion.
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Reset password with token",
        description="""
        Reset password using the token received via SMS.

        Note: This is a placeholder implementation. In production, you should:
        1. Store reset tokens in a database with expiration
        2. Validate token before allowing password reset
        3. Invalidate token after use
        """,
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="Password reset successfully",
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(
                description="Validation error or invalid token",
                response={
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            )
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Handle password reset."""
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                localize_api_payload(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        try:
            service = PasswordResetService()
            result = service.reset_password(token=token, new_password=new_password)
            return Response(localize_api_payload(result), status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                localize_api_payload(
                    e.message_dict if hasattr(e, 'message_dict') else {'error': e.messages}
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Logout (blacklist refresh token)', tags=['Authentication'])
    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response(
                localize_api_payload({'error': _('Refresh token is required.')}),
                status=status.HTTP_400_BAD_REQUEST,
            )
        from rest_framework_simplejwt.tokens import RefreshToken
        try:
            RefreshToken(refresh).blacklist()
        except Exception:
            return Response(
                localize_api_payload({'error': _('Invalid refresh token.')}),
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            localize_api_payload({'message': _('Logged out successfully.')}),
            status=status.HTTP_200_OK,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile endpoint.
    Single Responsibility: Handle user profile retrieval and updates.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user

    @extend_schema(
        summary="Get current user profile",
        description="Retrieve the profile of the authenticated user.",
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="User profile"
            ),
            401: OpenApiResponse(description="Unauthorized")
        },
        tags=['Authentication']
    )
    def get(self, request, *args, **kwargs):
        """Retrieve user profile."""
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update current user profile",
        description="Update the profile of the authenticated user.",
        request=UserSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="Updated user profile"
            ),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized")
        },
        tags=['Authentication']
    )
    def put(self, request, *args, **kwargs):
        """Update user profile."""
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update current user profile",
        description="Partially update the profile of the authenticated user.",
        request=UserSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="Updated user profile"
            ),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized")
        },
        tags=['Authentication']
    )
    def patch(self, request, *args, **kwargs):
        """Partially update user profile."""
        return super().patch(request, *args, **kwargs)


class UserListView(generics.ListCreateAPIView):
    """
    Paginated list of all application users (phone-based accounts).
    Restricted to HR or admin (see IsHrOrAdmin).

    Also supports HR/admin creation of new user accounts.
    """
    permission_classes = [IsAuthenticated, IsHrOrAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserRegistrationSerializer
        return UserListSerializer

    def get_queryset(self):
        return (
            User.objects.all()
            .order_by('-created_at', 'id')
            .prefetch_related(
                Prefetch(
                    'project_memberships',
                    queryset=ProjectMember.objects.select_related('project', 'position').order_by('project__project_name'),
                    to_attr='prefetched_memberships',
                )
            )
        )

    @extend_schema(
        summary="List users (HR / admin)",
        description=(
            "Returns paginated user accounts: phone, name, groups (roles), "
            "join date, and active flag. Requires `admin` or `hr` group, or staff / superuser."
        ),
        responses={
            200: OpenApiResponse(
                response=UserListSerializer(many=True),
                description="Paginated list",
            ),
            403: OpenApiResponse(description="Forbidden — not in HR or admin role"),
        },
        tags=["Authentication"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create user (HR / admin)",
        description=(
            "Create a new user account (phone-based). Requires `admin` or `hr` group, "
            "or staff / superuser. This is the same payload as public registration, "
            "but protected for HR/admin usage."
        ),
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                response=UserSerializer,
                description="User created successfully",
            ),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Forbidden — not in HR or admin role"),
        },
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserAssignmentsListView(generics.ListAPIView):
    serializer_class = ProjectMemberReadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        u = self.request.user
        if str(u.id) != str(user_id) and not IsHrOrAdmin().has_permission(self.request, self):
            raise PermissionDenied(
                _('You can only list your own assignments unless you are HR or admin.')
            )
        return (
            ProjectMember.objects.filter(user_id=user_id)
            .select_related('user', 'project', 'position')
            .order_by('project__project_name')
        )

    @extend_schema(
        summary='List assignments for a user',
        description='Returns all UserBusinessAssignment rows for the user. Owner or HR/admin only.',
        tags=['Authentication'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SystemRolesListView(APIView):
    """
    Read-only list of Django auth Group names (system roles). No CRUD via API.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='List system role names',
        description='Static groups used for global RBAC (e.g. admin, hr, visitor).',
        tags=['Authentication'],
    )
    def get(self, request):
        data = [
            {'name': g.name, 'label': g.name.replace('-', ' ').title()}
            for g in Group.objects.all().order_by('name')
        ]
        return Response(data)
