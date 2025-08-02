import time
import requests
import concurrent.futures
import threading
import json
import statistics
import random
import re
from datetime import datetime
import logging
from django.utils import timezone
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User agents list
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
]

# Human-like behavior patterns
READING_TIMES = {
    'short': (2, 5),      # Short content (e.g., product listing)
    'medium': (5, 15),    # Medium content (e.g., product details)
    'long': (15, 60)      # Long content (e.g., article, blog post)
}

class VirtualUser:
    """Class representing a virtual user with its own session and state"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.session = requests.Session()
        self.user_agent = random.choice(USER_AGENTS)
        self.session.headers.update({'User-Agent': self.user_agent})
        self.cookies = {}
        self.last_page = None
        self.last_request_time = None
        self.page_content = None
        self.current_url = None
        self.journey_state = {}  # Store state for the journey (e.g., extracted values)
    
    def wait_realistic_time(self, content_type='medium'):
        """Wait a realistic amount of time based on content type"""
        # If this is the first request, don't wait
        if self.last_request_time is None:
            self.last_request_time = time.time()
            return 0
        
        # Calculate time since last request
        time_since_last = time.time() - self.last_request_time
        
        # Get reading time range based on content type
        min_time, max_time = READING_TIMES.get(content_type, READING_TIMES['medium'])
        
        # If we've already waited enough, don't wait more
        if time_since_last >= min_time:
            self.last_request_time = time.time()
            return 0
        
        # Wait a random amount of time
        wait_time = random.uniform(min_time, max_time) - time_since_last
        if wait_time > 0:
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
        return wait_time
    
    def navigate_to(self, url, base_url=None):
        """Navigate to a URL"""
        # Handle relative URLs
        if base_url and not url.startswith(('http://', 'https://')):
            full_url = urljoin(base_url, url)
        else:
            full_url = url
        
        try:
            start_time = time.time()
            response = self.session.get(full_url, timeout=30)
            end_time = time.time()
            
            self.current_url = full_url
            self.page_content = response.text
            
            return {
                'success': 200 <= response.status_code < 400,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'content_length': len(response.content),
                'url': full_url
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'url': full_url
            }
    
    def extract_form_data(self, form_selector):
        """Extract form data from the current page"""
        # This is a simplified version - in a real implementation, you'd use a proper HTML parser
        if not self.page_content:
            return {}
        
        # Simple regex to find input fields in a form
        # This is just a basic example - a real implementation would be more robust
        form_data = {}
        
        # Find the form
        form_pattern = f'<form[^>]*{form_selector}[^>]*>(.*?)</form>'
        form_match = re.search(form_pattern, self.page_content, re.DOTALL | re.IGNORECASE)
        
        if not form_match:
            return {}
        
        form_content = form_match.group(1)
        
        # Find input fields
        input_pattern = r'<input[^>]*name=["\']([^"\']+)["\'][^>]*(?:value=["\']([^"\']*)["\'])?[^>]*>'
        input_matches = re.finditer(input_pattern, form_content, re.DOTALL | re.IGNORECASE)
        
        for match in input_matches:
            name = match.group(1)
            value = match.group(2) or ''
            form_data[name] = value
        
        return form_data
    
    def submit_form(self, form_selector, extra_data=None):
        """Submit a form on the current page"""
        if not self.page_content or not self.current_url:
            return {
                'success': False,
                'error': 'No page loaded',
                'url': None
            }
        
        # Extract form data
        form_data = self.extract_form_data(form_selector)
        
        # Add extra data
        if extra_data:
            form_data.update(extra_data)
        
        # Find form action and method
        form_pattern = f'<form[^>]*{form_selector}[^>]*action=["\']([^"\']+)["\'][^>]*(?:method=["\']([^"\']+)["\'])?[^>]*>'
        form_match = re.search(form_pattern, self.page_content, re.DOTALL | re.IGNORECASE)
        
        if form_match:
            action = form_match.group(1)
            method = form_match.group(2) or 'get'
        else:
            action = ''
            method = 'post'
        
        # Handle relative URLs
        if action and not action.startswith(('http://', 'https://')):
            action = urljoin(self.current_url, action)
        else:
            action = self.current_url
        
        try:
            start_time = time.time()
            
            if method.lower() == 'get':
                response = self.session.get(action, params=form_data, timeout=30)
            else:
                response = self.session.post(action, data=form_data, timeout=30)
            
            end_time = time.time()
            
            self.current_url = response.url
            self.page_content = response.text
            
            return {
                'success': 200 <= response.status_code < 400,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'content_length': len(response.content),
                'url': response.url
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'url': action
            }

class LoadTester:
    """Utility class for running load tests"""
    
    def __init__(self, test_instance):
        """Initialize with a LoadTest instance"""
        self.test = test_instance
        self.results = []
        self.stop_event = threading.Event()
        self.active_users = 0
        self.user_counter = 0
        self.virtual_users = {}  # Dictionary to store VirtualUser objects
    
    def make_request(self, virtual_user):
        """Make a single request to the target URL using a virtual user's session"""
        # Get headers from test configuration
        headers = {}
        if self.test.headers:
            try:
                headers = json.loads(self.test.headers)
            except json.JSONDecodeError:
                pass
        
        # Apply headers to the session
        for key, value in headers.items():
            virtual_user.session.headers[key] = value
        
        # Prepare request body
        body = None
        if self.test.body and self.test.http_method in ['POST', 'PUT']:
            try:
                body = json.loads(self.test.body)
            except json.JSONDecodeError:
                body = self.test.body
        
        # Wait a realistic amount of time before making the request
        wait_time = virtual_user.wait_realistic_time()
        
        # Prepare result object
        result = {
            'timestamp': timezone.now(),
            'success': False,
            'error': '',
            'status_code': None,
            'response_time': None,
            'user_agent': virtual_user.user_agent,
            'cookies': dict(virtual_user.session.cookies),
            'virtual_user_id': virtual_user.user_id,
            'wait_time': wait_time
        }
        
        try:
            # Make the request
            start_time = time.time()
            
            if self.test.http_method == 'GET':
                response = virtual_user.session.get(
                    self.test.target_url,
                    timeout=30
                )
            elif self.test.http_method == 'POST':
                response = virtual_user.session.post(
                    self.test.target_url,
                    json=body,
                    timeout=30
                )
            elif self.test.http_method == 'PUT':
                response = virtual_user.session.put(
                    self.test.target_url,
                    json=body,
                    timeout=30
                )
            elif self.test.http_method == 'DELETE':
                response = virtual_user.session.delete(
                    self.test.target_url,
                    timeout=30
                )
            else:
                # Fallback to generic request method
                response = virtual_user.session.request(
                    method=self.test.http_method,
                    url=self.test.target_url,
                    json=body if self.test.http_method in ['POST', 'PUT'] else None,
                    timeout=30
                )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Update virtual user's state
            virtual_user.last_page = self.test.target_url
            virtual_user.cookies = dict(virtual_user.session.cookies)
            virtual_user.page_content = response.text
            virtual_user.current_url = self.test.target_url
            
            # Update result
            result.update({
                'success': 200 <= response.status_code < 400,
                'status_code': response.status_code,
                'response_time': response_time,
                'content_length': len(response.content) if hasattr(response, 'content') else 0,
                'url': self.test.target_url
            })
            
        except requests.RequestException as e:
            result.update({
                'success': False,
                'error': str(e),
                'url': self.test.target_url
            })
        
        return result
    
    def execute_journey_step(self, virtual_user, step, journey):
        """Execute a single step in a user journey"""
        # Wait before executing the step
        wait_time = random.uniform(step.min_wait, step.max_wait)
        time.sleep(wait_time)
        
        # Prepare base result object
        result = {
            'timestamp': timezone.now(),
            'success': False,
            'error': '',
            'status_code': None,
            'response_time': None,
            'user_agent': virtual_user.user_agent,
            'cookies': dict(virtual_user.session.cookies),
            'virtual_user_id': virtual_user.user_id,
            'journey_id': journey.id,
            'journey_name': journey.name,
            'journey_step_id': step.id,
            'step_type': step.step_type,
            'wait_time': wait_time
        }
        
        try:
            # Execute the step based on its type
            if step.step_type == 'navigate':
                # Navigate to URL
                url = step.url
                step_result = virtual_user.navigate_to(url, journey.base_url)
                result.update(step_result)
            
            elif step.step_type == 'click':
                # Simulate clicking an element (in our simplified version, this is just another navigation)
                # In a real implementation with Selenium, this would actually click the element
                if not virtual_user.page_content:
                    result.update({
                        'success': False,
                        'error': 'No page loaded to click element on',
                        'url': virtual_user.current_url
                    })
                else:
                    # For now, we'll just simulate this by extracting the href and navigating to it
                    # This is a very simplified version - a real implementation would be more robust
                    href_pattern = f'<a[^>]*{step.selector}[^>]*href=["\']([^"\']+)["\'][^>]*>'
                    href_match = re.search(href_pattern, virtual_user.page_content, re.DOTALL | re.IGNORECASE)
                    
                    if href_match:
                        url = href_match.group(1)
                        step_result = virtual_user.navigate_to(url, journey.base_url)
                        result.update(step_result)
                    else:
                        result.update({
                            'success': False,
                            'error': f'Could not find element with selector: {step.selector}',
                            'url': virtual_user.current_url
                        })
            
            elif step.step_type == 'input':
                # Simulate inputting text (just store it for now)
                # In a real implementation with Selenium, this would actually input text
                if not virtual_user.page_content:
                    result.update({
                        'success': False,
                        'error': 'No page loaded to input text on',
                        'url': virtual_user.current_url
                    })
                else:
                    # Store the input value in the journey state
                    field_name = step.selector.split('=')[-1].strip('"\'')
                    virtual_user.journey_state[field_name] = step.value
                    
                    result.update({
                        'success': True,
                        'url': virtual_user.current_url
                    })
            
            elif step.step_type == 'submit':
                # Submit a form
                if not virtual_user.page_content:
                    result.update({
                        'success': False,
                        'error': 'No page loaded to submit form on',
                        'url': virtual_user.current_url
                    })
                else:
                    # Use the stored input values
                    step_result = virtual_user.submit_form(step.selector, virtual_user.journey_state)
                    result.update(step_result)
                    
                    # Clear the journey state after form submission
                    virtual_user.journey_state = {}
            
            elif step.step_type == 'wait':
                # Just wait (already done at the beginning of this method)
                result.update({
                    'success': True,
                    'url': virtual_user.current_url
                })
            
            else:
                result.update({
                    'success': False,
                    'error': f'Unknown step type: {step.step_type}',
                    'url': virtual_user.current_url
                })
        
        except Exception as e:
            result.update({
                'success': False,
                'error': f'Error executing step: {str(e)}',
                'url': virtual_user.current_url
            })
        
        return result
    
    def user_task(self, user_id):
        """Simulate a user making requests or executing a journey"""
        self.active_users += 1
        self.user_counter += 1
        
        # Create a virtual user with a persistent session
        virtual_user = VirtualUser(user_id)
        self.virtual_users[user_id] = virtual_user
        
        try:
            # Make requests until the test duration is reached
            while not self.stop_event.is_set():
                # Decide whether to use a journey based on probability
                use_journey = random.random() <= self.test.journey_probability
                
                if use_journey and (self.test.journey or self.test.journeys.exists()):
                    # Get a random journey
                    journey = self.test.get_random_journey()
                    
                    if journey:
                        # Execute the journey
                        journey_results = self.execute_journey(virtual_user, journey)
                        self.results.extend(journey_results)
                    else:
                        # No journey selected, make a single request to the target URL
                        if self.test.target_url:
                            result = self.make_request(virtual_user)
                            self.results.append(result)
                else:
                    # Make a single request to the target URL
                    if self.test.target_url:
                        result = self.make_request(virtual_user)
                        self.results.append(result)
                    else:
                        # No target URL and not using journey, sleep and continue
                        time.sleep(1)
        
        finally:
            self.active_users -= 1
            # Clean up the virtual user
            if user_id in self.virtual_users:
                del self.virtual_users[user_id]
    
    def execute_journey(self, virtual_user, journey):
        """Execute a complete user journey"""
        journey_results = []
        
        # Get all steps for the journey
        steps = journey.steps.all().order_by('order')
        
        for step in steps:
            # Check if we should stop
            if self.stop_event.is_set():
                break
            
            # Execute the step
            result = self.execute_journey_step(virtual_user, step, journey)
            journey_results.append(result)
            
            # If the step failed, stop the journey
            if not result['success']:
                break
        
        return journey_results
    
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
        successful = [r for r in self.results if r.get('success', False)]
        failed = [r for r in self.results if not r.get('success', False)]
        
        # Calculate response time statistics
        response_times = [r.get('response_time') for r in self.results if r.get('response_time') is not None]
        
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
        
        # Group results by virtual user
        users_data = {}
        for result in self.results:
            user_id = result.get('virtual_user_id')
            if user_id not in users_data:
                users_data[user_id] = {
                    'requests': 0,
                    'successful': 0,
                    'failed': 0
                }
            
            users_data[user_id]['requests'] += 1
            if result.get('success', False):
                users_data[user_id]['successful'] += 1
            else:
                users_data[user_id]['failed'] += 1
        
        # Calculate success rate for each user
        for user_id, data in users_data.items():
            if data['requests'] > 0:
                data['success_rate'] = (data['successful'] / data['requests']) * 100
            else:
                data['success_rate'] = 0
        
        # Group results by journey
        journeys_data = {}
        for result in self.results:
            journey_id = result.get('journey_id')
            if journey_id and journey_id not in journeys_data:
                journeys_data[journey_id] = {
                    'name': result.get('journey_name', f'Journey {journey_id}'),
                    'requests': 0,
                    'successful': 0,
                    'failed': 0,
                    'steps': {}
                }
            
            if journey_id:
                journeys_data[journey_id]['requests'] += 1
                if result.get('success', False):
                    journeys_data[journey_id]['successful'] += 1
                else:
                    journeys_data[journey_id]['failed'] += 1
                
                # Group by step within journey
                step_id = result.get('journey_step_id')
                if step_id and step_id not in journeys_data[journey_id]['steps']:
                    journeys_data[journey_id]['steps'][step_id] = {
                        'step_type': result.get('step_type', 'unknown'),
                        'requests': 0,
                        'successful': 0,
                        'failed': 0,
                        'response_times': []
                    }
                
                if step_id:
                    step_data = journeys_data[journey_id]['steps'][step_id]
                    step_data['requests'] += 1
                    if result.get('success', False):
                        step_data['successful'] += 1
                    else:
                        step_data['failed'] += 1
                    
                    if result.get('response_time') is not None:
                        step_data['response_times'].append(result.get('response_time'))
        
        # Calculate average response time for each step
        for journey_id, journey_data in journeys_data.items():
            for step_id, step_data in journey_data['steps'].items():
                if step_data['response_times']:
                    step_data['avg_response_time'] = statistics.mean(step_data['response_times'])
                    del step_data['response_times']  # Remove the raw data to save space
        
        return {
            'total_requests': len(self.results),
            'successful_requests': len(successful),
            'failed_requests': len(failed),
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'requests_per_second': requests_per_second,
            'users_data': users_data,
            'journeys_data': journeys_data,
            'detailed_results': self.results
        }