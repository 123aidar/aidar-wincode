from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Delivery, DeliveryItem
from suppliers.models import Supplier
from parts.models import Part


@login_required
def deliveries_list_view(request):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    deliveries = Delivery.objects.select_related('supplier', 'created_by').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    return render(request, 'deliveries/list.html', {
        'deliveries': deliveries,
        'status_filter': status_filter,
        'statuses': Delivery.Status.choices,
    })


@login_required
def delivery_create_view(request):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    suppliers = Supplier.objects.filter(is_active=True)
    parts = Part.objects.filter(is_active=True)
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        delivery_date = request.POST.get('delivery_date')
        notes = request.POST.get('notes', '').strip()

        part_ids = request.POST.getlist('part_id')
        quantities = request.POST.getlist('quantity')
        unit_prices = request.POST.getlist('unit_price')

        if not supplier_id or not delivery_date or not part_ids:
            messages.error(request, 'Заполните все обязательные поля и добавьте хотя бы одну позицию.')
            return render(request, 'deliveries/create.html', {'suppliers': suppliers, 'parts': parts})

        with transaction.atomic():
            delivery = Delivery.objects.create(
                supplier_id=supplier_id,
                delivery_date=delivery_date,
                notes=notes,
                created_by=request.user,
                status=Delivery.Status.CONFIRMED,
            )
            for pid, qty, price in zip(part_ids, quantities, unit_prices):
                if pid and qty and price:
                    DeliveryItem.objects.create(
                        delivery=delivery,
                        part_id=int(pid),
                        quantity=int(qty),
                        unit_price=price,
                    )
            delivery.recalc_total()

        messages.success(request, f'Поставка {delivery.invoice_number} создана.')
        return redirect('delivery_detail', pk=delivery.pk)

    return render(request, 'deliveries/create.html', {
        'suppliers': suppliers,
        'parts': parts,
    })


@login_required
def delivery_detail_view(request, pk):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    delivery = get_object_or_404(
        Delivery.objects.select_related('supplier', 'created_by')
                        .prefetch_related('items__part'),
        pk=pk
    )
    return render(request, 'deliveries/detail.html', {'delivery': delivery})


@login_required
def delivery_delete_view(request, pk):
    if request.user.role != 'admin':
        return redirect('deliveries_list')
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.method == 'POST':
        delivery.delete()
        messages.success(request, 'Поставка удалена.')
        return redirect('deliveries_list')
    return redirect('deliveries_list')


@login_required
def delivery_receive_view(request, pk):
    """Принять поставку — зачислить запчасти на склад."""
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.method == 'POST':
        if delivery.status != Delivery.Status.RECEIVED:
            delivery.apply_to_stock()
            delivery.status = Delivery.Status.RECEIVED
            delivery.save(update_fields=['status'])
            messages.success(request, f'Поставка {delivery.invoice_number} принята. Запчасти зачислены на склад.')
        else:
            messages.info(request, 'Поставка уже была принята ранее.')
    return redirect('delivery_detail', pk=pk)


@login_required
def delivery_cancel_view(request, pk):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.method == 'POST':
        if delivery.status not in (Delivery.Status.RECEIVED, Delivery.Status.CANCELLED):
            delivery.status = Delivery.Status.CANCELLED
            delivery.save(update_fields=['status'])
            messages.success(request, f'Поставка {delivery.invoice_number} отменена.')
        else:
            messages.error(request, 'Нельзя отменить уже принятую или отменённую поставку.')
    return redirect('delivery_detail', pk=pk)


@login_required
def delivery_invoice_view(request, pk):
    """Страница накладной — красивая, для печати."""
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    delivery = get_object_or_404(
        Delivery.objects.select_related('supplier', 'created_by')
                        .prefetch_related('items__part'),
        pk=pk
    )
    return render(request, 'deliveries/invoice.html', {'delivery': delivery})
