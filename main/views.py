from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from resources.models import Resource, Subject, AcademicYear, Semester
from accounts.models import Department, User
from django.shortcuts import get_object_or_404

def home(request):
    """Home page view for the website."""
    return redirect('dashboard')

@login_required
def dashboard(request):
    """Dashboard view for authenticated users."""
    user = request.user
    context = {
        'title': 'Dashboard - Usha Rama College of Engineering Resource Management System',
        'user': user,
    }
    
    # Different dashboard views based on user role
    if user.is_principal:
        # Principal dashboard
        context['departments'] = Department.objects.all()
        context['academic_years'] = AcademicYear.objects.all()
        context['total_faculty'] = User.objects.filter(role='FACULTY').count()
        context['total_hods'] = User.objects.filter(role='HOD').count()
        context['total_students'] = User.objects.filter(role='STUDENT').count()
        context['total_resources'] = Resource.objects.count()
        return render(request, 'main/dashboard_principal.html', context)
    
    elif user.is_hod:
        # HOD dashboard
        if user.department:
            # Faculty statistics
            context['faculty_count'] = User.objects.filter(department=user.department, role='FACULTY').count()
            context['faculty_members'] = User.objects.filter(department=user.department, role='FACULTY')
            
            # Subject statistics
            context['subject_count'] = Subject.objects.filter(department=user.department).count()
            context['subjects'] = Subject.objects.filter(department=user.department)
            
            # Resource statistics
            context['resource_count'] = Resource.objects.filter(subject__department=user.department).count()
            context['recent_resources'] = Resource.objects.filter(
                subject__department=user.department
            ).order_by('-created_at')[:5]
            
            # Student statistics
            context['student_count'] = User.objects.filter(department=user.department, role='STUDENT').count()
            
            # Faculty activities (placeholder - implement actual activity tracking)
            context['faculty_activities'] = []
            
        return render(request, 'main/dashboard_hod.html', context)
    
    elif user.is_faculty:
        # Faculty dashboard
        context['subjects'] = Subject.objects.filter(department=user.department)
        resources = Resource.objects.filter(uploaded_by=user)
        context['resources'] = resources
        context['pending_resources_count'] = resources.filter(is_approved=False).count()
        return render(request, 'main/dashboard_faculty.html', context)
    
    else:
        # Student dashboard
        context['departments'] = Department.objects.all()
        context['academic_years'] = AcademicYear.objects.filter(is_active=True)
        context['semesters'] = Semester.objects.filter(is_active=True)
        
        # Filter resources based on selected filters
        department_id = request.GET.get('department')
        academic_year_id = request.GET.get('academic_year')
        semester_id = request.GET.get('semester')
        
        subjects = Subject.objects.all()
        
        if department_id:
            subjects = subjects.filter(department_id=department_id)
        if academic_year_id:
            subjects = subjects.filter(academic_year_id=academic_year_id)
        if semester_id:
            subjects = subjects.filter(semester_id=semester_id)
        
        context['subjects'] = subjects
        
        subject_id = request.GET.get('subject')
        if subject_id:
            context['selected_subject'] = Subject.objects.get(id=subject_id)
            context['resources'] = Resource.objects.filter(subject_id=subject_id, is_approved=True)
        
        return render(request, 'main/dashboard_student.html', context)

def is_principal(user):
    return user.is_authenticated and user.is_principal

def is_principal_or_hod(user):
    return user.is_authenticated and (user.is_principal or user.is_hod)

def is_hod(user):
    return user.is_authenticated and user.is_hod

@login_required
@user_passes_test(is_principal)
def add_department(request):
    """View for adding a new department. Only accessible by principal."""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        
        if Department.objects.filter(code=code).exists():
            messages.error(request, 'Department with this code already exists.')
            return redirect('add_department')
            
        Department.objects.create(name=name, code=code)
        messages.success(request, f'Department {name} has been added successfully.')
        return redirect('dashboard')
        
    return render(request, 'main/add_department.html', {'title': 'Add Department'})

