from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from datetime import datetime
from .models import UserProfile, Job, JobApplication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .models import Job, JobApplication, JobCustomQuestion, JobApplicationAnswer
from django.db import transaction
from .models import Job, JobCustomQuestion, validate_phone_number
from .forms import JobForm, CustomQuestionFormSet, JobApplicationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from datetime import datetime, timedelta, date
from .forms import EditCompanyProfileForm
from django.utils.dateparse import parse_date
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import UserProfile, JobSeeker, JobProvider,SavedJob
from .forms import JobForm,JobSeekerProfileForm
import re
from django.db.models import Q
from django.http import HttpResponse
import xlwt
from django.db.models import Q
from django.db import models
from django.views.decorators.http import require_POST
from django.urls import reverse

from django.contrib import messages
from django.core.paginator import Paginator
import logging
import requests

# Home page view
def home(request):
    return render(request, 'home.html')

# About page view
def about(request):
    return render(request, 'about.html')

# Contact page view
def contact(request):
    return render(request, 'contact.html')

# User login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            profile = UserProfile.objects.get(user=user)
            if profile.role == 'seeker':
                return redirect('seeker_dashboard')
            elif profile.role == 'provider':
                return redirect('provider_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    
    return render(request, 'login.html')

def validate_password(password):
    return (
        len(password) >= 8 and
        re.search(r"\d", password) and
        re.search(r"[!@#$%^&*]", password) and
        re.search(r"[a-zA-Z]", password)
    )


@login_required
def seeker_profile(request):
    try:
        # Get the user's profile
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Check if the user is a seeker
        if user_profile.role != 'seeker':
            messages.error(request, "Access denied. This page is for job seekers only.")
            return redirect('user_login')
        
        # Get or create the job seeker profile
        job_seeker, created = JobSeeker.objects.get_or_create(
            user_profile=user_profile,
            defaults={
                'full_name': request.user.username,
                'skills': ''
            }
        )
        
        if request.method == 'POST':
            form = JobSeekerProfileForm(request.POST, request.FILES, instance=job_seeker)
            if form.is_valid():
                form.save()
                messages.success(request, "Your profile has been updated successfully!")
                return redirect('seeker_profile')
        else:
            form = JobSeekerProfileForm(instance=job_seeker)
        
        return render(request, 'seeker_profile.html', {'form': form, 'job_seeker': job_seeker})
    
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('seeker_dashboard')
def user_register_seeker(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        security_question = request.POST.get('security_question')
        security_answer = request.POST.get('security_answer')

        if not username or not email or not password or not security_question or not security_answer:
            return render(request, 'register_seeker.html', {'error': 'All fields are required.'})

        if not validate_password(password):
            return render(request, 'register_seeker.html', {
                'error': 'Password must be at least 8 characters long and include a letter, number, and special character.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'register_seeker.html', {'error': 'Username already exists.'})
            
        # Instead of checking if email exists in User, check if it exists in JobSeeker
        existing_seeker = JobSeeker.objects.filter(email=email).exists()
        
        if existing_seeker:
            return render(request, 'register_seeker.html', {'error': 'This email is already registered as a job seeker.'})

        user = User.objects.create_user(username=username, email=email, password=password)
        profile = UserProfile.objects.create(user=user, role='seeker')
        JobSeeker.objects.create(
            user_profile=profile,
            full_name=username,
            email=email,
            skills='',
            experience_years=None,
            security_question=security_question,
            security_answer=security_answer  # For production, consider hashing this
        )

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Registration successful! Next step: Set up your profile.')
            return redirect('seeker_dashboard')
        return redirect('user_login')

    return render(request, 'register_seeker.html')

def user_register_provider(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        security_question = request.POST.get('security_question')
        security_answer = request.POST.get('security_answer')

        if not username or not email or not password or not security_question or not security_answer:
            return render(request, 'register_provider.html', {'error': 'All fields are required.'})

        if not validate_password(password):
            return render(request, 'register_provider.html', {
                'error': 'Password must be at least 8 characters long and include a letter, number, and special character.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'register_provider.html', {'error': 'Username already exists.'})
            
        # Instead of checking if email exists in User, check if it exists in JobProvider
        existing_provider = JobProvider.objects.filter(contact_email=email).exists()
        
        if existing_provider:
            return render(request, 'register_provider.html', {'error': 'This email is already registered as a job provider.'})

        user = User.objects.create_user(username=username, email=email, password=password)
        profile = UserProfile.objects.create(user=user, role='provider')
        JobProvider.objects.create(
            user_profile=profile,
            company_name=username,  # Default value, can be updated later
            company_description='',
            contact_email=email,
            security_question=security_question,
            security_answer=security_answer  # For production, consider hashing this
        )

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Registration successful! Next step: Set up your profile.')
            return redirect('provider_dashboard')
            
        return redirect('user_login')

    return render(request, 'register_provider.html')
def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        security_answer = request.POST.get('security_answer')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Step 1: Verify username exists
        if 'username' in request.POST and not security_answer and not new_password:
            try:
                user = User.objects.get(username=username)
                # Find the associated profile and determine if user is a job seeker or provider
                profile = UserProfile.objects.get(user=user)
                
                if profile.role == 'seeker':
                    try:
                        seeker = JobSeeker.objects.get(user_profile=profile)
                        security_question = seeker.security_question
                        return render(request, 'forgot_password.html', {
                            'step': 'security',
                            'username': username,
                            'security_question': security_question
                        })
                    except JobSeeker.DoesNotExist:
                        return render(request, 'forgot_password.html', {
                            'step': 'verify',
                            'error': 'No security question found for this user.'
                        })
                        
                elif profile.role == 'provider':
                    try:
                        provider = JobProvider.objects.get(user_profile=profile)
                        security_question = provider.security_question
                        return render(request, 'forgot_password.html', {
                            'step': 'security',
                            'username': username,
                            'security_question': security_question
                        })
                    except JobProvider.DoesNotExist:
                        return render(request, 'forgot_password.html', {
                            'step': 'verify',
                            'error': 'No security question found for this user.'
                        })
                        
                else:
                    return render(request, 'forgot_password.html', {
                        'step': 'verify',
                        'error': 'User profile type not recognized.'
                    })
                    
            except User.DoesNotExist:
                return render(request, 'forgot_password.html', {
                    'step': 'verify',
                    'error': 'Username does not exist.'
                })
                
        # Step 2: Verify security answer
        elif username and security_answer and not new_password:
            try:
                user = User.objects.get(username=username)
                profile = UserProfile.objects.get(user=user)
                
                if profile.role == 'seeker':
                    seeker = JobSeeker.objects.get(user_profile=profile)
                    if seeker.security_answer.lower() == security_answer.lower():
                        return render(request, 'forgot_password.html', {
                            'step': 'reset',
                            'username': username
                        })
                    else:
                        return render(request, 'forgot_password.html', {
                            'step': 'security',
                            'username': username,
                            'security_question': seeker.security_question,
                            'error': 'Incorrect security answer.'
                        })
                        
                elif profile.role == 'provider':
                    provider = JobProvider.objects.get(user_profile=profile)
                    if provider.security_answer.lower() == security_answer.lower():
                        return render(request, 'forgot_password.html', {
                            'step': 'reset',
                            'username': username
                        })
                    else:
                        return render(request, 'forgot_password.html', {
                            'step': 'security',
                            'username': username,
                            'security_question': provider.security_question,
                            'error': 'Incorrect security answer.'
                        })
                        
            except (User.DoesNotExist, UserProfile.DoesNotExist, JobSeeker.DoesNotExist, JobProvider.DoesNotExist):
                return render(request, 'forgot_password.html', {
                    'step': 'verify',
                    'error': 'User not found.'
                })
                
        # Step 3: Reset password
        elif username and new_password and confirm_password:
            if new_password != confirm_password:
                return render(request, 'forgot_password.html', {
                    'step': 'reset',
                    'username': username,
                    'error': 'Passwords do not match.'
                })
                
            if not validate_password(new_password):
                return render(request, 'forgot_password.html', {
                    'step': 'reset',
                    'username': username,
                    'error': 'Password must be at least 8 characters long and include a letter, number, and special character.'
                })
                
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                
                # Get user profile to determine where to redirect
                profile = UserProfile.objects.get(user=user)
                
                # Log the user in
                user = authenticate(username=username, password=new_password)
                if user:
                    login(request, user)
                    
                    # Display success message
                    messages.success(request, 'Password has been reset successfully. You are now logged in.')
                    
                    # Redirect based on user role
                    if profile.role == 'seeker':
                        return redirect('seeker_dashboard')
                    elif profile.role == 'provider':
                        return redirect('provider_dashboard')
                    else:
                        return redirect('home')  # Fallback
                else:
                    # This should rarely happen, but just in case authentication fails
                    return render(request, 'forgot_password.html', {
                        'step': 'verify',
                        'success': 'Password has been reset successfully. Please login with your new password.',
                        'error': 'Automatic login failed. Please try logging in manually.'
                    })
                
            except User.DoesNotExist:
                return render(request, 'forgot_password.html', {
                    'step': 'verify',
                    'error': 'User not found.'
                })
    
    # Default: show the initial form
    return render(request, 'forgot_password.html', {'step': 'verify'})

@login_required
def edit_company_profile(request):
    try:
        # Get the user's profile
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Check if the user is a provider
        if user_profile.role != 'provider':
            messages.error(request, "Access denied. This page is for job providers only.")
            return redirect('user_login')
        
        # Get the job provider profile
        provider = JobProvider.objects.get(user_profile=user_profile)
        
        if request.method == 'POST':
            # Create a form instance with the POST data, but only for JobProvider fields
            # This ensures username is not affected
            form = EditCompanyProfileForm(request.POST, request.FILES, instance=provider)
            if form.is_valid():
                # Save only the JobProvider model changes
                form.save()
                
                # Handle the company logo separately if needed
                if 'company_logo' in request.FILES:
                    provider.company_logo = request.FILES['company_logo']
                    provider.save()
                    
                messages.success(request, "Your company profile has been updated successfully!")
                return redirect('edit_company_profile')
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = EditCompanyProfileForm(instance=provider)
        
        return render(request, 'edit_company_profile.html', {'form': form, 'provider': provider})
    
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('provider_dashboard')
    except JobProvider.DoesNotExist:
        messages.error(request, "Provider profile not found.")
        return redirect('provider_dashboard')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('provider_dashboard')
    
@login_required
def seeker_dashboard(request):
    jobs = Job.objects.all().order_by('-date_posted')
    today = timezone.now().date()
    
    # Get IDs of jobs saved by the current user
    saved_job_ids = SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True)
    
    # Get count of unseen application updates
    # Change 'user' to 'applicant' here:
    unseen_count = JobApplication.objects.filter(
        applicant=request.user,
        is_seen_by_seeker=False
    ).count()
    # Check if there are new jobs and user hasn't been notified this session
    new_jobs_count = Job.objects.filter(
        date_posted__gte=timezone.now() - timezone.timedelta(days=3)
    ).count()
    
    show_new_jobs_popup = False
    if new_jobs_count > 0 and not request.session.get('new_jobs_seen', False):
        show_new_jobs_popup = True
        request.session['new_jobs_seen'] = True

    return render(request, 'seeker_dashboard.html', {
        'jobs': jobs,
        'saved_job_ids': saved_job_ids,
        'today': today,
        'unseen_count': unseen_count,
        'new_jobs_count': new_jobs_count,
        'show_new_jobs_popup': show_new_jobs_popup,
    })
# Provider dashboard view
@login_required
def provider_dashboard(request):
    return render(request, 'provider_dashboard.html')

# View jobs posted by a provider

@login_required
def view_jobs(request):
    query = request.GET.get('q', '')
    jobs = Job.objects.filter(provider=request.user).order_by('-date_posted')
    
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) | 
            Q(location__icontains=query) |
            Q(description__icontains=query) |
            Q(company__icontains=query)
        )
    
    # Find jobs with new applications and add the count directly to job objects
    total_new_apps = 0
    
    # Get current time and calculate 24 hours ago
    now = timezone.now()
    recent_threshold = now - timedelta(hours=24)
    
    for job in jobs:
        # Count unseen applications for each job
        new_apps_count = JobApplication.objects.filter(
            job=job, 
            is_seen_by_provider=False
        ).count()
        
        # Add the count as an attribute to the job object
        job.new_apps_count = new_apps_count
        
        # Flag if the job is newly posted (within the last 24 hours)
        job.is_new = job.date_posted >= recent_threshold
        
        if new_apps_count > 0:
            total_new_apps += new_apps_count
    
    # Add notification if there are new applications
    if total_new_apps > 0:
        messages.success(request, f"You have {total_new_apps} new application(s) across your job postings!")

    return render(request, 'view_jobs.html', {
        'jobs': jobs,
        'query': query,
    })
@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Get all custom questions for this job
    custom_questions = JobCustomQuestion.objects.filter(job=job)

    # Check if the user has already applied to this job
    already_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()

    if already_applied:
        messages.warning(request, "You have already applied for this job.")
        return redirect('seeker_dashboard')

    if request.method == 'POST':
        # Create form instance with POST data
        form = JobApplicationForm(request.POST, request.FILES)
        
        # Manual validation for required fields
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        skills = request.POST.get('skills', '').strip()
        qualifications = request.POST.get('qualification', '').strip()
        resume = request.FILES.get('resume')
        experience = request.POST.get('experience', '').strip()
        
        errors = []
        
        # Validate required fields
        if not name:
            errors.append("Name is required.")
        if not email:
            errors.append("Email is required.")
        if not phone:
            errors.append("Phone number is required.")
        if not skills:
            errors.append("Skills are required.")
        if not resume:
            errors.append("Resume is required.")
        if not experience:
            errors.append("Experience is required.")
        
        # Validate phone number specifically
        if phone:
            try:
                validate_phone_number(phone)
            except ValidationError as e:
                errors.append(f"Phone validation error: {e.message}")
        
        # Validate custom questions
        for question in custom_questions:
            if question.is_required:
                answer = request.POST.get(f'question_{question.id}')
                file_answer = request.FILES.get(f'question_{question.id}')
                
                if question.question_type == 'file':
                    if not file_answer:
                        errors.append(f"Question '{question.question_text}' is required.")
                else:
                    if not answer or not answer.strip():
                        errors.append(f"Question '{question.question_text}' is required.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'apply.html', {
                'job': job, 
                'custom_questions': custom_questions,
                'form_data': request.POST  # Pass back form data to preserve user input
            })

        try:
            # Create the application
            application = JobApplication.objects.create(
                job=job,
                applicant=request.user,
                name=name,
                email=email,
                phone=phone,
                skills=skills,
                qualifications=qualifications,
                resume=resume,
                experience=experience,
            )
            
            # Process custom questions (same as before)
            for question in custom_questions:
                if question.question_type == 'text':
                    answer = request.POST.get(f'question_{question.id}')
                    if answer:  # Only create if there's an answer
                        JobApplicationAnswer.objects.create(
                            application=application,
                            question=question,
                            text_answer=answer
                        )
                
                elif question.question_type == 'yesno':
                    answer_value = request.POST.get(f'question_{question.id}')
                    if answer_value:
                        boolean_answer = True if answer_value == 'True' else False
                        JobApplicationAnswer.objects.create(
                            application=application,
                            question=question,
                            boolean_answer=boolean_answer
                        )
                
                elif question.question_type == 'file':
                    file_answer = request.FILES.get(f'question_{question.id}')
                    if file_answer:
                        JobApplicationAnswer.objects.create(
                            application=application,
                            question=question,
                            file_answer=file_answer
                        )
                
                elif question.question_type == 'link':
                    link_answer = request.POST.get(f'question_{question.id}')
                    if link_answer:
                        JobApplicationAnswer.objects.create(
                            application=application,
                            question=question,
                            link_answer=link_answer
                        )

            messages.success(request, "Application submitted successfully.")
            return redirect('seeker_dashboard')
            
        except ValidationError as e:
            messages.error(request, f"Validation error: {str(e)}")
            return render(request, 'apply.html', {
                'job': job, 
                'custom_questions': custom_questions,
                'form_data': request.POST
            })

    return render(request, 'apply.html', {'job': job, 'custom_questions': custom_questions})
# User logout view
@login_required
def user_logout(request):
    logout(request)
    return redirect('home')
@login_required
def view_job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applications = JobApplication.objects.filter(job=job)
    
    # Get all query parameters
    skill_query = request.GET.get('skill', '')
    qualification_query = request.GET.get('qualification', '')
    date_query = request.GET.get('date', '')
    status_query = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-created_at')  # Default sort by newest
    
    # Apply filters
    if skill_query:
        applications = applications.filter(skills__icontains=skill_query)
    if qualification_query:
        applications = applications.filter(qualifications__icontains=qualification_query)
    if date_query:
        parsed_date = parse_date(date_query)
        if parsed_date:
            applications = applications.filter(created_at__date=parsed_date)
    if status_query:
        applications = applications.filter(status=status_query)
    
    # Apply sorting
    valid_sort_fields = ['name', '-name', 'created_at', '-created_at', 'status', '-status']
    
    if sort_by in valid_sort_fields:
        applications = applications.order_by(sort_by)
    else:
        applications = applications.order_by('-created_at')  # Default sorting
    
    # Process bulk actions if submitted
    if request.method == 'POST':
        action = request.POST.get('bulk_action')
        selected_ids = request.POST.getlist('selected_applications')
        
        if selected_ids and action:
            selected_applications = JobApplication.objects.filter(id__in=selected_ids)
            
            if action == 'delete':
                # Only allow deletion of rejected applications
                rejected_apps = selected_applications.filter(status='rejected')
                rejected_count = rejected_apps.count()
                rejected_apps.delete()
                if rejected_count > 0:
                    messages.success(request, f"{rejected_count} rejected application(s) have been deleted.")
                if rejected_count < len(selected_ids):
                    messages.warning(request, f"{len(selected_ids) - rejected_count} application(s) were not deleted because they are not rejected.")
            
            elif action in dict(JobApplication.STATUS_CHOICES):
                selected_applications.update(status=action)
                messages.success(request, f"Status updated for {len(selected_ids)} application(s).")
        
        return redirect('view_job_applications', job_id=job.id)
    
    # Unseen application popup
    unseen_applications = JobApplication.objects.filter(job=job, is_seen_by_provider=False)
    unseen_ids = list(unseen_applications.values_list('id', flat=True))
    unseen_count = len(unseen_ids)
    
    # Show notification if there are unseen applications
    if unseen_count > 0:
        messages.success(request, f"You have {unseen_count} new application(s)!")
    
    # Mark applications as seen after showing the notification
    unseen_applications.update(is_seen_by_provider=True)
    
    return render(request, 'view_job_applications.html', {
        'job': job,
        'applications': applications,
        'skill_query': skill_query,
        'qualification_query': qualification_query,
        'date_query': date_query,
        'status_query': status_query,
        'sort_by': sort_by,  # Pass the sort parameter to the template
        'status_choices': JobApplication.STATUS_CHOICES,
        'unseen_ids': unseen_ids,
    })

@require_POST
@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    status = request.POST.get('status')
    if status in dict(JobApplication.STATUS_CHOICES):
        application.status = status
        application.save()
        messages.success(request, "Application status updated successfully!")
    return redirect('view_job_applications', job_id=application.job.id)
@require_POST
@login_required
def bulk_update_applications(request):
    job_id = request.POST.get('job_id')
    job = get_object_or_404(Job, id=job_id)
    
    # Get selected applications and new status
    selected_ids = request.POST.getlist('selected_applications')
    new_status = request.POST.get('bulk_status')
    
    if selected_ids and new_status in dict(JobApplication.STATUS_CHOICES):
        # Update all selected applications
        updated_count = JobApplication.objects.filter(id__in=selected_ids).update(status=new_status)
        messages.success(request, f"Status updated for {updated_count} application(s).")
    else:
        messages.error(request, "No applications selected or invalid status.")
    
    return redirect('view_job_applications', job_id=job_id)
@login_required
def delete_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    
    if application.status == 'rejected':
        job_id = application.job.id  # capture job_id before deleting
        application.delete()
        messages.success(request, "Rejected application deleted successfully!")
        return redirect('view_job_applications', job_id=job_id)
    else:
        messages.error(request, "Only rejected applications can be deleted!")
        return redirect('view_job_applications', job_id=application.job.id)


# Delete a job view
@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job listing deleted successfully.')
    return redirect('view_jobs') 


class ViewJobsView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        jobs = Job.objects.filter(provider=request.user).order_by('-date_posted')
        
        if query:
            jobs = jobs.filter(
                Q(title__icontains=query) | 
                Q(location__icontains=query) |
                Q(description__icontains=query) |
                Q(company__icontains=query)
            )
        
        # Find jobs with new applications and add the count directly to job objects
        total_new_apps = 0
        
        for job in jobs:
            # Count unseen applications for each job
            new_apps_count = JobApplication.objects.filter(
                job=job, 
                is_seen_by_provider=False
            ).count()
            
            # Add the count as an attribute to the job object
            job.new_apps_count = new_apps_count
            
            if new_apps_count > 0:
                total_new_apps += new_apps_count
        
        # Add notification if there are new applications
        if total_new_apps > 0:
            messages.success(request, f"You have {total_new_apps} new application(s) across your job postings!")
            
        return render(request, 'view_jobs.html', {
            'jobs': jobs,
            'query': query,
        })
        
class ProviderDashboardView(View):
    def get(self, request):
        return render(request, 'provider_dashboard.html')
    
class AddJobView(View):
    def get(self, request):
        form = JobForm()
        question_formset = CustomQuestionFormSet()
        return render(request, 'add_job.html', {
            'form': form,
            'question_formset': question_formset
        })

    def post(self, request):
        form = JobForm(request.POST, request.FILES)
        
        if form.is_valid():
            with transaction.atomic():
                # Save the job first without committing to get an ID
                job = form.save(commit=False)
                job.provider = request.user
                job.save()
                
                # Process the custom questions formset
                question_formset = CustomQuestionFormSet(request.POST, request.FILES, instance=job)
                
                if question_formset.is_valid():
                    question_formset.save()
                    messages.success(request, 'Job posted successfully!')
                    return redirect('view_jobs')  # or change this to 'add_job'
                else:
                    # If formset is not valid, we need to display errors
                    # Since we're in a transaction, if we rollback here, the job won't be saved
                    job.delete()  # Delete the already saved job
        
        # If we get here, either form or formset is invalid
        question_formset = CustomQuestionFormSet(request.POST, request.FILES)
        return render(request, 'add_job.html', {
            'form': form,
            'question_formset': question_formset
        })

@login_required
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    today = timezone.now().date()
    # Check if this job is saved by the current user
    is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()
    
    return render(request, 'job_details.html', {
        'job': job,
        'is_saved': is_saved,
        'today': today,
    })
def extract_min_salary(salary_str):
    if salary_str:
        nums = re.findall(r'\d+', salary_str)
        return int(nums[0]) if nums else 0
    return 0

def search_jobs(request):
    q = request.GET.get('q', '')
    company = request.GET.get('company', '')
    location = request.GET.get('location', '')
    min_salary = request.GET.get('min_salary', '')
    job_type = request.GET.get('job_type', '')
    experience_level = request.GET.get('experience_level', '')
    posted_date = request.GET.get('posted_date', '')
    last_date_range = request.GET.get('last_date_range', '')
    remote_only = request.GET.get('remote')
    sort_by = request.GET.get('sort_by', 'newest')  # Default to newest first
    
    today = date.today()
    
    jobs = Job.objects.all()
    
    # Apply search filters
    if q:
        jobs = jobs.filter(title__icontains=q)
    if company:
        jobs = jobs.filter(company__icontains=company)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type__iexact=job_type)
    if experience_level:
        jobs = jobs.filter(experience_level__iexact=experience_level)
    
    if remote_only:
        jobs = jobs.filter(location__icontains='remote')
    
    # Filter by posted_date if provided
    if posted_date:
        try:
            posted_date_obj = datetime.strptime(posted_date, '%Y-%m-%d').date()
            jobs = jobs.filter(date_posted__date=posted_date_obj)
        except ValueError:
            posted_date = ''
    
    # Filter by last_date_range if provided - jobs that close within X days
    if last_date_range:
        try:
            days = int(last_date_range)
            cutoff = today + timedelta(days=days)
            # Filter for jobs where last_date_to_apply is between today and cutoff
            jobs = jobs.filter(
                last_date_to_apply__gte=today,  # Greater than or equal to today
                last_date_to_apply__lte=cutoff  # Less than or equal to cutoff (today + X days)
            )
        except ValueError:
            pass
    
    # Apply sorting before converting to list for salary filtering
    if sort_by == 'newest':
        jobs = jobs.order_by('-date_posted')  # Newest first (descending order)
    elif sort_by == 'oldest':
        jobs = jobs.order_by('date_posted')  # Oldest first
    elif sort_by == 'closing_soon':
        jobs = jobs.order_by('last_date_to_apply')  # Closing soon first
    
    # Apply salary filtering after ordering (this will convert to a list)
    if min_salary:
        try:
            min_salary_value = int(min_salary)
            jobs = [job for job in jobs if extract_min_salary(job.salary) >= min_salary_value]
        except ValueError:
            min_salary = ''
    
    # Handle saved jobs for authenticated users
    saved_job_ids = []
    if request.user.is_authenticated:
        saved_job_ids = SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True)
    
    context = {
        'jobs': jobs,
        'q': q,
        'company': company,
        'location': location,
        'min_salary': min_salary,
        'job_type': job_type,
        'experience_level': experience_level,
        'sort_by': sort_by,  # Add sort_by to context
        'today': today,
        'saved_job_ids': saved_job_ids,
    }
    return render(request, 'seeker_dashboard.html', context)

@login_required
def my_applications(request):
    # Get all applications for the current user
    unseen_applications = JobApplication.objects.filter(
        applicant=request.user, 
        is_seen_by_seeker=False
    ).order_by('-created_at')
    
    seen_applications = JobApplication.objects.filter(
        applicant=request.user, 
        is_seen_by_seeker=True
    ).order_by('-created_at')
    
    # Count unseen applications for nav badge BEFORE any processing
    unseen_count = unseen_applications.count()
    
    # Combine both querysets using lists to preserve the is_seen_by_seeker value
    all_applications = list(unseen_applications) + list(seen_applications)
    
    # Handle search query
    search_query = request.GET.get('q', '')
    status_query = request.GET.get('status', '')
    
    # Filter applications if search parameters are present
    if search_query or status_query:
        filtered_applications = []
        for app in all_applications:
            matches_search = (search_query == '' or
                           search_query.lower() in app.job.title.lower() or
                           search_query.lower() in app.job.company.lower() or
                           search_query.lower() in app.job.location.lower())
            
            matches_status = (status_query == '' or app.status == status_query)
            
            if matches_search and matches_status:
                filtered_applications.append(app)
        applications = filtered_applications
    else:
        applications = all_applications
    
    # Only mark as seen if not searching/filtering
    if not search_query and not status_query:
        # Important: Mark applications as seen AFTER we've prepared the list for display
        # This way the template still sees them as unseen
        for app in unseen_applications:
            # Create a copy for database update, but don't modify our display objects
            app.is_seen_by_seeker = True
            app.save()
    
    return render(request, 'my_applications.html', {
        'applications': applications,
        'search_query': search_query,
        'status_query': status_query,
        'status_choices': JobApplication.STATUS_CHOICES,
        'unseen_count': unseen_count,  # Pass the count we calculated early on
    })

@login_required
def toggle_bookmark(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    
    if not created:
        # If it already existed, the user is unbookmarking it
        saved_job.delete()
        messages.success(request, f"'{job.title}' removed from your saved jobs.")
    else:
        messages.success(request, f"'{job.title}' saved to your bookmarks.")
    
    # Redirect back to the page where the user was
    return redirect(request.META.get('HTTP_REFERER', 'seeker_dashboard'))

@login_required
def saved_jobs(request):
    bookmarks = SavedJob.objects.filter(user=request.user).order_by('-saved_at')
    today = timezone.now().date()
    # Handle search query
    search_query = request.GET.get('q', '')
    if search_query:
        bookmarks = bookmarks.filter(
            models.Q(job__title__icontains=search_query) |
            models.Q(job__company__icontains=search_query) |
            models.Q(job__location__icontains=search_query)
        )
    
    return render(request, 'saved_jobs.html', {
        'bookmarks': bookmarks,
        'search_query': search_query,
        'today':today
    })

@login_required
def edit_job(request, job_id):
    # Get the job object or return 404 if not found
    job = get_object_or_404(Job, id=job_id, provider=request.user)
    
    if request.method == 'POST':
        # Create a form instance with POST data and files (for logo)
        form = JobForm(request.POST, request.FILES, instance=job)
        question_formset = CustomQuestionFormSet(request.POST, request.FILES, instance=job)
        
        if form.is_valid() and question_formset.is_valid():
            with transaction.atomic():
                # Save the job details
                job_obj = form.save()
                
                # Save custom questions
                question_formset.save()
                
                # Update has_custom_questions flag based on whether there are any questions
                has_questions = job.custom_questions.filter(question_text__isnull=False).exists()
                job.has_custom_questions = has_questions
                job.save()
                
                messages.success(request, 'Job updated successfully!')
                return redirect('view_jobs')
    else:
        # Create a form pre-filled with the job data
        form = JobForm(instance=job)
        question_formset = CustomQuestionFormSet(instance=job)
    
    return render(request, 'edit_job.html', {
        'form': form, 
        'job': job,
        'question_formset': question_formset
    })

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from .models import Job, JobSeeker
@login_required
def recommended_jobs(request):
    try:
        # Get JobSeeker profile
        job_seeker = JobSeeker.objects.get(user_profile__user=request.user)

        # Extract and clean skills
        seeker_skills = [skill.strip().lower() for skill in job_seeker.skills.split(',') if skill.strip()] if job_seeker.skills else []

        # Extract and clean location preferences
        seeker_locations = []
        if job_seeker.location_preferences:
            seeker_locations = [loc.strip().lower() for loc in job_seeker.location_preferences.split(',') if loc.strip()]

        # Add location keywords from address (fallback)
        if job_seeker.address:
            address_words = job_seeker.address.lower().split()
            for word in address_words:
                if len(word) > 3 and word.lower() not in seeker_locations:
                    seeker_locations.append(word.lower())

        # If both skills and locations are empty, show error
        if not seeker_skills and not seeker_locations:
            return render(request, 'recommended_jobs.html', {
                'error': 'No skills or location preferences found in your profile.',
                'job_seeker': job_seeker
            })

        # Determine experience level
        experience_level = "Fresher"
        if job_seeker.experience_years:
            if job_seeker.experience_years >= 5:
                experience_level = "Senior"
            elif job_seeker.experience_years >= 2:
                experience_level = "Mid-level"

        # Get current date
        today = date.today()
        
        # Get all active jobs (exclude closed jobs based on last_date_to_apply)
        all_jobs = Job.objects.filter(
            models.Q(last_date_to_apply__isnull=True) | models.Q(last_date_to_apply__gte=today)
        ).order_by('-date_posted')
        
        # Get jobs that the user has already applied for
        applied_job_ids = JobApplication.objects.filter(applicant=request.user).values_list('job_id', flat=True)
        
        # Filter manually to ensure proper matching
        recommended_jobs = []
        
        for job in all_jobs:
            # Skip jobs that the user has already applied for
            if job.id in applied_job_ids:
                continue
                
            # Check for skill matches
            job_skills = [skill.strip().lower() for skill in job.skills.split(',')] if job.skills else []
            has_skill_match = False
            matched_skills = []
            
            for seeker_skill in seeker_skills:
                for job_skill in job_skills:
                    if seeker_skill in job_skill or job_skill in seeker_skill:
                        has_skill_match = True
                        if seeker_skill not in matched_skills:
                            matched_skills.append(seeker_skill)
            
            # Check for location matches
            job_location_lower = job.location.lower() if job.location else ""
            has_location_match = False
            matched_locations = []
            
            for location in seeker_locations:
                if location in job_location_lower:
                    has_location_match = True
                    matched_locations.append(location)
            
            # Check for experience level match
            has_exp_match = (job.experience_level == experience_level)
            
            # Only include job if it matches at least ONE criteria
            # AND it has at least one matched skill or location
            if (has_skill_match or has_location_match or has_exp_match) and (matched_skills or matched_locations):
                recommended_jobs.append({
                    'job': job,
                    'matched_skills': matched_skills,
                    'matched_locations': matched_locations
                })

        # If no matches at all
        if not recommended_jobs:
            return render(request, 'recommended_jobs.html', {
                'error': 'No matching jobs found based on your skills or location preferences.',
                'job_seeker': job_seeker
            })

        # Get saved job IDs
        saved_job_ids = []
        if hasattr(job_seeker, 'saved_jobs'):
            saved_job_ids = job_seeker.saved_jobs.values_list('id', flat=True)

        context = {
            'jobs_with_matches': recommended_jobs,
            'saved_job_ids': saved_job_ids,
            'job_seeker': job_seeker
        }

        return render(request, 'recommended_jobs.html', context)

    except JobSeeker.DoesNotExist:
        return render(request, 'recommended_jobs.html', {
            'error': 'Please complete your profile to get job recommendations.'
        })
@login_required
def export_job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applications = JobApplication.objects.filter(job=job)
    
    # Apply the same filters as in the view
    skill_query = request.GET.get('skill', '')
    qualification_query = request.GET.get('qualification', '')
    date_query = request.GET.get('date', '')
    status_query = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Apply filters
    if skill_query:
        applications = applications.filter(skills__icontains=skill_query)
    if qualification_query:
        applications = applications.filter(qualifications__icontains=qualification_query)
    if date_query:
        parsed_date = parse_date(date_query)
        if parsed_date:
            applications = applications.filter(created_at__date=parsed_date)
    if status_query:
        applications = applications.filter(status=status_query)
    
    # Apply sorting
    valid_sort_fields = ['name', '-name', 'created_at', '-created_at', 'status', '-status']
    if sort_by in valid_sort_fields:
        applications = applications.order_by(sort_by)
    else:
        applications = applications.order_by('-created_at')
    
    # Create a workbook and add a worksheet
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet(f'Applications - {job.title}')
    
    # Sheet header with job information
    title_style = xlwt.easyxf('font: bold on, height 280; align: wrap on, vert centre, horiz center')
    worksheet.write_merge(0, 0, 0, 10, f'Job Applications for: {job.title}', title_style)
    
    # Add date and filter information
    date_style = xlwt.easyxf('font: height 180; align: wrap on, vert centre, horiz right')
    worksheet.write_merge(1, 1, 8, 10, f'Generated on: {datetime.now().strftime("%d %b %Y, %H:%M")}', date_style)
    
    filter_info = []
    if skill_query:
        filter_info.append(f"Skills: {skill_query}")
    if qualification_query:
        filter_info.append(f"Qualification: {qualification_query}")
    if status_query:
        status_display = dict(JobApplication.STATUS_CHOICES).get(status_query, status_query)
        filter_info.append(f"Status: {status_display}")
    if date_query:
        filter_info.append(f"Date: {date_query}")
        
    if filter_info:
        filter_style = xlwt.easyxf('font: italic on; align: wrap on, vert centre, horiz left')
        worksheet.write_merge(2, 2, 0, 10, f'Filters applied: {", ".join(filter_info)}', filter_style)
    
    # Column headers
    header_style = xlwt.easyxf(
        'font: bold on, color white, height 200; '
        'pattern: pattern solid, fore_colour dark_blue; '
        'align: wrap on, vert centre, horiz center'
    )
    columns = ['Name', 'Email', 'Phone', 'Skills', 'Qualification', 'Experience', 'Status', 'Applied On', 'Resume']
    
    row_offset = 4  # Start data rows after headers with filter info
    
    for col_num, column_title in enumerate(columns):
        worksheet.write(row_offset-1, col_num, column_title, header_style)
        worksheet.col(col_num).width = 5500  # Set column width
    
    # Sheet body
    row_num = row_offset
    font_style = xlwt.easyxf('align: wrap on, vert centre')
    link_style = xlwt.easyxf('font: color blue, underline single; align: wrap on, vert centre')
    
    # Get all custom questions for this job
    custom_questions = JobCustomQuestion.objects.filter(job=job)
    
    # If there are custom questions, add them as additional columns
    if custom_questions.exists():
        worksheet.col(10).width = 2000
        
        # Add custom question columns
        q_col_start = 9
        for idx, question in enumerate(custom_questions):
            col_num = q_col_start + idx
            worksheet.write(row_offset-1, col_num, f"Q: {question.question_text}", header_style)
            worksheet.col(col_num).width = 7500  # Set wider column width for questions/answers
    
    # Color styles for different statuses
    status_styles = {
        'pending': xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow; align: wrap on, vert centre'),
        'shortlisted': xlwt.easyxf('pattern: pattern solid, fore_colour light_green; align: wrap on, vert centre'),
        'interview': xlwt.easyxf('pattern: pattern solid, fore_colour light_blue; align: wrap on, vert centre'),
        'rejected': xlwt.easyxf('pattern: pattern solid, fore_colour rose; align: wrap on, vert centre'),
        'hired': xlwt.easyxf('pattern: pattern solid, fore_colour bright_green; align: wrap on, vert centre'),
    }
    
    # Now populate the data
    for application in applications:
        # Choose style based on status
        current_style = status_styles.get(application.status, font_style)
        
        worksheet.write(row_num, 0, application.name, current_style)
        worksheet.write(row_num, 1, application.email, current_style)
        worksheet.write(row_num, 2, application.phone, current_style)
        worksheet.write(row_num, 3, application.skills, current_style)
        worksheet.write(row_num, 4, application.qualifications, current_style)
        worksheet.write(row_num, 5, application.experience, current_style)
        worksheet.write(row_num, 6, application.get_status_display(), current_style)
        worksheet.write(row_num, 7, application.created_at.strftime("%d %b %Y, %H:%M"), current_style)
        
        if application.resume:
            resume_url = request.build_absolute_uri(application.resume.url)
            worksheet.write(row_num, 8, xlwt.Formula(f'HYPERLINK("{resume_url}";"View Resume")'), link_style)
        else:
            worksheet.write(row_num, 8, "No resume", current_style)
        
        # Add the custom question answers
        if custom_questions.exists():
            # Skip the separator column
            q_col_start = 9
            
            for idx, question in enumerate(custom_questions):
                col_num = q_col_start + idx
                
                # Try to find the answer for this question
                try:
                    answer = JobApplicationAnswer.objects.get(application=application, question=question)
                    
                    # Format the answer based on question type
                    if question.question_type == 'text':
                        answer_text = answer.text_answer or "N/A"
                        worksheet.write(row_num, col_num, answer_text, current_style)
                    elif question.question_type == 'yesno':
                        answer_text = "Yes" if answer.boolean_answer else "No"
                        worksheet.write(row_num, col_num, answer_text, current_style)
                    elif question.question_type == 'file':
                        if answer.file_answer:
                            file_url = request.build_absolute_uri(answer.file_answer.url)
                            worksheet.write(row_num, col_num, xlwt.Formula(f'HYPERLINK("{file_url}";"Download File")'), link_style)
                        else:
                            worksheet.write(row_num, col_num, "No file uploaded", current_style)
                    elif question.question_type == 'link':
                        if answer.link_answer:
                            worksheet.write(row_num, col_num, xlwt.Formula(f'HYPERLINK("{answer.link_answer}";"View Link")'), link_style)
                        else:
                            worksheet.write(row_num, col_num, "No link provided", current_style)
                    else:
                        worksheet.write(row_num, col_num, "Unknown answer type", current_style)
                        
                except JobApplicationAnswer.DoesNotExist:
                    worksheet.write(row_num, col_num, "Not answered", current_style)
                
        row_num += 1
    
    # Create HTTP response with filter indicators in filename
    filename_parts = [job.title]
    if status_query:
        filename_parts.append(dict(JobApplication.STATUS_CHOICES).get(status_query, status_query))
    filename = f"{'_'.join(filename_parts)}_applications_{datetime.now().strftime('%Y%m%d')}.xls"
    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    workbook.save(response)

    return response

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent logging out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('seeker_profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {
        'form': form
    })

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user  # Save the user object before logout
        logout(request)      # Log the user out first (clears session)
        user.delete()        # Now delete the user from DB
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('home')

    return redirect('seeker_profile')
@login_required
def provider_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent logging out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('edit_company_profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'provider_change_password.html', {
        'form': form
    })

