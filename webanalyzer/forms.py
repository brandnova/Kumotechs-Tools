from django import forms
from .models import WebsiteAnalysis

class WebsiteAnalysisForm(forms.Form):
    url = forms.URLField(
        label="Website URL",
        widget=forms.URLInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'https://example.com'
        }),
        help_text="Enter the full URL including http:// or https://"
    )
    
    def clean_url(self):
        url = self.cleaned_data['url']
        # Ensure URL has a scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

