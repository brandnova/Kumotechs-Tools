from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from webtester.models import LoadTest, UserJourney, JourneyStep
import json
import random

class Command(BaseCommand):
    help = 'Creates sample public test templates with various configurations'

    def handle(self, *args, **options):
        # Get or create a system user for the templates
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'email': 'admin@example.com'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.username}'))
        
        # Create some user journeys first
        login_journey = self._create_login_journey(admin_user)
        shopping_journey = self._create_shopping_journey(admin_user)
        search_journey = self._create_search_journey(admin_user)
        profile_journey = self._create_profile_journey(admin_user)
        checkout_journey = self._create_checkout_journey(admin_user)
        
        # Simple GET request template
        simple_get, created = LoadTest.objects.get_or_create(
            name="Simple GET Request",
            created_by=admin_user,
            defaults={
                'target_url': 'https://example.com',
                'http_method': 'GET',
                'num_users': 10,
                'spawn_rate': 2,
                'duration': 60,
                'is_public_template': True,
                'template_name': 'Simple GET Request',
                'template_description': "A simple GET request to test basic page loading performance."
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {simple_get.name}'))
        else:
            self.stdout.write(f'Template already exists: {simple_get.name}')
        
        # API POST request template
        api_post, created = LoadTest.objects.get_or_create(
            name="API POST Request",
            created_by=admin_user,
            defaults={
                'target_url': 'https://api.example.com/data',
                'http_method': 'POST',
                'headers': json.dumps({
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }),
                'body': json.dumps({
                    'key': 'value',
                    'example': 'data'
                }),
                'num_users': 5,
                'spawn_rate': 1,
                'duration': 30,
                'is_public_template': True,
                'template_name': 'API POST Request',
                'template_description': "A POST request to test API endpoint performance."
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {api_post.name}'))
        else:
            self.stdout.write(f'Template already exists: {api_post.name}')
        
        # High load test template
        high_load, created = LoadTest.objects.get_or_create(
            name="High Load Test",
            created_by=admin_user,
            defaults={
                'target_url': 'https://example.com',
                'http_method': 'GET',
                'num_users': 100,
                'spawn_rate': 10,
                'duration': 120,
                'is_public_template': True,
                'template_name': 'High Load Test',
                'template_description': "A high load test with many concurrent users."
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {high_load.name}'))
        else:
            self.stdout.write(f'Template already exists: {high_load.name}')
        
        # Single journey test template
        single_journey, created = LoadTest.objects.get_or_create(
            name="Login Journey Test",
            created_by=admin_user,
            defaults={
                'journey': login_journey,
                'num_users': 5,
                'spawn_rate': 1,
                'duration': 60,
                'is_public_template': True,
                'template_name': 'Login Journey Test',
                'template_description': "A user journey that simulates logging in and browsing the site."
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {single_journey.name}'))
        else:
            self.stdout.write(f'Template already exists: {single_journey.name}')
        
        # Multiple journeys test template (for when we implement this feature)
        # For now, we'll create it with a single journey and update it later
        multi_journey, created = LoadTest.objects.get_or_create(
            name="E-commerce Multi-Journey Test",
            created_by=admin_user,
            defaults={
                'journey': shopping_journey,  # Initially set a single journey
                'target_url': 'https://shop.example.com',  # Fallback URL for non-journey users
                'num_users': 20,
                'spawn_rate': 2,
                'duration': 180,
                'is_public_template': True,
                'template_name': 'E-commerce Multi-Journey Test',
                'template_description': "A comprehensive test that simulates various user journeys on an e-commerce site."
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {multi_journey.name}'))
        else:
            self.stdout.write(f'Template already exists: {multi_journey.name}')
        
        # Note: After implementing the many-to-many relationship, we'll update this template
        # to include multiple journeys with code like:
        # multi_journey.journeys.add(shopping_journey, login_journey, search_journey, checkout_journey)
        
        self.stdout.write(self.style.SUCCESS('Sample public templates created successfully!'))
    
    def _create_login_journey(self, user):
        """Create a login journey"""
        journey, created = UserJourney.objects.get_or_create(
            name="Login Journey",
            created_by=user,
            defaults={
                'description': "A journey that simulates a user logging in",
                'base_url': 'https://example.com'
            }
        )
        
        if created:
            # Add steps
            steps = [
                {'step_type': 'navigate', 'url': '/login', 'order': 1, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'input', 'selector': '#username', 'value': 'testuser', 'order': 2, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'input', 'selector': '#password', 'value': 'password123', 'order': 3, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'submit', 'selector': 'form', 'order': 4, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'navigate', 'url': '/dashboard', 'order': 5, 'min_wait': 2.0, 'max_wait': 5.0}
            ]
            
            for step_data in steps:
                JourneyStep.objects.create(journey=journey, **step_data)
            
            self.stdout.write(self.style.SUCCESS(f'Created journey: {journey.name} with {len(steps)} steps'))
        else:
            self.stdout.write(f'Journey already exists: {journey.name}')
        
        return journey
    
    def _create_shopping_journey(self, user):
        """Create a shopping journey"""
        journey, created = UserJourney.objects.get_or_create(
            name="Shopping Journey",
            created_by=user,
            defaults={
                'description': "A journey that simulates browsing and adding products to cart",
                'base_url': 'https://shop.example.com'
            }
        )
        
        if created:
            # Add steps
            steps = [
                {'step_type': 'navigate', 'url': '/products', 'order': 1, 'min_wait': 1.0, 'max_wait': 3.0},
                {'step_type': 'click', 'selector': '.product-item:first-child', 'order': 2, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'click', 'selector': '.add-to-cart', 'order': 3, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'navigate', 'url': '/cart', 'order': 4, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'click', 'selector': '.continue-shopping', 'order': 5, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'navigate', 'url': '/products/category/popular', 'order': 6, 'min_wait': 1.0, 'max_wait': 3.0},
                {'step_type': 'click', 'selector': '.product-item:nth-child(3)', 'order': 7, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'click', 'selector': '.add-to-cart', 'order': 8, 'min_wait': 0.5, 'max_wait': 1.5}
            ]
            
            for step_data in steps:
                JourneyStep.objects.create(journey=journey, **step_data)
            
            self.stdout.write(self.style.SUCCESS(f'Created journey: {journey.name} with {len(steps)} steps'))
        else:
            self.stdout.write(f'Journey already exists: {journey.name}')
        
        return journey
    
    def _create_search_journey(self, user):
        """Create a search journey"""
        journey, created = UserJourney.objects.get_or_create(
            name="Search Journey",
            created_by=user,
            defaults={
                'description': "A journey that simulates searching for products",
                'base_url': 'https://shop.example.com'
            }
        )
        
        if created:
            # Add steps
            steps = [
                {'step_type': 'navigate', 'url': '/', 'order': 1, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'input', 'selector': '#search-input', 'value': 'smartphone', 'order': 2, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'submit', 'selector': '#search-form', 'order': 3, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'click', 'selector': '.filter-price', 'order': 4, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'click', 'selector': '.sort-by-relevance', 'order': 5, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'click', 'selector': '.product-item:first-child', 'order': 6, 'min_wait': 1.0, 'max_wait': 2.0}
            ]
            
            for step_data in steps:
                JourneyStep.objects.create(journey=journey, **step_data)
            
            self.stdout.write(self.style.SUCCESS(f'Created journey: {journey.name} with {len(steps)} steps'))
        else:
            self.stdout.write(f'Journey already exists: {journey.name}')
        
        return journey
    
    def _create_profile_journey(self, user):
        """Create a profile management journey"""
        journey, created = UserJourney.objects.get_or_create(
            name="Profile Management Journey",
            created_by=user,
            defaults={
                'description': "A journey that simulates a user updating their profile",
                'base_url': 'https://example.com'
            }
        )
        
        if created:
            # Add steps
            steps = [
                {'step_type': 'navigate', 'url': '/login', 'order': 1, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'input', 'selector': '#username', 'value': 'testuser', 'order': 2, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'input', 'selector': '#password', 'value': 'password123', 'order': 3, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'submit', 'selector': 'form', 'order': 4, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'navigate', 'url': '/profile', 'order': 5, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'input', 'selector': '#display-name', 'value': 'Test User', 'order': 6, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'input', 'selector': '#bio', 'value': 'This is a test user profile.', 'order': 7, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'submit', 'selector': '#profile-form', 'order': 8, 'min_wait': 1.0, 'max_wait': 2.0}
            ]
            
            for step_data in steps:
                JourneyStep.objects.create(journey=journey, **step_data)
            
            self.stdout.write(self.style.SUCCESS(f'Created journey: {journey.name} with {len(steps)} steps'))
        else:
            self.stdout.write(f'Journey already exists: {journey.name}')
        
        return journey
    
    def _create_checkout_journey(self, user):
        """Create a checkout journey"""
        journey, created = UserJourney.objects.get_or_create(
            name="Checkout Journey",
            created_by=user,
            defaults={
                'description': "A journey that simulates completing a purchase",
                'base_url': 'https://shop.example.com'
            }
        )
        
        if created:
            # Add steps
            steps = [
                {'step_type': 'navigate', 'url': '/cart', 'order': 1, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'click', 'selector': '.checkout-button', 'order': 2, 'min_wait': 1.0, 'max_wait': 2.0},
                {'step_type': 'input', 'selector': '#email', 'value': 'test@example.com', 'order': 3, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'input', 'selector': '#shipping-address', 'value': '123 Test St', 'order': 4, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'input', 'selector': '#city', 'value': 'Test City', 'order': 5, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'input', 'selector': '#zip', 'value': '12345', 'order': 6, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'click', 'selector': '#payment-method-cc', 'order': 7, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'input', 'selector': '#cc-number', 'value': '4111111111111111', 'order': 8, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'input', 'selector': '#cc-exp', 'value': '12/25', 'order': 9, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'input', 'selector': '#cc-cvv', 'value': '123', 'order': 10, 'min_wait': 0.5, 'max_wait': 1.5},
                {'step_type': 'submit', 'selector': '#checkout-form', 'order': 11, 'min_wait': 1.0, 'max_wait': 2.0}
            ]
            
            for step_data in steps:
                JourneyStep.objects.create(journey=journey, **step_data)
            
            self.stdout.write(self.style.SUCCESS(f'Created journey: {journey.name} with {len(steps)} steps'))
        else:
            self.stdout.write(f'Journey already exists: {journey.name}')
        
        return journey