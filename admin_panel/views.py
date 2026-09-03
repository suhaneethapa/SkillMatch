import csv
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from accounts.models import User
from companies.models import Internship, CompanyProfile
from students.models import Application, JournalEntry
from core.models import Skill, Category, College


def admin_required(view_func):
    """Decorator to check if user is admin/superuser."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('accounts:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def dashboard(request):
    total_students = User.objects.filter(role='student').count()
    total_companies = User.objects.filter(role='company').count()
    total_listings = Internship.objects.count()
    total_applications = Application.objects.count()
    pending_internships = Internship.objects.filter(status='pending').count()
    pending_users = User.objects.filter(status='pending_admin').count()
    
    # Calculate placement rate
    approved_students = User.objects.filter(role='student', status='active').count()
    placed_students = Application.objects.filter(status='accepted').values('student').distinct().count()
    placement_rate = round((placed_students / approved_students * 100), 1) if approved_students > 0 else 0.0
    
    # Chart data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    application_volume = [12, 19, 15, 25, 32, 28, 35, 42, 38, 45, 50, 55]
    top_skills = ['Python', 'Django', 'JavaScript', 'React', 'MySQL', 'HTML/CSS', 'Git', 'REST API']
    skill_counts = [45, 38, 35, 30, 28, 25, 22, 20]
    status_labels = ['Pending', 'Offer Issued', 'Accepted', 'Rejected', 'Withdrawn']
    status_data = [120, 45, 30, 80, 5]
    
    recent_applications = Application.objects.select_related('student', 'internship').order_by('-applied_at')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    return render(request, 'admin_panel/dashboard.html', {
        'total_students': total_students,
        'total_companies': total_companies,
        'total_listings': total_listings,
        'total_applications': total_applications,
        'pending_internships': pending_internships,
        'pending_users': pending_users,
        'placement_rate': placement_rate,
        'months': json.dumps(months),
        'application_volume': json.dumps(application_volume),
        'top_skills': json.dumps(top_skills),
        'skill_counts': json.dumps(skill_counts),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'recent_applications': recent_applications,
        'recent_users': recent_users,
    })


@admin_required
def user_list(request):
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    users = User.objects.all().order_by('-date_joined')
    if role_filter:
        users = users.filter(role=role_filter)
    if status_filter:
        users = users.filter(status=status_filter)
    
    return render(request, 'admin_panel/user_list.html', {
        'users': users,
        'role_filter': role_filter,
        'status_filter': status_filter,
    })


@admin_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.status == 'active':
        user.status = 'suspended'
    elif user.status == 'suspended':
        user.status = 'active'
    elif user.status == 'pending_admin':
        user.status = 'active'
    user.save()
    messages.success(request, f"User {user.email} status updated to {user.status}")
    return redirect('admin_panel:user_list')


@admin_required
def internship_list(request):
    status_filter = request.GET.get('status', '')
    internships = Internship.objects.select_related('company').all().order_by('-created_at')
    if status_filter:
        internships = internships.filter(status=status_filter)
    
    return render(request, 'admin_panel/internship_list.html', {
        'internships': internships,
        'status_filter': status_filter,
    })


@admin_required
def approve_internship(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    if internship.status == 'pending':
        internship.status = 'approved'
        internship.save()
        messages.success(request, f"Internship '{internship.title}' approved.")
    elif internship.status == 'approved':
        internship.status = 'rejected'
        internship.save()
        messages.success(request, f"Internship '{internship.title}' rejected.")
    return redirect('admin_panel:internship_list')


@admin_required
def application_list(request):
    status_filter = request.GET.get('status', '')
    applications = Application.objects.select_related('student', 'internship').all().order_by('-applied_at')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    return render(request, 'admin_panel/application_list.html', {
        'applications': applications,
        'status_filter': status_filter,
    })


@admin_required
def skill_list(request):
    skills = Skill.objects.select_related('category').all().order_by('category__name', 'name')
    return render(request, 'admin_panel/skill_list.html', {'skills': skills})


@admin_required
def add_skill(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        if name and category_id:
            Skill.objects.create(name=name, category_id=category_id, is_active=True)
            messages.success(request, f"Skill '{name}' added.")
            return redirect('admin_panel:skill_list')
    
    categories = Category.objects.all()
    return render(request, 'admin_panel/add_skill.html', {'categories': categories})


@admin_required
def category_list(request):
    categories = Category.objects.prefetch_related('skills').all()
    return render(request, 'admin_panel/category_list.html', {'categories': categories})


@admin_required
def company_list(request):
    companies = CompanyProfile.objects.select_related('user').all().order_by('-created_at')
    return render(request, 'admin_panel/company_list.html', {'companies': companies})


@admin_required
def suspend_company(request, company_id):
    company = get_object_or_404(CompanyProfile, id=company_id)
    company.suspended = not company.suspended
    company.save()
    action = "suspended" if company.suspended else "reinstated"
    messages.success(request, f"Company '{company.organization_name}' {action}.")
    return redirect('admin_panel:company_list')


@admin_required
def journal_list(request):
    entries = JournalEntry.objects.select_related('student', 'application__internship').all().order_by('-entry_date')
    return render(request, 'admin_panel/journal_list.html', {'entries': entries})


@admin_required
def csv_export(request, data_type):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{data_type}.csv"'
    writer = csv.writer(response)
    
    if data_type == 'students':
        writer.writerow(['ID', 'Email', 'College', 'Department', 'Semester', 'Status'])
        for user in User.objects.filter(role='student'):
            try:
                profile = user.student_profile
                writer.writerow([user.id, user.email, profile.college.name, profile.department, profile.semester, user.status])
            except:
                writer.writerow([user.id, user.email, 'N/A', 'N/A', 'N/A', user.status])
    
    elif data_type == 'companies':
        writer.writerow(['ID', 'Email', 'Organization', 'Industry', 'Contact', 'Suspended'])
        for user in User.objects.filter(role='company'):
            try:
                profile = user.company_profile
                writer.writerow([user.id, user.email, profile.organization_name, profile.industry, profile.contact_person, profile.suspended])
            except:
                writer.writerow([user.id, user.email, 'N/A', 'N/A', 'N/A', 'N/A'])
    
    elif data_type == 'listings':
        writer.writerow(['ID', 'Title', 'Company', 'Category', 'Status', 'Positions', 'Deadline'])
        for i in Internship.objects.all():
            writer.writerow([i.id, i.title, i.company.organization_name, i.category.name, i.status, i.total_positions, i.deadline])
    
    elif data_type == 'applications':
        writer.writerow(['ID', 'Student', 'Internship', 'Company', 'Match Score', 'Status', 'Applied'])
        for a in Application.objects.all():
            writer.writerow([a.id, a.student.email, a.internship.title, a.internship.company.organization_name, a.match_score, a.status, a.applied_at])
    
    return response