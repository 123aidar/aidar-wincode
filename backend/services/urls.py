from django.urls import path
from . import views

urlpatterns = [
    path('', views.services_list_view, name='services_list'),
    path('create/', views.service_create_view, name='service_create'),
    path('<int:pk>/edit/', views.service_edit_view, name='service_edit'),
    path('<int:pk>/delete/', views.service_delete_view, name='service_delete'),
]
