from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    # General Project Fields
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project_number = models.CharField(max_length=100, blank=True, null=True)
    site_details = models.CharField(max_length=255)
    assigned_pms = models.ManyToManyField(User, related_name='assigned_projects')
    status = models.CharField(
        max_length=50,
        choices=[("In Progress", "In Progress"), ("Completed", "Completed"), ("On Hold", "On Hold")],
        default="In Progress"
    )
    is_conversion = models.BooleanField(default=False)  # Indicates if this is a conversion project

    # Conversion-Specific Fields
    previous_system_version = models.CharField(max_length=255, blank=True, null=True)
    ecos_version = models.CharField(max_length=255, blank=True, null=True)
    existing_ecos_site = models.CharField(max_length=255, blank=True, null=True)  # "Yes/No" or specific version

    # Controllers
    controller_type = models.CharField(
        max_length=50,
        choices=[("I2", "I2 (Not Changing Controllers)"), ("SmartX", "New SmartX")],
        blank=True,
        null=True
    )
    smartx_controllers_needed = models.TextField(blank=True, null=True)  # List of controllers needed
    controller_status = models.TextField(blank=True, null=True)  # Status info for each controller

    # DMP File
    dmp_file_status = models.CharField(
        max_length=50,
        choices=[("Uploaded", "Uploaded"), ("Not Uploaded", "Not Uploaded")],
        default="Not Uploaded"
    )
    dmp_conversion_status = models.TextField(blank=True, null=True)
    conversion_errors = models.TextField(blank=True, null=True)

    # Enterprise Server
    enterprise_server_required = models.BooleanField(default=False)

    # Automation Server
    automation_servers_required = models.PositiveIntegerField(blank=True, null=True)
    automation_server_status = models.TextField(blank=True, null=True)  # Info for each server
    automation_server_ip = models.TextField(blank=True, null=True)  # List of static IPs

    # Software & Licensing
    new_computer_needed = models.BooleanField(default=False)
    new_computer_status = models.TextField(blank=True, null=True)  # Status info for the computer
    computer_ip = models.CharField(max_length=255, blank=True, null=True)  # Static IP for the PC
    computer_setup_status = models.CharField(
        max_length=50,
        choices=[("Complete", "Complete"), ("Incomplete", "Incomplete")],
        default="Incomplete"
    )
    software_status = models.TextField(blank=True, null=True)  # Software downloaded/not downloaded
    licenses_required = models.TextField(blank=True, null=True)  # List of licenses needed
    license_status = models.TextField(blank=True, null=True)  # Status of licenses
    license_activated = models.BooleanField(default=False)

    # Deployment Readiness
    deployment_readiness = models.BooleanField(default=False)  # Automatically calculated
    deployed_date = models.DateField(blank=True, null=True)
    service_tech_installing = models.CharField(max_length=255, blank=True, null=True)

    # Graphics
    graphics_status = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Initialize default values for conversion projects
        if self.is_conversion and not self.previous_system_version:
            self.previous_system_version = "Specify previous system/version"
            self.ecos_version = "Specify EcoStruxure version"
            self.existing_ecos_site = "Yes/No"
            self.controller_type = "I2"
            self.smartx_controllers_needed = "List of controllers"
            self.controller_status = "Ordered/Delivered/Pending"
            self.dmp_conversion_status = "Pending"
            self.dmp_file_status = "Not Uploaded"
            self.licenses_required = "List specific licenses needed"
            self.license_status = "Pending"
            self.computer_setup_status = "Incomplete"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField(blank=True, null=True)
    priority = models.CharField(
        max_length=20,
        choices=[("High", "High"), ("Medium", "Medium"), ("Low", "Low")],
        default="Medium"  # Default value
    )
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("Not Started", "Not Started"), ("In Progress", "In Progress"), ("Blocked", "Blocked"), ("Completed", "Completed")],
        default="Not Started"  # Default value
    )
    dependency = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependent_tasks')

    def __str__(self):
        return self.title


class Resource(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    resource_type = models.CharField(
        max_length=50,
        choices=[("Controller", "Controller"), ("Server", "Server"), ("License", "License"), ("Other", "Other")],
        default="Other"  # Default value
    )
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=50,
        choices=[("Ordered", "Ordered"), ("Delivered", "Delivered"), ("Pending", "Pending")],
        default="Pending"  # Default value
    )
    uploaded_file = models.FileField(upload_to='resources/', blank=True, null=True)
    other_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.resource_type} for {self.project.name}" if self.project else "Unassigned Resource"


class File(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.project.name} by {self.uploaded_by.username if self.uploaded_by else 'Unknown'}"


class OutOfOffice(models.Model):
    date = models.DateField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Out on {self.date} - {self.reason or 'No reason provided'}"


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username}"


class Milestone(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    dependencies = models.ManyToManyField('self', blank=True, symmetrical=False)
    deadline = models.DateField()

    def clean(self):
        if self in self.dependencies.all():
            raise ValidationError("A milestone cannot depend on itself.")

    def __str__(self):
        return self.name


class TechnicianLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateField()
    tasks_completed = models.TextField()
    notes = models.TextField(blank=True, null=True)
    completed_by = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Log for {self.project.name} on {self.date}"
