# End-to-End Tests

This directory contains Playwright-based end-to-end tests for the Django boilerplate application.

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Install Playwright browsers:
   ```bash
   uv run playwright install
   ```

## Running Tests

### All E2E Tests
```bash
uv run pytest -c pytest-e2e.ini tests/e2e/
```

### Specific Test Files
```bash
# Registration tests
pytest tests/e2e/test_registration.py

# Login tests  
pytest tests/e2e/test_login.py

# Authenticated user tests
pytest tests/e2e/test_authenticated_flows.py

# API integration tests
pytest tests/e2e/test_api_integration.py
```

### Browser Options
```bash
# Run in headed mode (visible browser)
pytest tests/e2e/ --headed=true

# Run in headless mode (default)
pytest tests/e2e/ --headed=false

# Run with specific browser
pytest tests/e2e/ --browser chromium
pytest tests/e2e/ --browser firefox
pytest tests/e2e/ --browser webkit
```

## Test Structure

- **test_registration.py**: Tests user registration flow, validation, HTMX interactions
- **test_login.py**: Tests user login/logout, session management, redirects
- **test_authenticated_flows.py**: Tests authenticated user features, navigation, profile access
- **test_api_integration.py**: Tests API endpoints integration with UI, HTMX validation calls

## Configuration

- **pytest-e2e.ini**: Pytest configuration for E2E tests
- **conftest.py**: Test fixtures, Django test server setup, user creation
- **playwright.config.py**: Playwright browser configuration

## Test Features

- **Live Django Server**: Automatically starts Django development server
- **Test User Creation**: Creates test users for authentication tests
- **Database Isolation**: Each test runs with fresh database state
- **Network Monitoring**: Tests can monitor API calls and responses
- **HTMX Testing**: Validates real-time form validation
- **Responsive Testing**: Tests mobile and desktop viewports
- **Accessibility**: Basic accessibility checks (labels, keyboard navigation)

## Environment Variables

- `BASE_URL`: Override default server URL (default: http://localhost:8000)
- `HEADLESS`: Run in headless mode (default: true)
- `SLOW_MO`: Add delay between actions for debugging (default: 0)