@login_required
@user_passes_test(is_principal)
def delete_department(request, code):
    """View for deleting a department. Only accessible by principal."""
    department = get_object_or_404(Department, code=code)
    
    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f'Department {name} has been deleted successfully.')
        return redirect('dashboard')
        
    return render(request, 'main/delete_department.html', {
        'title': 'Delete Department',
        'department': department
    })

@login_required
@user_passes_test(is_principal)
def add_academic_year(request):
    """View for adding a new academic year. Only accessible by principal."""
    if request.method == 'POST':
        name = request.POST.get('name')
        is_active = request.POST.get('is_active') == 'on'
        
        if AcademicYear.objects.filter(name=name).exists():
            messages.error(request, 'Academic year with this name already exists.')
            return redirect('add_academic_year')
            
        AcademicYear.objects.create(name=name, is_active=is_active)
        messages.success(request, f'Academic year {name} has been added successfully.')
        return redirect('dashboard')
        
    return render(request, 'main/add_academic_year.html', {'title': 'Add Academic Year'})

@login_required
@user_passes_test(is_principal)
def delete_academic_year(request, id):
    """View for deleting an academic year. Only accessible by principal."""
    academic_year = get_object_or_404(AcademicYear, id=id)
    
    if request.method == 'POST':
        name = academic_year.name
        academic_year.delete()
        messages.success(request, f'Academic year {name} has been deleted successfully.')
        return redirect('dashboard')
        
    return render(request, 'main/delete_academic_year.html', {
        'title': 'Delete Academic Year',
        'academic_year': academic_year
    })

@login_required
@user_passes_test(is_hod)
def department_settings(request):
    """View for HOD to manage their department settings."""
    department = request.user.department
    subjects = Subject.objects.filter(department=department).select_related('academic_year', 'semester')
    academic_years = AcademicYear.objects.filter(is_active=True)
    semesters = Semester.objects.filter(is_active=True)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_subject':
            code = request.POST.get('code')
            name = request.POST.get('name')
            academic_year_id = request.POST.get('academic_year')
            semester_id = request.POST.get('semester')
            description = request.POST.get('description')
            
            if not Subject.objects.filter(code=code, department=department).exists():
                Subject.objects.create(
                    code=code,
                    name=name,
                    department=department,
                    academic_year_id=academic_year_id,
                    semester_id=semester_id,
                    description=description
                )
                messages.success(request, f'Subject {name} has been added successfully.')
            else:
                messages.error(request, 'Subject with this code already exists in your department.')
            
            return redirect('department_settings')
    
    context = {
        'title': 'Department Settings',
        'department': department,
        'subjects': subjects,
        'academic_years': academic_years,
        'semesters': semesters
    }
    return render(request, 'main/department_settings.html', context)

@login_required
@user_passes_test(is_hod)
def add_faculty_hod(request):
    """View for HOD to add faculty to their department."""
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        id_number = request.POST.get('id_number')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'User with this email already exists.')
            return redirect('add_faculty_hod')
            
        # Check if ID number already exists
        if User.objects.filter(id_number=id_number).exists():
            messages.error(request, 'User with this ID number already exists.')
            return redirect('add_faculty_hod')
            
        try:
            # Create user with FACULTY role in HOD's department
            user = User.objects.create_user(
                email=email,
                password='temp123',  # Temporary password
                first_name=first_name,
                last_name=last_name,
                department=request.user.department,
                role='FACULTY',
                id_number=id_number
            )
            messages.success(request, f'Faculty {user.get_full_name()} has been added successfully.')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error creating faculty: {str(e)}')
            return redirect('add_faculty_hod')
        
    context = {
        'title': 'Add Faculty',
        'department': request.user.department
    }
    return render(request, 'main/add_faculty_hod.html', context)

