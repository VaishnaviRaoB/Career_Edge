from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import ProviderDashboardView, AddJobView, ViewJobsView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.user_login, name='user_login'),
    path('register/seeker/', views.user_register_seeker, name='user_register_seeker'),
    path('register/provider/', views.user_register_provider, name='user_register_provider'),
    path('dashboard/seeker/', views.seeker_dashboard, name='seeker_dashboard'),
    path('dashboard/provider/', views.provider_dashboard, name='provider_dashboard'),
    path('logout/', views.user_logout, name='user_logout'),
    path('apply/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    path('dashboard/provider/job/<int:job_id>/applications/', views.view_job_applications, name='view_job_applications'),
    path('delete_job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('provider/add-job/', AddJobView.as_view(), name='add_job'),
    path('provider/view-jobs/', ViewJobsView.as_view(), name='view_jobs'),
    path('provider/dashboard/', ProviderDashboardView.as_view(), name='provider_dashboard'),
    path('job/<int:job_id>/', views.job_details, name='job_details'),
    path('search/', views.search_jobs, name='search_jobs'),
    path('dashboard/provider/application/<int:application_id>/update_status/', views.update_application_status, name='update_application_status'),
    path('edit-company-profile/', views.edit_company_profile, name='edit_company_profile'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('job/bookmark/<int:job_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
    path('jobs/edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path('seeker/profile/', views.seeker_profile, name='seeker_profile'),
    path('recommended-jobs/', views.recommended_jobs, name='recommended_jobs'),
    path('export-applications/<int:job_id>/', views.export_job_applications, name='export_job_applications'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

