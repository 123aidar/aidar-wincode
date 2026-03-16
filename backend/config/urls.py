from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls_auth')),
    path('dashboard/', include('analytics.urls')),
    path('analytics/', include('analytics.report_urls')),
    path('clients/', include('clients.urls')),
    path('cars/', include('cars.urls')),
    path('orders/', include('orders.urls')),
    path('services/', include('services.urls')),
    path('parts/', include('parts.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('payments/', include('payments.urls')),
    path('deliveries/', include('deliveries.urls')),
    path('users/', include('users.urls')),
    # API endpoints
    path('api/clients/', include('clients.api_urls')),
    path('api/cars/', include('cars.api_urls')),
    path('api/orders/', include('orders.api_urls')),
    path('api/services/', include('services.api_urls')),
    path('api/parts/', include('parts.api_urls')),
    path('api/suppliers/', include('suppliers.api_urls')),
    path('api/payments/', include('payments.api_urls')),
    path('api/analytics/', include('analytics.api_urls')),
    path('api/users/', include('users.api_urls')),
    # Root redirect
    path('', include('analytics.urls_root')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
