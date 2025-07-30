from django.db import models
from django.contrib.auth.models import User
import json
import random
from django.utils import timezone
from django.urls import reverse

class UserJourney(models.Model):
    """Model to define a user journey (sequence of steps)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    base_url = models.URLField(max_length=2000, help_text="Base URL for relative paths in journey steps")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journeys')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Journey'
        verbose_name_plural = 'User Journeys'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('webtester:journey_detail', kwargs={'pk': self.pk})

class JourneyStep(models.Model):
    """Model to define a step in a user journey"""
    STEP_TYPES = [
        ('navigate', 'Navigate to URL'),
        ('click', 'Click Element'),
        ('input', 'Input Text'),
        ('wait', 'Wait'),
        ('submit', 'Submit Form'),
    ]
    
    journey = models.ForeignKey(UserJourney, on_delete=models.CASCADE, related_name='steps')
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    order = models.PositiveIntegerField(help_text="Order of execution within the journey")
    url = models.CharField(max_length=2000, blank=True, null=True, help_text="Path relative to base URL (e.g., /login)")
    selector = models.CharField(max_length=255, blank=True, null=True, help_text="CSS selector for the element (for click, input, submit step types)")
    value = models.TextField(blank=True, null=True, help_text="Value to input (for input step type)")
    min_wait = models.FloatField(default=1.0, help_text="Minimum wait time in seconds before executing this step")
    max_wait = models.FloatField(default=3.0, help_text="Maximum wait time in seconds before executing this step")
    
    class Meta:
        ordering = ['journey', 'order']
        unique_together = ['journey', 'order']
    
    def __str__(self):
        return f"{self.get_step_type_display()} (Step {self.order})"

class LoadTest(models.Model):
    """Model to store load test configurations and results"""
    # Test configuration
    name = models.CharField(max_length=100)
    target_url = models.URLField(max_length=2000, blank=True, null=True, help_text="Target URL for simple tests (not used for journey tests)")
    journey = models.ForeignKey(UserJourney, on_delete=models.SET_NULL, null=True, blank=True, related_name='load_tests', help_text="User journey to execute (overrides target_url)")
    num_users = models.PositiveIntegerField(default=10, help_text="Number of virtual users to simulate")
    spawn_rate = models.PositiveIntegerField(default=1, help_text="Number of users to spawn per second")
    duration = models.PositiveIntegerField(default=60, help_text="Duration of the test in seconds")
    http_method = models.CharField(max_length=10, default='GET', choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
    ], help_text="HTTP method for simple tests (not used for journey tests)")
    headers = models.TextField(blank=True, null=True, help_text="HTTP headers in JSON format")
    body = models.TextField(blank=True, null=True, help_text="Request body for POST/PUT requests (not used for journey tests)")

    # Public template fields
    is_public_template = models.BooleanField(default=False, help_text="Make this test available as a public template for other users")
    template_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name to display in the public template library")
    template_description = models.TextField(blank=True, null=True, help_text="Description of what this template does")

    journeys = models.ManyToManyField(UserJourney, blank=True, related_name='load_tests_multi', help_text="User journeys to execute (overrides target_url)")
    journey_probability = models.FloatField(default=0.7, help_text="Probability (0-1) that a virtual user will use a journey instead of just hitting the target URL")
    
    # Test metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='load_tests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Test status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Test results summary
    total_requests = models.PositiveIntegerField(default=0)
    successful_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)
    avg_response_time = models.FloatField(null=True, blank=True)
    min_response_time = models.FloatField(null=True, blank=True)
    max_response_time = models.FloatField(null=True, blank=True)
    requests_per_second = models.FloatField(null=True, blank=True)
    users_data = models.TextField(blank=True, null=True, help_text="Virtual users data in JSON format")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Load Test'
        verbose_name_plural = 'Load Tests'
    
    def __str__(self):
        if self.journey:
            return f"{self.name} - Journey: {self.journey.name}"
        return f"{self.name} - {self.target_url}"
    
    def is_journey_test(self):
        """Check if this is a journey test"""
        return self.journeys.exists()
    
    def get_random_journey(self):
        """Get a random journey from the assigned journeys"""
        if not self.is_journey_test():
            return None
        
        # Decide whether to use a journey based on probability
        if random.random() > self.journey_probability:
            return None
        
        # Get all journeys
        journeys = list(self.journeys.all())
        if not journeys:
            return None
        
        # Return a random journey
        return random.choice(journeys)
    
    def __str__(self):
        return f"{self.name} - {self.target_url}"
    
    def get_headers_dict(self):
        """Convert headers JSON string to dictionary"""
        if not self.headers:
            return {}
        try:
            return json.loads(self.headers)
        except json.JSONDecodeError:
            return {}
    
    def set_headers_dict(self, headers_dict):
        """Convert headers dictionary to JSON string"""
        self.headers = json.dumps(headers_dict)
    
    def get_users_data_dict(self):
        """Convert users_data JSON string to dictionary"""
        if not self.users_data:
            return {}
        try:
            return json.loads(self.users_data)
        except json.JSONDecodeError:
            return {}
    
    def start_test(self):
        """Mark the test as started"""
        self.status = 'running'
        self.started_at = timezone.now()
        self.save()
    
    def complete_test(self, results):
        """Mark the test as completed and store results"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        
        # Store summary results
        self.total_requests = results.get('total_requests', 0)
        self.successful_requests = results.get('successful_requests', 0)
        self.failed_requests = results.get('failed_requests', 0)
        self.avg_response_time = results.get('avg_response_time')
        self.min_response_time = results.get('min_response_time')
        self.max_response_time = results.get('max_response_time')
        self.requests_per_second = results.get('requests_per_second')
        
        # Store users data
        if 'users_data' in results:
            self.users_data = json.dumps(results['users_data'])
        
        # Store detailed results
        detailed_results = results.get('detailed_results', [])
        if detailed_results:
            for result in detailed_results:
                # Convert cookies dict to JSON string
                cookies_json = None
                if 'cookies' in result and result['cookies']:
                    try:
                        cookies_json = json.dumps(result['cookies'])
                    except:
                        pass
                    
                TestResult.objects.create(
                    test=self,
                    timestamp=result.get('timestamp'),
                    response_time=result.get('response_time'),
                    status_code=result.get('status_code'),
                    success=result.get('success', False),
                    error=result.get('error', ''),
                    user_agent=result.get('user_agent', ''),
                    virtual_user_id=result.get('virtual_user_id'),
                    cookies=cookies_json,
                    content_length=result.get('content_length')
                )
        
        self.save()
    
    def fail_test(self, error):
        """Mark the test as failed"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        # Create a test result with the error
        TestResult.objects.create(
            test=self,
            timestamp=timezone.now(),
            success=False,
            error=str(error)
        )
        self.save()
    
    def get_duration(self):
        """Get the actual duration of the test in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def get_success_rate(self):
        """Get the success rate as a percentage"""
        if self.total_requests > 0:
            return (self.successful_requests / self.total_requests) * 100
        return 0

