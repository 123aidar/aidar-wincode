from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets
from .models import Part
from .serializers import PartSerializer
from suppliers.models import Supplier
from users.permissions import IsAdminOrManager


@login_required
def parts_list_view(request):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    q = request.GET.get('q', '')
    parts = Part.objects.select_related('supplier').all()
    if q:
        parts = parts.filter(name__icontains=q) | parts.filter(part_number__icontains=q)
    low_stock = request.GET.get('low_stock')
    if low_stock:
        parts = [p for p in parts if p.is_low_stock]
    return render(request, 'parts/list.html', {'parts': parts, 'q': q})


@login_required
def part_create_view(request):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    suppliers = Supplier.objects.filter(is_active=True)
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier') or None
        Part.objects.create(
            name=request.POST.get('name', '').strip(),
            part_number=request.POST.get('part_number', '').strip(),
            description=request.POST.get('description', '').strip(),
            price=request.POST.get('price', 0),
            cost_price=request.POST.get('cost_price', 0) or 0,
            quantity=request.POST.get('quantity', 0) or 0,
            minimum_stock=request.POST.get('minimum_stock', 5) or 5,
            supplier_id=supplier_id,
        )
        messages.success(request, 'Запчасть добавлена на склад.')
        return redirect('parts_list')
    return render(request, 'parts/create.html', {'suppliers': suppliers})


@login_required
def part_edit_view(request, pk):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    part = get_object_or_404(Part, pk=pk)
    suppliers = Supplier.objects.filter(is_active=True)
    if request.method == 'POST':
        part.name = request.POST.get('name', '').strip()
        part.part_number = request.POST.get('part_number', '').strip()
        part.description = request.POST.get('description', '').strip()
        part.price = request.POST.get('price', part.price)
        part.cost_price = request.POST.get('cost_price', part.cost_price) or 0
        part.quantity = request.POST.get('quantity', part.quantity) or 0
        part.minimum_stock = request.POST.get('minimum_stock', part.minimum_stock) or 5
        supplier_id = request.POST.get('supplier') or None
        part.supplier_id = supplier_id
        part.save()
        messages.success(request, f'{part.name} обновлена.')
        return redirect('parts_list')
    return render(request, 'parts/edit.html', {'part': part, 'suppliers': suppliers})


@login_required
def part_delete_view(request, pk):
    if request.user.role != 'admin':
        return redirect('parts_list')
    part = get_object_or_404(Part, pk=pk)
    if request.method == 'POST':
        part.delete()
        messages.success(request, f'Запчасть «{part.name}» удалена.')
        return redirect('parts_list')
    return redirect('parts_list')


class PartViewSet(viewsets.ModelViewSet):
    queryset = Part.objects.select_related('supplier').all()
    serializer_class = PartSerializer
    permission_classes = [IsAdminOrManager]
    search_fields = ['name', 'part_number']
    filterset_fields = ['supplier', 'is_active']