@login_required
def provider_delete_account(request):
    if request.method == 'POST':
        user = request.user  # Save the user object before logout
        logout(request)      # Log the user out first (clears session)
        user.delete()        # Now delete the user from DB
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('home')

    return redirect('edit_company_profile')


logger = logging.getLogger(__name__)

APP_ID = 'a85ff09d'
APP_KEY = 'e2e9029fc58f76be06e317d85018ab1a'

def fetch_adzuna_jobs(keyword="developer", location="India", results=10):
    """Fetch jobs from Adzuna API with error handling"""
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": keyword,
        "where": location,
        "results_per_page": min(results, 50),  # API limit is 50
        "content-type": "application/json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        jobs = data.get("results", [])
        
        print(f"API Response: Found {len(jobs)} jobs")  # Debug log
        print(f"API URL: {response.url}")  # Debug log
        
        # Clean and format job data
        formatted_jobs = []
        for job in jobs:
            # Handle missing company info
            if not job.get('company'):
                job['company'] = {'display_name': 'Company Not Specified'}
            elif isinstance(job.get('company'), dict) and not job['company'].get('display_name'):
                job['company']['display_name'] = 'Company Not Specified'
            
            # Handle missing location info
            if not job.get('location'):
                job['location'] = {'display_name': 'Location Not Specified'}
            elif isinstance(job.get('location'), dict) and not job['location'].get('display_name'):
                job['location']['display_name'] = 'Location Not Specified'
            
            # Format salary values - make them more readable
            if job.get('salary_min'):
                try:
                    job['salary_min'] = float(job['salary_min'])
                except (ValueError, TypeError):
                    job['salary_min'] = None
            if job.get('salary_max'):
                try:
                    job['salary_max'] = float(job['salary_max'])
                except (ValueError, TypeError):
                    job['salary_max'] = None
            
            # Clean description HTML and limit length
            if job.get('description'):
                import re
                # Remove HTML tags
                description = re.sub(r'<[^>]+>', '', job['description'])
                # Clean up extra whitespace
                description = ' '.join(description.split())
                job['description'] = description
            
            formatted_jobs.append(job)
        
        return formatted_jobs, None
    
    except requests.exceptions.Timeout:
        error_msg = "Request timed out. Please try again."
        logger.error(f"Adzuna API timeout: {error_msg}")
        return [], error_msg
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: Unable to fetch external jobs."
        logger.error(f"Adzuna API error: {str(e)}")
        return [], error_msg
    
    except ValueError as e:
        error_msg = "Invalid response from job service."
        logger.error(f"Adzuna API JSON error: {str(e)}")
        return [], error_msg
    
    except Exception as e:
        error_msg = "An unexpected error occurred."
        logger.error(f"Adzuna API unexpected error: {str(e)}")
        return [], error_msg

