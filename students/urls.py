from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('internships/', views.browse_internships, name='browse_internships'),
    path('applications/', views.my_applications, name='my_applications'),
    path('apply/<int:internship_id>/', views.apply_internship, name='apply_internship'),
]