class TestResult(models.Model):
    """Model to store individual test results"""
    test = models.ForeignKey(LoadTest, on_delete=models.CASCADE, related_name='results')
    timestamp = models.DateTimeField(default=timezone.now)
    response_time = models.FloatField(null=True, blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error = models.TextField(blank=True)
    user_agent = models.TextField(blank=True, null=True, help_text="User agent used for this request")
    virtual_user_id = models.IntegerField(null=True, blank=True, help_text="ID of the virtual user that made this request")
    cookies = models.TextField(blank=True, null=True, help_text="Cookies for this request in JSON format")
    content_length = models.PositiveIntegerField(null=True, blank=True, help_text="Length of the response content in bytes")
    journey_step = models.ForeignKey(JourneyStep, on_delete=models.SET_NULL, null=True, blank=True, related_name='results', help_text="Journey step that generated this result")
    url = models.URLField(max_length=2000, blank=True, null=True, help_text="URL that was accessed")
    step_type = models.CharField(max_length=20, blank=True, null=True, help_text="Type of step that was executed")
    wait_time = models.FloatField(null=True, blank=True, help_text="Time waited before executing this step")
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Result for {self.test.name} at {self.timestamp}"
    
    def get_cookies_dict(self):
        """Convert cookies JSON string to dictionary"""
        if not self.cookies:
            return {}
        try:
            return json.loads(self.cookies)
        except json.JSONDecodeError:
            return {}
        

class TestTemplate(models.Model):
    """Model to store test templates that can be cloned by users"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_journey = models.BooleanField(default=False, help_text="Whether this template is for a journey test")
    
    # Configuration for simple tests
    http_method = models.CharField(max_length=10, default='GET', choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
    ])
    headers = models.TextField(blank=True, null=True, help_text="HTTP headers in JSON format")
    body = models.TextField(blank=True, null=True, help_text="Request body for POST/PUT requests")
    
    # Default test parameters
    num_users = models.PositiveIntegerField(default=10, help_text="Default number of virtual users to simulate")
    spawn_rate = models.PositiveIntegerField(default=1, help_text="Default number of users to spawn per second")
    duration = models.PositiveIntegerField(default=60, help_text="Default duration of the test in seconds")
    
    # For journey templates
    journey_steps = models.TextField(blank=True, null=True, help_text="Journey steps in JSON format")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Test Template'
        verbose_name_plural = 'Test Templates'
    
    def __str__(self):
        return self.name
    
    def clone_for_user(self, user):
        """Clone this template to create a new test for a user"""
        if self.is_journey:
            # Create a journey first
            journey = None
            if self.journey_steps:
                try:
                    steps_data = json.loads(self.journey_steps)
                    journey = UserJourney.objects.create(
                        name=f"{self.name} Journey",
                        description=f"Journey created from template: {self.name}",
                        base_url="https://example.com",  # User will need to update this
                        created_by=user
                    )
                    
                    # Create steps for the journey
                    for i, step_data in enumerate(steps_data):
                        JourneyStep.objects.create(
                            journey=journey,
                            step_type=step_data.get('step_type', 'navigate'),
                            order=i + 1,
                            url=step_data.get('url', ''),
                            selector=step_data.get('selector', ''),
                            value=step_data.get('value', ''),
                            min_wait=step_data.get('min_wait', 1.0),
                            max_wait=step_data.get('max_wait', 3.0)
                        )
                except json.JSONDecodeError:
                    pass
            
            # Create the test with the journey
            test = LoadTest.objects.create(
                name=f"{self.name} (from template)",
                journey=journey,
                num_users=self.num_users,
                spawn_rate=self.spawn_rate,
                duration=self.duration,
                created_by=user
            )
        else:
            # Create a simple test
            test = LoadTest.objects.create(
                name=f"{self.name} (from template)",
                target_url="https://example.com",  # User will need to update this
                num_users=self.num_users,
                spawn_rate=self.spawn_rate,
                duration=self.duration,
                http_method=self.http_method,
                headers=self.headers,
                body=self.body,
                created_by=user
            )
        
        return test

class TestAssignment(models.Model):
    """Model to assign tests to specific users"""
    test = models.ForeignKey(LoadTest, on_delete=models.CASCADE, related_name='assignments')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tests')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="Notes for the assigned user")
    
    class Meta:
        unique_together = ['test', 'assigned_to']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.test.name} assigned to {self.assigned_to.username}"