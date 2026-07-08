# Authentication Endpoints

This document outlines the endpoints defined in the `authentication` Django application. These endpoints manage user identity, registration, session (JWT tokens), profile management, and global roles.

## Base Path
Routes defined in `urls.py` are typically mounted at `/api/auth/`.

## Endpoints

### Registration & Login
* **`/api/auth/register/` (POST)**: Registers a new user.
* **`/api/auth/login/` (POST)**: Authenticates a user and returns JWT access and refresh tokens.
* **`/api/auth/token/refresh/` (POST)**: Refreshes an expired JWT access token using a valid refresh token.

### Password Management
* **`/api/auth/change-password/` (POST)**: Allows an authenticated user to change their current password.
* **`/api/auth/forgot-password/` (POST)**: Initiates a password reset request (e.g., sends an OTP or token via email/SMS).
* **`/api/auth/reset-password/` (POST)**: Completes the password reset process using the provided token.

### User Management
* **`/api/auth/profile/` (GET, PUT, PATCH)**: Retrieves or updates the currently authenticated user's profile details.
* **`/api/auth/users/` (GET)**: Lists all users in the system. Typically restricted to HR or administrative roles.
* **`/api/auth/users/<user_id>/assignments/` (GET)**: Retrieves all business assignments associated with a specific user.

### System Roles
* **`/api/auth/system-roles/` (GET)**: Lists all available global system roles (e.g., System Admin, HR).
