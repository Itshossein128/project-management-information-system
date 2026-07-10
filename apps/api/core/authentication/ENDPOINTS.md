# Authentication Endpoints

This document details the endpoints provided by the `authentication` app for user lifecycle and profile management.

## Authentication & Authorization
- `POST /api/auth/register/`
  - **Purpose**: Allows a new user to sign up for the platform.
- `POST /api/auth/login/`
  - **Purpose**: Authenticates a user (via phone number and password) and issues JWT tokens.
- `POST /api/auth/token/refresh/`
  - **Purpose**: Refreshes an expired JWT access token using a valid refresh token.

## Password Management
- `POST /api/auth/change-password/`
  - **Purpose**: Allows an authenticated user to change their current password.
- `POST /api/auth/forgot-password/`
  - **Purpose**: Initiates the password recovery process (e.g., sending an OTP or reset link).
- `POST /api/auth/reset-password/`
  - **Purpose**: Completes the password recovery process using a verification token/OTP and a new password.

## User & Profile Management
- `GET/PUT /api/auth/profile/`
  - **Purpose**: Retrieves or updates the authenticated user's own profile information.
- `GET /api/auth/system-roles/`
  - **Purpose**: Lists available system-wide roles that can be assigned to users.
- `GET /api/auth/users/`
  - **Purpose**: Lists platform users (typically restricted to HR or Admin personnel).
- `GET /api/auth/users/<int:user_id>/assignments/`
  - **Purpose**: Retrieves the business role assignments for a specific user.
