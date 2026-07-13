# Authentication Endpoints

This module handles user authentication, registration, password management, and user profiles.
It uses JSON Web Tokens (JWT) for authentication. All endpoints are grouped under the `Authentication` tag in the API documentation.

## Base URL: `/api/auth/`

## Endpoints

### 1. User Registration
*   **URL:** `/register/`
*   **Method:** `POST`
*   **Description:** Creates a new user account using a phone number. Validates password strength and uniqueness. Returns JWT tokens upon successful registration.
*   **Permissions:** `AllowAny` (Publicly accessible)
*   **Rate Limit:** 10 requests per minute

### 2. User Login
*   **URL:** `/login/`
*   **Method:** `POST`
*   **Description:** Authenticates a user using their phone number and password. Returns a pair of JWT access and refresh tokens.
*   **Permissions:** `AllowAny`
*   **Rate Limit:** 10 requests per minute

### 3. Change Password
*   **URL:** `/change-password/`
*   **Method:** `POST`
*   **Description:** Allows an authenticated user to change their current password. Requires providing the old password and the new one.
*   **Permissions:** `IsAuthenticated`

### 4. Forgot Password
*   **URL:** `/forgot-password/`
*   **Method:** `POST`
*   **Description:** Initiates a password reset process. If the provided phone number exists, an SMS code (or email, depending on implementation) is sent. The response is consistent regardless of account existence to prevent user enumeration.
*   **Permissions:** `AllowAny`
*   **Rate Limit:** 5 requests per minute

### 5. Reset Password
*   **URL:** `/reset-password/`
*   **Method:** `POST`
*   **Description:** Completes the password reset process using the token received via the forgot password flow. Validates the new password.
*   **Permissions:** `AllowAny`
*   **Rate Limit:** 5 requests per minute

### 6. Token Refresh
*   **URL:** `/token/refresh/`
*   **Method:** `POST`
*   **Description:** Refreshes an expired JWT access token using a valid refresh token.
*   **Permissions:** `AllowAny`
*   **Rate Limit:** 30 requests per minute

### 7. Logout
*   **URL:** `/logout/`
*   **Method:** `POST`
*   **Description:** Logs out a user by blacklisting their provided refresh token, rendering it invalid for future use.
*   **Permissions:** `IsAuthenticated`

### 8. User Profile
*   **URL:** `/profile/`
*   **Methods:** `GET`, `PUT`, `PATCH`
*   **Description:**
    *   `GET`: Retrieves the profile information of the currently authenticated user.
    *   `PUT`: Updates the user's profile completely.
    *   `PATCH`: Partially updates the user's profile.
*   **Permissions:** `IsAuthenticated`

### 9. User Management (HR/Admin)
*   **URL:** `/users/`
*   **Methods:** `GET`, `POST`
*   **Description:**
    *   `GET`: Retrieves a paginated list of all application users. Includes pre-fetched group and project membership data.
    *   `POST`: Allows HR or Admin users to create new user accounts directly.
*   **Permissions:** `IsAuthenticated`, `IsHrOrAdmin`

### 10. User Assignments
*   **URL:** `/users/<user_id>/assignments/`
*   **Method:** `GET`
*   **Description:** Lists all project assignments for a specific user. Users can only view their own assignments unless they have HR or Admin privileges.
*   **Permissions:** `IsAuthenticated` (with object-level checks)

### 11. System Roles
*   **URL:** `/system-roles/`
*   **Method:** `GET`
*   **Description:** Returns a read-only list of available system roles (Django Groups).
*   **Permissions:** `IsAuthenticated`

### 12. Token Verify
*   **URL:** `/token/verify/`
*   **Method:** `POST`
*   **Description:** Verifies the validity of a JWT token.
*   **Permissions:** `AllowAny`

### 13. Token Blacklist
*   **URL:** `/token/blacklist/`
*   **Method:** `POST`
*   **Description:** Blacklists a specific JWT token.
*   **Permissions:** `AllowAny`
