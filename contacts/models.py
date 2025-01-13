# models.py
from django.db import models

class Contact(models.Model):
    PREFIX_CHOICES = [
        ('', 'None'),
        ('Mr.', 'Mr.'),
        ('Mrs.', 'Mrs.'),
        ('Ms.', 'Ms.'),
        ('Dr.', 'Dr.'),
    ]
    
    prefix = models.CharField(max_length=4, choices=PREFIX_CHOICES, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15)
    organization = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'prefix': self.prefix,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'organization': self.organization
        }