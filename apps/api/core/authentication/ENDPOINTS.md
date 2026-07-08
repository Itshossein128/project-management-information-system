# Authentication Endpoints

This directory handles authentication and user management for the application. The main URLs are defined in `urls.py` and map to views in `views.py`.

## Endpoints

- `POST /api/auth/register/`: Registers a new user.
- `POST /api/auth/login/`: Authenticates a user and returns JWT tokens (access & refresh).
- `POST /api/auth/token/refresh/`: Refreshes an expired JWT access token.
- `POST /api/auth/change-password/`: Allows an authenticated user to change their password.
- `POST /api/auth/forgot-password/`: Initiates the password reset process.
- `POST /api/auth/reset-password/`: Completes the password reset process using a token.
- `GET/PUT /api/auth/profile/`: Retrieves or updates the currently authenticated user's profile.
- `GET /api/auth/system-roles/`: Lists available system roles.
- `GET /api/auth/users/<int:user_id>/assignments/`: Lists roles and assignments for a specific user.
- `GET /api/auth/users/`: Lists all users in the system (typically restricted to admins/HR).

These endpoints delegate complex business logic (like JWT issuance, user creation) to `services.py` following the Dependency Inversion Principle.