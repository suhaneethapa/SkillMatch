import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import User
from companies.models import Internship, CompanyProfile
from students.models import Application


@login_required
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('accounts:home')
    
    total_students = User.objects.filter(role='student').count()
    total_companies = User.objects.filter(role='company').count()
    total_listings = Internship.objects.count()
    total_applications = Application.objects.count()
    placement_rate = 15.5
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    application_volume = [12, 19, 15, 25, 32, 28, 35, 42, 38, 45, 50, 55]
    top_skills = ['Python', 'Django', 'JavaScript', 'React', 'MySQL', 'HTML/CSS', 'Git', 'REST API']
    skill_counts = [45, 38, 35, 30, 28, 25, 22, 20]
    status_labels = ['Pending', 'Offer Issued', 'Accepted', 'Rejected', 'Withdrawn']
    status_data = [120, 45, 30, 80, 5]
    
    return render(request, 'admin_panel/dashboard.html', {
        'total_students': total_students,
        'total_companies': total_companies,
        'total_listings': total_listings,
        'total_applications': total_applications,
        'placement_rate': placement_rate,
        'months': json.dumps(months),
        'application_volume': json.dumps(application_volume),
        'top_skills': json.dumps(top_skills),
        'skill_counts': json.dumps(skill_counts),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
    })


@login_required
def approvals(request):
    if not request.user.is_superuser:
        return redirect('accounts:home')
    return render(request, 'admin_panel/approvals.html')


@login_required
def analytics(request):
    if not request.user.is_superuser:
        return redirect('accounts:home')
    return redirect('admin_panel:dashboard')