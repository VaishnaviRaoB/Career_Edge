# Generated by Django 3.2.16 on 2025-04-11 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('career_edge', '0044_jobapplication_is_seen_by_seeker'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='is_new',
            field=models.BooleanField(default=True),
        ),
    ]
