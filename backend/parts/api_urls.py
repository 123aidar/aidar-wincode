from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartViewSet

router = DefaultRouter()
router.register('', PartViewSet, basename='part')

urlpatterns = [path('', include(router.urls))]
