# Authentication Endpoints

This module handles user authentication and session management.

## Endpoints

- `POST /api/v1/auth/login/`: Authenticate user and issue JWT token.
- `POST /api/v1/auth/refresh/`: Refresh the access token using a valid refresh token.
- `POST /api/v1/auth/logout/`: Invalidate the current session or tokens.
- `GET /api/v1/auth/me/`: Retrieve profile information for the currently authenticated user.
