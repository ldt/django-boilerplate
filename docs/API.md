# API Documentation

This document outlines the available API endpoints for user authentication and profile management.

## Base URL
All API endpoints are prefixed with `/api/v1/`.

## Authentication
Most endpoints require authentication using JWT (JSON Web Tokens). Include the token in the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

## Endpoints

### Register a New User

**Endpoint:** `POST /api/v1/auth/register/`

**Request Body:**
```json
{
    "email": "user@example.com",
    "username": "newuser",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
}
```

**Success Response (201 Created):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Login

**Endpoint:** `POST /api/v1/auth/login/`

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Success Response (200 OK):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Refresh Token

**Endpoint:** `POST /api/v1/auth/token/refresh/`

**Request Body:**
```json
{
    "refresh": "your_refresh_token_here"
}
```

**Success Response (200 OK):**
```json
{
    "access": "new_access_token_here"
}
```

### Get User Profile

**Endpoint:** `GET /api/v1/auth/profile/`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Success Response (200 OK):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2023-01-01T12:00:00Z"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```
