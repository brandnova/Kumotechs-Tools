from django import forms
from .models import ShortLink, QRCodeCustomization

class ShortLinkForm(forms.ModelForm):
    class Meta:
        model = ShortLink
        fields = ['original_url', 'slug', 'name']
        widgets = {
            'original_url': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white', 'placeholder': 'https://example.com'}),
            'slug': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white', 'placeholder': 'custon link text (hyphens only)'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white', 'placeholder': 'Optional friendly name'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['name'].required = False

class QRCodeCustomizationForm(forms.ModelForm):
    class Meta:
        model = QRCodeCustomization
        fields = ['color', 'bg_color', 'logo', 'convert_logo_bw', 'text']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'h-10 w-full'}),
            'bg_color': forms.TextInput(attrs={'type': 'color', 'class': 'h-10 w-full'}),
            'logo': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
            'convert_logo_bw': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'text': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white', 'placeholder': 'Optional text (max 50 chars)', 'maxlength': '50'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['logo'].required = False
        self.fields['text'].required = False

