from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm, CompanyRegistrationForm, LoginForm


def home(request):
    if request.user.is_authenticated:
        if request.user.role == 'student':
            return redirect('students:dashboard')
        elif request.user.role == 'company':
            return redirect('companies:dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_panel:dashboard')
    return render(request, 'accounts/home.html')


def register(request):
    student_form = StudentRegistrationForm()
    company_form = CompanyRegistrationForm()
    
    if request.method == 'POST':
        if request.POST.get('role') == 'student':
            student_form = StudentRegistrationForm(request.POST)
            if student_form.is_valid():
                student_form.save()
                return redirect('accounts:login')
        else:
            company_form = CompanyRegistrationForm(request.POST)
            if company_form.is_valid():
                company_form.save()
                return redirect('accounts:login')
    
    return render(request, 'accounts/register.html', {
        'student_form': student_form,
        'company_form': company_form
    })


def login_view(request):
    form = LoginForm()
    error = None
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                if user.role == 'student':
                    return redirect('students:dashboard')
                elif user.role == 'company':
                    return redirect('companies:dashboard')
                else:
                    return redirect('admin_panel:dashboard')
            else:
                error = "Invalid email or password"
    
    return render(request, 'accounts/login.html', {'form': form, 'error': error})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:home')


def verify_email(request, token):
    # token captured from URL for future verification logic
    return render(request, 'accounts/verify.html', {'token': token})


def password_reset_request(request):
    # TODO: implement password reset flow
    return render(request, 'accounts/password_reset.html')