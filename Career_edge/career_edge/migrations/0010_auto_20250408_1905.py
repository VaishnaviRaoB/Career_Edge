# Generated by Django 3.2.16 on 2025-04-08 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('career_edge', '0009_jobprovider_jobseeker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobseeker',
            name='resume',
        ),
        migrations.AlterField(
            model_name='jobprovider',
            name='company_description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='jobprovider',
            name='company_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='jobprovider',
            name='contact_email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='jobseeker',
            name='experience_years',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='jobseeker',
            name='full_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='jobseeker',
            name='skills',
            field=models.TextField(),
        ),
    ]
