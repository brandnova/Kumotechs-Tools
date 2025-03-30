from django import forms
from .models import LoadTest
import json

class LoadTestForm(forms.ModelForm):
    """Form for creating and editing load tests"""
    class Meta:
        model = LoadTest
        fields = ['name', 'target_url', 'num_users', 'spawn_rate', 'duration', 'http_method', 'headers', 'body']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Test name'
            }),
            'target_url': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'https://example.com'
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

