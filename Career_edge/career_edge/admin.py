# career_edge/admin.py

from django.contrib import admin
from .models import UserProfile, Job, JobApplication

admin.site.register(UserProfile)
admin.site.register(Job)
admin.site.register(JobApplication)
