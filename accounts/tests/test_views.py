from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.register_url = reverse('register')
        cls.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'terms': 'on',
        }
        
    def setUp(self):
        self.client = Client()
        # Clear the test database before each test
        User.objects.all().delete()

    def test_register_page_loads(self):
        """Test that the registration page loads successfully"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertContains(response, 'Create your account')

    def test_register_user_success(self):
        """Test successful user registration"""
        # Get initial count
        initial_count = User.objects.count()
        
        response = self.client.post(self.register_url, data=self.valid_data)
        
        # Check if user was created
        self.assertEqual(User.objects.count(), initial_count + 1,
                        f"Expected {initial_count + 1} users, found {User.objects.count()}")
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        
        # Check redirection after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        # Create a user first
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='testpass123'
        )
        
        # Get initial count
        initial_count = User.objects.count()
        
        # Try to create another user with the same username
        response = self.client.post(self.register_url, data=self.valid_data)
        
        # Should not create a new user
        self.assertEqual(User.objects.count(), initial_count, 
                        f"Expected {initial_count} users, found {User.objects.count()}")
        # Should return to the same page with form errors
        self.assertEqual(response.status_code, 200)
        self.assertIn('A user with that username already exists.', response.content.decode())

    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get initial count
        initial_count = User.objects.count()
        
        # Try to create another user with the same email
        response = self.client.post(self.register_url, data=self.valid_data)
        
        # Should not create a new user
        self.assertEqual(User.objects.count(), initial_count,
                        f"Expected {initial_count} users, found {User.objects.count()}")
        # Should return to the same page with form errors
        self.assertEqual(response.status_code, 200)
        self.assertIn('A user with that email already exists.', response.content.decode())

    def test_register_invalid_data(self):
        """Test registration with invalid data"""
        # Get initial count
        initial_count = User.objects.count()
        
        invalid_data = self.valid_data.copy()
        invalid_data['password2'] = 'differentpassword'
        
        response = self.client.post(self.register_url, data=invalid_data, follow=True)
        
        # Should not create a user
        self.assertEqual(User.objects.count(), initial_count,
                        f"Expected {initial_count} users, found {User.objects.count()}")
        
        # Check that the form is invalid and contains the expected error
        form = response.context.get('form')
        self.assertIsNotNone(form, "Form not found in response context")
        self.assertFalse(form.is_valid(), "Form should be invalid with mismatched passwords")
        self.assertIn('password2', form.errors, "Password2 field should have an error")
        # Check for the error message, handling different types of apostrophes
        error_messages = [msg.replace("'", "'").replace('’', "'") for msg in form.errors['password2']]
        expected_message = "The two password fields didn't match.".replace("'", "'")
        self.assertIn(expected_message, error_messages, 
                     f"Expected error message '{expected_message}' not found in form errors: {form.errors}")


class CatchAllUrlTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_catch_all_redirects_to_register(self):
        """Test that non-existent URLs redirect to the registration page"""
        # Test with a non-existent URL
        response = self.client.get('/this-page-does-not-exist/')
        self.assertRedirects(
            response, 
            '/register/', 
            status_code=302, 
            target_status_code=200,
            msg_prefix='Non-existent URL should redirect to register page'
        )
        
        # Test with another non-existent URL with multiple segments
        response = self.client.get('/some/non/existent/path/')
        self.assertRedirects(
            response, 
            '/register/', 
            status_code=302, 
            target_status_code=200,
            msg_prefix='Deep non-existent URL should redirect to register page'
        )

    def test_existing_urls_not_redirected(self):
        """Test that existing URLs are not redirected"""
        # Test with admin URL (should redirect to login, not to register)
        response = self.client.get('/admin/')
        self.assertNotEqual(
            response.url,
            '/register/',
            'Admin URL should not redirect to register page'
        )
        
        # Test with API URL (should return 401 Unauthorized, not redirect to register)
        response = self.client.get('/api/v1/')
        self.assertNotEqual(
            response.status_code,
            302,
            'API URL should not redirect to register page'
        )

    def test_register_page_itself_not_redirected(self):
        """Test that the register page itself is not redirected"""
        response = self.client.get(self.register_url)
        self.assertEqual(
            response.status_code, 
            200, 
            'Register page should load directly without redirection'
        )
        self.assertTemplateUsed(response, 'registration/register.html')


class HTMXValidationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username_validation_url = reverse('validate_username')
        self.password_validation_url = reverse('validate_password')
        
    def test_username_validation_available(self):
        """Test that username validation endpoint works"""
        response = self.client.post(
            self.username_validation_url,
            data={'username': 'newuser'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'is_taken': False,
            'message': ''
        })
    
    def test_username_validation_taken(self):
        """Test that duplicate usernames are detected"""
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='testpass123'
        )
        
        response = self.client.post(
            self.username_validation_url,
            data={'username': 'existinguser'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'is_taken': True,
            'message': 'A user with this username already exists.'
        })
    
    def test_password_validation(self):
        """Test password validation endpoint"""
        # Test weak password
        response = self.client.post(
            self.password_validation_url,
            data={'password1': 'weak', 'password2': 'weak'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['is_valid'])
        self.assertIn('at least 8', data['message'])
        
        # Test matching passwords
        response = self.client.post(
            self.password_validation_url,
            data={'password1': 'StrongPass123!', 'password2': 'StrongPass123!'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_valid'])
        self.assertEqual(data['message'], '')
