from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_page_view, name='analytics_reports'),
    path('download/', views.report_download_view, name='report_download'),
]
