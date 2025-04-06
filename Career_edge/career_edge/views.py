from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfile, Job, JobApplication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View

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

# User registration view for seekers
def user_register_seeker(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = User.objects.filter(username=username).first()
        if user:
            return render(request, 'register_seeker.html', {'error': 'Username already exists.'})
        
        user = User.objects.create_user(username=username, password=password)
        profile, created = UserProfile.objects.get_or_create(user=user, role='seeker')
        
        return redirect('user_login')
    
    return render(request, 'register_seeker.html')

# User registration view for providers
def user_register_provider(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = User.objects.filter(username=username).first()
        if user:
            return render(request, 'register_provider.html', {'error': 'Username already exists.'})
        
        user = User.objects.create_user(username=username, password=password)
        profile, created = UserProfile.objects.get_or_create(user=user, role='provider')
        
        return redirect('user_login')
    
    return render(request, 'register_provider.html')

# Seeker dashboard view
@login_required
def seeker_dashboard(request):
    jobs = Job.objects.all()
    return render(request, 'seeker_dashboard.html', {'jobs': jobs})

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
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        skills = request.POST.get('skills')
        qualification = request.POST.get('qualification')
        resume = request.FILES.get('resume')
        
        JobApplication.objects.create(
            job=job,
            applicant=request.user,
            name=name,
            email=email,
            phone=phone,
            skills=skills,
            qualification=qualification,
            resume=resume
        )
        return redirect('seeker_dashboard')
    
    return render(request, 'apply.html', {'job': job})

# User logout view
@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

# View applications for a job
@login_required
def view_job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applications = JobApplication.objects.filter(job=job)
    return render(request, 'view_job_applications.html', {'job': job, 'applications': applications})

# Delete a job view
@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)

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
        return render(request, 'provider_dashboard.html')

# Class-based view to add a job
class AddJobView(View):
    def get(self, request):
        return render(request, 'add_job.html')

    def post(self, request):
        title = request.POST.get('title')
        description = request.POST.get('description')
        company = request.POST.get('company')
        location = request.POST.get('location')
        skills = request.POST.get('skills')  # Ensure skills are captured
        salary = request.POST.get('salary') 

        Job.objects.create(
            title=title,
            description=description,
            company=company,
            location=location,
            provider=request.user,
            skills=skills,  # Save skills to the Job object
            salary=salary, 
        )
        messages.success(request, 'Job listing added successfully.')
        return redirect('view_jobs')
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'job_details.html', {'job': job})
def search_jobs(request):
    # Logic to handle job search
    # Example: retrieve search query and filter jobs accordingly
    query = request.GET.get('q', '')
    jobs = Job.objects.filter(title__icontains=query)

    context = {
        'jobs': jobs,
    }
    return render(request, 'seeker_dashboard.html', context)