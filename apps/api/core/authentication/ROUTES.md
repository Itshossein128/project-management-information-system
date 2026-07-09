# Authentication Routes

API endpoints defined in `authentication/urls.py`. Base path is typically `/api/v1/auth/` (see `config/urls.py`).

## Endpoints

### `POST /register/`
**View:** `UserRegistrationView`
- Creates a new user account (public).
- Validates mobile/password, assigns the default `visitor` group, returns JWT access + refresh tokens.

### `POST /login/`
**View:** `LoginView`
- Authenticates with mobile + password; returns JWT tokens and user summary.
- Rate-limited via `LoginRateThrottle`.

### `POST /logout/`
**View:** `LogoutView`
- Blacklists the submitted refresh token (authenticated).

### `POST /token/refresh/`
**View:** `TokenRefreshView` (simplejwt)
- Exchanges a valid refresh token for a new access token.

### `POST /token/blacklist/`
**View:** `TokenBlacklistView` (simplejwt)
- Blacklists a refresh token.

### `PUT /change-password/`
**View:** `ChangePasswordView`
- Changes password for the authenticated user.

### `POST /forgot-password/`
**View:** `ForgotPasswordView`
- Starts password reset (public, rate-limited). Returns a generic success message.

### `POST /reset-password/`
**View:** `ResetPasswordView`
- Completes password reset with token + new password (public, rate-limited).

### `GET` / `PUT` / `PATCH /profile/`
**View:** `UserProfileView`
- Read or update the current user's profile.

### `GET /system-roles/`
**View:** `SystemRolesListView`
- Lists Django `Group` roles for UI pickers (authenticated).

### `GET /users/<uuid:user_id>/assignments/`
**View:** `UserAssignmentsListView`
- Lists `ProjectMember` assignments for a user (self or HR/admin).

### `GET` / `POST /users/`
**View:** `UserListView`
- `GET`: paginated user list (HR/admin).
- `POST`: create user via HR/admin flow.
