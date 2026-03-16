from django.urls import path
from . import views

urlpatterns = [
    path('revenue/monthly/', views.monthly_revenue_api, name='api_monthly_revenue'),
    path('services/popular/', views.service_popularity_api, name='api_service_popularity'),
    path('mechanics/workload/', views.mechanic_workload_api, name='api_mechanic_workload'),
    path('orders/status/', views.order_status_breakdown_api, name='api_order_status'),
]
