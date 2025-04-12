import os
import django
from django.db import transaction

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resource_management_system.settings')
django.setup()

from accounts.models import Department

def create_departments():
    departments = [
        {'name': 'Computer Science and Engineering', 'code': 'CSE'},
        {'name': 'Electronics and Communication Engineering', 'code': 'ECE'},
        {'name': 'Electrical and Electronics Engineering', 'code': 'EEE'},
        {'name': 'Mechanical Engineering', 'code': 'MECH'},
        {'name': 'Civil Engineering', 'code': 'CIVIL'},
        {'name': 'Information Technology', 'code': 'IT'},
    ]
    
    try:
        with transaction.atomic():
            for dept in departments:
                Department.objects.get_or_create(
                    code=dept['code'],
                    defaults={'name': dept['name']}
                )
            print("Departments created successfully!")
            
            # Print all departments
            all_departments = Department.objects.all()
            print("\nCurrent Departments:")
            for dept in all_departments:
                print(f"- {dept.name} ({dept.code})")
                
    except Exception as e:
        print(f"Error creating departments: {e}")

if __name__ == '__main__':
    create_departments()
