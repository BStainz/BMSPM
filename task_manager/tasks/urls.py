from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),  # Home page (project list)
    path('projects/', views.project_list, name='project_list'),  # List all projects
    path('projects/create/', views.create_project, name='create_project'),  # Create a new project
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),  # View project details
    path('projects/<int:project_id>/dashboard/', views.project_dashboard, name='project_dashboard'),  # Project dashboard
    path('projects/<int:project_id>/tasks/create/', views.create_task, name='create_task'),  # Create a task for a project
    path('projects/<int:project_id>/create_resource/', views.create_resource, name='create_resource'),  # Add resources
    path('projects/<int:project_id>/upload_file/', views.upload_file, name='upload_file'),  # Upload a file to a project
    path('pm_dashboard/', views.pm_dashboard, name='pm_dashboard'),
]
