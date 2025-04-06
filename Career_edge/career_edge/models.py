# career_edge/models.py

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_ROLES = (
        ('seeker', 'Seeker'),
        ('provider', 'Provider'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES)

    def __str__(self):
        return f'{self.user.username} - {self.role}'
class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.CharField(max_length=255, default='Not Specified')  # Default value for company
    location = models.CharField(max_length=255, default='Unknown')  # Default value for location
    provider = models.ForeignKey(User, on_delete=models.CASCADE)
    skills = models.CharField(max_length=255, default="")
    salary = models.CharField(max_length=100, blank=True, null=True)  
    def __str__(self):
        return self.title


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    skills = models.CharField(max_length=255)
    qualification = models.CharField(max_length=255)
    email = models.EmailField(max_length=255,  default="")  # Add email field
    phone = models.CharField(max_length=20,  default="")  
    resume = models.FileField(upload_to='resumes/')

    def __str__(self):
        return f'{self.name} - {self.job.title}'
