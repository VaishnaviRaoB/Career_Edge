# career_edge/urls.py

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
 

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from . import views

