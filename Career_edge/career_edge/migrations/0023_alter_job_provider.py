# Generated by Django 3.2.16 on 2025-04-09 09:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('career_edge', '0022_jobapplication_experience'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='career_edge.jobprovider'),
        ),
    ]
