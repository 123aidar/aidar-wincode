from django.urls import path
from . import views

urlpatterns = [
    path('', views.suppliers_list_view, name='suppliers_list'),
    path('create/', views.supplier_create_view, name='supplier_create'),
    path('<int:pk>/edit/', views.supplier_edit_view, name='supplier_edit'),
    path('<int:pk>/delete/', views.supplier_delete_view, name='supplier_delete'),
]
