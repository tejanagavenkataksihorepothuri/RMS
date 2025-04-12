from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
import os
import mimetypes

from .models import Resource, Subject, AcademicYear, Semester, ResourceType
from accounts.models import Department, UserHistory

def is_principal_or_hod(user):
    return user.is_principal or user.is_hod

@login_required
def resource_list(request):
    """View for listing resources based on user role and filters."""
    user = request.user
    
    # Get filter parameters
    department_id = request.GET.get('department')
    academic_year_id = request.GET.get('academic_year')
    semester_id = request.GET.get('semester')
    subject_id = request.GET.get('subject')
    resource_type_id = request.GET.get('resource_type')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    resources = Resource.objects.all()
    
    # Filter based on user role
    if user.is_student:
        resources = resources.filter(is_approved=True)
    elif user.is_faculty:
        resources = resources.filter(
            Q(uploaded_by=user) | 
            Q(subject__department=user.department, is_approved=True)
        )
    elif user.is_hod:
        if user.department:
            resources = resources.filter(subject__department=user.department)
    # Principal can see all resources
    
    # Apply filters
    if department_id:
        resources = resources.filter(subject__department_id=department_id)
    
    if academic_year_id:
        resources = resources.filter(subject__academic_year_id=academic_year_id)
    
    if semester_id:
        resources = resources.filter(subject__semester_id=semester_id)
    
    if subject_id:
        resources = resources.filter(subject_id=subject_id)
    
    if resource_type_id:
        resources = resources.filter(resource_type_id=resource_type_id)
    
    if search_query:
        resources = resources.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(subject__name__icontains=search_query)
        )
    
    # Order resources
    resources = resources.order_by('-created_at')
    
    # Get filter options
    departments = Department.objects.all()
    academic_years = AcademicYear.objects.filter(is_active=True)
    semesters = Semester.objects.filter(is_active=True)
    subjects = Subject.objects.all()
    resource_types = ResourceType.objects.all()
    
    # Pagination
    paginator = Paginator(resources, 20)  # Show 20 resources per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Resources - Usha Rama College of Engineering Resource Management System',
        'resources': page_obj,
        'departments': departments,
        'academic_years': academic_years,
        'semesters': semesters,
        'subjects': subjects,
        'resource_types': resource_types,
        'filters': {
            'department': department_id,
            'academic_year': academic_year_id,
            'semester': semester_id,
            'subject': subject_id,
            'resource_type': resource_type_id,
            'search': search_query,
        }
    }
    
    return render(request, 'resources/resource_list.html', context)

