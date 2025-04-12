from django.db import models
from django.conf import settings
from accounts.models import Department

class AcademicYear(models.Model):
    YEAR_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    ]
    name = models.CharField(max_length=50, choices=YEAR_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()

    @classmethod
    def create_defaults(cls):
        for value, name in cls.YEAR_CHOICES:
            cls.objects.get_or_create(name=value, defaults={'is_active': True})

class Semester(models.Model):
    SEMESTER_CHOICES = [
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
    ]
    name = models.CharField(max_length=50, choices=SEMESTER_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()

    @classmethod
    def create_defaults(cls):
        for value, name in cls.SEMESTER_CHOICES:
            cls.objects.get_or_create(name=value, defaults={'is_active': True})

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='subjects')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('code', 'department', 'academic_year', 'semester')
    
    def __str__(self):
        return f"{self.name} ({self.code}) - {self.department.name}"

class ResourceType(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Resource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='resources/')
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE, related_name='resources')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='resources')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_resources')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"
    
    def file_extension(self):
        import os
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()
    
    @property
    def is_video(self):
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']
        return self.file_extension() in video_extensions
    
    @property
    def is_document(self):
        doc_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt']
        return self.file_extension() in doc_extensions
    
    @property
    def is_image(self):
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']
        return self.file_extension() in image_extensions
