from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
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
    if request.user.role != 'company':
        return redirect('accounts:home')
    
    profile = request.user.company_profile
    internships = profile.internships.all()
    return render(request, 'companies/dashboard.html', {
        'internships': internships,
        'profile': profile,
        'today': date.today(),
    })


@login_required
def profile_edit(request):
    if request.user.role != 'company':
        return redirect('accounts:home')
    
    profile = request.user.company_profile
    
    if request.method == 'POST':
        profile.organization_name = request.POST.get('organization_name', profile.organization_name)
        profile.contact_person = request.POST.get('contact_person', profile.contact_person)
        profile.industry = request.POST.get('industry', profile.industry)
        profile.description = request.POST.get('description', profile.description)
        profile.website_url = request.POST.get('website_url', '')
        profile.hq_location = request.POST.get('hq_location', profile.hq_location)
        
        # Handle logo upload with validation
        if request.FILES.get('logo'):
            logo = request.FILES['logo']
            
            # Check file size (max 2MB)
            if logo.size > 2 * 1024 * 1024:
                messages.error(request, 'Logo file too large. Maximum size is 2MB.')
                return redirect('companies:profile_edit')
            
            # Check file type
            if not logo.content_type.startswith('image/'):
                messages.error(request, 'Only image files (PNG, JPG, GIF) are allowed for logo.')
                return redirect('companies:profile_edit')
            
            profile.logo = logo
            messages.success(request, 'Logo uploaded successfully!')
        
        profile.save()
        messages.success(request, 'Company profile updated successfully!')
        return redirect('companies:profile')
    
    return render(request, 'companies/profile_edit.html', {
        'profile': profile,
    })


@login_required
def my_listings(request):
    if request.user.role != 'company':
        return redirect('accounts:home')
    
    internships = request.user.company_profile.internships.all()
    return render(request, 'companies/listings.html', {
        'internships': internships,
        'today': date.today(),
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
            status='approved'
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
def delete_listing(request, internship_id):
    if request.user.role != 'company':
        return redirect('accounts:home')
    
    internship = get_object_or_404(Internship, id=internship_id, company=request.user.company_profile)
    
    if request.method == 'POST':
        internship.delete()
        messages.success(request, "Internship listing deleted successfully.")
        return redirect('companies:my_listings')
    
    return render(request, 'companies/confirm_delete.html', {
        'internship': internship,
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
    
    if request.method == 'POST':
        if request.FILES.get('offer_letter'):
            application.offer_letter = request.FILES['offer_letter']
        
        application.status = 'offer_issued'
        application.save()
        
        messages.success(request, "Offer letter issued successfully!")
        return redirect('companies:view_applicants', internship_id=application.internship.id)
    
    return render(request, 'companies/issue_offer.html', {
        'application': application
    })


@login_required
def reject_applicant(request, application_id):
    if request.user.role != 'company':
        return redirect('accounts:home')
    
    application = get_object_or_404(Application, id=application_id, internship__company=request.user.company_profile)
    application.status = 'rejected'
    application.rejection_feedback = request.POST.get('feedback', '')
    application.save()
    messages.success(request, "Applicant rejected.")
    return redirect('companies:view_applicants', internship_id=application.internship.id)