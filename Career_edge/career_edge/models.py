# career_edge/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    USER_ROLES = (
        ('seeker', 'Seeker'),
        ('provider', 'Provider'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES)

    def __str__(self):
        return f'{self.user.username} - {self.role}'


class JobSeeker(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    experience_years = models.IntegerField(null=True, blank=True)
    skills = models.TextField()

    def __str__(self):
        return self.full_name


class JobProvider(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    company_description = models.TextField()
    contact_email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    def __str__(self):
        return self.company_name
# models.py
class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.URLField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255)
    provider = models.ForeignKey(User, on_delete=models.CASCADE)
    skills = models.CharField(max_length=255, default="")
    salary = models.CharField(max_length=50, blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return self.title

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('interview', 'Interview Scheduled'),
        ('pending', 'Pending'),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    skills = models.CharField(max_length=255)
    qualifications = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255,  default="")  # Add email field
    phone = models.CharField(max_length=20,  default="")  
    resume = models.FileField(upload_to='resumes/')
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f'{self.name} - {self.job.title}'
