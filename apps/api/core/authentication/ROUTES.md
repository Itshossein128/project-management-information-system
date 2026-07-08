# Authentication Routes

This document outlines the API endpoints provided by the `authentication` application and details their purposes.

## Base Path
All routes here are typically prefixed by the application's base URL configuration (e.g., `/api/auth/`).

---

### `POST /register/`
**View:** `UserRegistrationView`
- **Purpose:** Handles the creation of new user accounts.
- **Details:** Validates registration data (phone number, password, etc.), ensures the phone number is unique, assigns a default role, and creates the new user in the system. Open to any unauthenticated user.

### `POST /login/`
**View:** `LoginView`
- **Purpose:** Authenticates users and returns JWT tokens.
- **Details:** Validates the provided phone number and password. If the credentials are valid, returns a JSON Web Token (JWT) access token and a refresh token along with basic user information.

### `POST /token/refresh/`
**View:** `TokenRefreshView` (from `rest_framework_simplejwt`)
- **Purpose:** Refreshes an expired JWT access token.
- **Details:** Takes a valid refresh token and returns a new access token, ensuring continuous access without requiring re-authentication.

### `PUT /change-password/`
**View:** `ChangePasswordView`
- **Purpose:** Allows a logged-in user to change their password securely.
- **Details:** Validates the user's current password and securely hashes/saves the newly provided password. Requires the user to be authenticated.

### `POST /forgot-password/`
**View:** `ForgotPasswordView`
- **Purpose:** Initiates the password reset process.
- **Details:** Receives a phone number and (in a production setting) sends an SMS with a secure token to allow the user to reset a forgotten password. Returns a generic success message regardless of whether the account exists, for security purposes.

### `POST /reset-password/`
**View:** `ResetPasswordView`
- **Purpose:** Completes the password reset process.
- **Details:** Receives the secure token (sent via SMS) along with a new password to reset the user's password. Note: Needs a full production implementation for token storage/validation.

### `GET/PUT/PATCH /profile/`
**View:** `UserProfileView`
- **Purpose:** Manages the current authenticated user's profile information.
- **Details:**
  - `GET`: Retrieves the logged-in user's profile details.
  - `PUT`: Fully updates the user's profile.
  - `PATCH`: Partially updates the user's profile.

### `GET /system-roles/`
**View:** `SystemRolesListView`
- **Purpose:** Provides a list of all available system roles (Django Groups).
- **Details:** Retrieves all static Django Group instances (e.g., visitor, manager, hr) and formats them into a read-only list for the frontend UI. Requires the user to be authenticated.

### `GET /users/<int:user_id>/assignments/`
**View:** `UserAssignmentsListView`
- **Purpose:** Lists all business assignments associated with a specific user.
- **Details:** Returns `UserBusinessAssignment` records for a specific user ID. The requesting user can only see their own assignments unless they have specific HR or Admin permissions.

### `GET/POST /users/`
**View:** `UserListView`
- **Purpose:** Handles listing all users and creating users (for HR/Admin).
- **Details:**
  - `GET`: Returns a paginated list of all registered users (including account status and assigned roles). Requires the user to be authenticated and have HR or Admin privileges.
  - `POST`: Allows HR/Admin users to directly create new user accounts in the system.
