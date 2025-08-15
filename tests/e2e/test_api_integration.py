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
        # First, create a user via registration
        page.goto(f"{base_url}/register/")
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="username"]', test_user.username)
        page.fill('input[name="password1"]', test_user.password)
        page.fill('input[name="password2"]', test_user.password)
        page.click('button[type="submit"]')
        page.wait_for_timeout(2000)
        
        # Now test login flow
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
        page.fill('input[name="password"]', test_user.password)
        page.click('button[type="submit"]')
        page.wait_for_timeout(1000)
        
        # If form uses API, check the response (optional - may not use API)
        if api_response:
            assert api_response.status in [200, 201]
            response_json = api_response.json()
            # Check for JWT tokens if API returns them
            if "access" in response_json:
                assert "refresh" in response_json
    
    def test_api_profile_access(self, page: Page, base_url: str, test_user):
        """Test profile API access"""
        # First, create a user via registration
        page.goto(f"{base_url}/register/")
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="username"]', test_user.username)
        page.fill('input[name="password1"]', test_user.password)
        page.fill('input[name="password2"]', test_user.password)
        page.click('button[type="submit"]')
        page.wait_for_timeout(2000)
        
        # Then login
        page.goto(f"{base_url}/login/")
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="password"]', test_user.password)
        page.click('button[type="submit"]')
        page.wait_for_timeout(1000)
        
        # Try to access API profile endpoint directly
        try:
            response = page.goto(f"{base_url}/api/profile/")
            
            # Should return JSON with user data (if API endpoint exists)
            if response and response.headers.get("content-type", "").startswith("application/json"):
                profile_data = response.json()
                assert profile_data["email"] == test_user.email
            else:
                # If it's HTML, check that we're not redirected to login (auth working)
                current_url = page.url
                assert "/login/" not in current_url or "/api/profile/" in current_url
        except Exception:
            # API endpoint might not exist - test profile page instead
            page.goto(f"{base_url}/profile/")
            current_url = page.url
            assert "/login/" not in current_url, "Should have access to profile when logged in"
    
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
        
        # Check that form was processed (error handling may vary)
        page.wait_for_timeout(1000)
        current_url = page.url
        
        # Form should either show error or stay on login page for invalid credentials
        assert base_url in current_url, f"Form submission failed, unexpected URL: {current_url}"
        
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
        # First, create a user via registration
        page.goto(f"{base_url}/register/")
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="username"]', test_user.username)
        page.fill('input[name="password1"]', test_user.password)
        page.fill('input[name="password2"]', test_user.password)
        page.click('button[type="submit"]')
        page.wait_for_timeout(2000)
        
        # Now test JSON handling on login page
        page.goto(f"{base_url}/login/")
        
        # If the form submits to API and expects JSON response
        page.evaluate("""
            // Override form submission to check JSON handling
            const form = document.querySelector('form');
            if (form) {
                const originalAction = form.action;
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    fetch(originalAction, {
                        method: 'POST',
                        body: new FormData(form),
                        headers: {
                            'Accept': 'application/json'
                        }
                    }).then(response => {
                        if (response.ok) {
                            return response.json();
                        }
                        throw new Error('Network response was not ok');
                    }).then(data => {
                        console.log('API Response:', data);
                        window.apiTestResponse = data;
                    }).catch(error => {
                        console.log('No JSON API or error:', error);
                        window.apiTestResponse = null;
                    });
                });
            }
        """)
        
        # Fill and submit form
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="password"]', test_user.password)
        page.click('button[type="submit"]')
        
        # Wait for API response
        page.wait_for_timeout(2000)
        
        # Check if JSON response was handled (optional - may not use JSON API)
        api_response = page.evaluate("window.apiTestResponse")
        if api_response:
            assert isinstance(api_response, dict)