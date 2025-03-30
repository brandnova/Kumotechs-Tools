from django.core.management.base import BaseCommand
from webtester.models import TestTemplate
import json

class Command(BaseCommand):
    help = 'Creates sample test templates'

    def handle(self, *args, **options):
        # Simple GET request template
        simple_get, created = TestTemplate.objects.get_or_create(
            name="Simple GET Request",
            defaults={
                'description': "A simple GET request to test basic page loading performance.",
                'is_journey': False,
                'http_method': 'GET',
                'num_users': 10,
                'spawn_rate': 2,
                'duration': 60
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {simple_get.name}'))
        else:
            self.stdout.write(f'Template already exists: {simple_get.name}')
        
        # API POST request template
        api_post, created = TestTemplate.objects.get_or_create(
            name="API POST Request",
            defaults={
                'description': "A POST request to test API endpoint performance.",
                'is_journey': False,
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
                'duration': 30
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {api_post.name}'))
        else:
            self.stdout.write(f'Template already exists: {api_post.name}')
        
        # High load test template
        high_load, created = TestTemplate.objects.get_or_create(
            name="High Load Test",
            defaults={
                'description': "A high load test with many concurrent users.",
                'is_journey': False,
                'http_method': 'GET',
                'num_users': 100,
                'spawn_rate': 10,
                'duration': 120
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {high_load.name}'))
        else:
            self.stdout.write(f'Template already exists: {high_load.name}')
        
        # Login and browse journey template
        login_journey_steps = [
            {
                'step_type': 'navigate',
                'url': '/login',
                'min_wait': 1.0,
                'max_wait': 2.0
            },
            {
                'step_type': 'input',
                'selector': '#username',
                'value': 'testuser',
                'min_wait': 0.5,
                'max_wait': 1.5
            },
            {
                'step_type': 'input',
                'selector': '#password',
                'value': 'password123',
                'min_wait': 0.5,
                'max_wait': 1.5
            },
            {
                'step_type': 'submit',
                'selector': 'form',
                'min_wait': 1.0,
                'max_wait': 2.0
            },
            {
                'step_type': 'navigate',
                'url': '/dashboard',
                'min_wait': 2.0,
                'max_wait': 5.0
            },
            {
                'step_type': 'click',
                'selector': '.profile-link',
                'min_wait': 1.0,
                'max_wait': 3.0
            }
        ]
        
        login_journey, created = TestTemplate.objects.get_or_create(
            name="Login and Browse Journey",
            defaults={
                'description': "A user journey that simulates logging in and browsing the site.",
                'is_journey': True,
                'num_users': 5,
                'spawn_rate': 1,
                'duration': 60,
                'journey_steps': json.dumps(login_journey_steps)
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {login_journey.name}'))
        else:
            self.stdout.write(f'Template already exists: {login_journey.name}')
        
        # E-commerce shopping journey template
        shopping_journey_steps = [
            {
                'step_type': 'navigate',
                'url': '/products',
                'min_wait': 1.0,
                'max_wait': 3.0
            },
            {
                'step_type': 'click',
                'selector': '.product-item:first-child',
                'min_wait': 1.0,
                'max_wait': 2.0
            },
            {
                'step_type': 'click',
                'selector': '.add-to-cart',
                'min_wait': 0.5,
                'max_wait': 1.5
            },
            {
                'step_type': 'navigate',
                'url': '/cart',
                'min_wait': 1.0,
                'max_wait': 2.0
            },
            {
                'step_type': 'click',
                'selector': '.checkout-button',
                'min_wait': 1.0,
                'max_wait': 2.0
            },
            {
                'step_type': 'input',
                'selector': '#email',
                'value': 'test@example.com',
                'min_wait': 0.5,
                'max_wait': 1.5
            },
            {
                'step_type': 'input',
                'selector': '#shipping-address',
                'value': '123 Test St',
                'min_wait': 0.5,
                'max_wait': 1.5
            },
            {
                'step_type': 'submit',
                'selector': 'form',
                'min_wait': 1.0,
                'max_wait': 2.0
            }
        ]
        
        shopping_journey, created = TestTemplate.objects.get_or_create(
            name="E-commerce Shopping Journey",
            defaults={
                'description': "A user journey that simulates browsing products, adding to cart, and checking out.",
                'is_journey': True,
                'num_users': 3,
                'spawn_rate': 1,
                'duration': 90,
                'journey_steps': json.dumps(shopping_journey_steps)
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {shopping_journey.name}'))
        else:
            self.stdout.write(f'Template already exists: {shopping_journey.name}')
        
        self.stdout.write(self.style.SUCCESS('Sample templates created successfully!'))