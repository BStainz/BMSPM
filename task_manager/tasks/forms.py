from django import forms
from .models import Project, Task, Resource, File


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'project_number', 'site_details',
            'assigned_pms', 'status', 'is_conversion',
            'previous_system_version', 'ecos_version', 'existing_ecos_site',
            'controller_type', 'smartx_controllers_needed', 'controller_status',
            'dmp_file_status', 'dmp_conversion_status', 'conversion_errors',
            'enterprise_server_required', 'automation_servers_required', 'automation_server_status',
            'automation_server_ip', 'new_computer_needed', 'new_computer_status',
            'computer_ip', 'computer_setup_status', 'software_status', 'licenses_required',
            'license_status', 'license_activated', 'deployment_readiness',
            'deployed_date', 'service_tech_installing', 'graphics_status'
        ]
        widgets = {
            'assigned_pms': forms.CheckboxSelectMultiple(),
            'smartx_controllers_needed': forms.Textarea(attrs={'rows': 3}),
            'software_status': forms.Textarea(attrs={'rows': 3}),
            'licenses_required': forms.Textarea(attrs={'rows': 3}),
            'graphics_status': forms.Textarea(attrs={'rows': 3}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'title', 'description', 'deadline', 'priority', 'assigned_to', 'status', 'dependency']
        widgets = {
            'dependency': forms.CheckboxSelectMultiple(),
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['project', 'resource_type', 'quantity', 'status', 'uploaded_file']


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class FileForm(forms.Form):
    files = forms.FileField(
        widget=MultiFileInput(attrs={'multiple': True}),
        required=True
    )