@login_required
def upload_resource(request):
    """View for uploading a new resource."""
    user = request.user
    
    # Only faculty, HOD, and principal can upload resources
    if not (user.is_faculty or user.is_hod or user.is_principal):
        messages.error(request, "You don't have permission to upload resources.")
        return redirect('dashboard')
    
    # Get filter options
    departments = Department.objects.all()
    academic_years = AcademicYear.objects.filter(is_active=True)
    semesters = Semester.objects.filter(is_active=True)
    resource_types = ResourceType.objects.all()
    
    # Get subjects based on user role and department
    if user.is_principal:
        subjects = Subject.objects.all()
    elif user.is_hod and user.department:
        subjects = Subject.objects.filter(department=user.department)
    elif user.is_faculty and user.department:
        subjects = Subject.objects.filter(department=user.department)
    else:
        subjects = Subject.objects.none()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        subject_id = request.POST.get('subject')
        resource_type_id = request.POST.get('resource_type')
        file = request.FILES.get('file')
        
        # Validate data
        if not all([title, subject_id, resource_type_id, file]):
            messages.error(request, "All fields are required.")
            return render(request, 'resources/upload_resource.html', {
                'departments': departments,
                'academic_years': academic_years,
                'semesters': semesters,
                'subjects': subjects,
                'resource_types': resource_types,
            })
        
        try:
            subject = Subject.objects.get(id=subject_id)
            resource_type = ResourceType.objects.get(id=resource_type_id)
            
            # Check if user has permission to upload to this subject
            if not user.is_principal and subject.department != user.department:
                messages.error(request, "You don't have permission to upload resources for this subject.")
                return redirect('upload_resource')
            
            # Create resource
            resource = Resource.objects.create(
                title=title,
                description=description,
                file=file,
                subject=subject,
                resource_type=resource_type,
                uploaded_by=user,
                is_approved=user.is_principal or user.is_hod  # Auto-approve for principal and HOD
            )
            
            # Log action
            UserHistory.objects.create(
                user=user,
                action='UPLOAD',
                description=f"Uploaded resource: {resource.title} for {subject.name}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f"Resource '{title}' uploaded successfully.")
            return redirect('resource_list')
        
        except Exception as e:
            messages.error(request, f"Error uploading resource: {str(e)}")
    
    context = {
        'title': 'Upload Resource - Usha Rama College of Engineering Resource Management System',
        'departments': departments,
        'academic_years': academic_years,
        'semesters': semesters,
        'subjects': subjects,
        'resource_types': resource_types,
    }
    
    return render(request, 'resources/upload_resource.html', context)

@login_required
def resource_detail(request, resource_id):
    """View for displaying resource details."""
    user = request.user
    resource = get_object_or_404(Resource, id=resource_id)
    
    # Check if user has permission to view this resource
    if user.is_student and not resource.is_approved:
        messages.error(request, "You don't have permission to view this resource.")
        return redirect('resource_list')
    
    if user.is_faculty and not (resource.uploaded_by == user or resource.subject.department == user.department):
        messages.error(request, "You don't have permission to view this resource.")
        return redirect('resource_list')
    
    if user.is_hod and resource.subject.department != user.department:
        messages.error(request, "You don't have permission to view this resource.")
        return redirect('resource_list')
    
    context = {
        'title': f'{resource.title} - Usha Rama College of Engineering Resource Management System',
        'resource': resource,
    }
    
    return render(request, 'resources/resource_detail.html', context)

@login_required
def download_resource(request, resource_id):
    """View for downloading a resource file."""
    user = request.user
    resource = get_object_or_404(Resource, id=resource_id)
    
    # Check if user has permission to download this resource
    if user.is_student and not resource.is_approved:
        messages.error(request, "You don't have permission to download this resource.")
        return redirect('resource_list')
    
    if user.is_faculty and not (resource.uploaded_by == user or resource.subject.department == user.department):
        messages.error(request, "You don't have permission to download this resource.")
        return redirect('resource_list')
    
    if user.is_hod and resource.subject.department != user.department:
        messages.error(request, "You don't have permission to download this resource.")
        return redirect('resource_list')
    
    # Log download action
    UserHistory.objects.create(
        user=user,
        action='OTHER',
        description=f"Downloaded resource: {resource.title}",
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    # Prepare file for download
    file_path = resource.file.path
    file_name = os.path.basename(file_path)
    
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read())
    
    content_type, encoding = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    
    response['Content-Type'] = content_type
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    
    return response

@login_required
@require_POST
def delete_resource(request, resource_id):
    """View for deleting a resource."""
    user = request.user
    resource = get_object_or_404(Resource, id=resource_id)
    
    # Check if user has permission to delete this resource
    if user.is_principal or (user.is_hod and resource.subject.department == user.department) or (user.is_faculty and resource.uploaded_by == user):
        try:
            resource_title = resource.title
            resource_subject = resource.subject.name
            
            # Delete resource
            resource.file.delete(save=False)  # Delete the file from storage
            resource.delete()
            
            # Log action
            UserHistory.objects.create(
                user=user,
                action='DELETE',
                description=f"Deleted resource: {resource_title} for {resource_subject}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f"Resource '{resource_title}' deleted successfully.")
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': "You don't have permission to delete this resource."}, status=403)

@login_required
@require_POST
def approve_resource(request, resource_id):
    """View for approving a resource (for HOD and Principal)."""
    user = request.user
    resource = get_object_or_404(Resource, id=resource_id)
    
    # Check if user has permission to approve this resource
    if user.is_principal or (user.is_hod and resource.subject.department == user.department):
        try:
            resource.is_approved = True
            resource.save()
            
            # Log action
            UserHistory.objects.create(
                user=user,
                action='OTHER',
                description=f"Approved resource: {resource.title} for {resource.subject.name}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f"Resource '{resource.title}' approved successfully.")
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': "You don't have permission to approve this resource."}, status=403)

@login_required
def get_subjects(request):
    """AJAX view for getting subjects based on department, academic year, and semester."""
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
    
    subjects_data = [{'id': subject.id, 'name': subject.name} for subject in subjects]
    
    return JsonResponse({'subjects': subjects_data})

@login_required
def add_subject(request):
    """View for HODs to add subjects to their department."""
    if not request.user.is_hod:
        messages.error(request, "You don't have permission to add subjects.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        academic_year_id = request.POST.get('academic_year')
        semester_id = request.POST.get('semester')
        description = request.POST.get('description')
        
        # Check if subject code already exists in the department
        if Subject.objects.filter(code=code, department=request.user.department).exists():
            messages.error(request, 'A subject with this code already exists in your department.')
            return redirect('add_subject')
        
        # Create new subject
        subject = Subject.objects.create(
            name=name,
            code=code,
            department=request.user.department,
            academic_year_id=academic_year_id,
            semester_id=semester_id,
            description=description
        )
        
        messages.success(request, f'Subject {subject.name} has been added successfully.')
        return redirect('dashboard')
    
    context = {
        'title': 'Add Subject',
        'academic_years': AcademicYear.objects.filter(is_active=True),
        'semesters': Semester.objects.filter(is_active=True)
    }
    return render(request, 'resources/add_subject.html', context)

@login_required
@user_passes_test(is_principal_or_hod)
def resource_type_list(request):
    """View for listing and managing resource types."""
    resource_types = ResourceType.objects.all()
    
    context = {
        'title': 'Resource Types',
        'resource_types': resource_types
    }
    return render(request, 'resources/resource_type_list.html', context)

@login_required
@user_passes_test(is_principal_or_hod)
def add_resource_type(request):
    """View for adding a new resource type."""
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if not name:
            messages.error(request, 'Resource type name is required.')
            return redirect('resource_type_list')
            
        if ResourceType.objects.filter(name=name).exists():
            messages.error(request, 'Resource type with this name already exists.')
            return redirect('resource_type_list')
            
        ResourceType.objects.create(name=name)
        messages.success(request, f'Resource type "{name}" has been added successfully.')
        return redirect('resource_type_list')
        
    return redirect('resource_type_list')

@login_required
@user_passes_test(is_principal_or_hod)
def delete_resource_type(request, type_id):
    """View for deleting a resource type."""
    try:
        resource_type = ResourceType.objects.get(pk=type_id)
        
        # Check if there are any resources using this type
        if resource_type.resources.exists():
            messages.error(request, f'Cannot delete "{resource_type.name}" as it is being used by some resources.')
            return redirect('resource_type_list')
            
        resource_type.delete()
        messages.success(request, f'Resource type "{resource_type.name}" has been deleted successfully.')
        return redirect('resource_type_list')
        
    except ResourceType.DoesNotExist:
        messages.error(request, 'Resource type not found.')
        return redirect('resource_type_list')

@login_required
def edit_resource(request, resource_id):
    """View for editing an existing resource."""
    try:
        resource = Resource.objects.select_related('subject', 'resource_type').get(pk=resource_id)
        
        # Check if user has permission to edit this resource
        if not (request.user.is_principal or request.user.is_hod or resource.uploaded_by == request.user):
            messages.error(request, 'You do not have permission to edit this resource.')
            return redirect('resource_list')
        
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            resource_type_id = request.POST.get('resource_type')
            subject_id = request.POST.get('subject')
            
            if not all([title, resource_type_id, subject_id]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('edit_resource', resource_id=resource_id)
            
            try:
                resource_type = ResourceType.objects.get(pk=resource_type_id)
                subject = Subject.objects.get(pk=subject_id)
                
                # Update resource
                resource.title = title
                resource.description = description
                resource.resource_type = resource_type
                resource.subject = subject
                
                # Handle file upload if provided
                if request.FILES.get('file'):
                    # Delete old file
                    if resource.file:
                        old_file_path = resource.file.path
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    
                    resource.file = request.FILES['file']
                
                resource.save()
                
                messages.success(request, 'Resource updated successfully.')
                return redirect('resource_list')
                
            except (ResourceType.DoesNotExist, Subject.DoesNotExist):
                messages.error(request, 'Invalid resource type or subject.')
                return redirect('edit_resource', resource_id=resource_id)
        
        # Get data for form
        academic_years = AcademicYear.objects.filter(is_active=True)
        semesters = Semester.objects.filter(is_active=True)
        resource_types = ResourceType.objects.all()
        
        if request.user.is_principal:
            departments = Department.objects.all()
        elif request.user.is_hod:
            departments = [request.user.department]
        else:
            departments = [request.user.department]
        
        context = {
            'title': 'Edit Resource',
            'resource': resource,
            'departments': departments,
            'academic_years': academic_years,
            'semesters': semesters,
            'resource_types': resource_types,
            'current_department': resource.subject.department.code if resource.subject else None,
            'current_year': resource.subject.academic_year.name if resource.subject else None,
            'current_semester': resource.subject.semester.name if resource.subject else None,
        }
        return render(request, 'resources/edit_resource.html', context)
        
    except Resource.DoesNotExist:
        messages.error(request, 'Resource not found.')
        return redirect('resource_list')
