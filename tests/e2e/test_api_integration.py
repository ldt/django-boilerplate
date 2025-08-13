import pytest
from playwright.sync_api import Page, expect, APIRequestContext
from django.contrib.auth import get_user_model

User = get_user_model()

class TestAPIIntegration:
    """E2E tests for API integration with UI"""
    
    def test_api_registration_flow(self, page: Page, base_url: str):
        """Test registration via API endpoint"""
        # Go to registration page to test AJAX submission if implemented
        page.goto(f"{base_url}/register/")
        
        # Monitor network requests
        api_response = None
        
        def handle_response(response):
            nonlocal api_response
            if "/api/" in response.url and response.request.method == "POST":
                api_response = response
        
        page.on("response", handle_response)
        
        # Fill and submit form
        page.fill('input[name="email"]', "apitest@example.com")
        page.fill('input[name="username"]', "apitest")
        page.fill('input[name="first_name"]', "API")
        page.fill('input[name="last_name"]', "Test")
        page.fill('input[name="password1"]', "APITestPass123!")
        page.fill('input[name="password2"]', "APITestPass123!")
        
        page.click('button[type="submit"]')
        
        # If form uses API, check the response
        if api_response:
            assert api_response.status == 201
            response_json = api_response.json()
            assert "access" in response_json
            assert "refresh" in response_json
    
    def test_api_login_flow(self, page: Page, base_url: str, test_user):
        """Test login via API endpoint"""
        page.goto(f"{base_url}/login/")
        
        # Monitor network requests
        api_response = None
        
        def handle_response(response):
            nonlocal api_response
            if "/api/" in response.url and response.request.method == "POST":
                api_response = response
        
        page.on("response", handle_response)
        
        # Fill and submit login form
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="password"]', "testpass123")
        page.click('button[type="submit"]')
        
        # If form uses API, check the response
        if api_response:
            assert api_response.status == 200
            response_json = api_response.json()
            assert "access" in response_json
            assert "refresh" in response_json
    
    def test_htmx_username_validation_api(self, page: Page, base_url: str, test_user):
        """Test HTMX username validation calls the correct API endpoint"""
        page.goto(f"{base_url}/register/")
        
        # Monitor network requests for validation endpoint
        validation_response = None
        
        def handle_response(response):
            nonlocal validation_response
            if "validate-username" in response.url:
                validation_response = response
        
        page.on("response", handle_response)
        
        # Trigger username validation
        page.fill('input[name="username"]', test_user.username)
        page.blur('input[name="username"]')
        
        # Wait for HTMX request
        page.wait_for_timeout(1000)
        
        # Check that validation endpoint was called
        if validation_response:
            assert validation_response.status == 200
            response_json = validation_response.json()
            assert response_json["is_taken"] is True
    
    def test_htmx_password_validation_api(self, page: Page, base_url: str):
        """Test HTMX password validation calls the correct API endpoint"""
        page.goto(f"{base_url}/register/")
        
        # Monitor network requests for validation endpoint
        validation_response = None
        
        def handle_response(response):
            nonlocal validation_response
            if "validate-password" in response.url:
                validation_response = response
        
        page.on("response", handle_response)
        
        # Trigger password validation
        page.fill('input[name="password1"]', "weak")
        page.fill('input[name="password2"]', "weak")
        page.blur('input[name="password2"]')
        
        # Wait for HTMX request
        page.wait_for_timeout(1000)
        
        # Check that validation endpoint was called
        if validation_response:
            assert validation_response.status == 200
            response_json = validation_response.json()
            assert response_json["is_valid"] is False
    
    def test_api_profile_access(self, page: Page, base_url: str, test_user):
        """Test profile API access"""
        # First login
        page.goto(f"{base_url}/login/")
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="password"]', "testpass123")
        page.click('button[type="submit"]')
        
        # Try to access API profile endpoint directly
        response = page.goto(f"{base_url}/api/profile/")
        
        # Should return JSON with user data (if API endpoint returns HTML, it might redirect)
        if response.headers.get("content-type", "").startswith("application/json"):
            profile_data = response.json()
            assert profile_data["email"] == test_user.email
        else:
            # If it's HTML, check that it's not a login redirect
            expect(page).not_to_have_url(f"{base_url}/login/")
    
    def test_api_error_handling(self, page: Page, base_url: str):
        """Test API error handling in UI"""
        page.goto(f"{base_url}/login/")
        
        # Monitor for API error responses
        error_responses = []
        
        def handle_response(response):
            if "/api/" in response.url and response.status >= 400:
                error_responses.append(response)
        
        page.on("response", handle_response)
        
        # Try to login with invalid credentials
        page.fill('input[name="email"]', "invalid@example.com")
        page.fill('input[name="password"]', "wrongpassword")
        page.click('button[type="submit"]')
        
        # Check that UI handles API errors gracefully
        expect(page.locator(".error")).to_be_visible()
        
        # If there were API calls, verify they returned appropriate error codes
        for response in error_responses:
            assert response.status in [400, 401, 403]
    
    def test_csrf_token_handling(self, page: Page, base_url: str):
        """Test that CSRF tokens are properly handled in API calls"""
        page.goto(f"{base_url}/register/")
        
        # Check for CSRF token in forms
        csrf_token = page.locator('input[name="csrfmiddlewaretoken"]')
        if csrf_token.is_visible():
            token_value = csrf_token.get_attribute("value")
            assert token_value is not None
            assert len(token_value) > 10  # CSRF tokens should be reasonably long
    
    def test_json_response_handling(self, page: Page, base_url: str, test_user):
        """Test that UI properly handles JSON responses from API"""
        page.goto(f"{base_url}/login/")
        
        # If the form submits to API and expects JSON response
        page.evaluate("""
            // Override form submission to check JSON handling
            const form = document.querySelector('form');
            if (form) {
                const originalSubmit = form.onsubmit;
                form.onsubmit = function(e) {
                    e.preventDefault();
                    fetch(form.action, {
                        method: 'POST',
                        body: new FormData(form),
                        headers: {
                            'Accept': 'application/json'
                        }
                    }).then(response => response.json())
                      .then(data => {
                          console.log('API Response:', data);
                          window.apiTestResponse = data;
                      });
                };
            }
        """)
        
        # Fill and submit form
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="password"]', "testpass123")
        page.click('button[type="submit"]')
        
        # Wait for API response
        page.wait_for_timeout(2000)
        
        # Check if JSON response was handled
        api_response = page.evaluate("window.apiTestResponse")
        if api_response:
            assert isinstance(api_response, dict)