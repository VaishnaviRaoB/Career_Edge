from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfile, Job, JobApplication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .forms import EditCompanyProfileForm
from django.utils.dateparse import parse_date
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import UserProfile, JobSeeker, JobProvider,SavedJob
from .forms import JobForm
import re
from django.views.decorators.http import require_POST
from django.urls import reverse
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

def user_register_seeker(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'register_seeker.html', {'error': 'All fields are required.'})

        if not validate_password(password):
            return render(request, 'register_seeker.html', {
                'error': 'Password must be at least 8 characters long and include a letter, number, and special character.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'register_seeker.html', {'error': 'Username already exists.'})

        user = User.objects.create_user(username=username, password=password)
        profile = UserProfile.objects.create(user=user, role='seeker')
        JobSeeker.objects.create(
    user_profile=profile,
    full_name=username,  # default placeholder
    skills='Not provided yet',   # default placeholder
    experience_years=None        # okay to leave empty
)

        return redirect('user_login')

    return render(request, 'register_seeker.html')


def user_register_provider(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'register_provider.html', {'error': 'All fields are required.'})

        if not validate_password(password):
            return render(request, 'register_provider.html', {
                'error': 'Password must be at least 8 characters long and include a letter, number, and special character.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'register_provider.html', {'error': 'Username already exists.'})

        user = User.objects.create_user(username=username, password=password)
        profile = UserProfile.objects.create(user=user, role='provider')
        JobProvider.objects.create(user_profile=profile)

        return redirect('user_login')

    return render(request, 'register_provider.html')
from django.contrib import messages

def edit_company_profile(request):
    provider = JobProvider.objects.get(user_profile__user=request.user)
    updated = False

    if request.method == 'POST':
        form = EditCompanyProfileForm(request.POST, request.FILES, instance=provider)
        if form.is_valid():
            form.save()
            updated = True  # Set flag to show message
    else:
        form = EditCompanyProfileForm(instance=provider)

    return render(request, 'edit_company_profile.html', {'form': form, 'updated': updated})
# Seeker dashboard view
@login_required
def seeker_dashboard(request):
    jobs = Job.objects.all()
    
    # Get IDs of jobs saved by the current user
    saved_job_ids = SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True)
    
    return render(request, 'seeker_dashboard.html', {
        'jobs': jobs,
        'saved_job_ids': saved_job_ids
    })
# Provider dashboard view
@login_required
def provider_dashboard(request):
    return render(request, 'provider_dashboard.html')

# View jobs posted by a provider
@login_required
def view_jobs(request):
    jobs = Job.objects.filter(provider=request.user)
    return render(request, 'view_jobs.html', {'jobs': jobs})

# Apply for a job view
@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Check if the user has already applied to this job
    already_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()

    if already_applied:
        messages.warning(request, "You have already applied for this job.")
        return redirect('seeker_dashboard')  # or show the same apply page with a message

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        skills = request.POST.get('skills')
        qualifications = request.POST.get('qualification')
        resume = request.FILES.get('resume')
        experience = request.POST.get('experience')

        JobApplication.objects.create(
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
        messages.success(request, "Application submitted successfully.")
        return redirect('seeker_dashboard')

    return render(request, 'apply.html', {'job': job})
# User logout view
@login_required
def user_logout(request):
    logout(request)
    return redirect('home')
@login_required
def view_job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applications = JobApplication.objects.filter(job=job)

    skill_query = request.GET.get('skill', '')
    qualification_query = request.GET.get('qualification', '')
    date_query = request.GET.get('date', '')

    if skill_query:
        applications = applications.filter(skills__icontains=skill_query)
    if qualification_query:
        applications = applications.filter(qualifications__icontains=qualification_query)
    if date_query:
        parsed_date = parse_date(date_query)
        if parsed_date:
            applications = applications.filter(created_at__date=parsed_date)

    return render(request, 'view_job_applications.html', {
        'job': job,
        'applications': applications,
        'skill_query': skill_query,
        'qualification_query': qualification_query,
        'date_query': date_query,
        'STATUS_CHOICES': JobApplication.STATUS_CHOICES,
    })
@require_POST
@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    status = request.POST.get('status')
    if status in dict(JobApplication.STATUS_CHOICES):
        application.status = status
        application.save()
    return redirect('view_job_applications', job_id=application.job.id)
# Delete a job view
@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job listing deleted successfully.')
    return redirect('view_jobs') 
# Class-based view to view jobs for a provider
class ViewJobsView(View):
    def get(self, request):
        jobs = Job.objects.filter(provider=request.user)
        return render(request, 'view_jobs.html', {'jobs': jobs})

# Class-based view for the provider dashboard
class ProviderDashboardView(View):
    def get(self, request):
        return render(request, 'provider_dashboard.html')# views.py
class AddJobView(View):
    def get(self, request):
        form = JobForm()
        return render(request, 'add_job.html', {'form': form})

    def post(self, request):
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.provider = request.user
            job.save()
            return redirect('view_jobs')  # or change this to 'add_job'
        return render(request, 'add_job.html', {'form': form})

@login_required
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if this job is saved by the current user
    is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()
    
    return render(request, 'job_details.html', {
        'job': job,
        'is_saved': is_saved
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


    jobs = Job.objects.all()

    if q:
        jobs = jobs.filter(title__icontains=q)
    if company:
        jobs = jobs.filter(company__icontains=company)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if min_salary:
        try:
            min_salary = int(min_salary)
            jobs = [job for job in jobs if extract_min_salary(job.salary) >= min_salary]
        except ValueError:
            min_salary = ''
    if job_type:
        jobs = jobs.filter(job_type__iexact=job_type)
    if experience_level:
        jobs = jobs.filter(experience_level__iexact=experience_level)
    if posted_date:
        try:
         from datetime import datetime
         posted_date_obj = datetime.strptime(posted_date, '%Y-%m-%d').date()
         jobs = jobs.filter(date_posted__date=posted_date_obj)
        except ValueError:
         posted_date = ''
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
        'posted_date': posted_date,
        'saved_job_ids': saved_job_ids,
    }
    return render(request, 'seeker_dashboard.html', context)

@login_required
def my_applications(request):
    # Get all applications for the current user
    applications = JobApplication.objects.filter(applicant=request.user).order_by('-created_at')
    
    return render(request, 'my_applications.html', {
        'applications': applications,
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
    return render(request, 'saved_jobs.html', {'bookmarks': bookmarks})