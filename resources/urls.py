from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_list, name='resource_list'),
    path('upload/', views.upload_resource, name='upload_resource'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('<int:resource_id>/download/', views.download_resource, name='download_resource'),
    path('<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),
    path('<int:resource_id>/approve/', views.approve_resource, name='approve_resource'),
    path('<int:resource_id>/edit/', views.edit_resource, name='edit_resource'),
    path('get-subjects/', views.get_subjects, name='get_subjects'),
    path('types/', views.resource_type_list, name='resource_type_list'),
    path('types/add/', views.add_resource_type, name='add_resource_type'),
    path('types/<int:type_id>/delete/', views.delete_resource_type, name='delete_resource_type'),
]