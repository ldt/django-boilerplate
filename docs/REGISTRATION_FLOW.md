# Registration Flow

This document outlines the user registration process in the application, covering both the frontend and backend components.

## Overview

The registration flow consists of the following steps:
1. User visits the registration page
2. Client-side validation using HTMX
3. Form submission
4. Server-side processing
5. Success/error handling

## Frontend (HTML/HTMX)

The registration form is located at `/templates/registration/register.html` and includes the following features:

### Real-time Validation

- **Username Availability**: Checks if username is already taken
- **Password Strength**: Validates password requirements
- **Email Format**: Ensures valid email format
- **Password Match**: Confirms password fields match

### Form Submission

```html
<form id="register-form" 
      hx-post="{% url 'register' %}"
      hx-target="#form-messages"
      hx-swap="innerHTML">
  <!-- Form fields -->
  <button type="submit">Create Account</button>
</form>
```

### Success Flow
1. Form is submitted via HTMX
2. Server processes the request
3. On success:
   - Success message is displayed
   - User is redirected to login page

### Error Handling
- Field-specific error messages are displayed below each field
- General form errors appear at the top of the form
- Server validation errors are shown to the user

## Backend (Django)

### Views

1. **RegisterView** (`accounts/views.py`)
   - Handles GET requests to display the form
   - Processes POST requests for form submission
   - Creates new user accounts
   - Logs in the user upon successful registration

2. **Validation Endpoints**
   - `POST /validate-username/`: Checks username availability
   - `POST /validate-password/`: Validates password strength

### Models

- **User** (`accounts/models.py`)
  - Custom user model with email as the unique identifier
  - Additional fields: first_name, last_name, etc.

### Forms

- **UserRegistrationForm** (`accounts/forms.py`)
  - Validates user input
  - Handles password confirmation
  - Includes terms acceptance checkbox

## Security Considerations

1. **Password Handling**
   - Passwords are hashed using PBKDF2
   - Password never stored in plaintext
   - Minimum length and complexity requirements

2. **CSRF Protection**
   - All forms include CSRF tokens
   - CSRF middleware enabled

3. **Rate Limiting**
   - Registration attempts are rate-limited
   - Failed login attempts are logged and limited

## Testing

Test coverage includes:

1. **Unit Tests**
   - Form validation
   - Model methods
   - View logic

2. **Integration Tests**
   - Complete registration flow
   - Error cases
   - Edge cases

3. **UI Tests**
   - Form validation
   - Error messages
   - Success flow

## Troubleshooting

### Common Issues

1. **Username already exists**
   - Check if the username is already taken
   - Usernames are case-insensitive

2. **Password validation fails**
   - Minimum 8 characters
   - Cannot be entirely numeric
   - Must match confirmation field

3. **Email already in use**
   - Each email can only be used once
   - Check for existing accounts with the same email

## Future Enhancements

1. Email verification
2. Social authentication
3. Multi-factor authentication
4. CAPTCHA integration
