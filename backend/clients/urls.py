from django.urls import path
from . import views

urlpatterns = [
    path('', views.clients_list_view, name='clients_list'),
    path('create/', views.client_create_view, name='client_create'),
    path('<int:pk>/', views.client_detail_view, name='client_detail'),
    path('<int:pk>/edit/', views.client_edit_view, name='client_edit'),
    path('<int:pk>/delete/', views.client_delete_view, name='client_delete'),
]
