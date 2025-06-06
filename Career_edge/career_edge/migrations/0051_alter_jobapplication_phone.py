# Generated by Django 3.2.16 on 2025-05-27 07:19

import career_edge.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('career_edge', '0050_alter_jobapplication_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobapplication',
            name='phone',
            field=models.CharField(help_text='Enter phone number (10-15 digits, optional country code with +)', max_length=20, validators=[career_edge.models.validate_phone_number]),
        ),
    ]
