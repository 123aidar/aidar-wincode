from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets
from .models import Client
from .serializers import ClientSerializer
from users.permissions import IsAdminOrManagerOrMechanic


@login_required
def clients_list_view(request):
    q = request.GET.get('q', '')
    clients = Client.objects.all()
    if q:
        clients = clients.filter(name__icontains=q) | clients.filter(phone__icontains=q)
    return render(request, 'clients/list.html', {'clients': clients, 'q': q})


@login_required
def client_detail_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'clients/detail.html', {'client': client})


@login_required
def client_create_view(request):
    if request.user.role == 'mechanic':
        return redirect('clients_list')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        notes = request.POST.get('notes', '').strip()
        if Client.objects.filter(phone=phone).exists():
            messages.error(request, 'Client with this phone already exists.')
        else:
            Client.objects.create(name=name, phone=phone, email=email, address=address, notes=notes)
            messages.success(request, f'Клиент {name} создан.')
            return redirect('clients_list')
    return render(request, 'clients/create.html')


@login_required
def client_edit_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.user.role == 'mechanic':
        return redirect('client_detail', pk=pk)
    if request.method == 'POST':
        client.name = request.POST.get('name', '').strip()
        client.phone = request.POST.get('phone', '').strip()
        client.email = request.POST.get('email', '').strip()
        client.address = request.POST.get('address', '').strip()
        client.notes = request.POST.get('notes', '').strip()
        client.save()
        messages.success(request, f'Клиент {client.name} обновлён.')
        return redirect('client_detail', pk=client.pk)
    return render(request, 'clients/edit.html', {'client': client})


@login_required
def client_delete_view(request, pk):
    if request.user.role != 'admin':
        return redirect('clients_list')
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, f'Клиент «{client.name}» удалён.')
        return redirect('clients_list')
    return redirect('clients_list')


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAdminOrManagerOrMechanic]
    search_fields = ['name', 'phone', 'email']
