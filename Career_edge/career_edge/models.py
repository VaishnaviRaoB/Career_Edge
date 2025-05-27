from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
import re

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
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    location_preferences = models.CharField(max_length=255, null=True, blank=True)
    education = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(null=True, blank=True)
    skills = models.TextField(blank=True,null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    security_question = models.CharField(max_length=50, blank=True, null=True)
    security_answer = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.full_name


class JobProvider(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    company_description = models.TextField()
    contact_email = models.EmailField()
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True) 
    location = models.CharField(max_length=100, blank=True, null=True)
    security_question = models.CharField(max_length=50, blank=True, null=True)
    security_answer = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.company_name


class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.URLField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50, choices=[("Full-time", "Full-time"), ("Part-time", "Part-time"), ("Internship", "Internship"), ("Contract", "Contract")], default="Full-time")
    experience_level = models.CharField(max_length=50, choices=[("Fresher", "Fresher"), ("Mid-level", "Mid-level"), ("Senior", "Senior")], default="Fresher")
    provider = models.ForeignKey(User, on_delete=models.CASCADE)
    skills = models.CharField(max_length=255, default="")
    salary = models.CharField(max_length=50, blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    logo = models.ImageField(upload_to='job_logos/', blank=True, null=True)
    last_date_to_apply = models.DateField(null=True, blank=True)
    is_new = models.BooleanField(default=True) 
    has_custom_questions = models.BooleanField(default=False)
    
    def is_recent(self):
        return (timezone.now() - self.date_posted).days <= 3
    def application_count(self):
        return self.jobapplication_set.count()
    def __str__(self):
        return self.title
def validate_phone_number(value):
    """Custom validator for phone numbers"""
    if not value:
        return  # Allow empty if field is not required
    
    # Remove common separators and spaces
    phone_clean = re.sub(r'[\s\-\(\)\.]', '', value.strip())
    
    # Check if it starts with + (international format)
    if phone_clean.startswith('+'):
        digits_part = phone_clean[1:]
        
        if not digits_part.isdigit():
            raise ValidationError("Phone number can only contain digits after country code (+).")
        
        if len(digits_part) < 10:
            raise ValidationError("International phone number must have at least 10 digits after country code.")
        elif len(digits_part) > 15:
            raise ValidationError("Phone number cannot exceed 15 digits.")
    else:
        # Domestic format
        if not phone_clean.isdigit():
            raise ValidationError("Phone number can only contain digits (and optional + for country code).")
        
        if len(phone_clean) < 10:
            raise ValidationError("Phone number must be at least 10 digits long.")
        elif len(phone_clean) > 15:
            raise ValidationError("Phone number cannot exceed 15 digits.")
        
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
    email = models.EmailField(max_length=255, default="")
    phone = models.CharField(
        max_length=20,  # Increased to accommodate international formats with formatting
        validators=[validate_phone_number],  # Using custom validator
        blank=False,  # Made required
        help_text="Enter phone number (10-15 digits, optional country code with +)"
    )
    resume = models.FileField(upload_to='resumes/')
    created_at = models.DateTimeField(default=timezone.now)
    experience = models.CharField(max_length=50, default="0") 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_seen_by_provider = models.BooleanField(default=False)
    is_seen_by_seeker = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            try:
                old_instance = JobApplication.objects.get(pk=self.pk)
                if old_instance.status != self.status:
                    self.is_seen_by_seeker = False
            except JobApplication.DoesNotExist:
                pass
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'{self.name} - {self.job.title}'

class SavedJob(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('job', 'user') 
        
    def __str__(self):
        return f"{self.user.username} - {self.job.title}"


class JobCustomQuestion(models.Model):
    QUESTION_TYPES = [
        ('text', 'Text Answer'),
        ('yesno', 'Yes/No Answer'),
        ('file', 'File Upload'),
        ('link', 'Link (URL)'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='custom_questions')
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='text')
    is_required = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.question_text} ({self.get_question_type_display()})"
        
# Add this to your models.py file after the JobApplication model

class JobApplicationAnswer(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(JobCustomQuestion, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    boolean_answer = models.BooleanField(null=True, blank=True)
    file_answer = models.FileField(upload_to='application_answers/', blank=True, null=True)
    link_answer = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"Answer for {self.question.question_text}"