from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets
from .models import Supplier
from .serializers import SupplierSerializer
from users.permissions import IsAdminOrManager


@login_required
def suppliers_list_view(request):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    suppliers = Supplier.objects.all()
    return render(request, 'suppliers/list.html', {'suppliers': suppliers})


@login_required
def supplier_create_view(request):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    if request.method == 'POST':
        Supplier.objects.create(
            name=request.POST.get('name', '').strip(),
            contact_person=request.POST.get('contact_person', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            email=request.POST.get('email', '').strip(),
            address=request.POST.get('address', '').strip(),
            notes=request.POST.get('notes', '').strip(),
        )
        messages.success(request, 'Поставщик создан.')
        return redirect('suppliers_list')
    return render(request, 'suppliers/create.html')


@login_required
def supplier_edit_view(request, pk):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.name = request.POST.get('name', '').strip()
        supplier.contact_person = request.POST.get('contact_person', '').strip()
        supplier.phone = request.POST.get('phone', '').strip()
        supplier.email = request.POST.get('email', '').strip()
        supplier.address = request.POST.get('address', '').strip()
        supplier.notes = request.POST.get('notes', '').strip()
        supplier.save()
        messages.success(request, 'Поставщик обновлён.')
        return redirect('suppliers_list')
    return render(request, 'suppliers/edit.html', {'supplier': supplier})


@login_required
def supplier_delete_view(request, pk):
    if request.user.role != 'admin':
        return redirect('suppliers_list')
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, f'Поставщик «{supplier.name}» удалён.')
        return redirect('suppliers_list')
    return redirect('suppliers_list')


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAdminOrManager]
    search_fields = ['name', 'phone']
