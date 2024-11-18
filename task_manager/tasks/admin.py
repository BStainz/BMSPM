from django.contrib import admin
from .models import Project, Task, Resource, File, OutOfOffice

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Resource)
admin.site.register(File)
admin.site.register(OutOfOffice)
# Register your models here.
