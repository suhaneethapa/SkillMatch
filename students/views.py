from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from companies.models import Internship, InternshipSkill, CompanyProfile
from .models import Application, StudentSkill
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
    return render(request, 'students/profile.html')


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
    
    return render(request, 'students/browse_internships.html', {
        'listings': listings_with_scores
    })


@login_required
def my_applications(request):
    if request.user.role != 'student':
        return redirect('accounts:home')
    
    applications = request.user.applications.select_related('internship').all()
    return render(request, 'students/applications.html', {
        'applications': applications
    })


@login_required
def apply_internship(request, internship_id):
    if request.user.role != 'student':
        return redirect('accounts:home')
    
    internship = get_object_or_404(Internship, id=internship_id, status='approved')
    
    # Check if already applied
    if Application.objects.filter(student=request.user, internship=internship).exists():
        messages.error(request, "You have already applied to this internship.")
        return redirect('students:browse_internships')
    
    # Compute match score
    student_skills = set(request.user.student_skills.values_list('skill__name', flat=True))
    req_skills = list(internship.internship_skills.values_list('skill__name', 'is_required'))
    score, gap = compute_match_score(student_skills, req_skills)
    
    if not is_eligible(score):
        messages.error(request, f"Your match score is {score}%. You need at least 50%. Missing: {', '.join(gap)}")
        return redirect('students:browse_internships')
    
    # Check CV uploaded
    if not request.user.student_profile.cv_file:
        messages.error(request, "Please upload your CV before applying.")
        return redirect('students:profile')
    
    Application.objects.create(
        student=request.user,
        internship=internship,
        match_score=score,
        status='pending'
    )
    
    messages.success(request, f"Application submitted! Match score: {score}%")
    return redirect('students:my_applications')