# Generated by Django 5.1.6 on 2025-03-29 20:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shortlinks', '0002_shortlink_qr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='shortlink',
            name='has_custom_qr',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='QRCodeCustomization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(default='#000000', max_length=20)),
                ('bg_color', models.CharField(default='#FFFFFF', max_length=20)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logos/')),
                ('shortlink', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='qr_customization', to='shortlinks.shortlink')),
            ],
        ),
    ]
