from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.jobs.models import Job, Application
from django.shortcuts import render

def home(request):
    return render(request, 'dashboard/home.html')
@login_required
def employer_dashboard(request):
    if not request.user.is_employer:
        messages.error(request, "Access denied. Employer account required.")
        return redirect('jobs:home')
    
    employer = request.user.employer
    posted_jobs = Job.objects.filter(employer=employer)
    recent_applications = Application.objects.filter(
        job__employer=employer
    ).order_by('-applied_date')[:5]
    
    context = {
        'employer': employer,  # ✅ This line is new
        'posted_jobs': posted_jobs,
        'recent_applications': recent_applications,
        'total_jobs': posted_jobs.count(),
        'total_applications': Application.objects.filter(
            job__employer=employer
        ).count(),
        'employer': request.user.employer,  # <-- Add this
    }
    return render(request, 'dashboard/employer_dashboard.html', context)


@login_required
def job_seeker_dashboard(request):
    if not request.user.is_job_seeker:
        messages.error(request, "Access denied. Job seeker account required.")
        return redirect('jobs:home')
    
    job_seeker = request.user.jobseeker  # get JobSeeker instance
    
    applications = Application.objects.filter(
        job_seeker=job_seeker
    ).order_by('-applied_date')
    
    context = {
        'job_seeker': job_seeker,  # add this line
        'applications': applications,
        'total_applications': applications.count(),
        'pending_applications': applications.filter(status='pending').count(),
        'accepted_applications': applications.filter(status='accepted').count(),
    }
    return render(request, 'dashboard/job_seeker_dashboard.html', context)

@login_required
def manage_application(request, application_id):
    if not request.user.is_employer:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    application = Application.objects.get(
        id=application_id,
        job__employer=request.user.employer
    )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, "Application status updated successfully!")
    
    return redirect('dashboard:employer_dashboard')

@login_required
def edit_application(request, application_id):
    application = get_object_or_404(Application, id=application_id, job_seeker=request.user.jobseeker)
    
    if application.status != 'pending':
        messages.error(request, "You can only edit pending applications.")
        return redirect('dashboard:jobseeker_dashboard')
    
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter')
        if cover_letter.strip():  # Check if cover letter is not empty
            application.cover_letter = cover_letter
            application.save()
            messages.success(request, "Application updated successfully!")
            return redirect('dashboard:job_seeker_dashboard')
        else:
            messages.error(request, "Cover letter cannot be empty.")
    
    # If GET request, render the edit form
    context = {'application': application}
    return render(request, 'dashboard/edit_application.html', context)


@login_required
def withdraw_application(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(Application, id=application_id, job_seeker=request.user.jobseeker)
        
        if application.status != 'pending':
            messages.error(request, "You can only withdraw pending applications.")
            return redirect('dashboard:job_seeker_dashboard')
        
        application.delete()
        messages.success(request, "Application withdrawn successfully!")
    
    return redirect('dashboard:job_seeker_dashboard')


@login_required
def view_application_detail(request, application_id):
    if not request.user.is_employer:
        messages.error(request, "Access denied.")
        return redirect('dashboard:employer_dashboard')

    application = get_object_or_404(Application, id=application_id, job__employer=request.user.employer)
    
    context = {
        'application': application
    }
    return render(request, 'dashboard/application_detail.html', context)


