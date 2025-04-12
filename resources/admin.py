from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import AcademicYear, Semester, Subject, ResourceType, Resource

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(Subject)
class SubjectAdmin(ImportExportModelAdmin):
    list_display = ('name', 'code', 'department', 'academic_year', 'semester')
    list_filter = ('department', 'academic_year', 'semester')
    search_fields = ('name', 'code', 'description')
    ordering = ('department', 'academic_year', 'semester', 'name')

@admin.register(ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'resource_type', 'uploaded_by', 'is_approved', 'created_at')
    list_filter = ('resource_type', 'is_approved', 'created_at', 'subject__department')
    search_fields = ('title', 'description', 'subject__name', 'uploaded_by__email')
    ordering = ('-created_at',)
