from django.db import models
from django.contrib.auth.models import User
import json
from django.utils import timezone

class LoadTest(models.Model):
    """Model to store load test configurations and results"""
    # Test configuration
    name = models.CharField(max_length=100)
    target_url = models.URLField(max_length=2000)
    num_users = models.PositiveIntegerField(default=10, help_text="Number of virtual users to simulate")
    spawn_rate = models.PositiveIntegerField(default=1, help_text="Number of users to spawn per second")
    duration = models.PositiveIntegerField(default=60, help_text="Duration of the test in seconds")
    http_method = models.CharField(max_length=10, default='GET', choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
    ])
    headers = models.TextField(blank=True, null=True, help_text="HTTP headers in JSON format")
    body = models.TextField(blank=True, null=True, help_text="Request body for POST/PUT requests")
    
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
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Load Test'
        verbose_name_plural = 'Load Tests'
    
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
        
        # Store detailed results
        detailed_results = results.get('detailed_results', [])
        if detailed_results:
            for result in detailed_results:
                TestResult.objects.create(
                    test=self,
                    timestamp=result.get('timestamp'),
                    response_time=result.get('response_time'),
                    status_code=result.get('status_code'),
                    success=result.get('success', False),
                    error=result.get('error', '')
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
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Result for {self.test.name} at {self.timestamp}"

