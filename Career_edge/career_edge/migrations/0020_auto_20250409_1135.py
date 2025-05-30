# Generated by Django 3.2.16 on 2025-04-09 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('career_edge', '0019_jobapplication_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobprovider',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='company_logos/'),
        ),
        migrations.AddField(
            model_name='jobprovider',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
    ]
