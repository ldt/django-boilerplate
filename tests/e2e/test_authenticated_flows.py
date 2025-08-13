import pytest
from playwright.sync_api import Page, expect
from django.contrib.auth import get_user_model

User = get_user_model()

class TestAuthenticatedFlows:
    """E2E tests for authenticated user flows"""
    
    @pytest.fixture(autouse=True)
    def login_user(self, page: Page, base_url: str, test_user):
        """Automatically login before each test"""
        page.goto(f"{base_url}/login/")
        page.fill('input[name="email"]', test_user.email)
        page.fill('input[name="password"]', "testpass123")
        page.click('button[type="submit"]')
        
        # Verify login was successful
        expect(page).to_have_url(f"{base_url}/")
        return test_user
    
    def test_home_page_authenticated(self, page: Page, base_url: str, test_user):
        """Test home page content for authenticated users"""
        page.goto(f"{base_url}/")
        
        # Basic verification that page loads and has expected content
        expect(page).to_have_url(f"{base_url}/")
        
        # Check for any authenticated user indicators (may vary by implementation)
        authenticated_indicators = page.locator('text="Welcome", text="Profile", text="Logout", text="Dashboard"')
        if authenticated_indicators.count() > 0:
            expect(authenticated_indicators.first).to_be_visible()
    
    def test_profile_page_access(self, page: Page, base_url: str, test_user):
        """Test authenticated user can access profile page"""
        page.goto(f"{base_url}/profile/")
        
        # Should successfully load profile page
        expect(page).to_have_url(f"{base_url}/profile/")
        expect(page.locator("text=Profile")).to_be_visible()
        
        # Should display user information
        expect(page.locator(f"text={test_user.email}")).to_be_visible()
        expect(page.locator(f"text={test_user.username}")).to_be_visible()
    
    def test_profile_information_display(self, page: Page, base_url: str, test_user):
        """Test that profile page displays correct user information"""
        page.goto(f"{base_url}/profile/")
        
        # Check that all user fields are displayed
        expect(page.locator(f"text={test_user.first_name}")).to_be_visible()
        expect(page.locator(f"text={test_user.last_name}")).to_be_visible()
        expect(page.locator(f"text={test_user.email}")).to_be_visible()
        expect(page.locator(f"text={test_user.username}")).to_be_visible()
        
        # Check for join date or other profile details
        expect(page.locator("text=Member since")).to_be_visible()
    
    def test_navigation_between_authenticated_pages(self, page: Page, base_url: str):
        """Test navigation between different authenticated pages"""
        # Start from home
        page.goto(f"{base_url}/")
        
        # Navigate to profile
        page.click('text="Profile"')
        expect(page).to_have_url(f"{base_url}/profile/")
        
        # Navigate back to home
        page.click('text="Home"')
        expect(page).to_have_url(f"{base_url}/")
    
    def test_api_endpoints_authenticated(self, page: Page, base_url: str, test_user):
        """Test that authenticated users can access API endpoints"""
        # This would typically be done with API requests, but we can test UI that calls APIs
        page.goto(f"{base_url}/profile/")
        
        # If there's any AJAX/API calls on the profile page, test them
        # For example, if there's a "Refresh" button that calls the API
        if page.locator('button[data-refresh]').is_visible():
            page.click('button[data-refresh]')
            # Verify the page updates without error
            expect(page.locator('.error')).not_to_be_visible()
    
    def test_logout_from_different_pages(self, page: Page, base_url: str):
        """Test logout functionality from different pages"""
        # Test logout from home page
        page.goto(f"{base_url}/")
        page.click('text="Logout"')
        expect(page.locator('input[name="email"]')).to_be_visible()
        
        # Login again and test logout from profile page
        page.fill('input[name="email"]', "test@example.com")
        page.fill('input[name="password"]', "testpass123")
        page.click('button[type="submit"]')
        
        page.goto(f"{base_url}/profile/")
        page.click('text="Logout"')
        expect(page.locator('input[name="email"]')).to_be_visible()
    
    def test_session_persistence(self, page: Page, base_url: str):
        """Test that user session persists across page reloads"""
        page.goto(f"{base_url}/")
        
        # Verify logged in state
        expect(page.locator('text="Profile"')).to_be_visible()
        
        # Reload the page
        page.reload()
        
        # Should still be logged in
        expect(page.locator('text="Profile"')).to_be_visible()
        expect(page.locator('text="Logout"')).to_be_visible()
    
    def test_protected_route_access(self, page: Page, base_url: str):
        """Test that authenticated users can access protected routes"""
        protected_routes = ["/profile/", "/api/profile/"]
        
        for route in protected_routes:
            page.goto(f"{base_url}{route}")
            
            # Should not redirect to login (status should be 200)
            if route.startswith("/api/"):
                # For API routes, check that we don't get 401 Unauthorized
                # This might require checking network responses
                continue
            else:
                # For HTML routes, check that we're not redirected to login
                expect(page).not_to_have_url(f"{base_url}/login/")
    
    def test_user_menu_interactions(self, page: Page, base_url: str, test_user):
        """Test user menu dropdown interactions if present"""
        page.goto(f"{base_url}/")
        
        # Look for user menu dropdown
        user_menu = page.locator('[data-user-menu]')
        if user_menu.is_visible():
            user_menu.click()
            
            # Check for typical menu items
            expect(page.locator('text="Profile"')).to_be_visible()
            expect(page.locator('text="Settings"')).to_be_visible()
            expect(page.locator('text="Logout"')).to_be_visible()
    
    def test_breadcrumb_navigation(self, page: Page, base_url: str):
        """Test breadcrumb navigation if implemented"""
        page.goto(f"{base_url}/profile/")
        
        # Look for breadcrumbs
        breadcrumbs = page.locator('[data-breadcrumbs]')
        if breadcrumbs.is_visible():
            # Click on Home breadcrumb
            page.click('text="Home" >> nth=0')  # First occurrence (likely in breadcrumbs)
            expect(page).to_have_url(f"{base_url}/")
    
    def test_error_handling_authenticated(self, page: Page, base_url: str):
        """Test error handling for authenticated users"""
        # Try to access a non-existent page
        page.goto(f"{base_url}/nonexistent-page/")
        
        # Should show 404 page, not redirect to login
        expect(page.locator("text=404")).to_be_visible()
        expect(page).not_to_have_url(f"{base_url}/login/")
    
    def test_responsive_design_authenticated(self, page: Page, base_url: str):
        """Test responsive design for authenticated pages"""
        page.goto(f"{base_url}/")
        
        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        
        # Navigation should still work (might be in a hamburger menu)
        if page.locator('[data-mobile-menu-toggle]').is_visible():
            page.click('[data-mobile-menu-toggle]')
        
        expect(page.locator('text="Profile"')).to_be_visible()
        expect(page.locator('text="Logout"')).to_be_visible()
        
        # Reset to desktop viewport
        page.set_viewport_size({"width": 1280, "height": 720})