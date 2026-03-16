from django.urls import path
from . import views

urlpatterns = [
    path('', views.parts_list_view, name='parts_list'),
    path('create/', views.part_create_view, name='part_create'),
    path('<int:pk>/edit/', views.part_edit_view, name='part_edit'),
    path('<int:pk>/delete/', views.part_delete_view, name='part_delete'),
]
