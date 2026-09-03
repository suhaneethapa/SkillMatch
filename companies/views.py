from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Internship, InternshipSkill, CompanyProfile
from core.models import Skill, Category
from students.models import Application


@login_required
def dashboard(request):
    if request.user.role != 'company':
        return redirect('accounts:home')
    
    profile = request.user.company_profile
    internships = profile.internships.all()
    return render(request, 'companies/dashboard.html', {
        'internships': internships,
        'profile': profile
    })


@login_required
def profile(request):
    return render(request, 'companies/profile.html')


@login_required
def my_listings(request):
    if request.user.role != 'company':
        return redirect('accounts:home')
    
    internships = request.user.company_profile.internships.all()
    return render(request, 'companies/listings.html', {
        'internships': internships
    })


@login_required
def create_listing(request):
    if request.user.role != 'company':
        return redirect('accounts:home')
    
    skills = Skill.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        location = request.POST.get('location_type')
        stipend = request.POST.get('stipend') or None
        deadline = request.POST.get('deadline')
        positions = request.POST.get('total_positions')
        duration = request.POST.get('expected_duration')
        required_skills = request.POST.getlist('required_skills')
        preferred_skills = request.POST.getlist('preferred_skills')
        
        internship = Internship.objects.create(
            company=request.user.company_profile,
            title=title,
            description=description,
            category_id=category_id,
            location_type=location,
            stipend=stipend,
            deadline=deadline,
            total_positions=positions,
            expected_duration=duration,
            status='approved'  # Auto-approve for demo
        )
        
        for skill_id in required_skills:
            InternshipSkill.objects.create(internship=internship, skill_id=skill_id, is_required=True)
        for skill_id in preferred_skills:
            InternshipSkill.objects.create(internship=internship, skill_id=skill_id, is_required=False)
        
        messages.success(request, "Internship posted successfully!")
        return redirect('companies:dashboard')
    
    return render(request, 'companies/create_listing.html', {
        'skills': skills,
        'categories': categories
    })


@login_required
def view_applicants(request, internship_id):
    if request.user.role != 'company':
        return redirect('accounts:home')
    
    internship = get_object_or_404(Internship, id=internship_id, company=request.user.company_profile)
    applications = internship.applications.select_related('student').order_by('-match_score')
    
    return render(request, 'companies/applicants.html', {
        'internship': internship,
        'applications': applications
    })


@login_required
def issue_offer(request, application_id):
    if request.user.role != 'company':
        return redirect('accounts:home')
    
    application = get_object_or_404(Application, id=application_id, internship__company=request.user.company_profile)
    
    with transaction.atomic():
        application.status = 'offer_issued'
        application.save()
        
        # Auto-close if positions filled
        internship = application.internship
        accepted_count = internship.applications.filter(status='accepted').count()
        if accepted_count >= internship.total_positions:
            internship.status = 'closed'
            internship.save()
            # Reject remaining pending
            internship.applications.filter(status='pending').update(status='rejected')
    
    messages.success(request, "Offer issued successfully!")
    return redirect('companies:view_applicants', internship_id=internship.id)