def external_jobs_view(request):
    """View for displaying external jobs from Adzuna"""
    
    # Get filter parameters with better defaults
    keyword = request.GET.get('keyword', '').strip()
    location = request.GET.get('location', '').strip()
    results_per_page = request.GET.get('results_per_page', '20')
    
    # Set defaults if empty
    if not keyword:
        keyword = 'software'  # More generic term
    if not location:  
        location = 'India'
    
    # Validate results_per_page
    try:
        results_per_page = int(results_per_page)
        results_per_page = min(max(results_per_page, 5), 50)  # Between 5 and 50
    except (ValueError, TypeError):
        results_per_page = 20
    
    context = {
        'loading': False,
        'error': None,
        'jobs': [],
        'search_keyword': keyword,
        'search_location': location,
        'search_results_per_page': results_per_page,
    }
    
    try:
        # Fetch jobs from Adzuna
        jobs, error = fetch_adzuna_jobs(
            keyword=keyword,
            location=location,
            results=results_per_page
        )
        
        if error:
            context['error'] = error
            messages.error(request, f"Could not load external jobs: {error}")
        elif jobs:
            context['jobs'] = jobs
            messages.success(request, f"Found {len(jobs)} external job opportunities!")
        else:
            messages.info(request, "No external jobs found for your search criteria. Try different keywords.")
        
        context['loading'] = False
    
    except Exception as e:
        logger.error(f"External jobs view error: {str(e)}")
        context['error'] = "Unable to load external jobs at this time."
        context['loading'] = False
        messages.error(request, "Unable to load external jobs. Please try again later.")
    
    return render(request, "external_jobs.html", context)

# Add a utility function to get popular job searches
def get_popular_searches():
    """Return popular job search terms for suggestions"""
    return [
        "Software Engineer",
        "Data Scientist", 
        "Product Manager",
        "Full Stack Developer",
        "DevOps Engineer",
        "UI/UX Designer",
        "Business Analyst",
        "Digital Marketing",
        "Python Developer",
        "Java Developer",
        "React Developer",
        "Marketing Manager",
    ]

# Add location suggestions
def get_popular_locations():
    """Return popular location searches"""
    return [
        "Bangalore",
        "Mumbai", 
        "Delhi",
        "Hyderabad",
        "Chennai",
        "Pune",
        "Gurgaon",
        "Noida",
        "Kolkata",
        "Remote",
    ]