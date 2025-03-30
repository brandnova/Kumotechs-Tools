from django import forms
from .models import LoadTest, UserJourney, JourneyStep
import json

class LoadTestForm(forms.ModelForm):
    """Form for creating and editing load tests"""
    class Meta:
        model = LoadTest
        fields = ['name', 'target_url', 'journey', 'num_users', 'spawn_rate', 'duration', 'http_method', 'headers', 'body']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Test name'
            }),
            'target_url': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'https://example.com'
            }),
            'journey': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white'
            }),
            'num_users': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'min': '1',
                'max': '1000'
            }),
            'spawn_rate': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'min': '1',
                'max': '100'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'min': '5',
                'max': '3600'
            }),
            'http_method': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white'
            }),
            'headers': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': '{"Content-Type": "application/json", "Authorization": "Bearer token"}',
                'rows': '3'
            }),
            'body': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': '{"key": "value"}',
                'rows': '3'
            }),
        }
    
    def clean_headers(self):
        """Validate that headers are valid JSON"""
        headers = self.cleaned_data.get('headers')
        if headers:
            try:
                json.loads(headers)
            except json.JSONDecodeError:
                raise forms.ValidationError("Headers must be valid JSON")
        return headers
    
    def clean_body(self):
        """Validate that body is valid JSON for POST/PUT requests"""
        body = self.cleaned_data.get('body')
        method = self.cleaned_data.get('http_method')
        
        if method in ['POST', 'PUT'] and body:
            try:
                json.loads(body)
            except json.JSONDecodeError:
                raise forms.ValidationError("Body must be valid JSON for POST/PUT requests")
        
        return body
    
    def clean(self):
        """Validate that either target_url or journey is provided, but not both"""
        cleaned_data = super().clean()
        target_url = cleaned_data.get('target_url')
        journey = cleaned_data.get('journey')
        
        if not target_url and not journey:
            raise forms.ValidationError("Either Target URL or User Journey must be provided")
        
        if target_url and journey:
            self.add_error('target_url', "Cannot specify both Target URL and User Journey")
            self.add_error('journey', "Cannot specify both Target URL and User Journey")
        
        return cleaned_data

class UserJourneyForm(forms.ModelForm):
    """Form for creating and editing user journeys"""
    class Meta:
        model = UserJourney
        fields = ['name', 'description', 'base_url']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Journey name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Description of the user journey',
                'rows': '3'
            }),
            'base_url': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'https://example.com'
            }),
        }

class JourneyStepForm(forms.ModelForm):
    """Form for creating and editing journey steps"""
    class Meta:
        model = JourneyStep
        fields = ['step_type', 'order', 'url', 'selector', 'value', 'min_wait', 'max_wait']
        widgets = {
            'step_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'min': '1'
            }),
            'url': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': '/path/to/page'
            }),
            'selector': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': '#element-id or .class-name'
            }),
            'value': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Text to input'
            }),
            'min_wait': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'min': '0',
                'step': '0.1'
            }),
            'max_wait': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'min': '0',
                'step': '0.1'
            }),
        }
    
    def clean(self):
        """Validate that the appropriate fields are filled based on step type"""
        cleaned_data = super().clean()
        step_type = cleaned_data.get('step_type')
        url = cleaned_data.get('url')
        selector = cleaned_data.get('selector')
        value = cleaned_data.get('value')
        
        if step_type == 'navigate' and not url:
            self.add_error('url', "URL is required for navigate step type")
        
        if step_type in ['click', 'input', 'submit'] and not selector:
            self.add_error('selector', f"Selector is required for {step_type} step type")
        
        if step_type == 'input' and not value:
            self.add_error('value', "Value is required for input step type")
        
        return cleaned_data