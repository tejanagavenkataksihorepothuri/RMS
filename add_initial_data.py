import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resource_management_system.settings')
django.setup()

from resources.models import AcademicYear, Semester, ResourceType

# Add Academic Years
academic_years = [
    "1ST YEAR",
    "2ND YEAR",
    "3RD YEAR",
    "4TH YEAR"
]

for year in academic_years:
    AcademicYear.objects.get_or_create(name=year, is_active=True)

# Add Semesters
semesters = [
    "SEM 1",
    "SEM 2"
]

for sem in semesters:
    Semester.objects.get_or_create(name=sem, is_active=True)

# Add Resource Types
resource_types = [
    "PDF",
    "WORD",
    "EXCEL"
]

for rt in resource_types:
    ResourceType.objects.get_or_create(name=rt)

print("Initial data added successfully!") 