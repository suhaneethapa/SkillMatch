from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('internships/', views.my_listings, name='my_listings'),
    path('internships/create/', views.create_listing, name='create_listing'),
    path('internships/<int:internship_id>/applicants/', views.view_applicants, name='view_applicants'),
    path('applications/<int:application_id>/offer/', views.issue_offer, name='issue_offer'),
    path('applications/<int:application_id>/reject/', views.reject_applicant, name='reject_applicant'),
]