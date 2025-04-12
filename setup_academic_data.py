import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resource_management_system.settings')
django.setup()

from resources.models import AcademicYear, Semester

def setup_academic_data():
    print("Setting up academic years...")
    for year_value, year_name in AcademicYear.YEAR_CHOICES:
        year, created = AcademicYear.objects.get_or_create(
            name=year_value,
            defaults={'is_active': True}
        )
        if created:
            print(f"Created academic year: {year_name}")
        else:
            print(f"Academic year exists: {year_name}")

    print("\nSetting up semesters...")
    for sem_value, sem_name in Semester.SEMESTER_CHOICES:
        semester, created = Semester.objects.get_or_create(
            name=sem_value,
            defaults={'is_active': True}
        )
        if created:
            print(f"Created semester: {sem_name}")
        else:
            print(f"Semester exists: {sem_name}")

if __name__ == '__main__':
    setup_academic_data()
