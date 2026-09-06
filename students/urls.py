from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('skills/edit/', views.skills_edit, name='skills_edit'),
    path('internships/', views.browse_internships, name='browse_internships'),
    path('applications/', views.my_applications, name='my_applications'),
    path('apply/<int:internship_id>/', views.apply_internship, name='apply_internship'),
    path('withdraw/<int:application_id>/', views.withdraw_application, name='withdraw_application'),
    path('offer/<int:application_id>/', views.view_offer, name='view_offer'),
    path('offer/<int:application_id>/accept/', views.accept_offer, name='accept_offer'),
    path('offer/<int:application_id>/decline/', views.decline_offer, name='decline_offer'),
]