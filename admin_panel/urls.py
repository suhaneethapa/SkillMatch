from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('approvals/', views.approvals, name='approvals'),
    path('analytics/', views.analytics, name='analytics'),
]