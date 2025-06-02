from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
import csv
import io
from .models import User, Department, UserHistory
from .forms import UserProfileForm
from resources.models import Resource

def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                
                # Log login action
                UserHistory.objects.create(
                    user=user,
                    action='LOGIN',
                    description=f"User logged in from {request.META.get('REMOTE_ADDR')}",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                messages.success(request, f"Welcome back, {user.get_full_name()}!")
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """User logout view."""
    if request.user.is_authenticated:
        # Log logout action
        UserHistory.objects.create(
            user=request.user,
            action='LOGOUT',
            description=f"User logged out from {request.META.get('REMOTE_ADDR')}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        logout(request)
        messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
def profile(request):
    """User profile view."""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    
    context = {
        'user': user,
        'form': form,
        'title': 'Profile - Usha Rama College of Engineering Resource Management System'
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def change_password(request):
    """Change password view."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'title': 'Change Password - Usha Rama College of Engineering Resource Management System'
    }
    return render(request, 'accounts/change_password.html', context)

@login_required
def employee_list(request):
    """View for listing employees (accessible by Principal and HODs)."""
    user = request.user
    
    if not (user.is_principal or user.is_hod):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    # Filter employees based on user role
    if user.is_principal:
        employees = User.objects.exclude(role='STUDENT').order_by('role', 'department__name', 'first_name')
    elif user.is_hod and user.department:
        employees = User.objects.filter(department=user.department).exclude(id=user.id).order_by('role', 'first_name')
    else:
        employees = User.objects.none()
    
    # Pagination
    paginator = Paginator(employees, 20)  # Show 20 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Employee List - Usha Rama College of Engineering Resource Management System',
        'employees': page_obj,
    }
    
    return render(request, 'accounts/employee_list.html', context)

@login_required
def employee_history(request, employee_id):
    """View for displaying employee history (accessible by Principal and HODs)."""
    user = request.user
    employee = get_object_or_404(User, id=employee_id)
    
    # Check permissions
    if user.is_principal or (user.is_hod and employee.department == user.department):
        history = UserHistory.objects.filter(user=employee).order_by('-timestamp')
        
        # Pagination
        paginator = Paginator(history, 20)  # Show 20 actions per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'title': f'History for {employee.get_full_name()} - Usha Rama College of Engineering Resource Management System',
            'employee': employee,
            'history': page_obj,
        }
        
        return render(request, 'accounts/employee_history.html', context)
    else:
        messages.error(request, "You don't have permission to view this employee's history.")
        return redirect('dashboard')

@login_required
def add_employee(request):
    """View for adding a new employee (accessible by Principal only)."""
    user = request.user
    
    if not user.is_principal:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    departments = Department.objects.all()
    
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        id_number = request.POST.get('id_number')
        phone_number = request.POST.get('phone_number')
        department_id = request.POST.get('department')
        role = request.POST.get('role')
        password = request.POST.get('password')
        
        # Validate data
        if not all([first_name, last_name, email, id_number, department_id, role, password]):
            messages.error(request, "All fields are required.")
            return render(request, 'accounts/add_employee.html', {'departments': departments})
        
        # Check if email or ID number already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'accounts/add_employee.html', {'departments': departments})
        
        if User.objects.filter(id_number=id_number).exists():
            messages.error(request, "ID number already exists.")
            return render(request, 'accounts/add_employee.html', {'departments': departments})
        
        # Create new user
        try:
            department = Department.objects.get(id=department_id)
            new_user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                id_number=id_number,
                phone_number=phone_number,
                department=department,
                role=role
            )
            
            # Log action
            UserHistory.objects.create(
                user=user,
                action='OTHER',
                description=f"Added new employee: {new_user.get_full_name()} ({new_user.get_role_display()})",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f"Employee {new_user.get_full_name()} added successfully.")
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f"Error adding employee: {str(e)}")
    
    context = {
        'title': 'Add Employee - Usha Rama College of Engineering Resource Management System',
        'departments': departments,
    }
    
    return render(request, 'accounts/add_employee.html', context)

@login_required
def bulk_add_employees(request):
    """View for bulk adding employees via CSV (accessible by Principal only)."""
    user = request.user
    
    if not user.is_principal:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if file is CSV
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a CSV file.")
            return redirect('bulk_add_employees')
        
        # Process CSV file
        try:
            csv_data = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            
            success_count = 0
            error_count = 0
            errors = []
            
            for row in csv_reader:
                try:
                    # Get department
                    department = None
                    if row.get('department'):
                        try:
                            department = Department.objects.get(name=row['department'])
                        except Department.DoesNotExist:
                            try:
                                department = Department.objects.get(code=row['department'])
                            except Department.DoesNotExist:
                                errors.append(f"Department not found for {row.get('email')}")
                                error_count += 1
                                continue
                    
                    # Check if user already exists
                    if User.objects.filter(email=row['email']).exists():
                        errors.append(f"Email already exists: {row['email']}")
                        error_count += 1
                        continue
                    
                    if User.objects.filter(id_number=row['id_number']).exists():
                        errors.append(f"ID number already exists: {row['id_number']}")
                        error_count += 1
                        continue
                    
                    # Create user
                    User.objects.create_user(
                        email=row['email'],
                        password=row['password'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        id_number=row['id_number'],
                        phone_number=row.get('phone_number', ''),
                        department=department,
                        role=row['role']
                    )
                    
                    success_count += 1
                
                except Exception as e:
                    errors.append(f"Error processing row for {row.get('email')}: {str(e)}")
                    error_count += 1
            
            # Log action
            UserHistory.objects.create(
                user=user,
                action='OTHER',
                description=f"Bulk added {success_count} employees with {error_count} errors",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            if success_count > 0:
                messages.success(request, f"Successfully added {success_count} employees.")
            
            if error_count > 0:
                messages.warning(request, f"Failed to add {error_count} employees. See details below.")
                for error in errors:
                    messages.error(request, error)
            
            return redirect('employee_list')
        
        except Exception as e:
            messages.error(request, f"Error processing CSV file: {str(e)}")
    
    context = {
        'title': 'Bulk Add Employees - Usha Rama College of Engineering Resource Management System',
    }
    
    return render(request, 'accounts/bulk_add_employees.html', context)

@login_required
@require_POST
def delete_employee(request, employee_id):
    """View for deleting an employee (accessible by Principal and HODs)."""
    user = request.user
    employee = get_object_or_404(User, id=employee_id)
    
    # Check permissions
    if user.is_principal or (user.is_hod and employee.department == user.department and employee.role == 'FACULTY'):
        try:
            employee_name = employee.get_full_name()
            employee_role = employee.get_role_display()
            
            # Delete employee
            employee.delete()
            
            # Log action
            UserHistory.objects.create(
                user=user,
                action='OTHER',
                description=f"Deleted employee: {employee_name} ({employee_role})",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f"Employee {employee_name} deleted successfully.")
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': "You don't have permission to delete this employee."}, status=403)

@login_required
def add_faculty(request):
    """View for HODs and Principal to add faculty members."""
    if not (request.user.is_hod or request.user.is_principal):
        messages.error(request, "You don't have permission to add faculty members.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        id_number = request.POST.get('id_number')
        department_id = request.POST.get('department') if request.user.is_principal else request.user.department.id
        role = request.POST.get('role')
        
        # Validate required fields
        if not all([first_name, last_name, email, phone_number, id_number, role]):
            messages.error(request, 'All fields are required.')
            return redirect('add_faculty')
        
        # Validate role
        if role not in ['HOD', 'FACULTY']:
            messages.error(request, 'Invalid role selected.')
            return redirect('add_faculty')
            
        # Only principal can add HODs
        if role == 'HOD' and not request.user.is_principal:
            messages.error(request, 'Only the principal can add HODs.')
            return redirect('add_faculty')
        
        # Check if email or ID number already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
            return redirect('add_faculty')
            
        if User.objects.filter(id_number=id_number).exists():
            messages.error(request, 'A user with this ID number already exists.')
            return redirect('add_faculty')
        
        try:
            department = Department.objects.get(id=department_id) if department_id else request.user.department
            # Create new user
            new_user = User.objects.create_user(
                email=email,
                password='changeme123',  # Default password that user will change on first login
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                id_number=id_number,
                role=role,
                department=department
            )
            
            # Log action
            UserHistory.objects.create(
                user=request.user,
                action='OTHER',
                description=f"Added new {new_user.get_role_display()}: {new_user.get_full_name()} to {department.name} department",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'{new_user.get_role_display()} {new_user.get_full_name()} has been added successfully.')
            return redirect('employee_list')
        except Department.DoesNotExist:
            messages.error(request, 'Invalid department selected.')
            return redirect('add_faculty')
    
    # Get departments for principal to choose from
    context = {
        'title': 'Add Employee',
        'departments': Department.objects.all() if request.user.is_principal else None
    }
    return render(request, 'accounts/add_employee.html', context)

def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    departments = Department.objects.all()
    
    # Define allowed roles for self-registration
    ALLOWED_ROLES = ['STUDENT', 'FACULTY', 'NON_TEACHING']
    
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        id_number = request.POST.get('id_number')
        phone_number = request.POST.get('phone_number')
        department_id = request.POST.get('department')
        role = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate data
        if not all([first_name, last_name, email, id_number, department_id, role, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return render(request, 'accounts/register.html', {'departments': departments})
        
        # Validate role
        if role not in ALLOWED_ROLES:
            messages.error(request, "Invalid role selected. HOD and Principal roles require administrator approval.")
            return render(request, 'accounts/register.html', {'departments': departments})
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html', {'departments': departments})
        
        # Check if email or ID number already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'accounts/register.html', {'departments': departments})
        
        if User.objects.filter(id_number=id_number).exists():
            messages.error(request, "ID number already exists.")
            return render(request, 'accounts/register.html', {'departments': departments})
        
        # Create new user
        try:
            department = Department.objects.get(id=department_id)
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                id_number=id_number,
                phone_number=phone_number,
                department=department,
                role=role
            )
            
            # Log action
            UserHistory.objects.create(
                user=user,
                action='REGISTER',
                description=f"User registered with role: {user.get_role_display()}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, "Registration successful! Please login with your credentials.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")
    
    context = {
        'title': 'Register - Usha Rama College of Engineering Resource Management System',
        'departments': departments,
    }
    return render(request, 'accounts/register.html', context)

@login_required
def export_employees(request):
    """Export employees data as CSV."""
    if not request.user.is_authenticated or not (request.user.is_principal or request.user.is_hod):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'

    writer = csv.writer(response)
    writer.writerow(['email', 'first_name', 'last_name', 'id_number', 'department', 'phone_number', 'role'])

    # Get employees based on user's role
    if request.user.is_principal:
        employees = User.objects.exclude(is_superuser=True)
    else:  # HOD
        employees = User.objects.filter(department=request.user.department).exclude(is_superuser=True)

    for employee in employees:
        writer.writerow([
            employee.email,
            employee.first_name,
            employee.last_name,
            employee.id_number,
            employee.department.name if employee.department else '',
            employee.phone_number or '',
            employee.role
        ])

    return response
