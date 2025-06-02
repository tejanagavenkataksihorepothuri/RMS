from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_faculty, name='add_faculty'),
    path('employees/bulk-add/', views.bulk_add_employees, name='bulk_add_employees'),
    path('employees/export/', views.export_employees, name='export_employees'),
    path('employees/<int:employee_id>/history/', views.employee_history, name='employee_history'),
    path('employees/<int:employee_id>/delete/', views.delete_employee, name='delete_employee'),
] 