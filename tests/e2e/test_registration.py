import pytest
from playwright.sync_api import Page, expect
from django.contrib.auth import get_user_model

User = get_user_model()

class TestRegistration:
    """E2E tests for user registration flow"""
    
    BASE_URL = "http://localhost:8001"
    
    def test_registration_page_loads(self, page: Page):
        """Test that the registration page loads correctly"""
        page.goto(f"{self.BASE_URL}/register/")
        
        # Check page title and heading
        expect(page).to_have_title("Register - Django Boilerplate")
        expect(page.locator("h1, h2")).to_contain_text("Create your account")
        
        # Check that all required form fields are present
        expect(page.locator('input[name="email"]')).to_be_visible()
        expect(page.locator('input[name="username"]')).to_be_visible()
        expect(page.locator('input[name="password1"]')).to_be_visible()
        expect(page.locator('input[name="password2"]')).to_be_visible()
        expect(page.locator('button[type="submit"]')).to_be_visible()
    
    def test_successful_registration(self, page: Page):
        """Test successful user registration"""
        page.goto(f"{self.BASE_URL}/register/")
        
        # Fill out the registration form
        page.fill('input[name="email"]', "newuser@example.com")
        page.fill('input[name="username"]', "newuser")
        page.fill('input[name="first_name"]', "New")
        page.fill('input[name="last_name"]', "User")
        page.fill('input[name="password1"]', "StrongPass123!")
        page.fill('input[name="password2"]', "StrongPass123!")
        
        # Submit the form
        page.click('button[type="submit"]')
        
        # Should redirect to home page or success page
        expect(page).to_have_url(f"{base_url}/")
        
        # Verify user was created in database
        user = User.objects.get(email="newuser@example.com")
        assert user.username == "newuser"
        assert user.first_name == "New"
        assert user.last_name == "User"
    
    def test_registration_validation_errors(self, page: Page):
        """Test form validation errors"""
        page.goto(f"{self.BASE_URL}/register/")
        
        # Try to submit empty form
        page.click('button[type="submit"]')
        
        # Should stay on registration page and show validation errors
        expect(page).to_have_url(f"{self.BASE_URL}/register/")
        expect(page.locator(".error, .alert-danger, .text-red-600")).to_be_visible()
    
    def test_password_mismatch_validation(self, page: Page, base_url: str):
        """Test password confirmation validation"""
        page.goto(f"{base_url}/register/")
        
        # Fill form with mismatched passwords
        page.fill('input[name="email"]', "test@example.com")
        page.fill('input[name="username"]', "testuser")
        page.fill('input[name="first_name"]', "Test")
        page.fill('input[name="last_name"]', "User")
        page.fill('input[name="password1"]', "StrongPass123!")
        page.fill('input[name="password2"]', "DifferentPass123!")
        
        page.click('button[type="submit"]')
        
        # Should show password mismatch error
        expect(page.locator(".error")).to_contain_text("password")
    
    def test_duplicate_email_validation(self, page: Page, base_url: str, test_user):
        """Test that duplicate email addresses are rejected"""
        page.goto(f"{base_url}/register/")
        
        # Try to register with existing user's email
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="username"]', "differentuser")
        page.fill('input[name="first_name"]', "Different")
        page.fill('input[name="last_name"]', "User")
        page.fill('input[name="password1"]', "StrongPass123!")
        page.fill('input[name="password2"]', "StrongPass123!")
        
        page.click('button[type="submit"]')
        
        # Should show email already exists error
        expect(page.locator(".error")).to_contain_text("email")
    
    def test_duplicate_username_validation(self, page: Page, base_url: str, test_user):
        """Test that duplicate usernames are rejected"""
        page.goto(f"{base_url}/register/")
        
        # Try to register with existing user's username
        page.fill('input[name="email"]', "different@example.com")
        page.fill('input[name="username"]', test_user.username)
        page.fill('input[name="first_name"]', "Different")
        page.fill('input[name="last_name"]', "User")
        page.fill('input[name="password1"]', "StrongPass123!")
        page.fill('input[name="password2"]', "StrongPass123!")
        
        page.click('button[type="submit"]')
        
        # Should show username already exists error
        expect(page.locator(".error")).to_contain_text("username")
    
    def test_htmx_username_validation(self, page: Page, base_url: str, test_user):
        """Test real-time username validation via HTMX"""
        page.goto(f"{base_url}/register/")
        
        # Fill in an existing username
        page.fill('input[name="username"]', test_user.username)
        page.blur('input[name="username"]')  # Trigger HTMX validation
        
        # Wait for HTMX response and check for validation message
        page.wait_for_timeout(500)  # Give HTMX time to respond
        expect(page.locator('[data-username-validation]')).to_contain_text("already exists")
    
    def test_htmx_password_validation(self, page: Page, base_url: str):
        """Test real-time password validation via HTMX"""
        page.goto(f"{base_url}/register/")
        
        # Test weak password
        page.fill('input[name="password1"]', "weak")
        page.fill('input[name="password2"]', "weak")
        page.blur('input[name="password2"]')  # Trigger HTMX validation
        
        # Wait for HTMX response and check for validation message
        page.wait_for_timeout(500)
        expect(page.locator('[data-password-validation]')).to_contain_text("at least 8")
    
    def test_navigation_to_login(self, page: Page, base_url: str):
        """Test navigation from registration to login page"""
        page.goto(f"{base_url}/register/")
        
        # Click on login link
        page.click('text="Already have an account?"')
        
        # Should navigate to login page
        expect(page).to_have_url(f"{base_url}/login/")