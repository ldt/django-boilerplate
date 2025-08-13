# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
- **Dependencies**: `uv sync` (installs from uv.lock)
- **Database migrations**: `python manage.py migrate`
- **Create superuser**: `python manage.py createsuperuser`
- **Development server**: `python manage.py runserver`

### Testing & Code Quality
- **Run unit tests**: `uv run pytest` or `pytest`
- **Run E2E tests**: `uv run pytest -c pytest-e2e.ini tests/e2e/`
- **Install Playwright browsers**: `uv run playwright install`
- **Code formatting & linting**: `uvx ruff check`
- **Single test file**: `pytest accounts/tests/test_authentication.py`
- **Test with verbose output**: `pytest -v`
- **E2E tests (headless)**: `pytest tests/e2e/ --headed=false`
- **E2E tests (headed)**: `pytest tests/e2e/ --headed=true`

### Django Management
- **Create migrations**: `python manage.py makemigrations`
- **Django shell**: `python manage.py shell`
- **Collect static files**: `python manage.py collectstatic`

## Architecture Overview

### Project Structure
This is a Django REST API boilerplate with JWT authentication using a modular settings approach:

- **core/**: Main Django project with split settings (base.py, development.py, production.py)
- **accounts/**: Custom user model with email-based authentication
- **api/**: Main API endpoints 
- **templates/**: Django templates for web views (includes registration/login)

### Key Technologies
- **Django 5.2+** with Django REST Framework
- **JWT Authentication** via djangorestframework-simplejwt
- **Custom User Model** (email as username field, located in accounts/models.py)
- **uv** for dependency management
- **pytest** with factory-boy for unit testing
- **Playwright** with pytest-playwright for E2E testing
- **drf-spectacular** for API documentation
- **CORS headers** configured for frontend integration

### Settings Configuration
- Uses `python-decouple` for environment variables
- Split settings: `core.settings.development` (default) and `core.settings.production`
- Custom user model: `AUTH_USER_MODEL = "accounts.User"`
- JWT tokens: 60-minute access, 7-day refresh with rotation
- CORS enabled for localhost:3000 (React development)

### Database & Testing
- **Development**: SQLite (db.sqlite3)
- **Testing**: In-memory SQLite via conftest.py
- **Production**: PostgreSQL support configured
- Test factories available in `accounts/tests/factories.py`

### API Structure
- Main API under `/api/v1/`
- Account endpoints under `/accounts/` (both API and web views)
- Auto-generated API docs via drf-spectacular
- JWT authentication required for most endpoints

### URL Configuration
- Root redirects to `/register/`
- Both API endpoints and traditional Django web views supported
- Static/media files configured for development and production

## Development Notes

### Custom User Model
The `User` model extends `AbstractUser` with:
- Email as primary authentication field
- Additional fields: `is_verified`, `created_at`, `updated_at`
- Property: `full_name` combining first and last names

### Testing Approach
- **Unit Tests**: Uses pytest-django with reusable database
- **Factory-boy**: For test data generation in `accounts/tests/factories.py`
- **E2E Tests**: Playwright-based tests in `tests/e2e/` directory
- **Test Structure**: 
  - `accounts/tests/` - Unit and integration tests
  - `tests/e2e/` - End-to-end browser tests
  - `tests/e2e/conftest.py` - E2E test fixtures and setup
- **E2E Test Coverage**: Registration, login, authenticated flows, API integration

### Environment Variables
Key variables (via .env file):
- `SECRET_KEY`: Django secret key
- `DEBUG`: Development mode toggle
- `DATABASE_URL`: Database connection (production)
- `ALLOWED_HOSTS`: Comma-separated hostnames
- `CORS_ALLOWED_ORIGINS`: Frontend URLs for CORS