# career_edge/admin.py

from django.contrib import admin
from .models import UserProfile, Job, JobApplication, JobSeeker, JobProvider

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')


@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'full_name', 'experience_years')


@admin.register(JobProvider)
class JobProviderAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'company_name', 'contact_email')


admin.site.register(Job)
admin.site.register(JobApplication)
