# Notifications Endpoints

This document describes the API endpoints available in the `notifications` app, which provides user-scoped in-app notifications functionality.

## `GET /`
**Purpose**: Lists notifications for the currently authenticated user.
**Query Parameters**:
- `is_read` (boolean, optional): Filter notifications by their read state.
- `project` (string, optional): Filter notifications by project ID.

## `GET /<uuid:pk>/`
**Purpose**: Retrieves the details of a specific notification.

## `GET /unread-count/`
**Purpose**: Returns the total number of unread notifications for the currently authenticated user.

## `POST /<uuid:pk>/mark-read/`
**Purpose**: Marks a specific notification as read and records the `read_at` timestamp. If the notification is already read, it does nothing.

## `POST /mark-all-read/`
**Purpose**: Batch updates all unread notifications for the currently authenticated user, marking them as read and setting their `read_at` timestamp to the current time.
