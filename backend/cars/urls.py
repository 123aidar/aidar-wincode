from django.urls import path
from . import views

urlpatterns = [
    path('', views.cars_list_view, name='cars_list'),
    path('create/', views.car_create_view, name='car_create'),
    path('<int:pk>/edit/', views.car_edit_view, name='car_edit'),
    path('<int:pk>/delete/', views.car_delete_view, name='car_delete'),
]
