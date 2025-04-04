# Generated by Django 5.1.6 on 2025-03-30 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webtester', '0002_testresult_user_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadtest',
            name='users_data',
            field=models.TextField(blank=True, help_text='Virtual users data in JSON format', null=True),
        ),
        migrations.AddField(
            model_name='testresult',
            name='content_length',
            field=models.PositiveIntegerField(blank=True, help_text='Length of the response content in bytes', null=True),
        ),
        migrations.AddField(
            model_name='testresult',
            name='cookies',
            field=models.TextField(blank=True, help_text='Cookies for this request in JSON format', null=True),
        ),
        migrations.AddField(
            model_name='testresult',
            name='virtual_user_id',
            field=models.IntegerField(blank=True, help_text='ID of the virtual user that made this request', null=True),
        ),
    ]
