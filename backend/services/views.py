from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets
from .models import Service
from .serializers import ServiceSerializer
from users.permissions import IsAdminOrManager


@login_required
def services_list_view(request):
    services = Service.objects.all()
    return render(request, 'services/list.html', {'services': services})


@login_required
def service_create_view(request):
    if request.user.role == 'mechanic':
        return redirect('services_list')
    if request.method == 'POST':
        Service.objects.create(
            name=request.POST.get('name', '').strip(),
            description=request.POST.get('description', '').strip(),
            price=request.POST.get('price', 0),
            duration_minutes=request.POST.get('duration_minutes', 60) or 60,
        )
        messages.success(request, 'Услуга создана.')
        return redirect('services_list')
    return render(request, 'services/create.html')


@login_required
def service_edit_view(request, pk):
    if request.user.role == 'mechanic':
        return redirect('services_list')
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.name = request.POST.get('name', '').strip()
        service.description = request.POST.get('description', '').strip()
        service.price = request.POST.get('price', service.price)
        service.duration_minutes = request.POST.get('duration_minutes', service.duration_minutes) or 60
        service.save()
        messages.success(request, 'Услуга обновлена.')
        return redirect('services_list')
    return render(request, 'services/edit.html', {'service': service})


@login_required
def service_delete_view(request, pk):
    if request.user.role != 'admin':
        return redirect('services_list')
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, f'Услуга «{service.name}» удалена.')
        return redirect('services_list')
    return redirect('services_list')


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrManager]
    search_fields = ['name']
