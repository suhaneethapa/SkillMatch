from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user'),
    path('internships/', views.internship_list, name='internship_list'),
    path('internships/<int:internship_id>/approve/', views.approve_internship, name='approve_internship'),
    path('applications/', views.application_list, name='application_list'),
    path('skills/', views.skill_list, name='skill_list'),
    path('skills/add/', views.add_skill, name='add_skill'),
    path('categories/', views.category_list, name='category_list'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/<int:company_id>/suspend/', views.suspend_company, name='suspend_company'),
    path('journal/', views.journal_list, name='journal_list'),
    path('csv-export/<str:data_type>/', views.csv_export, name='csv_export'),
]