from django.db import migrations

def add_default_academic_years_semesters(apps, schema_editor):
    AcademicYear = apps.get_model('resources', 'AcademicYear')
    Semester = apps.get_model('resources', 'Semester')
    
    # Add academic years
    academic_years = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    ]
    
    for year_value, year_name in academic_years:
        AcademicYear.objects.create(name=year_value, is_active=True)
    
    # Add semesters
    semesters = [
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
    ]
    
    for sem_value, sem_name in semesters:
        Semester.objects.create(name=sem_value, is_active=True)

def remove_default_academic_years_semesters(apps, schema_editor):
    AcademicYear = apps.get_model('resources', 'AcademicYear')
    Semester = apps.get_model('resources', 'Semester')
    
    AcademicYear.objects.all().delete()
    Semester.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_default_academic_years_semesters,
            remove_default_academic_years_semesters
        ),
    ]