@login_required
@user_passes_test(is_principal)
def add_faculty(request):
    """View for principal to add faculty to any department."""
    departments = Department.objects.all()
    
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        department_code = request.POST.get('department')
        role = request.POST.get('role', 'FACULTY')
        id_number = request.POST.get('id_number')
        
        # Validate role
        if role not in ['FACULTY', 'HOD']:
            messages.error(request, 'Invalid role selected.')
            return redirect('add_faculty')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'User with this email already exists.')
            return redirect('add_faculty')
            
        # Check if ID number already exists
        if User.objects.filter(id_number=id_number).exists():
            messages.error(request, 'User with this ID number already exists.')
            return redirect('add_faculty')
            
        try:
            department = Department.objects.get(code=department_code)
            
            # Create user
            user = User.objects.create_user(
                email=email,
                password='temp123',  # Temporary password
                first_name=first_name,
                last_name=last_name,
                department=department,
                role=role,
                id_number=id_number
            )
            
            messages.success(request, f'{user.get_role_display()} {user.get_full_name()} has been added successfully.')
            return redirect('dashboard')
            
        except Department.DoesNotExist:
            messages.error(request, 'Selected department does not exist.')
            return redirect('add_faculty')
        except Exception as e:
            messages.error(request, f'Error creating faculty: {str(e)}')
            return redirect('add_faculty')
    
    context = {
        'title': 'Add Faculty',
        'departments': departments
    }
    return render(request, 'main/add_faculty.html', context)

@login_required
@user_passes_test(is_principal_or_hod)
def employee_list(request):
    """View for listing employees (faculty members)."""
    if request.user.is_principal:
        employees = User.objects.filter(role__in=['FACULTY', 'HOD']).select_related('department')
    else:  # HOD
        employees = User.objects.filter(department=request.user.department, role='FACULTY')
    
    context = {
        'title': 'Employees',
        'employees': employees
    }
    return render(request, 'main/employee_list.html', context)

@login_required
@user_passes_test(is_principal_or_hod)
def employee_detail(request, pk):
    """View for showing employee details."""
    try:
        if request.user.is_principal:
            employee = User.objects.select_related('department').get(pk=pk, role__in=['FACULTY', 'HOD'])
        else:  # HOD
            employee = User.objects.select_related('department').get(
                pk=pk, 
                department=request.user.department,
                role='FACULTY'
            )
            
        context = {
            'title': f'Employee Details - {employee.get_full_name()}',
            'employee': employee
        }
        return render(request, 'main/employee_detail.html', context)
        
    except User.DoesNotExist:
        messages.error(request, 'Employee not found.')
        return redirect('employee_list')

@login_required
@user_passes_test(is_principal_or_hod)
def employee_delete(request, pk):
    """View for deleting an employee."""
    try:
        if request.user.is_principal:
            employee = User.objects.get(pk=pk, role__in=['FACULTY', 'HOD'])
        else:  # HOD
            employee = User.objects.get(
                pk=pk, 
                department=request.user.department,
                role='FACULTY'
            )
            
        if request.method == 'POST':
            employee_name = employee.get_full_name()
            employee.delete()
            messages.success(request, f'Employee {employee_name} has been deleted successfully.')
            return redirect('employee_list')
            
        context = {
            'title': f'Delete Employee - {employee.get_full_name()}',
            'employee': employee
        }
        return render(request, 'main/employee_delete.html', context)
        
    except User.DoesNotExist:
        messages.error(request, 'Employee not found.')
        return redirect('employee_list')

def about(request):
    """About page view."""
    context = {
        'title': 'About - Usha Rama College of Engineering Resource Management System'
    }
    return render(request, 'main/about.html', context)

def contact(request):
    """Contact page view."""
    context = {
        'title': 'Contact - Usha Rama College of Engineering Resource Management System'
    }
    return render(request, 'main/contact.html', context)
