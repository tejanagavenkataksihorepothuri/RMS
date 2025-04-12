import os
import django
from django.contrib.auth import get_user_model

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resource_management_system.settings')
django.setup()

def create_admin_user():
    User = get_user_model()
    
    try:
        # Check if admin user already exists
        admin_email = 'ur01@gmail.com'
        existing_user = User.objects.filter(email=admin_email).first()
        
        if existing_user:
            print(f"Found existing user: Email={existing_user.email}, Role={existing_user.role}, Is_superuser={existing_user.is_superuser}")
            # Update the existing user if needed
            existing_user.is_superuser = True
            existing_user.is_staff = True
            existing_user.role = 'PRINCIPAL'
            existing_user.set_password('admin')
            existing_user.save()
            print("Updated existing admin user with new credentials")
        else:
            # Create new superuser
            admin_user = User.objects.create_superuser(
                email=admin_email,
                password='admin',
                first_name='Principal',
                last_name='Admin',
                role='PRINCIPAL'
            )
            print(f"Created new admin user: Email={admin_user.email}, Role={admin_user.role}, Is_superuser={admin_user.is_superuser}")
            
    except Exception as e:
        print(f"Error creating admin user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_admin_user()
