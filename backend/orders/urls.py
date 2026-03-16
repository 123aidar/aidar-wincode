from django.urls import path
from . import views

urlpatterns = [
    path('', views.orders_list_view, name='orders_list'),
    path('create/', views.order_create_view, name='order_create'),
    path('<int:pk>/', views.order_detail_view, name='order_detail'),
    path('<int:pk>/status/', views.order_update_status_view, name='order_update_status'),
    path('<int:pk>/add-service/', views.order_add_service_view, name='order_add_service'),
    path('<int:pk>/add-part/', views.order_add_part_view, name='order_add_part'),
    path('<int:pk>/notes/', views.order_update_notes_view, name='order_update_notes'),
    path('<int:order_id>/repair-report/', views.repair_report_view, name='repair_report'),
    path('<int:order_id>/repair-report/pdf/', views.repair_report_pdf_view, name='repair_report_pdf'),
    path('<int:pk>/delete/', views.order_delete_view, name='order_delete'),
]
