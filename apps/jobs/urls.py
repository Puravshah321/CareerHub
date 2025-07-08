from django.urls import path
from . import views
from .views import gen_resume
from django.contrib import admin


app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('resume/', views.gen_resume, name = 'resume'),
    path('index/', views.index_view, name='index'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/post/', views.post_job, name='post_job'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('categories/', views.categories, name='categories'),
    path('companies/', views.companies, name='companies'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    #path('', views.index_view, name='index'),
    path("admin/", admin.site.urls),
   path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/job/edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path('employer/job/withdraw/<int:job_id>/', views.withdraw_job, name='withdraw_job'),
]