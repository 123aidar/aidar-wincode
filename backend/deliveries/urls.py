from django.urls import path
from . import views

urlpatterns = [
    path('', views.deliveries_list_view, name='deliveries_list'),
    path('create/', views.delivery_create_view, name='delivery_create'),
    path('<int:pk>/', views.delivery_detail_view, name='delivery_detail'),
    path('<int:pk>/receive/', views.delivery_receive_view, name='delivery_receive'),
    path('<int:pk>/cancel/', views.delivery_cancel_view, name='delivery_cancel'),
    path('<int:pk>/invoice/', views.delivery_invoice_view, name='delivery_invoice'),
    path('<int:pk>/delete/', views.delivery_delete_view, name='delivery_delete'),
]
