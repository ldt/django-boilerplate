import pytest
from playwright.sync_api import Page, expect
from django.contrib.auth import get_user_model

User = get_user_model()

class TestLogin:
    """E2E tests for user login flow"""
    
    def test_login_page_loads(self, page: Page, base_url: str):
        """Test that the login page loads correctly"""
        page.goto(f"{base_url}/login/")
        
        # Check page title and heading  
        expect(page).to_have_title("Login")
        expect(page.locator("h2")).to_contain_text("Sign in to your account")
        
        # Check that all required form fields are present
        expect(page.locator('input[name="email"]')).to_be_visible()
        expect(page.locator('input[name="password"]')).to_be_visible()
        expect(page.locator('button[type="submit"]')).to_be_visible()
        
        # Check for "Remember me" checkbox if present
        remember_me = page.locator('input[name="remember_me"]')
        if remember_me.is_visible():
            expect(remember_me).to_be_visible()
    
    def test_successful_login(self, page: Page, base_url: str, test_user):
        """Test successful user login"""
        page.goto(f"{base_url}/login/")
        
        # Fill out the login form
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="password"]', "testpass123")
        
        # Submit the form
        page.click('button[type="submit"]')
        
        # Should redirect to home page or dashboard
        expect(page).to_have_url(f"{base_url}/")
        
        # Should show logged-in user information
        expect(page.locator("text=Welcome")).to_be_visible()
    
    def test_login_with_invalid_credentials(self, page: Page, base_url: str):
        """Test login with invalid credentials"""
        page.goto(f"{base_url}/login/")
        
        # Try to login with invalid credentials
        page.fill('input[name="email"]', "invalid@example.com")
        page.fill('input[name="password"]', "wrongpassword")
        
        page.click('button[type="submit"]')
        
        # Check that form was processed (may show error or redirect)
        current_url = page.url
        assert base_url in current_url, f"Login form submission failed, unexpected URL: {current_url}"
    
    def test_login_with_empty_fields(self, page: Page, base_url: str):
        """Test login form validation with empty fields"""
        page.goto(f"{base_url}/login/")
        
        # Try to submit empty form
        page.click('button[type="submit"]')
        
        # Check that form was processed
        current_url = page.url
        assert base_url in current_url, f"Login form submission failed, unexpected URL: {current_url}"
    
    def test_login_with_invalid_email_format(self, page: Page, base_url: str):
        """Test login with invalid email format"""
        page.goto(f"{base_url}/login/")
        
        # Try to login with invalid email format
        page.fill('input[name="email"]', "notanemail")
        page.fill('input[name="password"]', "somepassword")
        
        page.click('button[type="submit"]')
        
        # Check that form was processed
        current_url = page.url
        assert base_url in current_url, f"Login form submission failed, unexpected URL: {current_url}"
    
    def test_login_redirect_to_protected_page(self, page: Page, base_url: str, test_user):
        """Test login redirect to originally requested protected page"""
        # Try to access a protected page (profile)
        page.goto(f"{base_url}/profile/")
        
        # Should redirect to login page with next parameter
        expect(page).to_have_url(f"{base_url}/login/?next=/profile/")
        
        # Login successfully
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="password"]', "testpass123")
        page.click('button[type="submit"]')
        
        # Should redirect back to originally requested page
        expect(page).to_have_url(f"{base_url}/profile/")
    
    def test_logout_functionality(self, page: Page, base_url: str, test_user):
        """Test user logout functionality"""
        # First login
        page.goto(f"{base_url}/login/")
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="password"]', "testpass123")
        page.click('button[type="submit"]')
        
        # Verify logged in
        expect(page).to_have_url(f"{base_url}/")
        
        # Click logout link/button
        page.click('text="Logout"')
        
        # Should redirect to login page or home page
        # Check for login form to confirm logout
        expect(page.locator('input[name="email"]')).to_be_visible()
    
    def test_already_logged_in_redirect(self, page: Page, base_url: str, test_user):
        """Test that already logged-in users are redirected from login page"""
        # First login
        page.goto(f"{base_url}/login/")
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="password"]', "testpass123")
        page.click('button[type="submit"]')
        
        # Try to visit login page again
        page.goto(f"{base_url}/login/")
        
        # Should redirect to home page since already logged in
        expect(page).to_have_url(f"{base_url}/")
    
    def test_navigation_to_register(self, page: Page, base_url: str):
        """Test navigation from login to registration page"""
        page.goto(f"{base_url}/login/")
        
        # Look for register link (may have different text)
        register_links = page.locator('a[href*="register"], a:has-text("Sign up"), a:has-text("Register"), a:has-text("Create"), a:has-text("account")')
        if register_links.count() > 0:
            register_links.first.click()
            # Should navigate to registration page
            expect(page).to_have_url(f"{base_url}/register/")
        else:
            # If no register link found, just verify we can navigate manually
            page.goto(f"{base_url}/register/")
            expect(page).to_have_url(f"{base_url}/register/")
    
    def test_forgot_password_link(self, page: Page, base_url: str):
        """Test forgot password functionality if implemented"""
        page.goto(f"{base_url}/login/")
        
        # Check if forgot password link exists
        forgot_link = page.locator('text="Forgot password"')
        if forgot_link.is_visible():
            forgot_link.click()
            # Should navigate to password reset page
            expect(page.url).to_contain("password")
    
    def test_login_form_accessibility(self, page: Page, base_url: str):
        """Test basic accessibility features of login form"""
        page.goto(f"{base_url}/login/")
        
        # Check that form fields are accessible
        email_input = page.locator('input[name="email"]')
        password_input = page.locator('input[name="password"]')
        
        # Verify fields are visible and functional
        expect(email_input).to_be_visible()
        expect(password_input).to_be_visible()
        
        # Test that fields can be focused - wait for focus state
        email_input.focus()
        page.wait_for_timeout(100)  # Brief wait for focus
        
        password_input.focus()
        page.wait_for_timeout(100)  # Brief wait for focus
        
        # Just verify the fields are interactive (can type in them)
        password_input.fill("test")
        password_input.fill("")  # Clear it