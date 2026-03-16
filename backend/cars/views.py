from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets
from .models import Car
from .serializers import CarSerializer
from clients.models import Client
from users.permissions import IsAdminOrManagerOrMechanic


@login_required
def cars_list_view(request):
    q = request.GET.get('q', '')
    cars = Car.objects.select_related('client').all()
    if q:
        cars = cars.filter(license_plate__icontains=q) | cars.filter(brand__icontains=q) | cars.filter(client__name__icontains=q)
    return render(request, 'cars/list.html', {'cars': cars, 'q': q})


@login_required
def car_create_view(request):
    if request.user.role == 'mechanic':
        return redirect('cars_list')
    clients = Client.objects.all()
    if request.method == 'POST':
        client_id = request.POST.get('client')
        brand = request.POST.get('brand', '').strip()
        model = request.POST.get('model', '').strip()
        year = request.POST.get('year', 0)
        vin = request.POST.get('vin', '').strip()
        license_plate = request.POST.get('license_plate', '').strip()
        color = request.POST.get('color', '').strip()
        mileage = request.POST.get('mileage', 0) or 0
        Car.objects.create(
            client_id=client_id, brand=brand, model=model,
            year=int(year), vin=vin, license_plate=license_plate,
            color=color, mileage=int(mileage)
        )
        messages.success(request, f'{brand} {model} зарегистрирован.')
        return redirect('cars_list')
    return render(request, 'cars/create.html', {'clients': clients})


@login_required
def car_edit_view(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.user.role == 'mechanic':
        return redirect('cars_list')
    clients = Client.objects.all()
    if request.method == 'POST':
        car.client_id = request.POST.get('client')
        car.brand = request.POST.get('brand', '').strip()
        car.model = request.POST.get('model', '').strip()
        car.year = int(request.POST.get('year', car.year))
        car.vin = request.POST.get('vin', '').strip()
        car.license_plate = request.POST.get('license_plate', '').strip()
        car.color = request.POST.get('color', '').strip()
        car.mileage = int(request.POST.get('mileage', car.mileage) or 0)
        car.save()
        messages.success(request, f'{car.brand} {car.model} обновлён.')
        return redirect('cars_list')
    return render(request, 'cars/edit.html', {'car': car, 'clients': clients})


@login_required
def car_delete_view(request, pk):
    if request.user.role != 'admin':
        return redirect('cars_list')
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        car.delete()
        messages.success(request, f'Автомобиль «{car.brand} {car.model}» удалён.')
        return redirect('cars_list')
    return redirect('cars_list')


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.select_related('client').all()
    serializer_class = CarSerializer
    permission_classes = [IsAdminOrManagerOrMechanic]
    search_fields = ['brand', 'model', 'license_plate', 'vin']
    filterset_fields = ['client']
