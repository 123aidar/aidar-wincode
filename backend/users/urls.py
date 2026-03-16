from django.urls import path
from . import views

urlpatterns = [
    path('', views.users_list_view, name='users_list'),
    path('create/', views.user_create_view, name='user_create'),
    path('<int:pk>/edit/', views.user_edit_view, name='user_edit'),
    path('<int:pk>/delete/', views.user_delete_view, name='user_delete'),
]
