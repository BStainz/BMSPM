
from django.shortcuts import render, get_object_or_404 , redirect#new
from django.http import HttpResponseRedirect
from .models import Project, Task, Resource, File, OutOfOffice, Notification, TechnicianLog
from django.urls import reverse
from .forms import ProjectForm, TaskForm, ResourceForm, FileForm 
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Count, Q
from datetime import datetime, timedelta

def project_list(request):
    query = request.GET.get('search', '')
    projects = Project.objects.filter(name__icontains=query) if query else Project.objects.all()
    return render(request, 'tasks/project_list.html', {'projects': projects})
# Create your views here.

def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    tasks = Task.objects.filter(project=project) 
    resources = Resource.objects.filter(project=project) 
    files = File.objects.filter(project=project) 
    context = {'project': project, 'tasks': tasks, 'resources': resources, 'files': files}
    return render(request, 'tasks/project_detail.html', context)

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'tasks/create_project.html', {'form': form})
def is_project_manager(user):
    return user.groups.filter(name='Project Managers').exists()

@login_required
def create_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm()
    return render(request, 'tasks/create_task.html', {'form': form, 'project': project})
@login_required
def create_resource(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.project = project
            resource.save()
            return HttpResponseRedirect(reverse('project_detail', args=[project_id]))
    else:
        form = ResourceForm()
    return render(request, 'tasks/create_resource.html', {'form': form, 'project': project})

@login_required
def upload_file(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            for file_data in request.FILES.getlist('files'):
                File.objects.create(project=project, file=file_data, uploaded_by=request.user)
            return HttpResponseRedirect(reverse('project_detail', args=[project_id]))
    else:
        form = FileForm()
    return render(request, 'tasks/upload_file.html', {'form': form, 'project': project})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Require admin approval
            user.save()
            messages.info(request, 'Registration pending approval.')
            return redirect('registration_pending')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def registration_pending(request):
    return render(request, 'registration/pending.html')

@user_passes_test(lambda u: u.is_superuser)  # Only allow superusers
def admin_dashboard(request):
    pending_users = User.objects.filter(is_active=False)
    context = {'pending_users': pending_users}
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def approve_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    # Optionally, send an email to the user notifying them of approval
    return redirect('admin_dashboard')

@login_required
def project_dashboard(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()
    task_summary = tasks.values('status').annotate(count=Count('status'))
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    return render(request, 'tasks/project_dashboard.html', {
        'project': project,
        'tasks': tasks,
        'task_summary': task_summary,
        'progress': progress,
    })
    
    def pm_dashboard(request):
        out_of_office = OutOfOffice.objects.filter(date__gte=datetime.now(), date__lte=datetime.now() + timedelta(days=3))
        return render(request, 'tasks/pm_dashboard.html', {
            'out_of_office': out_of_office,
            # Add other context variables as needed
    })
        
    def generate_report(request):
        tasks_summary = Task.objects.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='Completed')),
            pending=Count('id', filter=Q(status='Pending'))
        )

        resources_summary = Resource.objects.aggregate(
            delivered=Count('id', filter=Q(status='Delivered')),
            pending=Count('id', filter=Q(status='Pending'))
        )

        return render(request, 'tasks/report.html', {
            'tasks_summary': tasks_summary,
            'resources_summary': resources_summary,
        })
# tasks/views.py
def technician_logs(request, project_id):
    logs = TechnicianLog.objects.filter(project_id=project_id)
    return render(request, 'tasks/technician_logs.html', {'logs': logs})

def get_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    return render(request, 'tasks/notifications.html', {'notifications': notifications})

def pm_dashboard(request):
    pm_projects = Project.objects.filter(assigned_pm=request.user)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    out_of_office = OutOfOffice.objects.filter(date__gte=datetime.now(), date__lte=datetime.now() + timedelta(days=3))
    return render(request, 'tasks/pm_dashboard.html', {
        'projects': pm_projects,
        'notifications': notifications,
        'out_of_office': out_of_office,
    })