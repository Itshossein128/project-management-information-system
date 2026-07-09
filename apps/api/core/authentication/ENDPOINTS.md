# Authentication Endpoints Documentation

This application handles authentication, token lifecycle, and user profile management.

## Base Path
`/api/auth/`

## Endpoints

### Authentication & Token Management
*   **POST** `/register/`: Register a new user account.
*   **POST** `/login/`: Authenticate and obtain JWT access and refresh tokens.
*   **POST** `/token/refresh/`: Refresh an expired access token using a valid refresh token.

### Password Management
*   **POST** `/change-password/`: Update the authenticated user's password.
*   **POST** `/forgot-password/`: Initiate a password reset request via email.
*   **POST** `/reset-password/`: Complete a password reset request with a valid token.

### User Profile & Listing
*   **GET/PUT** `/profile/`: Retrieve or update the authenticated user's profile details.
*   **GET** `/users/`: List all users (usually restricted to admin/HR roles).
*   **GET** `/users/<int:user_id>/assignments/`: Retrieve all business assignments for a specific user.
*   **GET** `/system-roles/`: List all available system-level roles and permissions.
