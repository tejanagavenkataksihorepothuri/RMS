from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', login_required(views.home), name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('department/add/', views.add_department, name='add_department'),
    path('department/delete/<str:code>/', views.delete_department, name='delete_department'),
    path('department/settings/', views.department_settings, name='department_settings'),
    path('faculty/add/', views.add_faculty, name='add_faculty'),
    path('faculty/add/hod/', views.add_faculty_hod, name='add_faculty_hod'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employee/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employee/delete/<int:pk>/', views.employee_delete, name='employee_delete'),
]