"""
Authentication views following SOLID principles.
Views delegate business logic to services (Dependency Inversion Principle).
Uses phone_number as identifier (no username/email).
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTTokenRefreshView
from django.db.models import Prefetch
from rest_framework.exceptions import ValidationError
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
    AccountTokenRefreshSerializer,
)
from business_meta.serializers import ProjectMemberReadSerializer
from master_data.models import ProjectMember
from .permissions import IsHrOrAdmin, IsOrganizationalAccountAdmin
from .services import (
    UserRegistrationService,
    PasswordResetService,
    PasswordChangeService,
    LoginService,
    account_can_authenticate,
    blacklist_user_tokens,
)
from permissions.role_services import record_access_change
from projects.member_serializers import ProjectMemberListSerializer
from projects.services import AlreadyMember, InvitationInvalid, accept_invitation
from .utils import authenticate_user, get_tokens_for_user
from .ratelimit_handlers import auth_ratelimit

User = get_user_model()


def _first_message(errors) -> str:
    if isinstance(errors, dict):
        for value in errors.values():
            if isinstance(value, (list, tuple)) and value:
                return str(value[0])
            if value:
                return str(value)
    if isinstance(errors, (list, tuple)) and errors:
        return str(errors[0])
    return str(errors or _('Validation error.'))


def _error_envelope(message, code='validation_error', details=None, http_status=status.HTTP_400_BAD_REQUEST):
    return Response(
        localize_api_payload({
            'error': {
                'code': code,
                'message': str(message),
                'details': details or {},
            },
        }),
        status=http_status,
    )


@auth_ratelimit('10/m')
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
                service = UserRegistrationService()
                user, tokens = service.register_and_generate_tokens(**serializer.validated_data)
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


@auth_ratelimit('10/m')
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

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
            return _error_envelope(_first_message(serializer.errors), details=serializer.errors)

        login = serializer.validated_data['login']
        password = serializer.validated_data['password']

        service = LoginService()
        try:
            user, tokens = service.authenticate_and_issue_tokens(login, password)
        except ValidationError as e:
            return _error_envelope(
                _first_message(e.detail),
                code='authentication_failed',
                details=e.detail if isinstance(e.detail, dict) else {},
                http_status=status.HTTP_401_UNAUTHORIZED,
            )
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
            return _error_envelope(_first_message(serializer.errors), details=serializer.errors)

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
        except DjangoValidationError as e:
            details = e.message_dict if hasattr(e, 'message_dict') else {'password': e.messages}
            return _error_envelope(_first_message(details), details=details)
        except ValidationError as e:
            return _error_envelope(_first_message(e.detail), details=e.detail if isinstance(e.detail, dict) else {})


@auth_ratelimit('5/m')
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
            return _error_envelope(_first_message(serializer.errors), details=serializer.errors)

        phone_number = serializer.validated_data['phone_number']

        service = PasswordResetService()
        result = service.initiate_password_reset(phone_number)

        return Response(localize_api_payload(result), status=status.HTTP_200_OK)


@auth_ratelimit('5/m')
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
        Tokens are stored in the database with expiration and invalidated after use.
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
            return _error_envelope(_first_message(serializer.errors), details=serializer.errors)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        try:
            service = PasswordResetService()
            result = service.reset_password(token=token, new_password=new_password)
            return Response(localize_api_payload(result), status=status.HTTP_200_OK)
        except DjangoValidationError as e:
            details = e.message_dict if hasattr(e, 'message_dict') else {'password': e.messages}
            return _error_envelope(_first_message(details), details=details)
        except ValidationError as e:
            return _error_envelope(_first_message(e.detail), details=e.detail if isinstance(e.detail, dict) else {})


@auth_ratelimit('30/m')
class TokenRefreshView(SimpleJWTTokenRefreshView):
    """JWT refresh with IP rate limiting."""

    permission_classes = [AllowAny]
    serializer_class = AccountTokenRefreshSerializer


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
        try:
            token = RefreshToken(refresh)
        except TokenError:
            return _error_envelope(_('Invalid refresh token.'))
        if str(token.get(api_settings.USER_ID_CLAIM)) != str(request.user.pk):
            return _error_envelope(_('Invalid refresh token.'))
        try:
            token.blacklist()
        except TokenError:
            return _error_envelope(_('Invalid refresh token.'))
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


class AccountAdministrationDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'account_forbidden'
    default_detail = _('You cannot manage organizational accounts.')


class UserListView(generics.ListCreateAPIView):
    """
    Paginated list of all application users (phone-based accounts).
    Restricted to HR or admin (see IsHrOrAdmin).

    Also supports HR/admin creation of new user accounts.
    """
    permission_classes = [IsAuthenticated, IsOrganizationalAccountAdmin]

    def permission_denied(self, request, message=None, code=None):
        raise AccountAdministrationDenied()

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
                ),
                'groups', # ⚡ Bolt: Prefetch groups to avoid N+1 queries in UserListSerializer
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
        try:
            user = serializer.save()
        except DjangoValidationError as exc:
            details = exc.message_dict if hasattr(exc, 'message_dict') else {'password': exc.messages}
            return _error_envelope(_first_message(details), details=details)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class AccountStatusView(APIView):
    """Change the visible account status. Sign-in follows that status."""

    permission_classes = [IsAuthenticated, IsOrganizationalAccountAdmin]

    def permission_denied(self, request, message=None, code=None):
        raise AccountAdministrationDenied()

    @extend_schema(summary='Set organizational account status', tags=['Authentication'])
    def patch(self, request, user_id):
        next_status = (request.data or {}).get('status')
        if next_status not in ('active', 'inactive', 'suspended'):
            return Response(
                {'error': {'code': 'validation_error', 'message': _('Status must be active, inactive, or suspended.'), 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = get_object_or_404(User, pk=user_id)
        before = user.status
        sign_in_matches = user.is_active == (next_status == 'active')
        if before == next_status and sign_in_matches:
            return Response({'status': user.status, 'can_sign_in': account_can_authenticate(user)})
        user.status = next_status
        user.is_active = next_status == 'active'
        user.save(update_fields=['status', 'is_active'])
        if next_status in ('inactive', 'suspended'):
            blacklist_user_tokens(user)
        record_access_change(
            actor=request.user,
            project=None,
            subject_user=user,
            role=None,
            action='account_status_changed',
            before={'status': before},
            after={'status': next_status},
        )
        return Response({'status': user.status, 'can_sign_in': account_can_authenticate(user)})


class InvitationAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Accept a project invitation', tags=['Authentication'])
    def post(self, request):
        try:
            member = accept_invitation(token=(request.data or {}).get('token') or '', user=request.user)
        except InvitationInvalid:
            return Response(
                {
                    'error': {
                        'code': 'invitation_invalid',
                        'message': _('This invitation can no longer be used.'),
                        'details': {},
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except AlreadyMember:
            return Response(
                {
                    'error': {
                        'code': 'already_member',
                        'message': _('This person already has a membership in this project.'),
                        'details': {},
                    },
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(ProjectMemberListSerializer(member).data)


class UserAssignmentsListView(generics.ListAPIView):
    serializer_class = ProjectMemberReadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        u = self.request.user
        if str(u.pk) != str(user_id) and not IsOrganizationalAccountAdmin().has_permission(
            self.request, self
        ):
            raise PermissionDenied(
                _('You can only list your own assignments unless you are an account administrator.')
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
        labels = {
            'admin': _('Admin'),
            'hr': _('HR'),
            'manager': _('Manager'),
            'visitor': _('Visitor'),
            'engineer': _('Engineer'),
            'accountant': _('Accountant'),
            'business-setup': _('Business setup'),
        }
        data = [
            {
                'name': g.name,
                'label': str(labels.get(g.name, g.name.replace('-', ' ').title())),
            }
            for g in Group.objects.all().order_by('name')
        ]
        return Response(localize_api_payload(data))
