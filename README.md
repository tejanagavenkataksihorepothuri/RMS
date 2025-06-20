# Usha Rama College of Engineering Resource Management System

A comprehensive web-based system for managing educational resources, materials, and files with role-based access control.

## Features

- **Role-Based Access Control**
  - Students: View and download approved resources
  - Faculty: Upload, manage, and delete their own resources
  - HOD: Manage department resources and faculty
  - Principal: Full system administration

- **Resource Management**
  - Upload various file types (documents, videos, images)
  - Organize resources by department, academic year, semester, and subject
  - Search and filter resources
  - Download resources

- **User Management**
  - Add individual employees
  - Bulk add employees via CSV
  - View employee history and actions
  - Delete employees

- **Audit Logging**
  - Track user actions (login, logout, upload, delete)
  - View history by user

## Technology Stack

- **Backend**: Django 5.1
- **Frontend**: Bootstrap 4, jQuery, Font Awesome
- **Database**: SQLite (default), can be configured for PostgreSQL, MySQL, etc.
- **Additional Libraries**:
  - django-crispy-forms: For better form rendering
  - django-import-export: For bulk import/export functionality

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/resource-management-system.git
   cd resource-management-system
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Initial Setup

After installation, follow these steps to set up the system:

1. Log in as the superuser (principal)
2. Create departments
3. Create academic years and semesters
4. Create resource types
5. Add employees (faculty, HODs)
6. Add subjects for each department, academic year, and semester

## Project Structure

- **accounts**: User management, authentication, and history tracking
- **resources**: Resource management, including subjects, academic years, and semesters
- **main**: Core functionality, including dashboard and home page
- **templates**: HTML templates for the application
- **static**: Static files (CSS, JavaScript, images)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)
- [jQuery](https://jquery.com/) #   R M S  
 #   R M S  
 #   R M S  
 #   R M S  
 #   R M S  
 