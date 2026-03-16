from django.urls import path
from . import views

urlpatterns = [
    path('', views.payments_list_view, name='payments_list'),
    path('create/<int:order_pk>/', views.payment_create_view, name='payment_create'),
    path('receipt/<int:payment_id>/', views.payment_receipt_view, name='payment_receipt'),
    path('<int:pk>/delete/', views.payment_delete_view, name='payment_delete'),
]
