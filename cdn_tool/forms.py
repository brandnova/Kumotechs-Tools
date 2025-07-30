# cdn_tool/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import CDNFile

class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget to handle multiple file uploads"""
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    """Custom field to handle multiple file uploads"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class FileUploadForm(forms.Form):
    files = MultipleFileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'id': 'file-upload',
            'accept': 'image/*,.pdf,.doc,.docx,.zip,.txt,.csv'
        })
    )
    
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Optional: tag1, tag2, tag3'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'rows': 3,
            'placeholder': 'Optional description for this file'
        })
    )

    def clean_files(self):
        files = self.cleaned_data.get('files')
        if not files:
            return files
            
        # Define allowed file types and max size
        ALLOWED_TYPES = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
            'application/pdf', 'text/plain', 'text/csv',
            'application/zip', 'application/x-zip-compressed',
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        
        # Handle both single file and multiple files
        if not isinstance(files, list):
            files = [files]
        
        for file in files:
            if file:
                # Check file size
                if file.size > MAX_FILE_SIZE:
                    raise ValidationError(f'File "{file.name}" is too large. Maximum size is 50MB.')
                
                # Check file type
                if file.content_type not in ALLOWED_TYPES:
                    raise ValidationError(f'File type "{file.content_type}" is not allowed for file "{file.name}".')
        
        return files
