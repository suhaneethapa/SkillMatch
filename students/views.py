from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from companies.models import Internship
from .models import Application, StudentProfile, StudentSkill
from core.models import Skill, College
from matching.engine import compute_match_score, is_eligible


@login_required
def dashboard(request):
    if request.user.role != 'student':
        return redirect('accounts:home')
    applications = request.user.applications.select_related('internship__company').all()
    return render(request, 'students/dashboard.html', {
        'applications': applications
    })


@login_required
def profile(request):
    if request.user.role != 'student':
        return redirect('accounts:home')
    profile = request.user.student_profile
    skills = request.user.student_skills.select_related('skill__category').all()
    return render(request, 'students/profile.html', {
        'profile': profile,
        'skills': skills
    })


@login_required
def profile_edit(request):
    if request.user.role != 'student':
        return redirect('accounts:home')
    
    profile = request.user.student_profile
    colleges = College.objects.all()
    
    if request.method == 'POST':
        profile.department = request.POST.get('department', profile.department)
        profile.semester = request.POST.get('semester', profile.semester)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.github_url = request.POST.get('github_url', '')
        profile.linkedin_url = request.POST.get('linkedin_url', '')
        
        college_id = request.POST.get('college')
        if college_id:
            profile.college_id = college_id
        
        if request.FILES.get('cv_file'):
            profile.cv_file = request.FILES['cv_file']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('students:profile')
    
    return render(request, 'students/profile_edit.html', {
        'profile': profile,
        'colleges': colleges
    })


@login_required
def skills_edit(request):
    if request.user.role != 'student':
        return redirect('accounts:home')
    
    all_skills = Skill.objects.filter(is_active=True).select_related('category').order_by('category__name', 'name')
    user_skill_ids = set(request.user.student_skills.values_list('skill_id', flat=True))
    
    if request.method == 'POST':
        selected_skill_ids = request.POST.getlist('skills')
        
        with transaction.atomic():
            request.user.student_skills.all().delete()
            for skill_id in selected_skill_ids:
                StudentSkill.objects.create(student=request.user, skill_id=skill_id)
        
        messages.success(request, 'Skills updated successfully!')
        return redirect('students:profile')
    
    return render(request, 'students/skills_edit.html', {
        'all_skills': all_skills,
        'user_skill_ids': user_skill_ids
    })


@login_required
def browse_internships(request):
    if request.user.role != 'student':
        return redirect('accounts:home')
    
    internships = Internship.objects.filter(status='approved').select_related('company', 'category')
    student_skills = set(request.user.student_skills.values_list('skill__name', flat=True))
    
    listings_with_scores = []
    for internship in internships:
        req_skills = list(internship.internship_skills.values_list('skill__name', 'is_required'))
        score, gap = compute_match_score(student_skills, req_skills)
        listings_with_scores.append({
            'internship': internship,
            'score': score,
            'gap': gap,
            'eligible': is_eligible(score)
        })
    
    listings_with_scores.sort(key=lambda x: x['score'], reverse=True)
    
    from django.utils import timezone
    from datetime import date
    
    return render(request, 'students/browse_internships.html', {
        'listings': listings_with_scores,
        'today': timezone.now(),
    })


@login_required
def my_applications(request):
    if request.user.role != 'student':
        return redirect('accounts:home')
    applications = request.user.applications.select_related('internship__company').order_by('-applied_at')
    return render(request, 'students/applications.html', {
        'applications': applications
    })


@login_required
def apply_internship(request, internship_id):
    if request.user.role != 'student':
        return redirect('accounts:home')
    
    internship = get_object_or_404(Internship, id=internship_id, status='approved')
    
    if Application.objects.filter(student=request.user, internship=internship).exists():
        messages.error(request, "You have already applied to this internship.")
        return redirect('students:browse_internships')
    
    student_skills = set(request.user.student_skills.values_list('skill__name', flat=True))
    req_skills = list(internship.internship_skills.values_list('skill__name', 'is_required'))
    score, gap = compute_match_score(student_skills, req_skills)
    
    if not is_eligible(score):
        messages.error(request, f"Your match score is {score}%. You need at least 50%. Missing: {', '.join(gap) if gap else 'None'}")
        return redirect('students:browse_internships')
    
    if not request.user.student_profile.cv_file:
        messages.error(request, "Please upload your CV before applying.")
        return redirect('students:profile_edit')
    
    Application.objects.create(
        student=request.user,
        internship=internship,
        match_score=score,
        status='pending',
        cover_letter=request.POST.get('cover_letter', '')
    )
    
    messages.success(request, f"Application submitted! Match score: {score}%")
    return redirect('students:my_applications')


@login_required
def withdraw_application(request, application_id):
    if request.user.role != 'student':
        return redirect('accounts:home')
    
    application = get_object_or_404(Application, id=application_id, student=request.user, status='pending')
    application.status = 'withdrawn'
    application.save()
    messages.success(request, 'Application withdrawn successfully.')
    return redirect('students:my_applications')