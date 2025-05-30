# Generated by Django 3.2.16 on 2025-04-08 13:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('career_edge', '0008_auto_20240629_2022'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobSeeker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=100)),
                ('resume', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('skills', models.TextField(blank=True)),
                ('experience_years', models.IntegerField(blank=True, null=True)),
                ('user_profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='career_edge.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='JobProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(blank=True, max_length=100)),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('company_description', models.TextField(blank=True)),
                ('user_profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='career_edge.userprofile')),
            ],
        ),
    ]
