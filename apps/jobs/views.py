from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Job, Application, Category
from .forms import JobForm, JobApplicationForm, JobSearchForm, JobPostForm
from django.shortcuts import render
from .models import Category
from apps.accounts.models import Employer
from datetime import datetime, timedelta
import calendar
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Job, Category
from .forms import JobSearchForm


def companies(request):
    companies = Employer.objects.all()
    return render(request, 'jobs/companies.html', {'companies': companies})
def home(request):
    featured_jobs = Job.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()
    context = {
        'featured_jobs': featured_jobs,
        'categories': categories,
    }
    return render(request, 'jobs/home.html', context)   

def job_list(request):
    form = JobSearchForm(request.GET or None)
    jobs = Job.objects.filter(is_active=True)
    categories = Category.objects.all()

    if request.GET:
        search = request.GET.get('search')
        location = request.GET.get('location')
        category = request.GET.get('category')
        job_type = request.GET.get('job_type')
        posted_date = request.GET.get('posted_date')

        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        if location:
            jobs = jobs.filter(location__icontains=location)
        if category:
            jobs = jobs.filter(category=category)
        if job_type:
            jobs = jobs.filter(job_type=job_type)

        # Timezone-aware posted date filtering
        now = timezone.now()
        today = now.date()

        if posted_date == "today":
            start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
            end_of_day = timezone.make_aware(datetime.combine(today, datetime.max.time()))
            jobs = jobs.filter(posted_date__range=(start_of_day, end_of_day))

        elif posted_date == "this_week":
            start_of_week = timezone.make_aware(datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time()))
            end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
            jobs = jobs.filter(posted_date__range=(start_of_week, end_of_week))

        elif posted_date == "this_month":
            start_of_month = timezone.make_aware(datetime.combine(today.replace(day=1), datetime.min.time()))
            next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
            end_of_month = timezone.make_aware(datetime.combine(next_month - timedelta(days=1), datetime.max.time()))
            jobs = jobs.filter(posted_date__range=(start_of_month, end_of_month))

        elif posted_date == "last_month":
            first_day_this_month = today.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            first_day_last_month = last_day_last_month.replace(day=1)
            start = timezone.make_aware(datetime.combine(first_day_last_month, datetime.min.time()))
            end = timezone.make_aware(datetime.combine(last_day_last_month, datetime.max.time()))
            jobs = jobs.filter(posted_date__range=(start, end))

    paginator = Paginator(jobs, 9)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    context = {
        'jobs': jobs,
        'form': form,
        'categories': categories,
        'query_string': request.GET.urlencode(),
    }
    return render(request, 'jobs/job_list.html', context)



def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    application_form = JobApplicationForm() if request.user.is_authenticated else None
    has_applied = False

    if request.user.is_authenticated and hasattr(request.user, 'jobseeker'):
        has_applied = Application.objects.filter(
            job=job, job_seeker=request.user.jobseeker
        ).exists()

    context = {
        'job': job,
        'application_form': application_form,
        'has_applied': has_applied,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def post_job(request):
    if not hasattr(request.user, 'employer'):
        return redirect('home')
    
    if not request.user.is_employer:
        return HttpResponseForbidden("You are not allowed to post jobs.")
        
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user.employer
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobForm()

    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
def apply_job(request, job_id):
    if not request.user.is_job_seeker:
        messages.error(request, "Only job seekers can apply for jobs.")
        return redirect('jobs:job_detail', job_id=job_id)

    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    if Application.objects.filter(job=job, job_seeker=request.user.jobseeker).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect('jobs:job_detail', job_id=job_id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.job_seeker = request.user.jobseeker
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('jobs:job_detail', job_id=job_id)

    return redirect('jobs:job_detail', job_id=job_id)

def search_jobs(request):
    form = JobSearchForm(request.GET)
    jobs = Job.objects.filter(is_active=True)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        location = form.cleaned_data.get('location')
        category = form.cleaned_data.get('category')
        job_type = form.cleaned_data.get('job_type')

        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        if location:
            jobs = jobs.filter(location__icontains=location)
        if category:
            jobs = jobs.filter(category=category)
        if job_type:
            jobs = jobs.filter(job_type=job_type)

    paginator = Paginator(jobs, 9)  # 9 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    context = {
        'jobs': jobs,
        'form': form,
    }
    return render(request, 'jobs/search_results.html', context)

def categories(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'jobs/categories.html', context)

def company_detail(request, pk):
    company = get_object_or_404(Employer, pk=pk)
    active_jobs = Job.objects.filter(employer=company, is_active=True)
    
    context = {
        'company': company,
        'active_jobs': active_jobs,
    }
    return render(request, 'jobs/company_detail.html', context)


def jobs(request):
    return render(request, 'index.html')

def gen_resume(request):
    if request.method == 'POST':
        context = {
            'name': request.POST.get('name', ''),
            'about': request.POST.get('about', ''),
            'age': request.POST.get('age', ''),
            'email': request.POST.get('email', ''),
            'phone': request.POST.get('phone', ''),
            'education': [],
            'projects': [],
            'experience': [],
            'skills': [],
            'languages': [],
            'achievements': request.POST.getlist('achievement[]'),
        }

        # Education
        for degree, college, year in zip(
            request.POST.getlist('degree[]'),
            request.POST.getlist('college[]'),
            request.POST.getlist('year[]')
        ):
            context['education'].append({'degree': degree, 'college': college, 'year': year})

        # Projects
        for title, duration in zip(
            request.POST.getlist('project_title[]'),
            request.POST.getlist('project_duration[]')
        ):
            context['projects'].append({'title': title, 'duration': duration})

        # Experience
        for company, dur, desc in zip(
            request.POST.getlist('company[]'),
            # request.POST.getlist('post[]'),
            request.POST.getlist('exp_duration[]'),
            request.POST.getlist('exp_desc[]')
        ):
            context['experience'].append({
                'company': company, 'duration': dur, 'description': desc
            })

        # Skills
        skill_names = request.POST.getlist('skill[]')
        skill_levels = request.POST.getlist('skill_level[]')
        context['skills'] = [{'name': n, 'level': l} for n, l in zip(skill_names, skill_levels)]

        # Languages
        lang_names = request.POST.getlist('language[]')
        context['languages'] = [{'name': n} for n in lang_names]

        template = request.POST.get('template', 'modern')
        template_map = {
            'modern': 'jobs/resume_modern.html',
            'professional': 'jobs/resume_professional.html',
            'creative': 'jobs/resume_creative.html',
        }
        return render(request, template_map.get(template, 'jobs/resume_modern.html'), context)
    return render(request, 'jobs/index.html')


def index_view(request):
    return render(request, 'jobs/index.html')

def index(request):
    return render(request, 'index.html')


@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user.employer)

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('dashboard:employer_dashboard')
    else:
        form = JobPostForm(instance=job)

    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})


@login_required
def withdraw_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user.employer)
    job.is_active = False
    job.save()
    messages.success(request, "Job withdrawn successfully.")
    return redirect('dashboard:employer_dashboard')


@login_required
def employer_dashboard(request):
    if not hasattr(request.user, 'employer'):
        return HttpResponseForbidden("You are not authorized to access this page.")

    jobs = Job.objects.filter(employer=request.user.employer).order_by('-posted_date')
    context = {
        'jobs': jobs,
    }
    return render(request, 'jobs/employer_dashboard.html', context)
