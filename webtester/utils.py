import time
import requests
import concurrent.futures
import threading
import json
import statistics
from datetime import datetime
import logging
from django.utils import timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadTester:
    """Utility class for running load tests"""
    
    def __init__(self, test_instance):
        """Initialize with a LoadTest instance"""
        self.test = test_instance
        self.results = []
        self.stop_event = threading.Event()
        self.active_users = 0
        self.user_counter = 0
    
    def make_request(self):
        """Make a single request to the target URL"""
        headers = {}
        if self.test.headers:
            try:
                headers = json.loads(self.test.headers)
            except json.JSONDecodeError:
                pass
        
        body = None
        if self.test.body and self.test.http_method in ['POST', 'PUT']:
            try:
                body = json.loads(self.test.body)
            except json.JSONDecodeError:
                body = self.test.body
        
        result = {
            'timestamp': timezone.now(),
            'success': False,
            'error': '',
            'status_code': None,
            'response_time': None
        }
        
        try:
            start_time = time.time()
            
            response = requests.request(
                method=self.test.http_method,
                url=self.test.target_url,
                headers=headers,
                json=body if self.test.http_method in ['POST', 'PUT'] else None,
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result.update({
                'success': 200 <= response.status_code < 400,
                'status_code': response.status_code,
                'response_time': response_time
            })
            
        except requests.RequestException as e:
            result.update({
                'success': False,
                'error': str(e)
            })
        
        return result
    
    def user_task(self, user_id):
        """Simulate a user making requests"""
        self.active_users += 1
        self.user_counter += 1
        
        try:
            # Make requests until the test duration is reached
            while not self.stop_event.is_set():
                result = self.make_request()
                self.results.append(result)
                
                # Small delay to prevent overwhelming the target
                time.sleep(0.1)
        
        finally:
            self.active_users -= 1
    
    def run_test(self):
        """Run the load test with the configured parameters"""
        try:
            # Mark test as started
            self.test.start_test()
            
            # Calculate end time
            end_time = time.time() + self.test.duration
            
            # Create a thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.test.num_users) as executor:
                # Submit initial tasks based on spawn rate
                futures = []
                
                # Keep spawning users until we reach the target number
                for i in range(self.test.num_users):
                    if time.time() >= end_time:
                        break
                    
                    futures.append(executor.submit(self.user_task, i))
                    
                    # Respect the spawn rate
                    if i % self.test.spawn_rate == 0:
                        time.sleep(1)
                
                # Wait until the test duration is reached
                while time.time() < end_time and not self.stop_event.is_set():
                    time.sleep(0.5)
                
                # Signal all tasks to stop
                self.stop_event.set()
                
                # Wait for all tasks to complete
                concurrent.futures.wait(futures)
            
            # Process results
            test_results = self.process_results()
            
            # Mark test as completed
            self.test.complete_test(test_results)
            
            return test_results
            
        except Exception as e:
            logger.error(f"Error running load test: {str(e)}")
            self.test.fail_test(str(e))
            return {'error': str(e)}
    
    def process_results(self):
        """Process the test results and calculate statistics"""
        if not self.results:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'avg_response_time': None,
                'min_response_time': None,
                'max_response_time': None,
                'requests_per_second': 0,
                'detailed_results': []
            }
        
        # Count successful and failed requests
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        # Calculate response time statistics
        response_times = [r['response_time'] for r in self.results if r['response_time'] is not None]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = None
            min_response_time = None
            max_response_time = None
        
        # Calculate requests per second
        if self.test.started_at and self.test.completed_at:
            duration = (self.test.completed_at - self.test.started_at).total_seconds()
            requests_per_second = len(self.results) / duration if duration > 0 else 0
        else:
            requests_per_second = 0
        
        return {
            'total_requests': len(self.results),
            'successful_requests': len(successful),
            'failed_requests': len(failed),
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'requests_per_second': requests_per_second,
            'detailed_results': self.results
        }

